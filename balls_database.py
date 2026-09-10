"""
Motiv Bowling Ball Database - real current catalog

24 balls, matching Motiv's actual lineup at motivbowling.com/products/balls/
as of September 2026. Replaces an earlier 38-ball version that was mostly
fabricated placeholder data (invented names like "Marvel Pearl" that were
never real Motiv products) - see git history / BACKLOG.md.

Sourced from motivbowling.com's own product pages, cross-checked against
BowlerX/BowlersMart/BuddiesProShop where useful. Each ball carries its
source_url. A few notes on the data shape:

- `category` uses Motiv's own oil-range wording (Heavy Oil, Medium-Heavy Oil,
  Medium Oil, Light-Medium Oil, Light Oil, Entry Level, Spare) rather than an
  invented taxonomy.
- `weight_range_lbs` is the range Motiv actually drills that model in - not
  every ball goes down to 8lb or up to 16lb.
- `specs_by_weight` holds RG/differential per drilled weight where Motiv
  publishes it. Coverage is partial for a few balls (noted inline) - treat a
  missing weight as "not published," not zero.
- `motiv_length` / `motiv_backend` / `motiv_hook` are Motiv's own published
  ball-motion indices. These run roughly 0-100, NOT a 1-10 "backend rating" -
  the old database's `backend_rating` field was a fabricated 0-10 number and
  has been removed. `hook_potential_200` below is `motiv_hook * 2`, a
  deliberate rescale to fit a 0-200 display range - it is derived from a real
  published number, not an independent estimate.
- `flare_potential_in` / `flare_potential_plus`: Motiv publishes flare as a
  minimum threshold (e.g. "7"+"), so `flare_potential_plus=True` means "this
  many inches or more," not an exact figure.
"""

