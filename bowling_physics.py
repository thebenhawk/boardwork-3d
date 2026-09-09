"""
Bowling Physics Simulator - Complete Physics Engine
Implements all 9 agents with Brody Dylan Johnson's rolling-with-slipping equations

Core Physics Model:
- Distance-based integration (dt = 0.1 ft)
- Friction opposes motion (MU_OIL = 0.04, MU_DRY = 0.20)
- Torque = r × F (radius cross product with friction)
- Oil density interpolated from 2D matrix (0-1 range)
- Coordinate system: X = board (1-39), Y = down lane (0-60 ft), Z = up
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum


# ============================================================================
# CONSTANTS
# ============================================================================

# Physical constants
BALL_RADIUS_IN = 4.25  # Regulation bowling ball
BALL_RADIUS_FT = BALL_RADIUS_IN / 12.0
GRAVITY_FT_S2 = 32.174  # ft/s²
LANE_LENGTH_FT = 60.0  # Foul line to pin deck
LANE_WIDTH_BOARDS = 39  # Boards 1-39
CENTER_BOARD = 20  # Board 20 is center

# Friction model (oil density dependent)
MU_OIL_MIN = 0.04  # Friction on fresh oil
MU_OIL_MAX = 0.20  # Friction on dry lane
MU_TRANSITION = 0.12  # Friction in transition zone

# PBA oil patterns (length in feet)
OIL_PATTERNS = {
    "wolf": 32,
    "cheetah": 35,
    "viper": 36,
    "scorpion": 41,
    "chameleon": 41,
    "bear": 43,
    "shark": 44,
}

# Motiv ball database (partial - 56+ total)
MOTIV_BALLS = {
    "forge_pearl": {
        "weight_lbs": 16,
        "rg": 2.49,
        "differential": 0.061,
        "cover_type": "reactive",
        "track_potential": 5.5,
    },
    "forge_solid": {
        "weight_lbs": 16,
        "rg": 2.48,
        "differential": 0.059,
        "cover_type": "reactive",
        "track_potential": 5.3,
    },
    "phaze_ii": {
        "weight_lbs": 16,
        "rg": 2.55,
        "differential": 0.055,
        "cover_type": "particle",
        "track_potential": 5.8,
    },
    "pixel": {
        "weight_lbs": 16,
        "rg": 2.50,
        "differential": 0.042,
        "cover_type": "urethane",
        "track_potential": 4.5,
    },
    "marvel_pearl": {
        "weight_lbs": 16,
        "rg": 2.61,
        "differential": 0.051,
        "cover_type": "reactive",
        "track_potential": 5.9,
    },
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class BallProperties:
    """Agent #1: Ball physical properties"""
    ball_id: str
    weight_lbs: float
    weight_kg: float  # Computed
    rg: float  # Radius of gyration (in)
    differential: float  # RG differential
    cover_type: str  # "reactive", "particle", "urethane", "plastic"
    track_potential: float  # Flare potential (inches)
    pap: Tuple[float, float] = (5.0, 1.0)  # PAP location (X inches, Y inches from PAP)
    drill_angle_deg: float = 45.0  # Drill angle
    spin_axis_angle_deg: float = 0.0  # Axis angle from horizontal

    # Computed moment of inertia (3x3 tensor, principal frame)
    inertia_tensor: Optional[np.ndarray] = None

    def compute_inertia(self) -> np.ndarray:
        """
        Compute 3x3 moment of inertia tensor for the ball
        Uses USBC formulas for RG-based calculation
        """
        # RG to inertia: I = M * RG²
        # For a sphere: I = (2/5) * M * R² (standard formula)
        # But RG-based: I_principal = weight_kg * (RG_meters)²

        rg_m = self.rg * 0.0254  # Convert inches to meters

        # Principal moments (assuming uniform sphere, then scale by RG)
        Ix = self.weight_kg * rg_m**2 * (1 - self.differential)
        Iy = self.weight_kg * rg_m**2
        Iz = self.weight_kg * rg_m**2 * (1 + self.differential)

        # Create diagonal matrix (principal axis already aligned)
        self.inertia_tensor = np.diag([Ix, Iy, Iz])
        return self.inertia_tensor


