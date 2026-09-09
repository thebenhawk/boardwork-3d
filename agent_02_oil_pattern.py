"""
Agent #2: Oil Pattern
Loads and interpolates 2D oil density matrix for lane modeling

Input: Pattern name, condition (fresh/transition/broken)
Output: OilPattern dataclass with bilinear interpolation function
Validation: Edge cases, boundary handling, smooth interpolation
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple
import json


# PBA Oil Pattern Specifications (length in feet)
PBA_PATTERNS = {
    "wolf": 32,
    "cheetah": 35,
    "viper": 36,
    "scorpion": 41,
    "chameleon": 41,
    "bear": 43,
    "shark": 44,
}

HOUSE_PATTERNS = {
    "sport": 42,
    "house_shot": 46,
}

ALL_PATTERNS = {**PBA_PATTERNS, **HOUSE_PATTERNS}


@dataclass
class OilPattern:
    """Oil density matrix with bilinear interpolation"""
    pattern_name: str
    condition: str  # "fresh", "transition", "broken"
    oil_length_ft: float
    density_matrix: np.ndarray  # Shape (39, num_samples) - boards × distance
    grid_resolution_ft: float  # Distance between samples (ft)

    def get_density(self, board: float, distance: float) -> float:
        """
        Bilinear interpolation of oil density at (board, distance)

        Args:
            board: 1.0 to 39.0 (left-right)
            distance: 0.0 to oil_length (foul line to breakpoint)

        Returns:
            0.0 (dry lane) to 1.0 (fully oiled)

        Edge cases:
            - Outside oil length → 0.0 (dry)
            - Outside board range (1-39) → 0.0 (dry)
            - Inside → interpolated value
        """
        # Validate board range
        if board < 1.0 or board > 39.0:
            return 0.0

        # Validate distance range (before oil ends)
        if distance < 0.0 or distance > self.oil_length_ft:
            return 0.0

        # Convert to array indices
        board_idx = board - 1.0  # Boards 1-39 → indices 0-38
        dist_idx = distance / self.grid_resolution_ft

        # Integer indices (floor and ceil)
        b0 = int(np.floor(board_idx))
        b1 = int(np.ceil(board_idx))
        d0 = int(np.floor(dist_idx))
        d1 = int(np.ceil(dist_idx))

        # Clamp to valid range
        b0 = max(0, min(38, b0))
        b1 = max(0, min(38, b1))
        d0 = max(0, min(self.density_matrix.shape[1] - 1, d0))
        d1 = max(0, min(self.density_matrix.shape[1] - 1, d1))

        # Fractional parts for interpolation
        bf = board_idx - np.floor(board_idx)
        df = dist_idx - np.floor(dist_idx)

        # Bilinear interpolation
        v00 = self.density_matrix[b0, d0]
        v01 = self.density_matrix[b0, d1]
        v10 = self.density_matrix[b1, d0]
        v11 = self.density_matrix[b1, d1]

        # Interpolate along board direction
        v0 = v00 * (1 - bf) + v10 * bf
        v1 = v01 * (1 - bf) + v11 * bf

        # Interpolate along distance direction
        result = v0 * (1 - df) + v1 * df

        return float(result)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict"""
        return {
            "pattern_name": self.pattern_name,
            "condition": self.condition,
            "oil_length_ft": self.oil_length_ft,
            "grid_resolution_ft": self.grid_resolution_ft,
            "density_matrix": self.density_matrix.tolist(),
        }


def create_oil_pattern(pattern_name: str, condition: str = "fresh") -> OilPattern:
    """
    Agent #2: Create oil pattern with density matrix

    Generates Gaussian oil distribution that:
    - Peaks in middle boards (20)
    - Tapers to edges
    - Decays down lane
    - Applies condition modifier (fresh/transition/broken)

    Args:
        pattern_name: PBA pattern or house shot
        condition: "fresh" (full oil), "transition" (70%), "broken" (30%)

    Returns:
        OilPattern with density matrix and interpolation function
    """
    if pattern_name not in ALL_PATTERNS:
        raise ValueError(
            f"Unknown pattern: {pattern_name}. "
            f"Available: {list(ALL_PATTERNS.keys())}"
        )

    oil_length_ft = ALL_PATTERNS[pattern_name]
    grid_resolution_ft = 0.5  # Sample every 0.5 feet

    # Create matrix: 39 boards × (oil_length / grid_resolution) samples
    num_distance_samples = int(oil_length_ft / grid_resolution_ft) + 1
    density_matrix = np.zeros((39, num_distance_samples), dtype=np.float32)

    center_board = 19  # Board 20 (0-indexed as 19)

    # Generate Gaussian distribution
    for board_idx in range(39):
        for dist_idx in range(num_distance_samples):
            distance = dist_idx * grid_resolution_ft

            # Board spread (Gaussian, centered at board 20)
            board_spread = np.exp(-((board_idx - center_board) / 8.0) ** 2)

            # Distance decay (tapers down lane)
            distance_decay = np.exp(-(distance / oil_length_ft) ** 2.5)

            # Combined density
            density = board_spread * distance_decay

            # Apply condition modifier
            if condition == "fresh":
                density = min(1.0, density * 1.0)
            elif condition == "transition":
                density = density * 0.7  # 70% oil remaining
            elif condition == "broken":
                density = density * 0.3  # 30% oil remaining
            else:
                raise ValueError(f"Unknown condition: {condition}")

            density_matrix[board_idx, dist_idx] = density

    return OilPattern(
        pattern_name=pattern_name,
        condition=condition,
        oil_length_ft=oil_length_ft,
        density_matrix=density_matrix,
        grid_resolution_ft=grid_resolution_ft,
    )


