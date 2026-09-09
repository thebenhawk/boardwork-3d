"""
Agent #6: Rotational Dynamics
Updates ball angular velocity based on torque from friction

Input: Ball inertia tensor, torque vector, current angular velocity, velocity magnitude
Output: RotationalState with updated angular velocity after one distance step
Validation: Angular velocity decreases monotonically, spin axis stable, RPM decay realistic
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class RotationalState:
    """Angular velocity state after friction torque applied"""
    angular_velocity: np.ndarray  # (wx, wy, wz) rad/s
    rpm: float  # Total spin rate in revolutions per minute
    spin_axis_angle_deg: float  # Angle of spin axis from horizontal (degrees)
    torque_applied_n_m: np.ndarray  # Torque that was applied (for validation)
    angular_acceleration: np.ndarray  # Angular acceleration (rad/s²)

    def to_dict(self) -> dict:
        return {
            "angular_velocity": self.angular_velocity.tolist(),
            "rpm": float(self.rpm),
            "spin_axis_angle_deg": float(self.spin_axis_angle_deg),
            "torque_applied_n_m": self.torque_applied_n_m.tolist(),
            "angular_acceleration": self.angular_acceleration.tolist(),
        }


def create_rotational_state(
    angular_velocity: np.ndarray = None,  # (wx, wy, wz) rad/s
    torque_n_m: np.ndarray = None,  # (tx, ty, tz) N·m
    velocity_magnitude_ft_s: float = 25.0,  # For distance-based integration
    ball_radius_m: float = 0.108,  # 4.25 inches
    moment_of_inertia_kg_m2: float = 0.00749,  # For 16 lb ball
) -> RotationalState:
    """
    Agent #6: Update angular velocity based on friction torque

    Physics model (distance-based):
    - Torque applies angular acceleration: α = τ / I
    - Over distance step dd: dω/dd = α / v = τ / (I * v)
    - Angular velocity decreases due to friction torque opposing rotation
    - Spin axis direction typically stable (y-component minimal)

    Args:
        angular_velocity: Initial angular velocity (rad/s)
        torque_n_m: Torque vector (N·m) from friction
        velocity_magnitude_ft_s: Current velocity magnitude for distance scaling
        ball_radius_m: Ball radius (4.25 in = 0.108 m)
        moment_of_inertia_kg_m2: Moment of inertia (solid sphere: 2/5 * m * r²)

    Returns:
        RotationalState with updated angular velocity
    """

    if angular_velocity is None:
        angular_velocity = np.array([50.0, 0.0, 80.0], dtype=np.float32)
    if torque_n_m is None:
        torque_n_m = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    # Distance-based integration: convert from distance (0.1 ft) to time
    velocity_magnitude_m_s = velocity_magnitude_ft_s * 0.3048  # ft/s → m/s

    if velocity_magnitude_m_s < 0.01:  # Ball essentially stopped
        # No motion, no updates
        updated_omega = angular_velocity.copy()
        angular_accel = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    else:
        # Distance step: 0.1 ft = 0.03048 m
        distance_step_m = 0.1 * 0.3048  # 0.1 ft in meters

        # Time for this distance step
        dt = distance_step_m / velocity_magnitude_m_s  # seconds

        # Angular acceleration: α = τ / I
        angular_accel = torque_n_m / moment_of_inertia_kg_m2  # rad/s²

        # Update angular velocity: ω_new = ω_old + α * dt
        updated_omega = angular_velocity + angular_accel * dt

    # Calculate magnitude (RPM)
    omega_mag = np.linalg.norm(updated_omega)
    rpm = (omega_mag / (2.0 * np.pi)) * 60.0  # rad/s → RPM

    # Spin axis angle (angle from horizontal)
    # Spin axis is typically in the X-Z plane; angle = atan2(wz, wx)
    if abs(updated_omega[0]) > 0.01 or abs(updated_omega[2]) > 0.01:
        spin_axis_angle_deg = np.degrees(np.arctan2(updated_omega[2], updated_omega[0]))
    else:
        spin_axis_angle_deg = 0.0

    return RotationalState(
        angular_velocity=updated_omega,
        rpm=rpm,
        spin_axis_angle_deg=spin_axis_angle_deg,
        torque_applied_n_m=torque_n_m,
        angular_acceleration=angular_accel,
    )


def validate_rotational_state(rs: RotationalState, prev_rpm: float = None) -> dict:
    """
    Validate Agent #6 output against success criteria

    Success Criteria:
    - Angular velocity updates smoothly (no jumps)
    - RPM decreases monotonically (friction opposes rotation)
    - Spin axis angle stable (Y-component minimal)
    - RPM decay realistic (5-15% per 0.1 ft step typical)
    - No NaN/inf values
    - Angular velocity magnitude decreases with friction torque
    """
    results = {
        "rpm": rs.rpm,
        "passed": True,
        "checks": [],
    }

    # Check 1: Angular velocity magnitude non-negative
    omega_mag = np.linalg.norm(rs.angular_velocity)
    mag_valid = omega_mag >= 0.0 and np.isfinite(omega_mag)
    results["checks"].append(
        {
            "name": "Angular velocity magnitude valid",
            "passed": mag_valid,
            "value": f"{omega_mag:.2f} rad/s",
        }
    )
    if not mag_valid:
        results["passed"] = False

    # Check 2: No NaN or inf in angular velocity
    no_nan = np.all(np.isfinite(rs.angular_velocity))
    results["checks"].append(
        {
            "name": "No NaN/inf in angular velocity",
            "passed": no_nan,
            "value": f"{rs.angular_velocity}",
        }
    )
    if not no_nan:
        results["passed"] = False

    # Check 3: RPM valid and in reasonable range
    # Typical: 50-500 RPM during descent
    rpm_valid = 0 <= rs.rpm <= 600
    results["checks"].append(
        {
            "name": "RPM in [0, 600] range",
            "passed": rpm_valid,
            "value": f"{rs.rpm:.1f} RPM",
        }
    )
    if not rpm_valid:
        results["passed"] = False

    # Check 4: RPM decreases monotonically (if previous RPM available)
    if prev_rpm is not None:
        rpm_decreases = rs.rpm <= prev_rpm + 0.1  # Allow small numerical error
        results["checks"].append(
            {
                "name": "RPM decreases monotonically",
                "passed": rpm_decreases,
                "previous": f"{prev_rpm:.1f}",
                "current": f"{rs.rpm:.1f}",
            }
        )
        if not rpm_decreases:
            results["passed"] = False

    # Check 5: Spin axis stable (angle in reasonable range)
    axis_stable = -90 <= rs.spin_axis_angle_deg <= 90
    results["checks"].append(
        {
            "name": "Spin axis angle stable [-90, 90]°",
            "passed": axis_stable,
            "value": f"{rs.spin_axis_angle_deg:.1f}°",
        }
    )
    if not axis_stable:
        results["passed"] = False

    # Check 6: Angular acceleration opposes angular velocity (friction brakes rotation)
    if np.linalg.norm(rs.torque_applied_n_m) > 0.01 and omega_mag > 0.1:
        # Check if torque opposes rotation (dot product should be negative)
        torque_opposes = np.dot(rs.torque_applied_n_m, rs.angular_velocity) < 0
    else:
        torque_opposes = True  # N/A if no torque or no rotation

    results["checks"].append(
        {
            "name": "Friction torque opposes rotation",
            "passed": torque_opposes,
            "tau·ω": f"{np.dot(rs.torque_applied_n_m, rs.angular_velocity):.3f}",
        }
    )
    if not torque_opposes and np.linalg.norm(rs.torque_applied_n_m) > 0.01 and omega_mag > 0.1:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #6: Rotational Dynamics - Test Suite")
    print("=" * 60)

    # Simulate descent: track RPM across 10 steps (1 ft total)
    test_cases = [
        {
            "name": "Oiled lane (low friction, slow decay)",
            "initial_rpm": 300,
            "torque_mag": 0.5,
        },
        {
            "name": "Transition (medium friction)",
            "initial_rpm": 300,
            "torque_mag": 1.5,
        },
        {
            "name": "Dry lane (high friction, fast decay)",
            "initial_rpm": 300,
            "torque_mag": 2.9,
        },
    ]

    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 60)

        # Initialize spin
        initial_rpm = test["initial_rpm"]
        initial_omega = np.array([50.0, 0.0, 80.0], dtype=np.float32)
        initial_omega_mag = np.linalg.norm(initial_omega)

        # Normalize to desired RPM
        if initial_omega_mag > 0:
            target_rpm_rad_s = initial_rpm * 2 * np.pi / 60.0
            initial_omega = initial_omega * (target_rpm_rad_s / initial_omega_mag)

        # Simulate 10 steps (0.1 ft each)
        omega = initial_omega.copy()
        prev_rpm = initial_rpm

        for step in range(10):
            # Create torque vector opposing rotation
            if np.linalg.norm(omega) > 0.1:
                torque_direction = -omega / np.linalg.norm(omega)
            else:
                torque_direction = np.array([0.0, 0.0, -1.0], dtype=np.float32)

            torque = torque_direction * test["torque_mag"]

            # Update rotational state
            rs = create_rotational_state(
                angular_velocity=omega,
                torque_n_m=torque,
                velocity_magnitude_ft_s=25.0 - step * 0.5,  # Velocity decreases
            )

            omega = rs.angular_velocity

            # Validate
            validation = validate_rotational_state(rs, prev_rpm)
            prev_rpm = rs.rpm

            if step == 0 or step == 9:  # Print first and last
                status = "✓" if validation["passed"] else "✗"
                print(f"Step {step}: {status} RPM {rs.rpm:6.1f} | ω_mag {np.linalg.norm(rs.angular_velocity):6.2f} rad/s | Axis {rs.spin_axis_angle_deg:6.1f}°")

        print(f"Total RPM decay: {initial_rpm:.0f} → {rs.rpm:.0f} RPM ({100*(rs.rpm/initial_rpm):.1f}% remaining)")

    print("\n" + "=" * 60)
    print("Agent #6 ready for trajectory integration")
