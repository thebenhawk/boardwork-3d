"""
Agent #5: Friction & Torque
Calculates friction force and torque on the ball from contact patch state

Input: Ball properties, contact patch (area, normal force, mu), velocity, angular velocity
Output: FrictionState with force vector, torque vector, spin decrement
Validation: Friction opposes motion, torque = r × f, energy dissipation monotonic
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class FrictionState:
    """Friction force and torque from lane contact"""
    friction_force_n: np.ndarray  # (fx, fy, fz) in Newtons, world frame
    torque_n_m: np.ndarray  # (tx, ty, tz) in Newton-meters, world frame
    friction_magnitude_n: float  # Magnitude of friction force
    torque_magnitude_n_m: float  # Magnitude of torque
    slip_ratio: float  # Ratio of slide to roll (measure of skid)

    def to_dict(self) -> dict:
        return {
            "friction_force_n": self.friction_force_n.tolist(),
            "torque_n_m": self.torque_n_m.tolist(),
            "friction_magnitude_n": float(self.friction_magnitude_n),
            "torque_magnitude_n_m": float(self.torque_magnitude_n_m),
            "slip_ratio": float(self.slip_ratio),
        }


def create_friction_state(
    ball_mass_kg: float = 7.257,  # 16 lbs
    ball_radius_m: float = 0.108,  # 4.25 inches
    velocity: np.ndarray = None,  # (vx, vy, vz) ft/s
    angular_velocity: np.ndarray = None,  # (wx, wy, wz) rad/s
    friction_coefficient: float = 0.12,  # From contact patch (oil-dependent)
    normal_force_n: float = 135.3,  # From contact patch
) -> FrictionState:
    """
    Agent #5: Calculate friction force and torque on the ball

    Physics model:
    - Friction force opposes relative velocity at contact point: f = -mu * N * v_hat
    - Torque is perpendicular to force: tau = r × f (where r is contact radius)
    - Spin is reduced by friction: omega decays as torque opposes rotation
    - Slip ratio = v_slip / v_roll measures skidding vs. pure rolling

    Args:
        ball_mass_kg: Ball mass in kg (default 16 lbs = 7.257 kg)
        ball_radius_m: Ball radius in meters (4.25 in = 0.108 m)
        velocity: Velocity vector (vx, vy, vz) in ft/s, default [0, 27, 0]
        angular_velocity: Angular velocity (wx, wy, wz) in rad/s, default [50, 0, 80]
        friction_coefficient: Friction coefficient (0.04-0.20)
        normal_force_n: Normal force in Newtons

    Returns:
        FrictionState with friction force, torque, and slip metrics
    """

    if velocity is None:
        velocity = np.array([0.0, 27.0, 0.0], dtype=np.float32)
    if angular_velocity is None:
        angular_velocity = np.array([50.0, 0.0, 80.0], dtype=np.float32)

    # Convert velocity from ft/s to m/s for SI calculations
    velocity_m_s = velocity * 0.3048  # 1 ft/s = 0.3048 m/s

    # Velocity magnitude
    v_mag = np.linalg.norm(velocity_m_s)

    # Calculate slip velocity at contact point
    # Contact point is at bottom of ball: r_contact = -R * z_hat (downward)
    # v_contact = v_cm + omega × r_contact
    # For straight motion down lane (Y): r_contact = [0, 0, -R]
    # v_slip = v - R*omega_x (lateral slip from X-axis spin)

    # Slip velocity components:
    # - Longitudinal slip: v_y - R * omega_x (roll slip in Y direction)
    # - Lateral slip: v_x + R * omega_z (skid slip in X direction from Z-spin)

    ball_radius_ft = ball_radius_m / 0.3048  # Convert back to ft for consistency with velocity units

    # Slip velocity in ft/s
    slip_long = velocity[1] - ball_radius_ft * angular_velocity[0]  # Lane direction slip
    slip_lat = velocity[0] + ball_radius_ft * angular_velocity[2]  # Lateral slip
    slip_vert = velocity[2]  # Vertical component (minimal, ball on lane)

    slip_velocity_ft_s = np.array([slip_lat, slip_long, slip_vert], dtype=np.float32)
    slip_mag_ft_s = np.linalg.norm(slip_velocity_ft_s)

    # Friction force opposes slip direction
    # If there's no slip, friction is static (just enough to prevent sliding)
    # If there is slip, friction is kinetic and points opposite to slip

    if slip_mag_ft_s > 0.01:  # Has significant slip
        slip_direction = slip_velocity_ft_s / slip_mag_ft_s
        # Friction opposes slip
        friction_force_direction = -slip_direction
    else:  # Rolling without slip (pure roll)
        # Friction is static and minimal, mainly due to rolling resistance
        # Point opposite to velocity direction (gentle braking)
        if v_mag > 0.01:
            friction_force_direction = -velocity_m_s / (v_mag * 0.3048)
        else:
            friction_force_direction = np.array([0.0, -1.0, 0.0], dtype=np.float32)

    # Friction force magnitude: F_friction = mu * N
    friction_force_magnitude_n = friction_coefficient * normal_force_n

    # Friction force vector in SI units (convert back to ft/s output)
    friction_force_n = friction_force_magnitude_n * friction_force_direction

    # Torque from friction: tau = r × F
    # r is the moment arm from ball center to contact point
    # Contact point is at -R in z-direction (below ball center)
    # In world frame, for a ball rolling down lane:
    # r_contact = [0, 0, -ball_radius_m]
    # tau = r × F

    r_contact = np.array([0.0, 0.0, -ball_radius_m], dtype=np.float32)
    torque_n_m = np.cross(r_contact, friction_force_n)

    # Slip ratio: measure of sliding vs. rolling
    # At pure roll: slip_ratio = 0
    # At full slide: slip_ratio = infinity (or capped at high value)
    if v_mag > 0.01:
        slip_ratio = slip_mag_ft_s / (v_mag * 3.28084)  # Convert m/s back to ft/s
    else:
        slip_ratio = 0.0

    slip_ratio = min(slip_ratio, 2.0)  # Cap at 2.0 for stability

    return FrictionState(
        friction_force_n=friction_force_n,
        torque_n_m=torque_n_m,
        friction_magnitude_n=friction_force_magnitude_n,
        torque_magnitude_n_m=np.linalg.norm(torque_n_m),
        slip_ratio=slip_ratio,
    )


def validate_friction_state(fs: FrictionState, velocity: np.ndarray) -> dict:
    """
    Validate Agent #5 output against success criteria

    Success Criteria:
    - Friction force non-zero and reasonable magnitude (5-27 N for typical bowling)
    - Friction opposes velocity (dot product < 0)
    - Torque non-zero (rotation induced by friction)
    - Torque magnitude scales with friction force (tau ≈ R × F)
    - Slip ratio in [0, 2] (0=pure roll, high=skidding)
    - Energy dissipation from friction is positive (work done against motion)
    """
    results = {
        "friction_mag": fs.friction_magnitude_n,
        "torque_mag": fs.torque_magnitude_n_m,
        "passed": True,
        "checks": [],
    }

    # Check 1: Friction force magnitude reasonable (F = mu * N, mu in [0.04, 0.20], N ~135 N)
    # Expected range: 0.04*135 to 0.20*135 = 5.4 to 27 N
    friction_valid = 0.1 < fs.friction_magnitude_n < 30.0
    results["checks"].append(
        {
            "name": "Friction magnitude (5-27 N typical)",
            "passed": friction_valid,
            "value": f"{fs.friction_magnitude_n:.3f} N",
        }
    )
    if not friction_valid:
        results["passed"] = False

    # Check 2: Friction opposes velocity (should have negative dot product)
    if np.linalg.norm(velocity) > 0.1:
        dot_product = np.dot(fs.friction_force_n, velocity)
        friction_opposes = dot_product < 0
    else:
        friction_opposes = True  # Stationary case, skip check

    results["checks"].append(
        {
            "name": "Friction opposes velocity",
            "passed": friction_opposes,
            "dot_product": f"{dot_product:.3f}" if np.linalg.norm(velocity) > 0.1 else "N/A",
        }
    )
    if not friction_opposes and np.linalg.norm(velocity) > 0.1:
        results["passed"] = False

    # Check 3: Torque non-zero (friction creates rotation)
    torque_valid = fs.torque_magnitude_n_m > 0.01
    results["checks"].append(
        {
            "name": "Torque induced by friction",
            "passed": torque_valid,
            "value": f"{fs.torque_magnitude_n_m:.4f} N·m",
        }
    )
    if not torque_valid:
        results["passed"] = False

    # Check 4: Torque scales with friction (tau ≈ R × F)
    # Magnitude should be roughly friction_force * ball_radius
    ball_radius_m = 0.108
    expected_torque_mag = fs.friction_magnitude_n * ball_radius_m
    torque_scale_valid = abs(fs.torque_magnitude_n_m - expected_torque_mag) / (expected_torque_mag + 0.001) < 0.5
    results["checks"].append(
        {
            "name": "Torque = R × F relationship",
            "passed": torque_scale_valid,
            "actual": f"{fs.torque_magnitude_n_m:.4f}",
            "expected": f"{expected_torque_mag:.4f}",
        }
    )
    if not torque_scale_valid:
        results["passed"] = False

    # Check 5: Slip ratio in [0, 2]
    slip_valid = 0.0 <= fs.slip_ratio <= 2.0
    results["checks"].append(
        {
            "name": "Slip ratio [0, 2]",
            "passed": slip_valid,
            "value": f"{fs.slip_ratio:.3f}",
        }
    )
    if not slip_valid:
        results["passed"] = False

    # Check 6: Energy dissipation is positive (friction does negative work)
    velocity_mag_m_s = np.linalg.norm(velocity) * 0.3048
    if velocity_mag_m_s > 0.1:
        power_dissipated = -np.dot(fs.friction_force_n, velocity * 0.3048)  # Negative work = energy loss
        energy_valid = power_dissipated > 0  # Friction should dissipate energy (do negative work on ball)
    else:
        energy_valid = True
        power_dissipated = 0.0

    results["checks"].append(
        {
            "name": "Energy dissipation positive (friction brakes ball)",
            "passed": energy_valid,
            "power": f"{power_dissipated:.3f} W" if velocity_mag_m_s > 0.1 else "N/A",
        }
    )
    if not energy_valid and velocity_mag_m_s > 0.1:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #5: Friction & Torque - Test Suite")
    print("=" * 60)

    # Test cases: different oil conditions and ball states
    test_cases = [
        {
            "name": "Oiled lane, rolling",
            "velocity": np.array([0.0, 27.0, 0.0], dtype=np.float32),
            "angular_velocity": np.array([50.0, 0.0, 80.0], dtype=np.float32),
            "mu": 0.04,
        },
        {
            "name": "Transition, some slip",
            "velocity": np.array([2.0, 26.0, 0.0], dtype=np.float32),
            "angular_velocity": np.array([40.0, 0.0, 70.0], dtype=np.float32),
            "mu": 0.12,
        },
        {
            "name": "Dry lane, high slip",
            "velocity": np.array([5.0, 25.0, 0.0], dtype=np.float32),
            "angular_velocity": np.array([20.0, 0.0, 50.0], dtype=np.float32),
            "mu": 0.20,
        },
    ]

    for test in test_cases:
        print(f"\nTest: {test['name']}")
        fs = create_friction_state(
            velocity=test["velocity"],
            angular_velocity=test["angular_velocity"],
            friction_coefficient=test["mu"],
        )
        validation = validate_friction_state(fs, test["velocity"])

        status = "✓ PASS" if validation["passed"] else "✗ FAIL"
        print(f"Status: {status}")
        print(f"  Friction: {fs.friction_magnitude_n:.3f} N")
        print(f"  Torque: {fs.torque_magnitude_n_m:.4f} N·m")
        print(f"  Slip Ratio: {fs.slip_ratio:.3f}")

        for check in validation["checks"]:
            check_status = "✓" if check["passed"] else "✗"
            print(f"  {check_status} {check['name']}")

    print("\n" + "=" * 60)
    print("Agent #5 ready for integration with Agent #4")
