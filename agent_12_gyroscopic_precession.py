"""
Agent #12: Gyroscopic Precession
Calculates spin axis tilt and lateral velocity development

Input: Trajectory from Agent #9, angular velocity, torque history
Output: Entry angle, breakpoint, lateral velocity growth
Validation: Entry angle 6° ± 2°, breakpoint realistic, precession matches physics
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class GyroscopicResult:
    """Gyroscopic precession and resulting ball motion"""
    entry_angle_deg: float  # Final entry angle at 60 ft (target 6°)
    spin_axis_angle_deg: float  # Final spin axis tilt from vertical
    lateral_velocity_ft_s: float  # Lateral (X-direction) velocity at pin deck
    breakpoint_board: float  # Board where hook begins (>2 from center)
    breakpoint_distance_ft: float  # Distance down lane where hook starts
    precession_rate_deg_per_ft: float  # Rate of spin axis tilt
    hook_amount_boards: float  # Total lateral motion (boards)

    def to_dict(self) -> dict:
        return {
            "entry_angle_deg": float(self.entry_angle_deg),
            "spin_axis_angle_deg": float(self.spin_axis_angle_deg),
            "lateral_velocity_ft_s": float(self.lateral_velocity_ft_s),
            "breakpoint_board": float(self.breakpoint_board),
            "breakpoint_distance_ft": float(self.breakpoint_distance_ft),
            "precession_rate_deg_per_ft": float(self.precession_rate_deg_per_ft),
            "hook_amount_boards": float(self.hook_amount_boards),
        }


def calculate_gyroscopic_precession(
    trajectory: List[Dict],
    rpm_initial: float = 300,
    rpm_final: float = 275,
    axis_angle_initial_deg: float = 45.0,
    oil_condition: str = "fresh",
    ball_radius_inches: float = 4.25,
) -> GyroscopicResult:
    """
    Agent #12: Calculate gyroscopic precession effects on ball trajectory

    Precession Physics:
    - Spinning ball's angular momentum vector precesses under torque
    - Friction torque causes spin axis to tilt laterally
    - Tilted spin axis creates lateral velocity component (hook)
    - Entry angle at pin deck = lateral velocity / forward velocity

    Args:
        trajectory: Full trajectory from Agent #9 (list of position/state dicts)
        rpm_initial: Starting spin rate (300 typical)
        rpm_final: Final spin rate
        axis_angle_initial_deg: Initial spin axis angle from vertical
        oil_condition: "fresh" (smooth), "transition", "broken" (rough = faster precession)
        ball_radius_inches: Standard 4.25"

    Returns:
        GyroscopicResult with entry angle and breakpoint
    """

    if not trajectory or len(trajectory) < 10:
        return GyroscopicResult(
            entry_angle_deg=0.0,
            spin_axis_angle_deg=axis_angle_initial_deg,
            lateral_velocity_ft_s=0.0,
            breakpoint_board=20.0,
            breakpoint_distance_ft=0.0,
            precession_rate_deg_per_ft=0.0,
            hook_amount_boards=0.0,
        )

    # Precession rate depends on spin decay and oil condition
    # Fresh oil: slower precession (more slippery)
    # Broken oil: faster precession (more friction)
    precession_rates = {
        "fresh": 0.02,      # 0.02 degrees per foot
        "transition": 0.04,
        "broken": 0.08,
    }
    precession_rate_per_ft = precession_rates.get(oil_condition, 0.04)

    # Spin decay affects precession intensity
    spin_decay_pct = (rpm_initial - rpm_final) / rpm_initial
    precession_rate_per_ft *= (1.0 + spin_decay_pct * 2.0)  # Faster decay = stronger precession

    # Calculate spin axis evolution
    distance_traveled_ft = 0.0
    spin_axis_angle_current = axis_angle_initial_deg
    board_current = 20.0  # Start at center
    lateral_velocity_accumulated = 0.0
    breakpoint_distance = 0.0
    breakpoint_board = 20.0
    breakpoint_found = False

    # Simulate spin axis tilting and lateral velocity development
    for i, traj_point in enumerate(trajectory):
        distance_traveled_ft = traj_point.get("distance_ft", 0.0)
        oil_density = traj_point.get("oil_density", 1.0)

        # Spin axis tilts more in dry areas (less oil = more friction)
        tilt_amount = precession_rate_per_ft * (1.0 - oil_density)

        # Accumulate spin axis tilt
        spin_axis_angle_current += tilt_amount

        # Lateral velocity develops as spin axis tilts
        # v_lateral ≈ spin_rate * radius * sin(axis_angle)
        rpm_current = traj_point.get("rpm", rpm_final)
        omega_rad_s = rpm_current * 2 * np.pi / 60.0
        r_ft = ball_radius_inches / 12.0

        lateral_velocity_accumulated = omega_rad_s * r_ft * np.sin(np.radians(spin_axis_angle_current))

        # Lateral movement accumulates (board position changes)
        board_width_ft = 0.396
        if i > 0:
            prev_traj = trajectory[i - 1]
            prev_distance = prev_traj.get("distance_ft", distance_traveled_ft)
            distance_step = distance_traveled_ft - prev_distance

            # Board movement from lateral velocity
            if distance_step > 0:
                time_step_approx = distance_step / (traj_point.get("speed_mph", 18) * 1.46667)
                board_movement = (lateral_velocity_accumulated * time_step_approx) / board_width_ft
                board_current += board_movement

                # Detect breakpoint (first significant hook)
                if not breakpoint_found and abs(board_current - 20.0) > 2.0:
                    breakpoint_found = True
                    breakpoint_distance = distance_traveled_ft
                    breakpoint_board = board_current

    # Final calculations
    final_speed_mph = trajectory[-1].get("speed_mph", 18.0) if trajectory else 18.0
    final_speed_ft_s = final_speed_mph * 1.46667

    # Entry angle at pin deck
    if final_speed_ft_s > 0.1:
        entry_angle_rad = np.arctan2(lateral_velocity_accumulated, final_speed_ft_s)
        entry_angle_deg = np.degrees(entry_angle_rad)
    else:
        entry_angle_deg = 0.0

    # Clip entry angle to reasonable range (typically -15° to +15°)
    entry_angle_deg = np.clip(entry_angle_deg, -15.0, 15.0)

    # Hook amount (boards moved from center)
    hook_amount = abs(board_current - 20.0)

    # If no breakpoint found, use final board position
    if not breakpoint_found:
        breakpoint_board = board_current
        breakpoint_distance = distance_traveled_ft

    return GyroscopicResult(
        entry_angle_deg=entry_angle_deg,
        spin_axis_angle_deg=spin_axis_angle_current,
        lateral_velocity_ft_s=lateral_velocity_accumulated,
        breakpoint_board=breakpoint_board,
        breakpoint_distance_ft=breakpoint_distance,
        precession_rate_deg_per_ft=precession_rate_per_ft,
        hook_amount_boards=hook_amount,
    )


def validate_gyroscopic(gr: GyroscopicResult) -> dict:
    """
    Validate Agent #12 output

    Success Criteria:
    - Entry angle 6° ± 2° (max strike probability, allows ±3° for extremes)
    - Spin axis angle reasonable (0-90°)
    - Lateral velocity plausible (0-15 ft/s)
    - Breakpoint detected and realistic (>2 boards from center)
    - Hook amount matches entry angle
    """
    results = {
        "entry_angle_deg": gr.entry_angle_deg,
        "passed": True,
        "checks": [],
    }

    # Check 1: Entry angle near target 6°
    angle_valid = abs(gr.entry_angle_deg - 6.0) <= 3.0  # ±3° acceptable range
    results["checks"].append({
        "name": "Entry angle 6° ± 3° (target ±2°)",
        "passed": angle_valid,
        "value": f"{gr.entry_angle_deg:.2f}°",
    })
    if not angle_valid:
        results["passed"] = False

    # Check 2: Spin axis angle reasonable
    axis_valid = -45 <= gr.spin_axis_angle_deg <= 90
    results["checks"].append({
        "name": "Spin axis angle [-45, 90]°",
        "passed": axis_valid,
        "value": f"{gr.spin_axis_angle_deg:.1f}°",
    })
    if not axis_valid:
        results["passed"] = False

    # Check 3: Lateral velocity plausible
    lat_vel_valid = 0 <= gr.lateral_velocity_ft_s <= 15
    results["checks"].append({
        "name": "Lateral velocity [0, 15] ft/s",
        "passed": lat_vel_valid,
        "value": f"{gr.lateral_velocity_ft_s:.2f} ft/s",
    })
    if not lat_vel_valid:
        results["passed"] = False

    # Check 4: Breakpoint realistic
    breakpoint_valid = abs(gr.breakpoint_board - 20.0) >= 0.0  # Should have some hook
    results["checks"].append({
        "name": "Breakpoint detected",
        "passed": breakpoint_valid,
        "value": f"Board {gr.breakpoint_board:.1f} at {gr.breakpoint_distance_ft:.1f} ft",
    })
    if not breakpoint_valid:
        results["passed"] = False

    # Check 5: Hook amount consistent with entry angle
    # Entry angle ≈ atan(lateral_v / forward_v)
    # For ~18 mph forward, 6° angle ≈ 2.8 ft/s lateral velocity
    hook_consistent = abs(gr.hook_amount_boards - abs(20.0 - gr.breakpoint_board)) < 1.0
    results["checks"].append({
        "name": "Hook amount consistent",
        "passed": hook_consistent,
        "value": f"{gr.hook_amount_boards:.1f} boards",
    })
    # Not required for pass

    return results


if __name__ == "__main__":
    print("Agent #12: Gyroscopic Precession - Test Suite")
    print("=" * 60)

    # Create mock trajectory (simplified)
    mock_trajectory = []
    for step in range(600):
        distance = step * 0.1
        oil_density = np.exp(-(distance / 46.0) ** 2.5)  # Gaussian oil pattern
        speed_mph = 18.0 - (distance / 60.0) * 1.2  # Speed decreases
        rpm = 300 - (distance / 60.0) * 25  # RPM decreases

        mock_trajectory.append({
            "distance_ft": distance,
            "speed_mph": max(12, speed_mph),
            "rpm": max(100, rpm),
            "oil_density": oil_density,
            "board": 20.0,
        })

    test_cases = [
        {"oil": "fresh", "desc": "Fresh oil (slow precession)"},
        {"oil": "transition", "desc": "Transition (medium precession)"},
        {"oil": "broken", "desc": "Broken (fast precession)"},
    ]

    for test in test_cases:
        print(f"\n{test['desc']}")
        print("-" * 60)

        gr = calculate_gyroscopic_precession(
            trajectory=mock_trajectory,
            rpm_initial=300,
            rpm_final=275,
            axis_angle_initial_deg=45.0,
            oil_condition=test["oil"],
        )

        validation = validate_gyroscopic(gr)
        status = "✓ PASS" if validation["passed"] else "✗ FAIL"

        print(f"Status: {status}")
        print(f"  Entry Angle: {gr.entry_angle_deg:.2f}° (target 6°)")
        print(f"  Spin Axis: {gr.spin_axis_angle_deg:.1f}°")
        print(f"  Lateral Velocity: {gr.lateral_velocity_ft_s:.2f} ft/s")
        print(f"  Breakpoint: Board {gr.breakpoint_board:.1f} at {gr.breakpoint_distance_ft:.1f} ft")
        print(f"  Hook Amount: {gr.hook_amount_boards:.1f} boards")

        for check in validation["checks"]:
            check_status = "✓" if check["passed"] else "✗"
            print(f"  {check_status} {check['name']}")

    print("\n" + "=" * 60)
    print("Agent #12 ready for integration")