MOTIV_BALLS_COMPLETE = {
    "jackal_onyx": {
        "name": "Jackal Onyx",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.047}, 15: {"rg": 2.47, "diff": 0.054},
            14: {"rg": 2.51, "diff": 0.049}, 13: {"rg": 2.57, "diff": 0.040},
            12: {"rg": 2.64, "diff": 0.030},
        },
        "rg": 2.47, "differential": 0.054,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Leverage HXC Solid Reactive, 1000 Grit LSS",
        "core_name": "Predator V2 (asymmetric)",
        "category": "Heavy Oil", "release_year": 2025,
        "motiv_length": 53, "motiv_backend": 70, "motiv_hook": 87,
        "flare_potential_in": 7, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/heavy-oil/jackal-onyx.html",
    },
    "raptor_reign": {
        "name": "Raptor Reign",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.053}, 15: {"rg": 2.48, "diff": 0.055},
            14: {"rg": 2.50, "diff": 0.053}, 13: {"rg": 2.57, "diff": 0.040},
            12: {"rg": 2.64, "diff": 0.029},
        },
        "rg": 2.48, "differential": 0.055,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Leverage MXV Solid Reactive, 2000 Grit LSS",
        "core_name": "Affliction V2 (symmetric)",
        "category": "Heavy Oil", "release_year": 2025,
        "motiv_length": 60, "motiv_backend": 74, "motiv_hook": 83,
        "flare_potential_in": 5, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/heavy-oil/raptor-reign.html",
    },
    "jackal_ghost_v2": {
        "name": "Jackal Ghost V2",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.047}, 15: {"rg": 2.47, "diff": 0.054},
            14: {"rg": 2.51, "diff": 0.049}, 13: {"rg": 2.57, "diff": 0.040},
            12: {"rg": 2.64, "diff": 0.030},
        },
        "rg": 2.47, "differential": 0.054,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Leverage HFS Reactive, 3000 Grit LSS",
        "core_name": "Predator V2 (asymmetric)",
        "category": "Heavy Oil", "release_year": 2026,
        "motiv_length": 65, "motiv_backend": 76, "motiv_hook": 80,
        "flare_potential_in": 7, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/heavy-oil/jackal-ghost-v2.html",
    },
    "apex_jackal": {
        "name": "Apex Jackal",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        # only 15lb diff was published; other weights are RG-only (Motiv didn't list their diff)
        "specs_by_weight": {
            16: {"rg": 2.53, "diff": None}, 15: {"rg": 2.52, "diff": 0.055},
            14: {"rg": 2.55, "diff": None}, 13: {"rg": 2.64, "diff": None},
            12: {"rg": 2.64, "diff": None},
        },
        "rg": 2.52, "differential": 0.055,
        "intermediate_diff_range": [0.014, 0.020],
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Propulsion MXV Pearl Reactive, 5000 Grit LSS",
        "core_name": "Apex Predator (asymmetric, dual-density)",
        "category": "Heavy Oil", "release_year": 2026,
        "motiv_length": 73, "motiv_backend": 87, "motiv_hook": 78,
        "flare_potential_in": 7, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/heavy-oil/apex-jackal.html",
        "note": "listed out of stock as of research",
    },
    "forge_fuel": {
        "name": "Forge Fuel",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.47, "diff": 0.054}, 15: {"rg": 2.47, "diff": 0.055},
            14: {"rg": 2.49, "diff": 0.054}, 13: {"rg": 2.55, "diff": 0.045},
            12: {"rg": 2.62, "diff": 0.032},
        },
        "rg": 2.47, "differential": 0.055,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Leverage MXT Solid Reactive, 1000 Grit LSS (Duramax)",
        "core_name": "Detonator (symmetric)",
        "category": "Medium-Heavy Oil", "release_year": 2026,
        "motiv_length": 55, "motiv_backend": 73, "motiv_hook": 78,
        "flare_potential_in": 5, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/medium-heavy-oil/forge-fuel.html",
    },
    "evoke_mayhem": {
        "name": "Evoke Mayhem",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.045}, 15: {"rg": 2.48, "diff": 0.050},
            14: {"rg": 2.51, "diff": 0.045}, 13: {"rg": 2.57, "diff": 0.035},
            12: {"rg": 2.64, "diff": 0.025},
        },
        "rg": 2.48, "differential": 0.050,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Propulsion MXV Solid Reactive, 2000 Grit LSS",
        "core_name": "Overload (asymmetric)",
        "category": "Medium-Heavy Oil", "release_year": 2026,
        "motiv_length": 65, "motiv_backend": 78, "motiv_hook": 77,
        "flare_potential_in": 7, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/medium-heavy-oil/evoke-mayhem.html",
    },
    "evoke_hysteria": {
        "name": "Evoke Hysteria",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.045}, 15: {"rg": 2.48, "diff": 0.050},
            14: {"rg": 2.51, "diff": 0.045}, 13: {"rg": 2.57, "diff": 0.035},
            12: {"rg": 2.64, "diff": 0.025},
        },
        "rg": 2.48, "differential": 0.050,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Propulsion MXV Pearl Reactive, 4000 Grit LSS",
        "core_name": "Overload (asymmetric, tunable differential)",
        "category": "Medium-Heavy Oil", "release_year": 2025,
        "motiv_length": 70, "motiv_backend": 84, "motiv_hook": 72,
        "flare_potential_in": 7, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/medium-heavy-oil/evoke-hysteria.html",
    },
    "steel_forge": {
        "name": "Steel Forge",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.47, "diff": 0.054}, 15: {"rg": 2.47, "diff": 0.055},
            14: {"rg": 2.49, "diff": 0.054}, 13: {"rg": 2.55, "diff": 0.045},
            12: {"rg": 2.62, "diff": 0.032},
        },
        "rg": 2.47, "differential": 0.055,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Propulsion MXV Pearl Reactive, 5000 Grit LSS",
        "core_name": "Detonator (symmetric)",
        "category": "Medium-Heavy Oil", "release_year": 2025,
        "motiv_length": 74, "motiv_backend": 88, "motiv_hook": 76,
        "flare_potential_in": 5, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/medium-heavy-oil/steel-forge.html",
    },
    "primal_ghost": {
        "name": "Primal Ghost",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.54, "diff": 0.049}, 15: {"rg": 2.55, "diff": 0.050},
            14: {"rg": 2.56, "diff": 0.054}, 13: {"rg": 2.60, "diff": 0.055},
            12: {"rg": 2.67, "diff": 0.040},
        },
        "rg": 2.55, "differential": 0.050,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Coercion HFS Reactive (Solid), 3000 Grit LSS",
        "core_name": "Impulse V2 (symmetric)",
        "category": "Medium Oil", "release_year": 2025,
        "motiv_length": 63, "motiv_backend": 70, "motiv_hook": 67,
        "flare_potential_in": 5, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/medium-oil/primal-ghost.html",
    },
    "sigma_tour_pearl": {
        "name": "Sigma Tour Pearl",
        # Motiv's own spec table is centered on 16lb for this one, not 15lb
        "weight_lbs": 16,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.46, "diff": 0.044},
            # 15/14lb rows are from secondary retailer listings, not directly
            # fetched from Motiv's full weight table - lower confidence
            15: {"rg": 2.47, "diff": 0.047}, 14: {"rg": 2.51, "diff": 0.040},
        },
        "rg": 2.46, "differential": 0.044,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Atomic Propulsion Pearl Reactive, 5000 Grit LSS",
        "core_name": "Sigma (symmetric)",
        "category": "Medium Oil", "release_year": 2026,
        "motiv_length": 67, "motiv_backend": 78, "motiv_hook": 65,
        "flare_potential_in": 4, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/medium-oil/sigma-tour-pearl.html",
    },
    "nebula": {
        "name": "Nebula",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.50, "diff": 0.038}, 15: {"rg": 2.50, "diff": 0.045},
            14: {"rg": 2.51, "diff": 0.049}, 13: {"rg": 2.65, "diff": 0.020},
            12: {"rg": 2.65, "diff": 0.020},
        },
        "rg": 2.50, "differential": 0.045,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Dark Matter Propulsion Pearl Reactive, 5500 Grit LSP",
        "core_name": "Hadron (symmetric, dual-density)",
        "category": "Medium Oil", "release_year": 2025,
        "motiv_length": 74, "motiv_backend": 90, "motiv_hook": 62,
        "flare_potential_in": 5, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/medium-oil/nebula.html",
    },
    "shadow_tank": {
        "name": "Shadow Tank",
        "weight_lbs": 15,
        "weight_range_lbs": [14, 16],
        "specs_by_weight": {
            16: {"rg": None, "diff": 0.013}, 15: {"rg": 2.57, "diff": 0.015},
            14: {"rg": None, "diff": 0.018},
        },
        "rg": 2.57, "differential": 0.015,
        # Motiv markets this as proprietary "MCP" (Microcell Polymer), which
        # doesn't cleanly fit reactive/urethane/particle/plastic - "particle"
        # is the closest approximation, not a confirmed classification
        "cover_type": "particle", "finish": "Pearl Reactive",
        "coverstock_name": "Frixion M7 Pearl MCP, 78D+ hardness, 1000 Grit LSS",
        "core_name": "Flux (symmetric)",
        "category": "Light Oil", "release_year": 2025,
        "motiv_length": 37, "motiv_backend": 35, "motiv_hook": 36,
        "flare_potential_in": 2, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-oil/shadow-tank.html",
    },
    "hyper_venom": {
        "name": "Hyper Venom",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.031}, 15: {"rg": 2.48, "diff": 0.034},
            14: {"rg": 2.52, "diff": 0.029}, 13: {"rg": 2.58, "diff": 0.023},
            12: {"rg": 2.65, "diff": 0.016},
        },
        "rg": 2.48, "differential": 0.034,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Propulsion MXR Pearl Reactive, 5500 Grit LSP",
        "core_name": "Gear (symmetric)",
        "category": "Light-Medium Oil", "release_year": 2024,
        "motiv_length": 76, "motiv_backend": 81, "motiv_hook": 48,
        "flare_potential_in": 3, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-medium-oil/hyper-venom.html",
    },
    "black_venom": {
        "name": "Black Venom",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.032}, 15: {"rg": 2.47, "diff": 0.036},
            14: {"rg": 2.50, "diff": 0.033}, 13: {"rg": 2.56, "diff": 0.028},
            12: {"rg": 2.63, "diff": 0.020},
        },
        "rg": 2.47, "differential": 0.036,
        "intermediate_diff": 0.013,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Leverage MFS Solid Reactive, 4000 Grit LSS",
        "core_name": "Gear APG (asymmetric)",
        "category": "Light-Medium Oil", "release_year": 2023,
        "motiv_length": 56, "motiv_backend": 70, "motiv_hook": 58,
        "flare_potential_in": 3, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-medium-oil/black-venom.html",
    },
    "venom_shock": {
        "name": "Venom Shock",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.031}, 15: {"rg": 2.48, "diff": 0.034},
            14: {"rg": 2.52, "diff": 0.029}, 13: {"rg": 2.58, "diff": 0.023},
            12: {"rg": 2.65, "diff": 0.016},
        },
        "rg": 2.48, "differential": 0.034,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Turmoil MFS Solid Reactive, 4000 Grit LSS",
        "core_name": "Gear (symmetric)",
        "category": "Light-Medium Oil", "release_year": 2014,
        "motiv_length": 60, "motiv_backend": 75, "motiv_hook": 55,
        "flare_potential_in": 3, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-medium-oil/venom-shock.html",
        "note": "long-running benchmark ball, in the catalog 12+ years",
    },
    "lethal_venom": {
        "name": "Lethal Venom",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {15: {"rg": 2.47, "diff": 0.036}},
        "rg": 2.47, "differential": 0.036,
        "intermediate_diff": 0.013,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Leverage MXC Solid Reactive (Duramax), 3000 Grit LSS",
        "core_name": "Gear APG (asymmetric)",
        "category": "Light-Medium Oil", "release_year": 2025,
        "motiv_length": 51, "motiv_backend": 62, "motiv_hook": 60,
        "flare_potential_in": 3, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-medium-oil/lethal-venom.html",
    },
    "supra_sport": {
        "name": "Supra Sport",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.54, "diff": 0.040}, 15: {"rg": 2.55, "diff": 0.043},
            14: {"rg": 2.56, "diff": 0.043}, 13: {"rg": 2.58, "diff": 0.047},
            12: {"rg": 2.58, "diff": 0.050},
        },
        "rg": 2.55, "differential": 0.043,
        "cover_type": "reactive", "finish": "Solid Reactive",
        "coverstock_name": "Leverage MFS Solid Reactive, 4000 Grit LSS",
        "core_name": "Quadfire (symmetric)",
        "category": "Light-Medium Oil", "release_year": 2026,
        "motiv_length": 54, "motiv_backend": 68, "motiv_hook": 60,
        "flare_potential_in": 4, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-medium-oil/supra-sport.html",
        "note": "first solid-covered Supra release",
    },
    "venom_hysteria": {
        "name": "Venom Hysteria",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.48, "diff": 0.031}, 15: {"rg": 2.48, "diff": 0.034},
            14: {"rg": 2.52, "diff": 0.029}, 13: {"rg": 2.58, "diff": 0.023},
            12: {"rg": 2.65, "diff": 0.016},
        },
        "rg": 2.48, "differential": 0.034,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Propulsion MXV Pearl Reactive, 5000 Grit LSS",
        "core_name": "Gear (symmetric)",
        "category": "Light-Medium Oil", "release_year": 2026,
        "motiv_length": 74, "motiv_backend": 77, "motiv_hook": 53,
        "flare_potential_in": 3, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-medium-oil/venom-hysteria.html",
        "note": "marketed as a step down from Evoke Hysteria",
    },
    "supra_clutch": {
        "name": "Supra Clutch",
        "weight_lbs": 15,
        "weight_range_lbs": [12, 16],
        "specs_by_weight": {
            16: {"rg": 2.54, "diff": 0.040}, 15: {"rg": 2.55, "diff": 0.043},
            14: {"rg": 2.56, "diff": 0.043}, 13: {"rg": 2.58, "diff": 0.047},
            12: {"rg": 2.58, "diff": 0.050},
        },
        "rg": 2.55, "differential": 0.043,
        "cover_type": "reactive", "finish": "Hybrid Reactive",
        "coverstock_name": "Propulsion XRT Hybrid Reactive, 5500 Grit LSP",
        "core_name": "Quadfire (symmetric)",
        "category": "Light-Medium Oil", "release_year": 2025,
        "motiv_length": 80, "motiv_backend": 90, "motiv_hook": 54,
        "flare_potential_in": 4, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-medium-oil/supra-clutch.html",
    },
    "max_thrill_hybrid": {
        "name": "Max Thrill Hybrid",
        "weight_lbs": 15,
        "weight_range_lbs": [10, 16],
        "specs_by_weight": {15: {"rg": 2.55, "diff": 0.037}},
        "rg": 2.55, "differential": 0.037,
        "cover_type": "reactive", "finish": "Hybrid Reactive",
        "coverstock_name": "Turmoil XP3 Hybrid Reactive, 5500 Grit LSP",
        "core_name": "Halogen (symmetric)",
        "category": "Light Oil", "release_year": 2025,
        "motiv_length": 70, "motiv_backend": 76, "motiv_hook": 45,
        "flare_potential_in": 4, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-oil/max-thrill-hybrid.html",
    },
    "max_thrill_pearl": {
        "name": "Max Thrill Pearl",
        "weight_lbs": 16,
        "weight_range_lbs": [10, 16],
        "specs_by_weight": {16: {"rg": 2.54, "diff": 0.036}},
        "rg": 2.54, "differential": 0.036,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Turmoil XP3 Pearl Reactive, 5500 Grit LSP",
        "core_name": "Halogen (symmetric)",
        "category": "Light Oil", "release_year": 2024,
        "motiv_length": 80, "motiv_backend": 82, "motiv_hook": 44,
        "flare_potential_in": 4, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/light-oil/max-thrill-pearl.html",
        "note": "returned after a 6-year hiatus; 15lb RG not directly confirmed, official table centers on 16lb",
    },
    "frenzy": {
        "name": "Frenzy",
        "weight_lbs": 15,
        "weight_range_lbs": [10, 15],
        "specs_by_weight": {
            15: {"rg": 2.55, "diff": 0.030}, 14: {"rg": 2.57, "diff": 0.030},
            13: {"rg": 2.60, "diff": 0.031}, 12: {"rg": 2.64, "diff": 0.026},
            11: {"rg": 2.71, "diff": 0.018}, 10: {"rg": 2.78, "diff": 0.011},
        },
        "rg": 2.55, "differential": 0.030,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Vitality Pearl Reactive, 5500 Grit LSP",
        "core_name": "Excel (symmetric)",
        # Motiv's own category tag, despite this being positioned/marketed as
        # an entry-level upgrade ball
        "category": "Light-Medium Oil", "release_year": 2026,
        "motiv_length": 74, "motiv_backend": 72, "motiv_hook": 40,
        "flare_potential_in": 2, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/entry-level/frenzy-red-black.html",
    },
    "ascend": {
        "name": "Ascend",
        "weight_lbs": 15,
        "weight_range_lbs": [10, 15],
        "specs_by_weight": {
            15: {"rg": 2.59, "diff": 0.023}, 14: {"rg": 2.60, "diff": 0.024},
            13: {"rg": 2.65, "diff": 0.017}, 12: {"rg": 2.72, "diff": 0.015},
            11: {"rg": 2.76, "diff": 0.015}, 10: {"rg": 2.83, "diff": 0.015},
        },
        "rg": 2.59, "differential": 0.023,
        "cover_type": "reactive", "finish": "Pearl Reactive",
        "coverstock_name": "Vitality Pearl Reactive, 5500 Grit LSP",
        "core_name": "Flux V2 (symmetric)",
        # No explicit oil-range tag on Motiv's site for this one - using
        # their catalog section instead of guessing an oil range
        "category": "Entry Level", "release_year": 2025,
        "motiv_length": 80, "motiv_backend": 70, "motiv_hook": 35,
        "flare_potential_in": 2, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/entry-level/ascend-green-teal-black.html",
    },
    "aspire": {
        "name": "Aspire",
        "weight_lbs": 15,
        "weight_range_lbs": [8, 15],
        "specs_by_weight": {
            15: {"rg": 2.75, "diff": 0.028}, 14: {"rg": 2.75, "diff": 0.024},
            13: {"rg": 2.78, "diff": 0.030}, 12: {"rg": 2.81, "diff": 0.025},
            11: {"rg": 2.84, "diff": 0.026}, 10: {"rg": 2.87, "diff": 0.026},
            9: {"rg": 2.85, "diff": 0.013}, 8: {"rg": 2.89, "diff": 0.013},
        },
        "rg": 2.75, "differential": 0.028,
        "cover_type": "plastic", "finish": "Plastic",
        "coverstock_name": "Polyester, 6000 Grit LSP",
        "core_name": "Tyro weight block",
        "category": "Spare", "release_year": 2025,
        "motiv_length": 100, "motiv_backend": 0, "motiv_hook": 0,
        "flare_potential_in": 1, "flare_potential_plus": True,
        "source_url": "https://www.motivbowling.com/products/balls/spare/aspire-navy-red-blue.html",
        "note": "designed not to hook - spare ball",
    },
}

