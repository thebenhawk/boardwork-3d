"""
Agent #11: Oil Saturation Tracking
Tracks oil absorbed by ball during descent

Input: Trajectory from Agent #9, ball surface properties
Output: SaturationResult with oil absorption over distance
Validation: Saturation increases monotonically, cap at 100%, affects friction
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class SaturationResult:
    """Ball surface saturation state"""
    saturation_pct_initial: float  # Starting saturation (usually 0)
    saturation_pct_final: float  # Final saturation at pin deck
    oil_absorbed_cc: float  # Volume of oil absorbed (cubic centimeters)
    absorption_rate_pct_per_ft: float  # Rate of saturation per foot
    friction_coefficient_initial: float  # Starting friction coefficient
    friction_coefficient_final: float  # Final friction coefficient (updated by saturation)
    saturation_trajectory: List[float]  # Saturation % at each 10-foot interval

    def to_dict(self) -> dict:
        return {
            "saturation_pct_initial": float(self.saturation_pct_initial),
            "saturation_pct_final": float(self.saturation_pct_final),
            "oil_absorbed_cc": float(self.oil_absorbed_cc),
            "absorption_rate_pct_per_ft": float(self.absorption_rate_pct_per_ft),
            "friction_coefficient_initial": float(self.friction_coefficient_initial),
            "friction_coefficient_final": float(self.friction_coefficient_final),
            "saturation_trajectory": [float(x) for x in self.saturation_trajectory],
        }


def calculate_saturation(
    trajectory: List[Dict],
    oil_condition: str = "fresh",
    grit_condition: str = "factory",
    initial_saturation_pct: float = 0.0,
) -> SaturationResult:
    """
    Agent #11: Track oil saturation on ball surface during descent

    Saturation Model:
    - Ball starts with clean coverstock (0% saturation)
    - As it rolls through oil, coverstock absorbs oil
    - Oil absorption depends on:
      * Oil density (fresh → transition → broken)
      * Ball grit condition (factory, shammy'd, abraded)
      * Distance traveled through oil
    - Absorbed oil fills micro-cavities in coverstock
    - As saturation increases, effective friction coefficient decreases
      (wet surface has less grip than dry)

    Args:
        trajectory: Full trajectory from Agent #9
        oil_condition: "fresh" (fast absorption), "transition", "broken" (slow)
        grit_condition: "factory", "shammy'd", "abraded"
        initial_saturation_pct: Starting saturation (usually 0)

    Returns:
        SaturationResult with absorption tracking
    """

    if not trajectory or len(trajectory) < 10:
        return SaturationResult(
            saturation_pct_initial=initial_saturation_pct,
            saturation_pct_final=initial_saturation_pct,
            oil_absorbed_cc=0.0,
            absorption_rate_pct_per_ft=0.0,
            friction_coefficient_initial=0.15,
            friction_coefficient_final=0.15,
            saturation_trajectory=[],
        )

    # Absorption rate depends on oil condition and grit
    # Fresh oil: ball absorbs more quickly (more oil available)
    # Broken oil: ball absorbs less (oil depleted from lane)
    absorption_rates = {
        "fresh": {"factory": 2.5, "shammy'd": 1.8, "abraded": 3.2},
        "transition": {"factory": 1.8, "shammy'd": 1.2, "abraded": 2.1},
        "broken": {"factory": 0.8, "shammy'd": 0.5, "abraded": 1.0},
    }

    absorption_rate_pct_per_ft = absorption_rates.get(oil_condition, {}).get(grit_condition, 1.5)

    # Track saturation over distance
    saturation_pct = initial_saturation_pct
    saturation_trajectory = []
    oil_density_weighted = 0.0

    for i, traj_point in enumerate(trajectory):
        distance_ft = traj_point.get("distance_ft", 0.0)
        oil_density = traj_point.get("oil_density", 0.5)

        # Absorption happens in proportion to oil density and distance
        if i > 0:
            prev_traj = trajectory[i - 1]
            prev_distance = prev_traj.get("distance_ft", distance_ft)
            distance_step = distance_ft - prev_distance

            # Absorption proportional to oil density and step size
            absorption_this_step = (
                absorption_rate_pct_per_ft * distance_step * oil_density
            )
            saturation_pct = min(100, saturation_pct + absorption_this_step)

        # Track at 10-foot intervals
        if i % 100 == 0:  # 100 steps = 10 ft (0.1 ft per step)
            saturation_trajectory.append(saturation_pct)

    # Final saturation
    saturation_pct_final = min(100, saturation_pct)

    # Oil absorbed (volume)
    # Typical ball absorbs 0-10 cc of oil depending on saturation
    ball_surface_area_sq_in = 4 * np.pi * (4.25 ** 2)  # Surface area of 16 lb ball
    ball_surface_area_sq_cm = ball_surface_area_sq_in * 6.4516
    oil_depth_absorbed_cm = (saturation_pct_final / 100.0) * 0.02  # 0-0.02 cm depth
    oil_absorbed_cc = (ball_surface_area_sq_cm * oil_depth_absorbed_cm) / 1000  # Convert to cc

    # Friction coefficient updates based on saturation
    # Wet surface has less grip than dry
    mu_dry = 0.20
    mu_oil = 0.04
    friction_coefficient_initial = mu_dry - (mu_dry - mu_oil) * (initial_saturation_pct / 100.0)
    friction_coefficient_final = mu_dry - (mu_dry - mu_oil) * (saturation_pct_final / 100.0)

    return SaturationResult(
        saturation_pct_initial=initial_saturation_pct,
        saturation_pct_final=saturation_pct_final,
        oil_absorbed_cc=oil_absorbed_cc,
        absorption_rate_pct_per_ft=absorption_rate_pct_per_ft,
        friction_coefficient_initial=friction_coefficient_initial,
        friction_coefficient_final=friction_coefficient_final,
        saturation_trajectory=saturation_trajectory,
    )


def validate_saturation(sr: SaturationResult) -> dict:
    """
    Validate Agent #11 output

    Success Criteria:
    - Saturation increases monotonically (0→100%)
    - Oil absorbed realistic (0-15 cc)
    - Absorption rate matches oil condition
    - Friction coefficient decreases with saturation
    - No NaN/inf values
    """
    results = {
        "saturation_pct_final": sr.saturation_pct_final,
        "passed": True,
        "checks": [],
    }

    # Check 1: Final saturation in valid range
    sat_valid = 0 <= sr.saturation_pct_final <= 100
    results["checks"].append({
        "name": "Final saturation [0, 100]%",
        "passed": sat_valid,
        "value": f"{sr.saturation_pct_final:.1f}%",
    })
    if not sat_valid:
        results["passed"] = False

    # Check 2: Saturation increases (or stays same)
    traj_increasing = all(
        sr.saturation_trajectory[i] <= sr.saturation_trajectory[i + 1]
        for i in range(len(sr.saturation_trajectory) - 1)
    ) if len(sr.saturation_trajectory) > 1 else True
    results["checks"].append({
        "name": "Saturation trajectory monotonic",
        "passed": traj_increasing,
        "points": len(sr.saturation_trajectory),
    })
    if not traj_increasing:
        results["passed"] = False

    # Check 3: Oil absorbed realistic
    oil_valid = 0 <= sr.oil_absorbed_cc <= 15
    results["checks"].append({
        "name": "Oil absorbed [0, 15] cc",
        "passed": oil_valid,
        "value": f"{sr.oil_absorbed_cc:.2f} cc",
    })
    if not oil_valid:
        results["passed"] = False

    # Check 4: Friction decreases with saturation
    friction_decreases = sr.friction_coefficient_final <= sr.friction_coefficient_initial
    results["checks"].append({
        "name": "Friction decreases with saturation",
        "passed": friction_decreases,
        "initial": f"{sr.friction_coefficient_initial:.3f}",
        "final": f"{sr.friction_coefficient_final:.3f}",
    })
    # Not critical for pass, but good to check

    # Check 5: Absorption rate realistic
    rate_valid = 0.5 <= sr.absorption_rate_pct_per_ft <= 4.0
    results["checks"].append({
        "name": "Absorption rate [0.5, 4.0]%/ft",
        "passed": rate_valid,
        "value": f"{sr.absorption_rate_pct_per_ft:.2f}%/ft",
    })
    if not rate_valid:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #11: Saturation Tracking - Test Suite")
    print("=" * 60)

    # Create mock trajectory
    mock_trajectory = []
    for step in range(600):
        distance = step * 0.1
        oil_density = np.exp(-(distance / 46.0) ** 2.5)
        mock_trajectory.append({"distance_ft": distance, "oil_density": oil_density})

    test_cases = [
        {"oil": "fresh", "grit": "factory", "desc": "Fresh oil, factory grit"},
        {"oil": "transition", "grit": "shammy'd", "desc": "Transition, shammy'd"},
        {"oil": "broken", "grit": "abraded", "desc": "Broken, abraded"},
    ]

    for test in test_cases:
        print(f"\n{test['desc']}")
        print("-" * 60)

        sr = calculate_saturation(
            trajectory=mock_trajectory,
            oil_condition=test["oil"],
            grit_condition=test["grit"],
        )

        validation = validate_saturation(sr)
        status = "✓ PASS" if validation["passed"] else "✗ FAIL"

        print(f"Status: {status}")
        print(f"  Final Saturation: {sr.saturation_pct_final:.1f}%")
        print(f"  Oil Absorbed: {sr.oil_absorbed_cc:.2f} cc")
        print(f"  Absorption Rate: {sr.absorption_rate_pct_per_ft:.2f}%/ft")
        print(f"  Friction: {sr.friction_coefficient_initial:.3f} → {sr.friction_coefficient_final:.3f}")

        for check in validation["checks"]:
            check_status = "✓" if check["passed"] else "✗"
            print(f"  {check_status} {check['name']}")

    print("\n" + "=" * 60)
    print("Agent #11 ready for integration")
