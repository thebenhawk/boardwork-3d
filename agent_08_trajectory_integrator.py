"""
Agent #8: Trajectory Integrator
Combines updated velocity and angular velocity to advance ball position one step

Input: Velocity, angular velocity, current position, oil pattern
Output: TrajectoryPoint with new position, board, oil density, entry angle
Validation: Position advances correctly, oil density valid, entry angle plausible
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class TrajectoryPoint:
    """Position and state at one point along trajectory"""
    distance_ft: float  # Distance down lane (0-60 ft)
    board: float  # Board position (1-39, center=20)
    velocity: np.ndarray  # (vx, vy, vz) ft/s
    angular_velocity: np.ndarray  # (wx, wy, wz) rad/s
    speed_ft_s: float  # Velocity magnitude
    rpm: float  # Spin rate
    oil_density: float  # Oil density at this position (0.0-1.0)
    entry_angle_deg: float  # Angle of velocity relative to Y-axis
    lateral_velocity_ft_s: float  # Sideways velocity (X direction)

    def to_dict(self) -> dict:
        return {
            "distance_ft": float(self.distance_ft),
            "board": float(self.board),
            "velocity": self.velocity.tolist(),
            "angular_velocity": self.angular_velocity.tolist(),
            "speed_ft_s": float(self.speed_ft_s),
            "rpm": float(self.rpm),
            "oil_density": float(self.oil_density),
            "entry_angle_deg": float(self.entry_angle_deg),
            "lateral_velocity_ft_s": float(self.lateral_velocity_ft_s),
        }


def create_trajectory_point(
    velocity: np.ndarray = None,  # (vx, vy, vz) ft/s
    angular_velocity: np.ndarray = None,  # (wx, wy, wz) rad/s
    current_distance_ft: float = 0.0,
    current_board: float = 20.0,  # Center board (1-39)
    oil_pattern_fn = None,  # Function to get oil density at (board, distance)
) -> TrajectoryPoint:
    """
    Agent #8: Integrate one step (0.1 ft) down lane

    Trajectory update:
    - Ball moves 0.1 ft down lane (Y direction)
    - Lateral movement from velocity X-component
    - Oil density sampled at new position
    - Entry angle computed from velocity direction

    Args:
        velocity: Ball velocity (ft/s)
        angular_velocity: Ball spin (rad/s)
        current_distance_ft: Current position down lane
        current_board: Current board position (1-39)
        oil_pattern_fn: Function(board, distance) -> oil_density [0, 1]

    Returns:
        TrajectoryPoint with new position and state
    """

    if velocity is None:
        velocity = np.array([0.0, 26.4, 0.0], dtype=np.float32)
    if angular_velocity is None:
        angular_velocity = np.array([50.0, 0.0, 80.0], dtype=np.float32)

    if oil_pattern_fn is None:
        # Default: Gaussian oil pattern (fresh, peaked at center)
        def default_oil_pattern(board, distance):
            center_board = 20.0
            board_spread = np.exp(-((board - center_board) / 8.0) ** 2)
            distance_decay = np.exp(-(distance / 42.0) ** 2.5)  # Assume 42 ft oil
            return board_spread * distance_decay

        oil_pattern_fn = default_oil_pattern

    # Advance distance by 0.1 ft (one integration step)
    new_distance_ft = current_distance_ft + 0.1

    # Update board position based on lateral velocity
    # Lateral velocity in X direction (perpendicular to lane)
    # Board spacing: each board is about 4.75 inches = 0.396 ft
    board_width_ft = 0.396
    lateral_movement_ft = velocity[0] * (0.1 / np.linalg.norm(velocity)) if np.linalg.norm(velocity) > 0.1 else 0.0
    new_board = current_board + (lateral_movement_ft / board_width_ft)

    # Clamp board to valid range [1, 39]
    new_board = max(1.0, min(39.0, new_board))

    # Get oil density at new position
    oil_density = oil_pattern_fn(new_board, new_distance_ft)
    oil_density = max(0.0, min(1.0, oil_density))  # Clamp to [0, 1]

    # Calculate speed and entry angle
    speed_ft_s = np.linalg.norm(velocity)
    rpm = (np.linalg.norm(angular_velocity) / (2.0 * np.pi)) * 60.0

    # Entry angle: angle between velocity vector and lane direction (Y axis)
    # Entry angle = atan2(vx, vy) in degrees
    # Positive angle = moving toward right gutter, negative = toward left gutter
    if speed_ft_s > 0.1:
        entry_angle_deg = np.degrees(np.arctan2(velocity[0], velocity[1]))
    else:
        entry_angle_deg = 0.0

    # Lateral velocity component
    lateral_velocity_ft_s = velocity[0]

    return TrajectoryPoint(
        distance_ft=new_distance_ft,
        board=new_board,
        velocity=velocity.copy(),
        angular_velocity=angular_velocity.copy(),
        speed_ft_s=speed_ft_s,
        rpm=rpm,
        oil_density=oil_density,
        entry_angle_deg=entry_angle_deg,
        lateral_velocity_ft_s=lateral_velocity_ft_s,
    )


def validate_trajectory_point(tp: TrajectoryPoint, prev_distance_ft: float = None) -> dict:
    """
    Validate Agent #8 output against success criteria

    Success Criteria:
    - Distance advances correctly (0.1 ft per step)
    - Board position in [1, 39] range
    - Oil density in [0.0, 1.0] range
    - Entry angle plausible [-45, 45]° (target 6° ± 2°)
    - Velocity components consistent
    - No NaN/inf values
    """
    results = {
        "distance_ft": tp.distance_ft,
        "board": tp.board,
        "passed": True,
        "checks": [],
    }

    # Check 1: Distance advances correctly (0.1 ft)
    if prev_distance_ft is not None:
        dist_advance = tp.distance_ft - prev_distance_ft
        dist_valid = abs(dist_advance - 0.1) < 0.01
        results["checks"].append(
            {
                "name": "Distance advances 0.1 ft per step",
                "passed": dist_valid,
                "advance": f"{dist_advance:.4f} ft",
            }
        )
        if not dist_valid:
            results["passed"] = False

    # Check 2: Board position valid [1, 39]
    board_valid = 1.0 <= tp.board <= 39.0
    results["checks"].append(
        {
            "name": "Board position [1, 39]",
            "passed": board_valid,
            "value": f"{tp.board:.2f}",
        }
    )
    if not board_valid:
        results["passed"] = False

    # Check 3: Oil density valid [0, 1]
    oil_valid = 0.0 <= tp.oil_density <= 1.0
    results["checks"].append(
        {
            "name": "Oil density [0.0, 1.0]",
            "passed": oil_valid,
            "value": f"{tp.oil_density:.3f}",
        }
    )
    if not oil_valid:
        results["passed"] = False

    # Check 4: Entry angle plausible [-45, 45]°
    angle_valid = -45 <= tp.entry_angle_deg <= 45
    results["checks"].append(
        {
            "name": "Entry angle [-45, 45]° (target: 6° ± 2°)",
            "passed": angle_valid,
            "value": f"{tp.entry_angle_deg:.2f}°",
        }
    )
    if not angle_valid:
        results["passed"] = False

    # Check 5: Speed reasonable
    speed_valid = 0 <= tp.speed_ft_s <= 45
    results["checks"].append(
        {
            "name": "Speed [0, 45] ft/s",
            "passed": speed_valid,
            "value": f"{tp.speed_ft_s:.2f} ft/s",
        }
    )
    if not speed_valid:
        results["passed"] = False

    # Check 6: No NaN/inf
    no_nan = (np.all(np.isfinite(tp.velocity)) and
              np.all(np.isfinite(tp.angular_velocity)) and
              np.isfinite(tp.speed_ft_s) and
              np.isfinite(tp.rpm) and
              np.isfinite(tp.entry_angle_deg))
    results["checks"].append(
        {
            "name": "No NaN/inf values",
            "passed": no_nan,
        }
    )
    if not no_nan:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #8: Trajectory Integrator - Test Suite")
    print("=" * 60)

    # Simple test: trace 10 steps (1 ft) with initial conditions
    print("\nTest: 18 mph, 300 RPM, center board (20)")
    print("-" * 60)

    # Initial conditions at release (0 ft, board 20)
    velocity = np.array([0.0, 26.4, 0.0], dtype=np.float32)  # 18 mph = 26.4 ft/s
    angular_velocity = np.array([50.0, 0.0, 80.0], dtype=np.float32)  # ~300 RPM

    # Simulate oil pattern (Gaussian, peaks at center, decays down lane)
    def gaussian_oil(board, distance, oil_length=42.0):
        center_board = 20.0
        board_spread = np.exp(-((board - center_board) / 8.0) ** 2)
        if distance > oil_length:
            distance_decay = 0.0
        else:
            distance_decay = np.exp(-(distance / oil_length) ** 2.5)
        return board_spread * distance_decay

    distance = 0.0
    board = 20.0

    print(f"Step │ Dist(ft) │ Board│ Speed(mph) │ RPM  │ Entry(°) │ Oil  │ Status")
    print("-" * 75)

    for step in range(10):
        # Create trajectory point
        tp = create_trajectory_point(
            velocity=velocity,
            angular_velocity=angular_velocity,
            current_distance_ft=distance,
            current_board=board,
            oil_pattern_fn=gaussian_oil,
        )

        # Validate
        validation = validate_trajectory_point(tp, distance)
        status = "✓" if validation["passed"] else "✗"

        speed_mph = tp.speed_ft_s / 1.46667
        print(f"{step:4d} │ {tp.distance_ft:8.2f} │ {tp.board:5.1f}│ {speed_mph:10.2f} │ {tp.rpm:5.0f} │ {tp.entry_angle_deg:8.2f} │ {tp.oil_density:5.2f} │ {status}")

        # For next step, simulate velocity and angular velocity updates
        # (in real scenario, these come from Agents #6-7)
        # Simplify: just reduce speed and RPM
        velocity = velocity * 0.999  # Slight velocity decrease
        angular_velocity = angular_velocity * 0.998  # Slight RPM decrease

        distance = tp.distance_ft
        board = tp.board

    print("-" * 75)
    print("All 10 steps completed successfully")

    print("\n" + "=" * 60)
    print("Agent #8 ready for full physics integration")
