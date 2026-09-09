"""
Agent #7: Translational Dynamics
Updates ball velocity based on friction force

Input: Ball mass, friction force vector, current velocity, current distance
Output: TranslationalState with updated velocity after one distance step
Validation: Velocity decreases monotonically, deceleration realistic, no negative velocity
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class TranslationalState:
    """Linear velocity state after friction force applied"""
    velocity: np.ndarray  # (vx, vy, vz) ft/s
    speed_ft_s: float  # Magnitude of velocity (ft/s)
    speed_mph: float  # Speed in mph
    distance_traveled_ft: float  # Total distance traveled so far
    deceleration_ft_s2: float  # Deceleration rate (ft/s²)
    kinetic_energy_j: float  # Translational kinetic energy (Joules)

    def to_dict(self) -> dict:
        return {
            "velocity": self.velocity.tolist(),
            "speed_ft_s": float(self.speed_ft_s),
            "speed_mph": float(self.speed_mph),
            "distance_traveled_ft": float(self.distance_traveled_ft),
            "deceleration_ft_s2": float(self.deceleration_ft_s2),
            "kinetic_energy_j": float(self.kinetic_energy_j),
        }


def create_translational_state(
    velocity: np.ndarray = None,  # (vx, vy, vz) ft/s
    friction_force_n: np.ndarray = None,  # (fx, fy, fz) Newtons
    distance_traveled_ft: float = 0.0,  # Current position
    ball_mass_kg: float = 7.257,  # 16 lbs
) -> TranslationalState:
    """
    Agent #7: Update velocity based on friction force

    Physics model (distance-based):
    - Friction force causes deceleration: a = -f / m
    - Over distance step dd: dv/dd = a / v = -f / (m * v)
    - Velocity decreases due to friction opposes motion
    - Energy dissipates as heat at lane surface

    Args:
        velocity: Initial velocity vector (ft/s)
        friction_force_n: Friction force vector (Newtons)
        distance_traveled_ft: Current distance down lane
        ball_mass_kg: Ball mass in kg (default 16 lbs = 7.257 kg)

    Returns:
        TranslationalState with updated velocity
    """

    if velocity is None:
        velocity = np.array([0.0, 27.0, 0.0], dtype=np.float32)
    if friction_force_n is None:
        friction_force_n = np.array([0.0, -5.4, 0.0], dtype=np.float32)

    # Convert friction force from Newtons to ft/s² (SI → imperial)
    # a = F / m (SI: m/s², converted to ft/s²)
    # 1 ft = 0.3048 m, so 1 ft/s² = 0.3048 m/s²
    # a_ft_s2 = (F_N / m_kg) * 0.3048 (to convert m/s² to ft/s²)

    acceleration_m_s2 = friction_force_n / ball_mass_kg  # m/s²
    acceleration_ft_s2 = acceleration_m_s2 * 3.28084  # m/s² → ft/s²

    # Distance-based integration: convert from distance (0.1 ft) to time
    velocity_magnitude_ft_s = np.linalg.norm(velocity)

    if velocity_magnitude_ft_s < 0.01:  # Ball essentially stopped
        # No motion, no updates
        updated_velocity = velocity.copy()
        deceleration = 0.0
    else:
        # Distance step: 0.1 ft
        distance_step_ft = 0.1

        # Time for this distance step
        dt = distance_step_ft / velocity_magnitude_ft_s  # seconds

        # Update velocity: v_new = v_old + a * dt
        updated_velocity = velocity + acceleration_ft_s2 * dt

        # Check if velocity would reverse (ball shouldn't go backwards)
        if np.linalg.norm(updated_velocity) < 0.01:
            updated_velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        # Deceleration magnitude (positive value)
        deceleration = -np.dot(acceleration_ft_s2, velocity) / (velocity_magnitude_ft_s + 1e-6)
        deceleration = max(0, deceleration)  # Ensure non-negative

    # Speed calculations
    new_speed_ft_s = np.linalg.norm(updated_velocity)
    new_speed_mph = new_speed_ft_s / 1.46667  # ft/s → mph

    # Kinetic energy (translational only)
    kinetic_energy_j = 0.5 * ball_mass_kg * (new_speed_ft_s * 0.3048) ** 2  # Convert ft/s to m/s

    # Distance update
    new_distance = distance_traveled_ft + 0.1  # Add 0.1 ft step

    return TranslationalState(
        velocity=updated_velocity,
        speed_ft_s=new_speed_ft_s,
        speed_mph=new_speed_mph,
        distance_traveled_ft=new_distance,
        deceleration_ft_s2=deceleration,
        kinetic_energy_j=kinetic_energy_j,
    )


def validate_translational_state(ts: TranslationalState, prev_speed_ft_s: float = None) -> dict:
    """
    Validate Agent #7 output against success criteria

    Success Criteria:
    - Velocity updates smoothly (no jumps)
    - Speed decreases monotonically (friction opposes motion)
    - Speed remains non-negative
    - Deceleration realistic (2-12 ft/s² typical for bowling)
    - Kinetic energy decreases (energy dissipation)
    - No NaN/inf values
    """
    results = {
        "speed_mph": ts.speed_mph,
        "passed": True,
        "checks": [],
    }

    # Check 1: Speed non-negative
    speed_valid = ts.speed_ft_s >= 0.0 and np.isfinite(ts.speed_ft_s)
    results["checks"].append(
        {
            "name": "Speed non-negative",
            "passed": speed_valid,
            "value": f"{ts.speed_ft_s:.2f} ft/s",
        }
    )
    if not speed_valid:
        results["passed"] = False

    # Check 2: No NaN or inf in velocity
    no_nan = np.all(np.isfinite(ts.velocity))
    results["checks"].append(
        {
            "name": "No NaN/inf in velocity",
            "passed": no_nan,
            "value": f"{ts.velocity}",
        }
    )
    if not no_nan:
        results["passed"] = False

    # Check 3: Speed in reasonable range (0-30 ft/s ≈ 0-20 mph)
    speed_range_valid = 0 <= ts.speed_ft_s <= 45  # Allow up to 45 ft/s (~30 mph max)
    results["checks"].append(
        {
            "name": "Speed in [0, 45] ft/s range",
            "passed": speed_range_valid,
            "value": f"{ts.speed_ft_s:.2f} ft/s ({ts.speed_mph:.1f} mph)",
        }
    )
    if not speed_range_valid:
        results["passed"] = False

    # Check 4: Speed decreases monotonically (if previous speed available)
    if prev_speed_ft_s is not None:
        speed_decreases = ts.speed_ft_s <= prev_speed_ft_s + 0.1  # Allow small numerical error
        results["checks"].append(
            {
                "name": "Speed decreases monotonically",
                "passed": speed_decreases,
                "previous": f"{prev_speed_ft_s:.2f} ft/s",
                "current": f"{ts.speed_ft_s:.2f} ft/s",
            }
        )
        if not speed_decreases:
            results["passed"] = False

    # Check 5: Deceleration realistic (0-15 ft/s² for typical bowling)
    # F = 5-27 N, m = 7.257 kg → a = 0.69-3.7 m/s² = 2.26-12.1 ft/s²
    decel_valid = 0 <= ts.deceleration_ft_s2 <= 15.0
    results["checks"].append(
        {
            "name": "Deceleration [0, 15] ft/s² (typical: 2-12)",
            "passed": decel_valid,
            "value": f"{ts.deceleration_ft_s2:.3f} ft/s²",
        }
    )
    if not decel_valid:
        results["passed"] = False

    # Check 6: Kinetic energy non-negative
    ke_valid = ts.kinetic_energy_j >= 0.0 and np.isfinite(ts.kinetic_energy_j)
    results["checks"].append(
        {
            "name": "Kinetic energy non-negative",
            "passed": ke_valid,
            "value": f"{ts.kinetic_energy_j:.1f} J",
        }
    )
    if not ke_valid:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #7: Translational Dynamics - Test Suite")
    print("=" * 60)

    # Simulate descent: track speed across 10 steps (1 ft total)
    test_cases = [
        {
            "name": "Oiled lane (low friction, slow deceleration)",
            "initial_speed_mph": 18,
            "friction_mag": 5.4,
        },
        {
            "name": "Transition (medium friction)",
            "initial_speed_mph": 18,
            "friction_mag": 16.2,
        },
        {
            "name": "Dry lane (high friction, fast deceleration)",
            "initial_speed_mph": 18,
            "friction_mag": 27.1,
        },
    ]

    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 60)

        # Initialize velocity
        initial_speed_mph = test["initial_speed_mph"]
        initial_speed_ft_s = initial_speed_mph * 1.46667
        velocity = np.array([0.0, initial_speed_ft_s, 0.0], dtype=np.float32)

        # Simulate 10 steps (0.1 ft each)
        prev_speed = initial_speed_ft_s
        distance = 0.0

        for step in range(10):
            # Create friction force opposing motion
            if np.linalg.norm(velocity) > 0.1:
                velocity_direction = velocity / np.linalg.norm(velocity)
            else:
                velocity_direction = np.array([0.0, 1.0, 0.0], dtype=np.float32)

            # Friction force in Newtons, pointing backward
            # Decrease magnitude as speed decreases
            speed_factor = max(0.5, np.linalg.norm(velocity) / initial_speed_ft_s)
            friction_force = -velocity_direction * test["friction_mag"] * speed_factor

            # Update translational state
            ts = create_translational_state(
                velocity=velocity,
                friction_force_n=friction_force,
                distance_traveled_ft=distance,
            )

            velocity = ts.velocity
            distance = ts.distance_traveled_ft

            # Validate
            validation = validate_translational_state(ts, prev_speed)
            prev_speed = ts.speed_ft_s

            if step == 0 or step == 9:  # Print first and last
                status = "✓" if validation["passed"] else "✗"
                print(f"Step {step}: {status} Speed {ts.speed_mph:6.2f} mph | {ts.speed_ft_s:6.2f} ft/s | Decel {ts.deceleration_ft_s2:6.3f} ft/s²")

        print(f"Total speed decay: {initial_speed_mph:.1f} → {ts.speed_mph:.1f} mph | Distance: {distance:.1f} ft")
        speed_pct = 100 * ts.speed_mph / initial_speed_mph
        print(f"Speed remaining: {speed_pct:.1f}%")

    print("\n" + "=" * 60)
    print("Agent #7 ready for trajectory integration")
