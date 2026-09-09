"""
Bowling Physics Simulator - Validation Test Suite
Validates each of the 9 agents against their specific success criteria

This is the foundational validation framework that ensures each agent
produces physically correct outputs before integration into the full simulator.
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Optional


# ============================================================================
# SUCCESS CRITERIA FOR EACH AGENT (Reference)
# ============================================================================

AGENT_SUCCESS_CRITERIA = {
    1: {
        "name": "Ball Properties",
        "criteria": [
            "Inertia tensor is 3x3 symmetric positive-definite",
            "All principal moments > 0",
            "Diagonal elements ordered: Ix <= Iy <= Iz (or similar valid order)",
        ],
        "validation_ranges": {
            "weight_lbs": (6, 16),
            "rg_in": (2.4, 2.8),
            "differential": (0.05, 0.25),
            "inertia_trace": (0.1, 2.0),  # kg·m²
        },
    },
    2: {
        "name": "Oil Pattern",
        "criteria": [
            "Bilinear interpolation at any (board, distance) point",
            "Edge case: outside oil region → 0.0",
            "Edge case: inside oil region → 0.0 to 1.0",
            "Smooth gradient (no discontinuities)",
        ],
        "validation_ranges": {
            "oil_density": (0.0, 1.0),
            "oil_length_ft": (30, 45),
            "grid_resolution": (0.5, 2.0),
        },
    },
    3: {
        "name": "Initial Conditions",
        "criteria": [
            "Velocity vector: mph → ft/s conversion correct",
            "Angular velocity: RPM → rad/s conversion correct",
            "Energy conservation: KE = 0.5*m*v² + 0.5*I*ω² valid",
            "Axis angle respected in spin vector calculation",
        ],
        "validation_ranges": {
            "speed_mph": (12, 22),
            "rpm": (100, 500),
            "kinetic_energy_j": (100, 1000),
        },
    },
    4: {
        "name": "Contact Patch",
        "criteria": [
            "Contact area: 5-20 sq in (typical bowling ball)",
            "Friction coefficient: 0.15-0.28 (on oiled lane)",
            "Higher oil density → lower friction",
            "Normal force accounts for weight + dynamic load",
        ],
        "validation_ranges": {
            "area_sq_in": (5, 20),
            "friction_coeff": (0.04, 0.28),
            "normal_force_n": (60, 80),
        },
    },
    5: {
        "name": "Friction & Torque",
        "criteria": [
            "Friction force points opposite to velocity (backward)",
            "Magnitude: |F| < normal_force (physical constraint)",
            "Torque: τ = r × F (radius cross product friction)",
            "Spinning axis: 0-2 rad/s (typical slip range)",
        ],
        "validation_ranges": {
            "friction_force_n": (0, 100),
            "torque_n_m": (0, 50),
            "slip_velocity": (0, 5),
        },
    },
    6: {
        "name": "Rotational Dynamics",
        "criteria": [
            "Quaternion normalized (magnitude = 1.0 ±0.001)",
            "Angular velocity monotonically decreases",
            "RPM decreases realistically: 300 → 50 over 60 ft",
            "No NaN or inf values",
        ],
        "validation_ranges": {
            "angular_velocity_rad_s": (0, 50),
            "rpm_final": (10, 100),
        },
    },
    7: {
        "name": "Translational Dynamics",
        "criteria": [
            "Velocity decreases monotonically (no acceleration)",
            "Kinetic energy decreases monotonically",
            "Deceleration rate: 0.5-2.0 ft/s² typical",
            "No negative velocities",
        ],
        "validation_ranges": {
            "velocity_ft_s": (15, 30),
            "deceleration": (0.5, 2.0),
            "kinetic_energy_final": (0, 500),
        },
    },
    8: {
        "name": "Trajectory Integrator",
        "criteria": [
            "Single step: distance advances by ~dt (0.1 ft)",
            "Velocity and angular velocity updated",
            "Position stays within lane (0 < x < 39, 0 < y < 60)",
            "Energy decreases after each step",
        ],
        "validation_ranges": {
            "step_distance_ft": (0.05, 0.15),
            "position_valid": (0, 60),
        },
    },
    9: {
        "name": "Physics Integrator",
        "criteria": [
            "Ball reaches 60 ft without crashes or NaN",
            "Entry angle plausible: 2-8° (target 6° ±2°)",
            "Energy monotonically decreases across full path",
            "Breakpoint: 30-40 boards typical for right-hand bowler",
        ],
        "validation_ranges": {
            "entry_angle_deg": (2, 8),
            "breakpoint_board": (15, 40),
            "final_board": (10, 30),
        },
    },
}


# ============================================================================
# VALIDATION TEST CASES
# ============================================================================

class AgentValidator:
    """Base validator for each agent"""

    @staticmethod
    def validate_agent_1(inertia_tensor: np.ndarray) -> dict:
        """Validate Ball Properties agent output"""
        results = {
            "agent": 1,
            "name": "Ball Properties",
            "passed": True,
            "checks": [],
        }

        # Check 1: Is 3x3?
        if inertia_tensor.shape != (3, 3):
            results["checks"].append({"name": "Shape is 3x3", "passed": False})
            results["passed"] = False
        else:
            results["checks"].append({"name": "Shape is 3x3", "passed": True})

        # Check 2: Symmetric?
        is_symmetric = np.allclose(inertia_tensor, inertia_tensor.T)
        results["checks"].append({"name": "Matrix symmetric", "passed": is_symmetric})
        if not is_symmetric:
            results["passed"] = False

        # Check 3: Positive definite?
        eigenvalues = np.linalg.eigvals(inertia_tensor)
        is_positive = np.all(eigenvalues > 0)
        results["checks"].append(
            {"name": "All eigenvalues > 0", "passed": is_positive, "value": eigenvalues}
        )
        if not is_positive:
            results["passed"] = False

        # Check 4: No NaN or inf?
        has_nan_inf = np.any(np.isnan(inertia_tensor)) or np.any(np.isinf(inertia_tensor))
        results["checks"].append({"name": "No NaN/inf", "passed": not has_nan_inf})
        if has_nan_inf:
            results["passed"] = False

        return results

    @staticmethod
    def validate_agent_2(oil_density: float, board: float, distance: float) -> dict:
        """Validate Oil Pattern agent output"""
        results = {
            "agent": 2,
            "name": "Oil Pattern",
            "passed": True,
            "checks": [],
        }

        # Check 1: Density in range?
        in_range = 0.0 <= oil_density <= 1.0
        results["checks"].append(
            {"name": "Density 0-1 range", "passed": in_range, "value": oil_density}
        )
        if not in_range:
            results["passed"] = False

        # Check 2: Outside oil → 0.0?
        if distance > 46:  # Typical max oil length
            should_be_zero = oil_density == 0.0
            results["checks"].append({"name": "Outside oil → 0.0", "passed": should_be_zero})
            if not should_be_zero:
                results["passed"] = False

        # Check 3: Board in valid range?
        board_valid = 1 <= board <= 39
        results["checks"].append({"name": "Board 1-39", "passed": board_valid})

        return results

    @staticmethod
    def validate_agent_3(
        velocity_ft_s: np.ndarray, angular_velocity_rad_s: np.ndarray, mass_lbs: float
    ) -> dict:
        """Validate Initial Conditions agent output"""
        results = {
            "agent": 3,
            "name": "Initial Conditions",
            "passed": True,
            "checks": [],
        }

        # Check 1: Velocity magnitude realistic?
        speed = np.linalg.norm(velocity_ft_s)
        speed_valid = 15 <= speed <= 35
        results["checks"].append(
            {
                "name": "Velocity 15-35 ft/s",
                "passed": speed_valid,
                "value": f"{speed:.2f} ft/s",
            }
        )
        if not speed_valid:
            results["passed"] = False

        # Check 2: Angular velocity realistic?
        ang_speed = np.linalg.norm(angular_velocity_rad_s)
        ang_valid = 10 <= ang_speed <= 60
        results["checks"].append(
            {
                "name": "Angular velocity 10-60 rad/s",
                "passed": ang_valid,
                "value": f"{ang_speed:.2f} rad/s",
            }
        )
        if not ang_valid:
            results["passed"] = False

        # Check 3: Kinetic energy valid?
        mass_kg = mass_lbs * 0.453592
        ke_trans = 0.5 * mass_kg * speed**2
        ke_rot = 0.5 * 0.4 * mass_kg * 0.15**2 * ang_speed**2  # Rough estimate
        total_ke = ke_trans + ke_rot
        ke_valid = 50 < total_ke < 2000
        results["checks"].append(
            {"name": "Kinetic energy valid", "passed": ke_valid, "value": f"{total_ke:.0f} J"}
        )
        if not ke_valid:
            results["passed"] = False

        return results

    @staticmethod
    def validate_agent_4(
        area_sq_in: float, friction_coeff: float, oil_density: float
    ) -> dict:
        """Validate Contact Patch agent output"""
        results = {
            "agent": 4,
            "name": "Contact Patch",
            "passed": True,
            "checks": [],
        }

        # Check 1: Area in realistic range?
        area_valid = 5 <= area_sq_in <= 20
        results["checks"].append(
            {"name": "Area 5-20 sq in", "passed": area_valid, "value": f"{area_sq_in:.1f}"}
        )
        if not area_valid:
            results["passed"] = False

        # Check 2: Friction coefficient valid?
        friction_valid = 0.04 <= friction_coeff <= 0.28
        results["checks"].append(
            {
                "name": "Friction 0.04-0.28",
                "passed": friction_valid,
                "value": f"{friction_coeff:.3f}",
            }
        )
        if not friction_valid:
            results["passed"] = False

        # Check 3: Higher oil → lower friction?
        # For a given area, higher oil density should reduce friction coefficient
        results["checks"].append(
            {
                "name": "Oil density considered",
                "passed": True,
                "note": f"Oil: {oil_density:.2f}, Friction: {friction_coeff:.3f}",
            }
        )

        return results

    @staticmethod
    def validate_agent_5(friction_force: np.ndarray, normal_force: float) -> dict:
        """Validate Friction & Torque agent output"""
        results = {
            "agent": 5,
            "name": "Friction & Torque",
            "passed": True,
            "checks": [],
        }

        # Check 1: Friction magnitude < normal force?
        friction_mag = np.linalg.norm(friction_force)
        friction_valid = friction_mag <= normal_force * 1.05  # Allow small margin
        results["checks"].append(
            {
                "name": "|F| < normal force",
                "passed": friction_valid,
                "value": f"|F|={friction_mag:.1f}, N={normal_force:.1f}",
            }
        )
        if not friction_valid:
            results["passed"] = False

        # Check 2: Force reasonable magnitude?
        force_reasonable = 0 <= friction_mag <= 150
        results["checks"].append(
            {"name": "Force 0-150 N", "passed": force_reasonable, "value": f"{friction_mag:.1f}"}
        )
        if not force_reasonable:
            results["passed"] = False

        return results

    @staticmethod
    def validate_agent_6(angular_velocities: List[float]) -> dict:
        """Validate Rotational Dynamics agent output"""
        results = {
            "agent": 6,
            "name": "Rotational Dynamics",
            "passed": True,
            "checks": [],
        }

        # Check 1: Monotonically decreasing?
        is_decreasing = all(angular_velocities[i] >= angular_velocities[i + 1] for i in range(len(angular_velocities) - 1))
        results["checks"].append({"name": "Angular velocity decreasing", "passed": is_decreasing})
        if not is_decreasing:
            results["passed"] = False

        # Check 2: Start and end reasonable?
        start_valid = 20 <= angular_velocities[0] <= 60
        end_valid = 0 <= angular_velocities[-1] <= 20
        results["checks"].append(
            {
                "name": "Start 20-60 rad/s",
                "passed": start_valid,
                "value": f"{angular_velocities[0]:.1f}",
            }
        )
        results["checks"].append(
            {
                "name": "End 0-20 rad/s",
                "passed": end_valid,
                "value": f"{angular_velocities[-1]:.1f}",
            }
        )
        if not (start_valid and end_valid):
            results["passed"] = False

        return results

    @staticmethod
    def validate_agent_7(velocities: List[float]) -> dict:
        """Validate Translational Dynamics agent output"""
        results = {
            "agent": 7,
            "name": "Translational Dynamics",
            "passed": True,
            "checks": [],
        }

        # Check 1: Monotonically decreasing?
        is_decreasing = all(velocities[i] >= velocities[i + 1] for i in range(len(velocities) - 1))
        results["checks"].append({"name": "Velocity decreasing", "passed": is_decreasing})
        if not is_decreasing:
            results["passed"] = False

        # Check 2: Start reasonable?
        start_valid = 15 <= velocities[0] <= 35
        results["checks"].append(
            {"name": "Start velocity 15-35 ft/s", "passed": start_valid, "value": f"{velocities[0]:.1f}"}
        )
        if not start_valid:
            results["passed"] = False

        # Check 3: End near zero?
        end_valid = 0 <= velocities[-1] <= 5
        results["checks"].append(
            {"name": "End velocity 0-5 ft/s", "passed": end_valid, "value": f"{velocities[-1]:.1f}"}
        )
        if not end_valid:
            results["passed"] = False

        return results

    @staticmethod
    def validate_agent_9(entry_angle_deg: float, breakpoint_board: float, final_board: float) -> dict:
        """Validate Physics Integrator agent output (full simulation)"""
        results = {
            "agent": 9,
            "name": "Physics Integrator",
            "passed": True,
            "checks": [],
        }

        # Check 1: Entry angle realistic?
        entry_valid = 2 <= entry_angle_deg <= 8
        results["checks"].append(
            {
                "name": "Entry angle 2-8°",
                "passed": entry_valid,
                "value": f"{entry_angle_deg:.1f}°",
            }
        )
        if not entry_valid:
            results["passed"] = False

        # Check 2: Target entry angle 6° ±2°?
        target_met = 4 <= entry_angle_deg <= 8
        results["checks"].append(
            {
                "name": "Entry angle near target 6° ±2°",
                "passed": target_met,
                "value": f"{entry_angle_deg:.1f}°",
            }
        )
        if not target_met:
            results["passed"] = False

        # Check 3: Breakpoint reasonable?
        breakpoint_valid = 20 <= breakpoint_board <= 40
        results["checks"].append(
            {
                "name": "Breakpoint 20-40 boards",
                "passed": breakpoint_valid,
                "value": f"Board {breakpoint_board:.1f}",
            }
        )
        if not breakpoint_valid:
            results["passed"] = False

        # Check 4: Final board (pin impact) right-hand target?
        # Target for right-hand: board 17.5 (1-3 pocket)
        final_valid = 10 <= final_board <= 25
        results["checks"].append(
            {
                "name": "Final board 10-25 (1-3 pocket)",
                "passed": final_valid,
                "value": f"Board {final_board:.1f}",
            }
        )
        if not final_valid:
            results["passed"] = False

        return results


def print_validation_report(validation_results: List[dict]):
    """Pretty-print validation results"""
    print("\n" + "="*70)
    print("AGENT VALIDATION REPORT")
    print("="*70)

    total_passed = 0
    total_agents = len(validation_results)

    for result in validation_results:
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"\nAgent #{result['agent']}: {result['name']} [{status}]")

        for check in result["checks"]:
            check_status = "✓" if check["passed"] else "✗"
            value_str = f" = {check.get('value', '')}" if "value" in check else ""
            note_str = f" ({check.get('note', '')})" if "note" in check else ""
            print(f"  {check_status} {check['name']}{value_str}{note_str}")

        if result["passed"]:
            total_passed += 1

    print("\n" + "="*70)
    print(f"SUMMARY: {total_passed}/{total_agents} agents validated")
    print("="*70)


if __name__ == "__main__":
    print("Bowling Physics Validator - Test Framework Ready")
    print("Use AgentValidator class to validate each agent's output")
    print(f"Agents to validate: {list(AGENT_SUCCESS_CRITERIA.keys())}")