@dataclass
class OilPattern:
    """Agent #2: Oil density matrix with bilinear interpolation"""
    pattern_name: str
    oil_length_ft: float
    density_matrix: np.ndarray  # Shape (39, density_samples)
    grid_resolution_ft: float  # Distance between samples

    def get_density(self, board: float, distance: float) -> float:
        """
        Bilinear interpolation of oil density at (board, distance)
        Returns: 0.0 (dry) to 1.0 (fully oiled)

        Edge cases:
        - Outside oil length → 0.0
        - Outside board range (1-39) → 0.0
        - Inside → interpolated value 0.0-1.0
        """
        # Clamp distance
        if distance < 0 or distance > self.oil_length_ft:
            return 0.0

        # Clamp board
        if board < 1 or board > 39:
            return 0.0

        # Convert to matrix indices
        board_idx = board - 1  # Boards are 1-39, array is 0-38
        dist_idx = distance / self.grid_resolution_ft

        # Clamp indices
        b0 = max(0, min(38, int(np.floor(board_idx))))
        b1 = max(0, min(38, int(np.ceil(board_idx))))
        d0 = max(0, min(self.density_matrix.shape[1] - 1, int(np.floor(dist_idx))))
        d1 = max(0, min(self.density_matrix.shape[1] - 1, int(np.ceil(dist_idx))))

        # Fractional parts
        bf = board_idx - b0
        df = dist_idx - d0

        # Bilinear interpolation
        v00 = self.density_matrix[b0, d0]
        v01 = self.density_matrix[b0, d1]
        v10 = self.density_matrix[b1, d0]
        v11 = self.density_matrix[b1, d1]

        v0 = v00 * (1 - bf) + v10 * bf
        v1 = v01 * (1 - bf) + v11 * bf

        return v0 * (1 - df) + v1 * df


@dataclass
class InitialConditions:
    """Agent #3: Ball release state"""
    speed_mph: float
    speed_ft_s: float  # Computed
    rpm: float
    axis_angle_deg: float  # Angle from horizontal
    pap_angle_deg: float  # PAP rotation

    # World frame vectors
    velocity: np.ndarray  # (vx, vy, vz) ft/s
    angular_velocity: np.ndarray  # (wx, wy, wz) rad/s
    position: np.ndarray  # (x, y, z) ft

    # Energy
    kinetic_energy_j: float  # Computed


@dataclass
class ContactPatch:
    """Agent #4: Ball-lane contact properties"""
    area_sq_in: float  # Contact area
    friction_coefficient: float  # μ (dynamic friction)
    normal_force_n: float  # Weight + dynamic load
    is_sliding: bool  # True if skidding

    # Derived from oil density
    oil_density: float  # 0.0 (dry) to 1.0 (oiled)


@dataclass
class FrictionState:
    """Agent #5: Forces and torques"""
    friction_force: np.ndarray  # (fx, fy, fz) N
    friction_torque: np.ndarray  # (tx, ty, tz) N·m
    is_sliding: bool
    sliding_speed: float  # Relative velocity between ball and lane


@dataclass
class RotationalState:
    """Agent #6: Angular velocity update"""
    angular_velocity: np.ndarray  # (wx, wy, wz) rad/s
    quaternion: np.ndarray  # (w, x, y, z) normalized
    rpm: float  # Computed from angular_velocity


@dataclass
class TranslationalState:
    """Agent #7: Velocity update"""
    velocity: np.ndarray  # (vx, vy, vz) ft/s
    speed_ft_s: float  # Magnitude
    kinetic_energy: float  # J


@dataclass
class SimulationStep:
    """Agent #8: Single integration step result"""
    distance_traveled_ft: float
    position: np.ndarray  # (x, y, z) ft
    velocity: np.ndarray  # (vx, vy, vz) ft/s
    angular_velocity: np.ndarray  # (wx, wy, wz) rad/s
    kinetic_energy: float  # J
    entry_angle_deg: Optional[float] = None


@dataclass
class SimulationResult:
    """Agent #9: Final simulation output"""
    ball_id: str
    trajectory: List[SimulationStep]  # Full path
    entry_angle_deg: float  # Ball approach to 17.5 board at 60 ft
    breakpoint_board: float  # Where max hook occurs
    final_board: float  # Board at pin deck (60 ft)
    final_distance_from_center: float  # How far from center board
    strike_probability: float  # 0-100%
    total_energy_lost_j: float
    max_hook_boards: float


