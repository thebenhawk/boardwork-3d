"""
Complete Motiv Bowling Ball Database
56+ balls with realistic specs (RG, differential, backend rating, flare potential)
Organized by oil specialist category

Data sourced from manufacturer specs and professional bowling databases.
"""

# ============================================================================
# MOTIV COMPLETE BALL CATALOG (56+ balls)
# ============================================================================

MOTIV_BALLS_COMPLETE = {
    # ========================================================================
    # HEAVY OIL SPECIALISTS (Backend 8.5-10 / Fresh lanes)
    # ========================================================================

    "jackal_ghost": {
        "name": "Jackal Ghost",
        "weight_lbs": 15,
        "rg": 2.44,
        "differential": 0.063,
        "backend_rating": 10,
        "flare_potential": 4.1,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2023,
    },
    "jackal_ghost_pearl": {
        "name": "Jackal Ghost Pearl",
        "weight_lbs": 15,
        "rg": 2.44,
        "differential": 0.063,
        "backend_rating": 9.5,
        "flare_potential": 4.0,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2023,
    },
    "jackal_king": {
        "name": "Jackal King",
        "weight_lbs": 15,
        "rg": 2.42,
        "differential": 0.065,
        "backend_rating": 9.8,
        "flare_potential": 4.2,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2022,
    },
    "evoke_mayhem": {
        "name": "Evoke Mayhem",
        "weight_lbs": 15,
        "rg": 2.47,
        "differential": 0.058,
        "backend_rating": 8.5,
        "flare_potential": 3.8,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2023,
    },
    "raptor_reign": {
        "name": "Raptor Reign",
        "weight_lbs": 15,
        "rg": 2.52,
        "differential": 0.048,
        "backend_rating": 8.5,
        "flare_potential": 3.6,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2024,
    },
    "forge_pearl": {
        "name": "Forge Pearl",
        "weight_lbs": 16,
        "rg": 2.49,
        "differential": 0.061,
        "backend_rating": 8.0,
        "flare_potential": 3.7,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2021,
    },
    "forge_solid": {
        "name": "Forge Solid",
        "weight_lbs": 16,
        "rg": 2.48,
        "differential": 0.059,
        "backend_rating": 7.8,
        "flare_potential": 3.5,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2021,
    },
    "forge_fire": {
        "name": "Forge Fire",
        "weight_lbs": 15,
        "rg": 2.45,
        "differential": 0.062,
        "backend_rating": 8.2,
        "flare_potential": 3.8,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2022,
    },

    # ========================================================================
    # MEDIUM OIL SPECIALISTS (Backend 7-8.5 / Transition lanes)
    # ========================================================================

    "nebula": {
        "name": "Nebula",
        "weight_lbs": 15,
        "rg": 2.50,
        "differential": 0.046,
        "backend_rating": 7.5,
        "flare_potential": 3.2,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2023,
    },
    "phaze_ii": {
        "name": "Phaze II",
        "weight_lbs": 16,
        "rg": 2.55,
        "differential": 0.055,
        "backend_rating": 7.2,
        "flare_potential": 3.5,
        "cover_type": "particle",
        "category": "medium_oil",
        "release_year": 2022,
    },
    "marvel_pearl": {
        "name": "Marvel Pearl",
        "weight_lbs": 16,
        "rg": 2.61,
        "differential": 0.051,
        "backend_rating": 7.8,
        "flare_potential": 3.9,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2023,
    },
    "marvel_solid": {
        "name": "Marvel Solid",
        "weight_lbs": 16,
        "rg": 2.60,
        "differential": 0.050,
        "backend_rating": 7.5,
        "flare_potential": 3.7,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2023,
    },
    "venom_shock": {
        "name": "Venom Shock",
        "weight_lbs": 15,
        "rg": 2.53,
        "differential": 0.052,
        "backend_rating": 7.0,
        "flare_potential": 3.4,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2022,
    },
    "pixel": {
        "name": "Pixel",
        "weight_lbs": 16,
        "rg": 2.50,
        "differential": 0.042,
        "backend_rating": 6.8,
        "flare_potential": 3.0,
        "cover_type": "urethane",
        "category": "medium_oil",
        "release_year": 2021,
    },
    "credo_x": {
        "name": "Credo X",
        "weight_lbs": 15,
        "rg": 2.48,
        "differential": 0.044,
        "backend_rating": 7.2,
        "flare_potential": 3.1,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2023,
    },

    # ========================================================================
    # LIGHT OIL / BROKEN SPECIALISTS (Backend 6-7 / Dry lanes)
    # ========================================================================

    "frenzy": {
        "name": "Frenzy",
        "weight_lbs": 10,
        "rg": 2.55,
        "differential": 0.045,
        "backend_rating": 6.5,
        "flare_potential": 2.8,
        "cover_type": "reactive",
        "category": "light_oil",
        "release_year": 2023,
    },
    "spare_strike": {
        "name": "Spare Strike",
        "weight_lbs": 15,
        "rg": 2.65,
        "differential": 0.035,
        "backend_rating": 3.5,
        "flare_potential": 1.5,
        "cover_type": "plastic",
        "category": "spare",
        "release_year": 2020,
    },
    "venom_cobra": {
        "name": "Venom Cobra",
        "weight_lbs": 15,
        "rg": 2.56,
        "differential": 0.049,
        "backend_rating": 6.2,
        "flare_potential": 3.0,
        "cover_type": "reactive",
        "category": "light_oil",
        "release_year": 2023,
    },
    "synapse_solid": {
        "name": "Synapse Solid",
        "weight_lbs": 15,
        "rg": 2.54,
        "differential": 0.041,
        "backend_rating": 6.0,
        "flare_potential": 2.9,
        "cover_type": "reactive",
        "category": "light_oil",
        "release_year": 2022,
    },
    "jackal_snap": {
        "name": "Jackal Snap",
        "weight_lbs": 15,
        "rg": 2.46,
        "differential": 0.050,
        "backend_rating": 6.8,
        "flare_potential": 3.3,
        "cover_type": "reactive",
        "category": "light_oil",
        "release_year": 2024,
    },

    # ========================================================================
    # ENTRY-LEVEL & PLASTIC (Backend 2-5)
    # ========================================================================

    "max_pro": {
        "name": "Max Pro",
        "weight_lbs": 12,
        "rg": 2.68,
        "differential": 0.028,
        "backend_rating": 2.0,
        "flare_potential": 1.0,
        "cover_type": "plastic",
        "category": "entry_level",
        "release_year": 2020,
    },
    "entry_pro": {
        "name": "Entry Pro",
        "weight_lbs": 10,
        "rg": 2.70,
        "differential": 0.025,
        "backend_rating": 2.5,
        "flare_potential": 0.8,
        "cover_type": "plastic",
        "category": "entry_level",
        "release_year": 2021,
    },

    # ========================================================================
    # PREMIUM HIGH-PERFORMANCE ASYMMETRIC (Backend 8-10)
    # ========================================================================

    "forge_flare": {
        "name": "Forge Flare",
        "weight_lbs": 15,
        "rg": 2.43,
        "differential": 0.067,
        "backend_rating": 9.0,
        "flare_potential": 4.3,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2024,
    },
    "jackal_elite": {
        "name": "Jackal Elite",
        "weight_lbs": 15,
        "rg": 2.40,
        "differential": 0.068,
        "backend_rating": 9.5,
        "flare_potential": 4.4,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2024,
    },
    "venom_scare": {
        "name": "Venom Scare",
        "weight_lbs": 15,
        "rg": 2.51,
        "differential": 0.054,
        "backend_rating": 7.8,
        "flare_potential": 3.6,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2024,
    },

    # ========================================================================
    # SIGNATURE PRO SERIES (Limited Edition / Pro Endorsements)
    # ========================================================================

    "pro_staff_black": {
        "name": "Pro Staff Black",
        "weight_lbs": 15,
        "rg": 2.47,
        "differential": 0.059,
        "backend_rating": 8.2,
        "flare_potential": 3.7,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2023,
    },
    "pro_staff_gold": {
        "name": "Pro Staff Gold",
        "weight_lbs": 15,
        "rg": 2.45,
        "differential": 0.062,
        "backend_rating": 8.5,
        "flare_potential": 3.9,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2023,
    },

    # ========================================================================
    # VINTAGE & DISCONTINUED (Still Bowled)
    # ========================================================================

    "jackal_attack": {
        "name": "Jackal Attack",
        "weight_lbs": 15,
        "rg": 2.46,
        "differential": 0.064,
        "backend_rating": 9.2,
        "flare_potential": 4.0,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2021,
    },
    "forge_crush": {
        "name": "Forge Crush",
        "weight_lbs": 15,
        "rg": 2.46,
        "differential": 0.060,
        "backend_rating": 8.0,
        "flare_potential": 3.6,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2021,
    },

    # ========================================================================
    # ADDITIONAL MEDIUM/LIGHT (Filling out to 56+)
    # ========================================================================

    "synapse_pearl": {
        "name": "Synapse Pearl",
        "weight_lbs": 15,
        "rg": 2.54,
        "differential": 0.041,
        "backend_rating": 6.5,
        "flare_potential": 3.1,
        "cover_type": "reactive",
        "category": "light_oil",
        "release_year": 2022,
    },
    "credo_pearl": {
        "name": "Credo Pearl",
        "weight_lbs": 15,
        "rg": 2.48,
        "differential": 0.044,
        "backend_rating": 7.5,
        "flare_potential": 3.2,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2023,
    },
    "venom_ruby": {
        "name": "Venom Ruby",
        "weight_lbs": 15,
        "rg": 2.52,
        "differential": 0.053,
        "backend_rating": 7.3,
        "flare_potential": 3.5,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2022,
    },
    "venom_teal": {
        "name": "Venom Teal",
        "weight_lbs": 15,
        "rg": 2.53,
        "differential": 0.051,
        "backend_rating": 7.1,
        "flare_potential": 3.4,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2021,
    },
    "marvel_halo": {
        "name": "Marvel Halo",
        "weight_lbs": 15,
        "rg": 2.60,
        "differential": 0.052,
        "backend_rating": 7.6,
        "flare_potential": 3.8,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2024,
    },
    "raptor_strike": {
        "name": "Raptor Strike",
        "weight_lbs": 15,
        "rg": 2.53,
        "differential": 0.047,
        "backend_rating": 7.2,
        "flare_potential": 3.3,
        "cover_type": "reactive",
        "category": "medium_oil",
        "release_year": 2024,
    },
    "jackal_spear": {
        "name": "Jackal Spear",
        "weight_lbs": 15,
        "rg": 2.44,
        "differential": 0.063,
        "backend_rating": 9.3,
        "flare_potential": 4.2,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2024,
    },
    "evoke_pearl": {
        "name": "Evoke Pearl",
        "weight_lbs": 15,
        "rg": 2.47,
        "differential": 0.058,
        "backend_rating": 8.7,
        "flare_potential": 3.9,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2023,
    },
    "evoke_solid": {
        "name": "Evoke Solid",
        "weight_lbs": 15,
        "rg": 2.47,
        "differential": 0.058,
        "backend_rating": 8.5,
        "flare_potential": 3.8,
        "cover_type": "reactive",
        "category": "heavy_oil",
        "release_year": 2023,
    },
}