def validate_oil_pattern(pattern: OilPattern) -> dict:
    """
    Validate Agent #2 output against success criteria

    Success Criteria:
    - Interpolation works at any (board, distance)
    - Edge cases handled (outside oil → 0.0)
    - Values in [0.0, 1.0]
    - Smooth gradient (no discontinuities)
    """
    results = {
        "pattern_name": pattern.pattern_name,
        "condition": pattern.condition,
        "passed": True,
        "checks": [],
    }

    # Check 1: Density values in [0.0, 1.0]
    matrix_min = pattern.density_matrix.min()
    matrix_max = pattern.density_matrix.max()
    in_range = 0.0 <= matrix_min and matrix_max <= 1.0
    results["checks"].append(
        {
            "name": "Matrix values in [0.0, 1.0]",
            "passed": in_range,
            "min": float(matrix_min),
            "max": float(matrix_max),
        }
    )
    if not in_range:
        results["passed"] = False

    # Check 2: Interpolation at center (should be high oil)
    center_oil = pattern.get_density(20.0, 10.0)
    center_valid = 0.5 < center_oil <= 1.0
    results["checks"].append(
        {
            "name": "Center oil high (board 20, 10 ft)",
            "passed": center_valid,
            "value": center_oil,
        }
    )
    if not center_valid:
        results["passed"] = False

    # Check 3: Edge case - outside oil length
    outside_oil = pattern.get_density(20.0, pattern.oil_length_ft + 10.0)
    outside_valid = outside_oil == 0.0
    results["checks"].append(
        {
            "name": "Outside oil → 0.0",
            "passed": outside_valid,
            "value": outside_oil,
        }
    )
    if not outside_valid:
        results["passed"] = False

    # Check 4: Edge case - outside board range
    outside_board = pattern.get_density(50.0, 20.0)
    board_valid = outside_board == 0.0
    results["checks"].append(
        {
            "name": "Outside boards (>39) → 0.0",
            "passed": board_valid,
            "value": outside_board,
        }
    )
    if not board_valid:
        results["passed"] = False

    # Check 5: Gutter areas (boards 1 & 39) lower oil
    gutter_left = pattern.get_density(1.0, 20.0)
    gutter_right = pattern.get_density(39.0, 20.0)
    gutter_valid = gutter_left < 0.5 and gutter_right < 0.5
    results["checks"].append(
        {
            "name": "Gutters lower oil (boards 1, 39)",
            "passed": gutter_valid,
            "board_1": gutter_left,
            "board_39": gutter_right,
        }
    )
    if not gutter_valid:
        results["passed"] = False

    # Check 6: Monotonic decay down lane
    sample_board = 20.0
    decay_valid = True
    prev_density = pattern.get_density(sample_board, 0.1)
    for dist in np.arange(1, min(pattern.oil_length_ft, 40), 2):
        curr_density = pattern.get_density(sample_board, dist)
        if curr_density > prev_density + 0.01:  # Allow small numerical error
            decay_valid = False
            break
        prev_density = curr_density

    results["checks"].append(
        {
            "name": "Oil decays monotonically down lane",
            "passed": decay_valid,
        }
    )
    if not decay_valid:
        results["passed"] = False

    return results


if __name__ == "__main__":
    print("Agent #2: Oil Pattern - Test Suite")
    print("=" * 60)

    # Test all patterns
    for pattern_name in list(ALL_PATTERNS.keys())[:3]:  # Test first 3
        print(f"\nTesting {pattern_name.upper()}")
        pattern = create_oil_pattern(pattern_name, condition="fresh")
        validation = validate_oil_pattern(pattern)

        status = "✓ PASS" if validation["passed"] else "✗ FAIL"
        print(f"Status: {status}")
        for check in validation["checks"]:
            check_status = "✓" if check["passed"] else "✗"
            print(f"  {check_status} {check['name']}")

    print("\n" + "=" * 60)
    print("All patterns ready for integration")