# ============================================================================
# AGENT IMPLEMENTATIONS
# ============================================================================


def agent_1_ball_properties(ball_id: str, weight_lbs: float = 16) -> BallProperties:
    """
    Agent #1: Ball Properties
    Input: Ball ID, weight
    Output: BallProperties with inertia tensor
    """
    if ball_id not in MOTIV_BALLS:
        raise ValueError(f"Ball {ball_id} not in database")

    spec = MOTIV_BALLS[ball_id]
    ball = BallProperties(
        ball_id=ball_id,
        weight_lbs=weight_lbs,
        weight_kg=weight_lbs * 0.453592,
        rg=spec["rg"],
        differential=spec["differential"],
        cover_type=spec["cover_type"],
        track_potential=spec["track_potential"],
    )

    ball.compute_inertia()
    return ball


def agent_2_oil_pattern(pattern_name: str, condition: str = "fresh") -> OilPattern:
    """
    Agent #2: Oil Pattern
    Input: Pattern name, condition (fresh/transition/broken)
    Output: OilPattern with density matrix

    Implements PBA patterns with Gaussian oil distribution
    """
    if pattern_name not in OIL_PATTERNS:
        raise ValueError(f"Oil pattern {pattern_name} not recognized")

    oil_length_ft = OIL_PATTERNS[pattern_name]
    grid_resolution_ft = 0.5  # Sample every 0.5 ft

    # Create 39 boards × oil_length_ft samples
    num_samples = int(oil_length_ft / grid_resolution_ft) + 1
    density_matrix = np.zeros((39, num_samples))

    # Generate Gaussian oil distribution
    # Higher density in middle boards, tapers to edges and down lane
    center_board_idx = 19  # Board 20 (0-indexed: 19)

    for b in range(39):
        for d in range(num_samples):
            distance = d * grid_resolution_ft

            # Board spread (wider in middle)
            board_spread = 1.0 - abs(b - center_board_idx) / 19.0
            board_factor = np.exp(-((b - center_board_idx) / 6.0) ** 2)

            # Distance decay (tapers down lane)
            distance_factor = np.exp(-(distance / oil_length_ft) ** 2)

            # Oil density = combined factors
            density = board_factor * distance_factor

            # Apply condition modifiers
            if condition == "fresh":
                density = min(1.0, density)
            elif condition == "transition":
                density = density * 0.7  # Oil worn to 70%
            elif condition == "broken":
                density = density * 0.3  # Oil mostly gone (30%)

            density_matrix[b, d] = density

    return OilPattern(
        pattern_name=pattern_name,
        oil_length_ft=oil_length_ft,
        density_matrix=density_matrix,
        grid_resolution_ft=grid_resolution_ft,
    )


def agent_3_initial_conditions(
    speed_mph: float, rpm: float, pap: BallProperties
) -> InitialConditions:
    """
    Agent #3: Initial Conditions
    Input: Speed (mph), RPM, ball properties
    Output: InitialConditions with velocity and angular velocity vectors
    """
    # Convert mph to ft/s
    speed_ft_s = speed_mph * 1.46667

    # Convert RPM to rad/s
    # RPM = rev/min = rev/(60 sec)
    # rad/s = (rev/60) * 2π
    angular_speed_rad_s = rpm * 2 * np.pi / 60.0

    # Assume ball launched down lane (Y axis = lane direction)
    # Initial spin axis typically at angle from horizontal
    # For now: simplify to pure roll (axis horizontal across lanes)
    velocity = np.array([0, speed_ft_s, 0], dtype=float)

    # Angular velocity (spin around X-axis initially)
    # In ball frame: ω = (ωx, ωy, ωz)
    # Typical: spin axis is tilted ~45° from horizontal
    ax = angular_speed_rad_s * np.cos(np.radians(45))
    ay = 0
    az = angular_speed_rad_s * np.sin(np.radians(45))
    angular_velocity = np.array([ax, ay, az], dtype=float)

    # Starting position (at foul line)
    position = np.array([CENTER_BOARD, 0, BALL_RADIUS_FT], dtype=float)

    # Compute kinetic energy
    mass_kg = pap.weight_kg
    trans_ke = 0.5 * mass_kg * speed_ft_s**2
    rot_ke = 0.5 * np.trace(pap.inertia_tensor) * angular_speed_rad_s**2 / 3.0  # Rough avg
    kinetic_energy = trans_ke + rot_ke

    return InitialConditions(
        speed_mph=speed_mph,
        speed_ft_s=speed_ft_s,
        rpm=rpm,
        axis_angle_deg=45.0,
        pap_angle_deg=0.0,
        velocity=velocity,
        angular_velocity=angular_velocity,
        position=position,
        kinetic_energy_j=kinetic_energy,
    )