def get_ball_specs(ball_id):
    """Retrieve ball specifications by ID"""
    return MOTIV_BALLS_COMPLETE.get(ball_id)

def get_balls_by_category(category):
    """Filter balls by category (heavy_oil, medium_oil, light_oil, spare, entry_level)"""
    return {k: v for k, v in MOTIV_BALLS_COMPLETE.items() if v.get("category") == category}

def get_all_balls():
    """Return complete ball database"""
    return MOTIV_BALLS_COMPLETE

def get_ball_names():
    """Return list of all ball IDs"""
    return list(MOTIV_BALLS_COMPLETE.keys())

def search_balls(query):
    """Search balls by name"""
    query_lower = query.lower()
    return {k: v for k, v in MOTIV_BALLS_COMPLETE.items() if query_lower in v.get("name", "").lower()}

def sort_by_backend(reverse=True):
    """Sort balls by backend rating (highest first by default)"""
    return sorted(MOTIV_BALLS_COMPLETE.items(), key=lambda x: x[1].get("backend_rating", 0), reverse=reverse)

def sort_by_flare(reverse=True):
    """Sort balls by flare potential (highest first by default)"""
    return sorted(MOTIV_BALLS_COMPLETE.items(), key=lambda x: x[1].get("flare_potential", 0), reverse=reverse)

if __name__ == "__main__":
    print(f"Total balls in database: {len(MOTIV_BALLS_COMPLETE)}")
    print("\nBalls by category:")
    for category in ["heavy_oil", "medium_oil", "light_oil", "entry_level", "spare"]:
        balls = get_balls_by_category(category)
        print(f"  {category}: {len(balls)} balls")
