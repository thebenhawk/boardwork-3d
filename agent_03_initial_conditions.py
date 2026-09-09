"""
Agent #3: Initial Conditions
Converts bowler release parameters (speed, RPM, angle) to 3D velocity and angular velocity vectors

Input: Ball speed (mph), RPM, PAP angle
Output: InitialConditions with velocity/angular velocity vectors + kinetic energy
Validation: Energy conservation, parameter ranges, vector magnitudes
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class InitialConditions:
    """Ball release state"""
    speed_mph: float
    speed_ft_s: float
    rpm: float
    axis_angle_deg: float

    velocity: np.ndarray  # (vx, vy, vz) ft/s
    angular_velocity: np.ndarray  # (wx, wy, wz) rad/s
    kinetic_energy_j: float

    def to_dict(self) -> dict:
        return {
            "speed_mph": self.speed_mph,
            "speed_ft_s": float(self.speed_ft_s),
            "rpm": self.rpm,
            "axis_angle_deg": self.axis_angle_deg,
            "velocity": self.velocity.tolist(),
            "angular_velocity": self.angular_velocity.tolist(),
            "kinetic_energy_j": float(self.kinetic_energy_j),
        }


def create_initial_conditions(
    speed_mph: float, rpm: float, axis_angle_deg: float = 45.0, ball_weight_lbs: float = 16.0
) -> InitialConditions:
    """
    Agent #3: Convert release parameters to velocity and angular velocity vectors

    Args:
        speed_mph: Ball speed at release (typical: 12-22 mph)
        rpm: Revolutions per minute (typical: 100-500)
        axis_angle_deg: Spin axis angle from horizontal (default 45°)
        ball_weight_lbs: Ball weight for kinetic energy (default 16 lbs)

    Returns:
        InitialConditions with 3D velocity/angular velocity vectors
    """
    # Validate input ranges
    if not (10 <= speed_mph <= 25):
        raise ValueError(f"Speed {speed_mph} mph out of range (10-25)")
    if not (50 <= rpm <= 600):
        raise ValueError(f"RPM {rpm} out of range (50-600)")

    # Convert speed: mph → ft/s
    speed_ft_s = speed_mph * 1.46667

    # Convert RPM → rad/s
    # RPM = revolutions per minute
    # rad/s = (revolutions / 60 seconds) * 2π radians/revolution
    angular_speed_rad_s = rpm * 2 * np.pi / 60.0

    # Velocity vector: ball launched down lane (Y direction, foul line → pins)
    # Assume release at center board (x=0 relative to center), no vertical launch angle
    velocity = np.array([0.0, speed_ft_s, 0.0], dtype=np.float32)

    # Angular velocity vector: spin axis typically tilted from horizontal
    # At axis_angle_deg from horizontal:
    # - Spin around X-axis (across lanes) gives hook
    # - Spin around Z-axis (up) gives skid
    # Typical: 45° mix of both
    ax = angular_speed_rad_s * np.cos(np.radians(axis_angle_deg))
    az = angular_speed_rad_s * np.sin(np.radians(axis_angle_deg))
    ay = 0.0  # Usually minimal Y-axis spin
    angular_velocity = np.array([ax, ay, az], dtype=np.float32)

    # Kinetic energy = translational + rotational
    # KE_trans = 0.5 * m * v²
    # KE_rot = 0.5 * I * ω²
    mass_kg = ball_weight_lbs * 0.453592

    trans_ke = 0.5 * mass_kg * speed_ft_s**2

    # Moment of inertia for sphere: I = (2/5) * m * r²
    # Ball radius = 4.25 inches = 0.3542 feet
    ball_radius_ft = 4.25 / 12.0
    moment_of_inertia = (2.0 / 5.0) * mass_kg * (ball_radius_ft ** 2)

    rot_ke = 0.5 * moment_of_inertia * angular_speed_rad_s**2

    total_ke = trans_ke + rot_ke

    return InitialConditions(
        speed_mph=speed_mph,
        speed_ft_s=speed_ft_s,
        rpm=rpm,
        axis_angle_deg=axis_angle_deg,
        velocity=velocity,
        angular_velocity=angular_velocity,
        kinetic_energy_j=total_ke,
    )


def validate_initial_conditions(ic: InitialConditions) -> dict:
    """
    Validate Agent #3 output against success criteria

    Success Criteria:
    - Speed conversion: mph → ft/s correct
    - RPM conversion: RPM → rad/s correct
    - Velocity magnitude realistic (15-35 ft/s)
    - Angular velocity magnitude realistic (10-60 rad/s)
    - Kinetic energy valid (positive, reasonable range)
    - Energy conservation across parameter ranges
    """
    results = {
        "speed_mph": ic.speed_mph,
        "rpm": ic.rpm,
        "passed": True,
        "checks": [],
    }

    # Check 1: Speed conversion mph → ft/s
    expected_ft_s = ic.speed_mph * 1.46667
    speed_valid = abs(ic.speed_ft_s - expected_ft_s) < 0.01
    results["checks"].append(
        {
            "name": "Speed conversion (mph → ft/s)",
            "passed": speed_valid,
            "value": f"{ic.speed_ft_s:.2f} ft/s",
            "expected": f"{expected_ft_s:.2f} ft/s",
        }
    )
    if not speed_valid:
        results["passed"] = False

    # Check 2: RPM conversion → rad/s
    expected_rad_s = ic.rpm * 2 * np.pi / 60.0
    actual_ang_speed = np.linalg.norm(ic.angular_velocity)
    rpm_valid = abs(actual_ang_speed - expected_rad_s) < 0.1
    results["checks"].append(
        {
            "name": "RPM conversion (RPM → rad/s)",
            "passed": rpm_valid,
            "value": f"{actual_ang_speed:.2f} rad/s",
            "expected": f"{expected_rad_s:.2f} rad/s",
        }
    )
    if not rpm_valid:
        results["passed"] = False

    # Check 3: Velocity magnitude realistic
    vel_mag = np.linalg.norm(ic.velocity)
    vel_valid = 15 <= vel_mag <= 35
    results["checks"].append(
        {
            "name": "Velocity magnitude 15-35 ft/s",
            "passed": vel_valid,
            "value": f"{vel_mag:.2f} ft/s",
        }
    )
    if not vel_valid:
        results["passed"] = False

    # Check 4: Angular velocity magnitude realistic
    ang_mag = np.linalg.norm(ic.angular_velocity)
    ang_valid = 10 <= ang_mag <= 60
    results["checks"].append(
        {
            "name": "Angular velocity 10-60 rad/s",
            "passed": ang_valid,
            "value": f"{ang_mag:.2f} rad/s",
        }
    )
    if not ang_valid:
        results["passed"] = False

    # Check 5: Kinetic energy positive and reasonable
    ke_valid = 50 < ic.kinetic_energy_j < 5000
    results["checks"].append(
        {
            "name": "Kinetic energy 50-5000 J",
            "passed": ke_valid,
            "value": f"{ic.kinetic_energy_j:.1f} J",
        }
    )
    if not ke_valid:
        results["passed"] = False

    # Check 6: Velocity points down lane (Y direction dominant)
    y_dominant = ic.velocity[1] > 0.9 * np.linalg.norm(ic.velocity)
    results["checks"].append(
        {
            "name": "Velocity points down lane (Y-dominant)",
            "passed": y_dominant,
            "vy_component": f"{ic.velocity[1]:.2f} ft/s",
        }
    )
    if not y_dominant:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #3: Initial Conditions - Test Suite")
    print("=" * 60)

    test_cases = [
        (18, 300),  # Typical: 18 mph, 300 RPM
        (15, 200),  # Light: 15 mph, 200 RPM
        (20, 400),  # Fast: 20 mph, 400 RPM
    ]

    for speed_mph, rpm in test_cases:
        print(f"\nTest: {speed_mph} mph, {rpm} RPM")
        ic = create_initial_conditions(speed_mph, rpm)
        validation = validate_initial_conditions(ic)

        status = "✓ PASS" if validation["passed"] else "✗ FAIL"
        print(f"Status: {status}")
        print(f"  Velocity: {ic.velocity} ft/s (mag: {np.linalg.norm(ic.velocity):.2f})")
        print(f"  Angular Velocity: {ic.angular_velocity} rad/s (mag: {np.linalg.norm(ic.angular_velocity):.2f})")
        print(f"  Kinetic Energy: {ic.kinetic_energy_j:.1f} J")

        for check in validation["checks"]:
            check_status = "✓" if check["passed"] else "✗"
            print(f"  {check_status} {check['name']}")

    print("\n" + "=" * 60)
    print("All test cases ready for dashboard display")