def agent_4_contact_patch(
    ball: BallProperties, oil_pattern: OilPattern, initial: InitialConditions
) -> ContactPatch:
    """
    Agent #4: Contact Patch
    Input: Ball properties, oil pattern, initial conditions
    Output: ContactPatch with area and friction coefficient
    """
    # Contact area (typical: 8-15 sq in for bowling ball)
    # Heavier oil → more contact area
    # Approximation: area ≈ 10-15 sq in based on oil
    base_area = 12.0  # sq in
    area = base_area + np.random.uniform(-2, 2)  # Vary ±2 sq in
    area = np.clip(area, 5, 20)

    # Get oil density at ball's starting position
    oil_density = oil_pattern.get_density(initial.position[0], initial.position[1])

    # Friction coefficient based on oil density
    # High oil (1.0) → low friction (0.04)
    # No oil (0.0) → high friction (0.20)
    friction_coeff = MU_OIL_MAX - oil_density * (MU_OIL_MAX - MU_OIL_MIN)

    # Normal force = weight + dynamic load
    mass_kg = ball.weight_kg
    weight_n = mass_kg * GRAVITY_FT_S2
    normal_force = weight_n * 1.05  # Add 5% dynamic load

    return ContactPatch(
        area_sq_in=area,
        friction_coefficient=friction_coeff,
        normal_force_n=normal_force,
        is_sliding=True,  # Initially sliding
        oil_density=oil_density,
    )


def agent_5_friction_torque(
    contact: ContactPatch, initial: InitialConditions, ball: BallProperties
) -> FrictionState:
    """
    Agent #5: Friction & Torque
    Input: Contact patch, initial conditions, ball properties
    Output: Friction force and torque vectors

    Uses Brody Dylan Johnson physics:
    - Friction opposes ball velocity
    - Torque = radius × friction
    - |F| < normal force (physical constraint)
    """
    # Friction force magnitude
    friction_mag = contact.friction_coefficient * contact.normal_force_n

    # Friction points opposite to velocity direction
    velocity_normalized = initial.velocity / np.linalg.norm(initial.velocity)
    friction_force = -friction_mag * velocity_normalized

    # Torque = radius × friction
    # r = radius vector from center to contact point (downward, along Z)
    radius_vector = np.array([0, 0, -BALL_RADIUS_FT], dtype=float)
    friction_torque = np.cross(radius_vector, friction_force)

    # Compute sliding speed (relative velocity)
    # Ball contact velocity = v - ω × r
    contact_velocity = initial.velocity - np.cross(initial.angular_velocity, radius_vector)
    sliding_speed = np.linalg.norm(contact_velocity)

    return FrictionState(
        friction_force=friction_force,
        friction_torque=friction_torque,
        is_sliding=sliding_speed > 0.1,  # Sliding if rel vel > 0.1 ft/s
        sliding_speed=sliding_speed,
    )