CATEGORIES = ["Heavy Oil", "Medium-Heavy Oil", "Medium Oil", "Light-Medium Oil",
              "Light Oil", "Entry Level", "Spare"]


def get_ball_specs(ball_id):
    """Retrieve ball specifications by ID"""
    return MOTIV_BALLS_COMPLETE.get(ball_id)


def get_balls_by_category(category):
    """Filter balls by category (see CATEGORIES for the valid values)"""
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


def specs_at_weight(ball_id, weight_lbs):
    """RG/diff for a ball at a specific drilled weight, falling back to the
    nearest weight with published data if the exact one isn't available."""
    ball = MOTIV_BALLS_COMPLETE.get(ball_id)
    if not ball:
        return None
    table = ball.get("specs_by_weight", {})
    if weight_lbs in table:
        return {"weight_lbs": weight_lbs, **table[weight_lbs], "exact": True}
    if not table:
        return {"weight_lbs": ball["weight_lbs"], "rg": ball["rg"], "diff": ball["differential"], "exact": False}
    nearest = min(table.keys(), key=lambda w: abs(w - weight_lbs))
    return {"weight_lbs": nearest, **table[nearest], "exact": False}


def sort_by_backend(reverse=True):
    """Sort balls by Motiv's published Backend index (highest first by default).
    Kept as `sort_by_backend` (not `sort_by_hook`) since app.py imports it by
    this name - the field it reads is now motiv_backend, a real 0-100ish
    published index, not the old fabricated 0-10 backend_rating."""
    return sorted(MOTIV_BALLS_COMPLETE.items(), key=lambda x: x[1].get("motiv_backend", 0), reverse=reverse)


def sort_by_flare(reverse=True):
    """Sort balls by flare potential (highest first by default)"""
    return sorted(MOTIV_BALLS_COMPLETE.items(), key=lambda x: x[1].get("flare_potential_in", 0), reverse=reverse)


if __name__ == "__main__":
    print(f"Total balls in database: {len(MOTIV_BALLS_COMPLETE)}")
    print("\nBalls by category:")
    for category in CATEGORIES:
        balls = get_balls_by_category(category)
        print(f"  {category}: {len(balls)} balls")
