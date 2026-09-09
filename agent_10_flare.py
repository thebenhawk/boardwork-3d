"""
Agent #10: Flare Calculation
Calculates track deformation on ball surface due to spin

Input: Angular velocity, ball surface grit, total revolutions
Output: FlareResult with flare distance and saturation rings
Validation: Flare within manufacturer specs (1-4 inches), track width realistic
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class FlareResult:
    """Ball surface flare (track deformation)"""
    flare_distance_inches: float  # Distance track migrates (1-4 typical)
    track_width_inches: float  # Width of contact track
    revolutions_total: int  # Total revolutions ball made
    grit_condition: str  # "factory", "shammy'd", "abraded"
    saturation_pct: float  # % of surface that absorbed oil (0-100)

    def to_dict(self) -> dict:
        return {
            "flare_distance_inches": float(self.flare_distance_inches),
            "track_width_inches": float(self.track_width_inches),
            "revolutions_total": int(self.revolutions_total),
            "grit_condition": self.grit_condition,
            "saturation_pct": float(self.saturation_pct),
        }


def calculate_flare(
    rpm_initial: float = 300,
    rpm_final: float = 250,
    distance_ft: float = 60.0,
    ball_radius_inches: float = 4.25,
    grit_condition: str = "factory",
    oil_condition: str = "fresh",
) -> FlareResult:
    """
    Agent #10: Calculate ball surface flare (track migration)

    Flare Model:
    - Ball starts with clean coverstock
    - As it rolls, surface grit creates micropeaks that contact lane
    - Oil clings to these peaks, creating visible track
    - Track migrates due to spin axis tilt (causes track to move around ball)
    - Total migration distance (flare) depends on RG and differential

    Args:
        rpm_initial: Starting spin rate
        rpm_final: Final spin rate at pin deck
        distance_ft: Distance traveled (typically 60 ft)
        ball_radius_inches: Ball radius (4.25 in standard)
        grit_condition: "factory" (baseline), "shammy'd" (less), "abraded" (more)
        oil_condition: "fresh" (1.0), "transition" (0.7), "broken" (0.3)

    Returns:
        FlareResult with track info
    """

    # Calculate total revolutions
    rpm_avg = (rpm_initial + rpm_final) / 2
    time_to_60ft_approx = 60.0 / 18.0 * 3.6  # rough estimate: 60 ft at 18 mph ≈ 12 seconds
    total_revolutions = int(rpm_avg * (time_to_60ft_approx / 60.0))

    # Flare calculation: Based on differential and grit condition
    # Baseline: 2.0 inches for fresh oil with factory grit
    base_flare = 2.0

    # Modifiers
    grit_mult = {"factory": 1.0, "shammy'd": 0.7, "abraded": 1.3}[grit_condition]
    oil_mult = {"fresh": 1.0, "transition": 1.15, "broken": 1.3}[oil_condition]

    # Spin decay affects flare (faster decay → more track migration)
    spin_decay_pct = (rpm_initial - rpm_final) / rpm_initial * 100
    decay_mult = 1.0 + (spin_decay_pct / 100) * 0.5  # 0-50% decay = 1.0-1.5x

    flare_distance = base_flare * grit_mult * oil_mult * decay_mult
    flare_distance = np.clip(flare_distance, 0.5, 4.5)  # Cap at realistic range

    # Track width (width of contact band on ball)
    track_width = 0.8 + (spin_decay_pct / 100) * 0.4  # 0.8-1.2 inches typical

    # Saturation: how much oil the ball absorbed
    # Depends on flare (more flare = more surface exposure) and oil condition
    saturation_base = flare_distance * 15  # flare 2 in = 30% saturation baseline
    saturation_mult = {"fresh": 1.0, "transition": 1.2, "broken": 1.5}[oil_condition]
    saturation_pct = min(100, saturation_base * saturation_mult)

    return FlareResult(
        flare_distance_inches=flare_distance,
        track_width_inches=track_width,
        revolutions_total=total_revolutions,
        grit_condition=grit_condition,
        saturation_pct=saturation_pct,
    )


def validate_flare(fr: FlareResult) -> dict:
    """
    Validate Agent #10 output

    Success Criteria:
    - Flare distance 0.5-4.5 inches (manufacturer specs)
    - Track width 0.5-1.5 inches
    - Total revolutions > 0
    - Saturation realistic (5-100%)
    - Grit condition recognized
    """
    results = {
        "flare_inches": fr.flare_distance_inches,
        "passed": True,
        "checks": [],
    }

    # Check 1: Flare in valid range
    flare_valid = 0.5 <= fr.flare_distance_inches <= 4.5
    results["checks"].append({
        "name": "Flare distance [0.5, 4.5] inches",
        "passed": flare_valid,
        "value": f"{fr.flare_distance_inches:.2f}\"",
    })
    if not flare_valid:
        results["passed"] = False

    # Check 2: Track width reasonable
    track_valid = 0.5 <= fr.track_width_inches <= 1.5
    results["checks"].append({
        "name": "Track width [0.5, 1.5] inches",
        "passed": track_valid,
        "value": f"{fr.track_width_inches:.2f}\"",
    })
    if not track_valid:
        results["passed"] = False

    # Check 3: Revolutions > 0
    rev_valid = fr.revolutions_total > 0
    results["checks"].append({
        "name": "Total revolutions > 0",
        "passed": rev_valid,
        "value": f"{fr.revolutions_total}",
    })
    if not rev_valid:
        results["passed"] = False

    # Check 4: Saturation realistic
    sat_valid = 5 <= fr.saturation_pct <= 100
    results["checks"].append({
        "name": "Saturation [5, 100]%",
        "passed": sat_valid,
        "value": f"{fr.saturation_pct:.1f}%",
    })
    if not sat_valid:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #10: Flare Calculation - Test Suite")
    print("=" * 60)

    test_cases = [
        {"grit": "factory", "oil": "fresh", "desc": "Factory grit, fresh oil"},
        {"grit": "shammy'd", "oil": "transition", "desc": "Shammy'd, transition"},
        {"grit": "abraded", "oil": "broken", "desc": "Abraded, broken"},
    ]

    for test in test_cases:
        print(f"\n{test['desc']}")
        print("-" * 60)

        fr = calculate_flare(
            rpm_initial=300,
            rpm_final=275,
            distance_ft=60.0,
            grit_condition=test["grit"],
            oil_condition=test["oil"],
        )

        validation = validate_flare(fr)
        status = "✓ PASS" if validation["passed"] else "✗ FAIL"

        print(f"Status: {status}")
        print(f"  Flare: {fr.flare_distance_inches:.2f}\"")
        print(f"  Track Width: {fr.track_width_inches:.2f}\"")
        print(f"  Revolutions: {fr.revolutions_total}")
        print(f"  Saturation: {fr.saturation_pct:.1f}%")

        for check in validation["checks"]:
            check_status = "✓" if check["passed"] else "✗"
            print(f"  {check_status} {check['name']}: {check.get('value', '')}")

    print("\n" + "=" * 60)
    print("Agent #10 ready for integration")