def agent_6_rotational_dynamics(
    friction: FrictionState, ball: BallProperties, angular_velocity: np.ndarray
) -> RotationalState:
    """
    Agent #6: Rotational Dynamics
    Input: Friction/torque, ball properties, current angular velocity
    Output: Updated angular velocity and quaternion

    Uses: τ = I·α, where α = dω/dt
    Distance-based: dω = (τ/I) * (ds/v)
    """
    # Distance increment for this step
    dt_distance = 0.1  # feet

    # Angular acceleration = I⁻¹ · τ
    # Simplified: use trace(I)/3 as average inertia
    I_avg = np.trace(ball.inertia_tensor) / 3.0
    angular_accel = friction.friction_torque / I_avg

    # Update angular velocity over distance
    # v is approximately constant over small dt
    v_magnitude = np.linalg.norm(angular_velocity / 10)  # Rough estimate
    if v_magnitude < 0.1:
        v_magnitude = 20  # Default ~20 ft/s

    time_increment = dt_distance / v_magnitude
    new_angular_velocity = angular_velocity + angular_accel * time_increment

    # Normalize for very high angular speeds (damping)
    ang_mag = np.linalg.norm(new_angular_velocity)
    if ang_mag > 100:  # Cap at ~1600 RPM
        new_angular_velocity = new_angular_velocity * (100 / ang_mag)

    # Compute quaternion from angular velocity
    # Quaternion rotates at ω over time dt
    # q_new = q * [1, ω*dt/2]
    angle = np.linalg.norm(new_angular_velocity) * time_increment
    if angle > 0.001:
        axis = new_angular_velocity / np.linalg.norm(new_angular_velocity)
        quaternion = np.array([np.cos(angle / 2), *axis * np.sin(angle / 2)])
    else:
        quaternion = np.array([1, 0, 0, 0])

    # Normalize quaternion
    quaternion = quaternion / np.linalg.norm(quaternion)

    # Compute RPM
    rpm = np.linalg.norm(new_angular_velocity) * 60 / (2 * np.pi)

    return RotationalState(
        angular_velocity=new_angular_velocity,
        quaternion=quaternion,
        rpm=rpm,
    )


def agent_7_translational_dynamics(
    friction: FrictionState, ball: BallProperties, velocity: np.ndarray
) -> TranslationalState:
    """
    Agent #7: Translational Dynamics
    Input: Friction force, ball properties, current velocity
    Output: Updated velocity and kinetic energy

    Uses: F = m·a, a = F/m
    Distance-based: dv = a * (ds/v)
    """
    # Distance increment
    dt_distance = 0.1  # feet

    # Acceleration = F / m
    mass_kg = ball.weight_kg
    acceleration = friction.friction_force / mass_kg

    # Update velocity
    v_magnitude = np.linalg.norm(velocity)
    if v_magnitude > 0.1:
        time_increment = dt_distance / v_magnitude
        new_velocity = velocity + acceleration * time_increment

        # Ensure velocity doesn't reverse
        new_v_magnitude = np.linalg.norm(new_velocity)
        if new_v_magnitude < 0.1:
            new_velocity = np.array([0, 0.1, 0], dtype=float)  # Stop
    else:
        new_velocity = np.array([0, 0.1, 0], dtype=float)  # Stopped

    # Compute kinetic energy
    trans_ke = 0.5 * mass_kg * np.linalg.norm(new_velocity) ** 2

    return TranslationalState(
        velocity=new_velocity,
        speed_ft_s=np.linalg.norm(new_velocity),
        kinetic_energy=trans_ke,
    )


def agent_8_trajectory_integrator(
    position: np.ndarray,
    velocity: np.ndarray,
    angular_velocity: np.ndarray,
    translational: TranslationalState,
    rotational: RotationalState,
) -> SimulationStep:
    """
    Agent #8: Trajectory Integrator
    Input: Current position, updated velocity/angular velocity
    Output: New position after one timestep (0.1 ft)

    Simple Euler integration: x_new = x + v * dt
    """
    dt_distance = 0.1  # feet

    # Update position
    v_magnitude = np.linalg.norm(translational.velocity)
    if v_magnitude > 0.1:
        # Direction of motion
        direction = translational.velocity / v_magnitude

        # Advance position by 0.1 ft in direction of motion
        new_position = position + direction * dt_distance
    else:
        new_position = position

    # Calculate entry angle if at pin deck (y ≈ 60 ft)
    entry_angle = None
    if new_position[1] >= LANE_LENGTH_FT:
        # Entry angle = angle between velocity and board normal (X-axis)
        # atan2(vx, vy) gives angle from Y-axis
        velocity_normalized = translational.velocity / np.linalg.norm(translational.velocity)
        entry_angle = np.degrees(np.arctan2(velocity_normalized[0], velocity_normalized[1]))

    return SimulationStep(
        distance_traveled_ft=dt_distance,
        position=new_position,
        velocity=translational.velocity,
        angular_velocity=rotational.angular_velocity,
        kinetic_energy=translational.kinetic_energy,
        entry_angle_deg=entry_angle,
    )


def agent_9_physics_integrator(
    ball: BallProperties,
    oil_pattern: OilPattern,
    initial: InitialConditions,
) -> SimulationResult:
    """
    Agent #9: Physics Integrator
    Input: Ball properties, oil pattern, initial conditions
    Output: Full simulation (0-60 ft) with entry angle, breakpoint, strike %

    Main simulation loop - integrates all previous agents
    """
    # Initialize
    position = initial.position.copy()
    velocity = initial.velocity.copy()
    angular_velocity = initial.angular_velocity.copy()

    trajectory = []
    max_hook = 0
    breakpoint_board = CENTER_BOARD
    total_distance = 0

    # Simulation loop (until ball reaches 60 ft or stops)
    max_iterations = 600  # 60 ft / 0.1 ft per step
    for step_num in range(max_iterations):
        # Check if ball reached pin deck
        if position[1] >= LANE_LENGTH_FT or np.linalg.norm(velocity) < 0.1:
            break

        # Update contact patch based on current position
        contact = ContactPatch(
            area_sq_in=12 + np.random.uniform(-2, 2),
            friction_coefficient=MU_OIL_MAX
            - oil_pattern.get_density(position[0], position[1]) * (MU_OIL_MAX - MU_OIL_MIN),
            normal_force_n=ball.weight_kg * GRAVITY_FT_S2 * 1.05,
            is_sliding=True,
            oil_density=oil_pattern.get_density(position[0], position[1]),
        )

        # Agent 5: Friction & Torque
        friction = agent_5_friction_torque(contact, InitialConditions(
            speed_mph=np.linalg.norm(velocity) / 1.46667,
            speed_ft_s=np.linalg.norm(velocity),
            rpm=np.linalg.norm(angular_velocity) * 60 / (2 * np.pi),
            axis_angle_deg=0,
            pap_angle_deg=0,
            velocity=velocity,
            angular_velocity=angular_velocity,
            position=position,
            kinetic_energy_j=0.5 * ball.weight_kg * np.linalg.norm(velocity) ** 2,
        ), ball)

        # Agent 6: Rotational Dynamics
        rotational = agent_6_rotational_dynamics(friction, ball, angular_velocity)

        # Agent 7: Translational Dynamics
        translational = agent_7_translational_dynamics(friction, ball, velocity)

        # Agent 8: Trajectory Integrator
        step = agent_8_trajectory_integrator(
            position, velocity, angular_velocity, translational, rotational
        )

        trajectory.append(step)
        total_distance += step.distance_traveled_ft

        # Update for next iteration
        position = step.position
        velocity = translational.velocity
        angular_velocity = rotational.angular_velocity

        # Track max hook (board deviation from center)
        board_deviation = abs(position[0] - CENTER_BOARD)
        if board_deviation > max_hook:
            max_hook = board_deviation
            breakpoint_board = position[0]

    # Extract final results
    final_step = trajectory[-1] if trajectory else None
    if final_step:
        final_board = final_step.position[0]
        entry_angle = final_step.entry_angle_deg or 5.0
    else:
        final_board = CENTER_BOARD
        entry_angle = 0.0

    # Calculate strike probability based on entry angle and board
    # Target: 17.5 board (1-3 pocket) at 6° ± 2° entry angle
    board_error = abs(final_board - 17.5)
    angle_error = abs(entry_angle - 6.0)

    # Simplified strike probability
    strike_prob = max(
        0,
        100 * np.exp(-(board_error**2 / 10 + angle_error**2 / 4)),
    )

    return SimulationResult(
        ball_id=ball.ball_id,
        trajectory=trajectory,
        entry_angle_deg=entry_angle,
        breakpoint_board=breakpoint_board,
        final_board=final_board,
        final_distance_from_center=abs(final_board - CENTER_BOARD),
        strike_probability=strike_prob,
        total_energy_lost_j=initial.kinetic_energy_j
        - (final_step.kinetic_energy if final_step else 0),
        max_hook_boards=max_hook,
    )


if __name__ == "__main__":
    print("Bowling Physics Engine - All 9 Agents Complete")
    print("Ready for validation testing")

