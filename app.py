"""
Bowling Visualizer MVP - Flask Backend
Exposes simulation API for interactive MVP UI
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import traceback
from datetime import datetime

# Import all agents
from agent_02_oil_pattern import create_oil_pattern, validate_oil_pattern
from agent_03_initial_conditions import create_initial_conditions, validate_initial_conditions
from agent_04_contact_patch import create_contact_patch, validate_contact_patch
from agent_05_friction_torque import create_friction_state, validate_friction_state
from agent_06_rotational_dynamics import create_rotational_state, validate_rotational_state
from agent_07_translational_dynamics import create_translational_state, validate_translational_state
from agent_08_trajectory_integrator import create_trajectory_point, validate_trajectory_point
from agent_09_physics_integrator import run_physics_simulation, validate_simulation

from agent_10_flare import calculate_flare, validate_flare
from agent_11_saturation import calculate_saturation, validate_saturation
from agent_12_gyroscopic_precession import calculate_gyroscopic_precession, validate_gyroscopic

# Import ball database
from balls_database import get_all_balls, get_ball_specs, get_balls_by_category, sort_by_backend, sort_by_flare

app = Flask(__name__)
CORS(app)

def convert_to_native(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native(item) for item in obj]
    return obj

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/balls', methods=['GET'])
def get_balls():
    """
    Get all available balls in arsenal
    Optional query params:
    - category: 'heavy_oil', 'medium_oil', 'light_oil', 'entry_level', 'spare'
    - sort_by: 'backend', 'flare', 'name'
    """
    try:
        category = request.args.get('category', None)
        sort_by = request.args.get('sort_by', 'name')

        if category:
            balls = get_balls_by_category(category)
        else:
            balls = get_all_balls()

        # Sort
        if sort_by == 'backend':
            balls = dict(sort_by_backend(reverse=True))
        elif sort_by == 'flare':
            balls = dict(sort_by_flare(reverse=True))
        else:  # sort by name (default)
            balls = dict(sorted(balls.items(), key=lambda x: x[1].get('name', '')))

        # Convert to list with IDs
        result = []
        for ball_id, specs in balls.items():
            ball_data = specs.copy()
            ball_data['id'] = ball_id
            result.append(ball_data)

        return jsonify({
            "success": True,
            "count": len(result),
            "balls": result,
            "categories": ["heavy_oil", "medium_oil", "light_oil", "entry_level", "spare"],
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error in /api/balls: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/balls/<ball_id>', methods=['GET'])
def get_ball(ball_id):
    """Get specific ball specs by ID"""
    try:
        specs = get_ball_specs(ball_id)
        if not specs:
            return jsonify({"success": False, "error": f"Ball {ball_id} not found"}), 404

        ball_data = specs.copy()
        ball_data['id'] = ball_id

        return jsonify({"success": True, "ball": ball_data, "timestamp": datetime.now().isoformat()})

    except Exception as e:
        print(f"Error in /api/balls/{ball_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/patterns', methods=['GET'])
def get_patterns():
    """Get available oil patterns"""
    patterns = {
        "house_shot": {
            "name": "House Shot",
            "oil_length_ft": 40,
            "description": "Typical league pattern, center-loaded",
            "difficulty": "beginner"
        },
        "pba_50": {
            "name": "PBA 50",
            "oil_length_ft": 50,
            "description": "Heavy oil PBA pattern",
            "difficulty": "advanced"
        },
        "pba_42": {
            "name": "PBA 42",
            "oil_length_ft": 42,
            "description": "Medium oil PBA pattern",
            "difficulty": "intermediate"
        },
        "pba_40": {
            "name": "PBA 40",
            "oil_length_ft": 40,
            "description": "Medium-light PBA pattern",
            "difficulty": "intermediate"
        },
        "pba_37": {
            "name": "PBA 37",
            "oil_length_ft": 37,
            "description": "Light oil PBA pattern",
            "difficulty": "intermediate"
        },
        "pba_scorpion": {
            "name": "PBA Scorpion",
            "oil_length_ft": 41,
            "description": "Sport shot - challenging",
            "difficulty": "advanced"
        },
        "pba_shark": {
            "name": "PBA Shark",
            "oil_length_ft": 32,
            "description": "Very challenging - heavy backend",
            "difficulty": "professional"
        },
    }

    return jsonify({
        "success": True,
        "count": len(patterns),
        "patterns": patterns,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    Run complete bowling simulation

    Request body:
    {
        "ball_id": "jackal_ghost",     # Required: ball from database
        "ball_speed_mph": 18.0,
        "ball_rpm": 300,
        "oil_pattern": "house_shot",   # or "pba_40", "pba_sport", etc.
        "oil_condition": "fresh",      # or "transition", "broken"
        "axis_angle_deg": 45.0
    }

    Response:
    {
        "success": bool,
        "entry_angle_deg": float,
        "breakpoint_board": float,
        "hook_amount_boards": float,
        "final_speed_mph": float,
        "final_rpm": float,
        "saturation_pct": float,
        "flare_distance_inches": float,
        "trajectory": [...],
        "ball": { ball_specs... }
    }
    """

    try:
        data = request.get_json()

        # Extract ball ID (required for data integration)
        ball_id = data.get('ball_id', 'jackal_ghost')
        ball_specs = get_ball_specs(ball_id)

        if not ball_specs:
            return jsonify({
                "success": False,
                "error": f"Ball '{ball_id}' not found in database",
                "timestamp": datetime.now().isoformat()
            }), 404

        # Extract parameters with defaults
        ball_speed_mph = data.get('ball_speed_mph', 18.0)
        ball_rpm = data.get('ball_rpm', 300)
        oil_pattern = data.get('oil_pattern', 'house_shot')
        oil_condition = data.get('oil_condition', 'fresh')
        axis_angle_deg = data.get('axis_angle_deg', 45.0)

        # Validate inputs
        ball_speed_mph = max(14.0, min(24.0, float(ball_speed_mph)))
        ball_rpm = max(50, min(400, int(ball_rpm)))

        # Run Agent #9: Physics Integration (full simulation)
        sim = run_physics_simulation(
            ball_speed_mph=ball_speed_mph,
            ball_rpm=ball_rpm,
            axis_angle_deg=axis_angle_deg,
            oil_pattern_name=oil_pattern,
            oil_condition=oil_condition
        )

        # Run Agent #10: Flare
        flare = calculate_flare(
            rpm_initial=sim.initial_rpm,
            rpm_final=sim.final_rpm,
            distance_ft=sim.final_distance_ft,
            grit_condition="factory",
            oil_condition=oil_condition
        )

        # Run Agent #11: Saturation
        saturation = calculate_saturation(
            trajectory=sim.trajectory if hasattr(sim, 'trajectory') else [],
            oil_condition=oil_condition,
            grit_condition="factory",
            initial_saturation_pct=0.0
        )

        # Run Agent #12: Gyroscopic Precession
        gyroscopic = calculate_gyroscopic_precession(
            trajectory=sim.trajectory if hasattr(sim, 'trajectory') else [],
            rpm_initial=sim.initial_rpm,
            rpm_final=sim.final_rpm,
            axis_angle_initial_deg=axis_angle_deg,
            oil_condition=oil_condition
        )

        # Use gyroscopic entry angle if available, otherwise physics integrator's
        entry_angle = gyroscopic.entry_angle_deg if gyroscopic.entry_angle_deg != 0 else sim.entry_angle_deg
        breakpoint = gyroscopic.breakpoint_board if hasattr(gyroscopic, 'breakpoint_board') else sim.breakpoint_board
        hook_amount = gyroscopic.hook_amount_boards if hasattr(gyroscopic, 'hook_amount_boards') else abs(breakpoint - 20.0)

        # Calculate strike probability (80% at 6°, drops off as angle deviates)
        strike_chance = max(0, 90 - abs(entry_angle - 6.0) * 5)

        # Determine impact board (entry point at pin deck)
        impact_board = breakpoint

        # Build trajectory for visualization (simplify to key points)
        trajectory_vis = []
        if hasattr(sim, 'trajectory') and sim.trajectory:
            # Sample every 10 points for smooth curve
            for i, point in enumerate(sim.trajectory):
                if i % 10 == 0 or i == len(sim.trajectory) - 1:
                    trajectory_vis.append({
                        'distance_ft': point.get('distance_ft', 0.0),
                        'board': point.get('board', 20.0)
                    })

        # Build ball info for response
        ball_info = ball_specs.copy()
        ball_info['id'] = ball_id

        response = {
            "success": True,
            "input": {
                "ball_id": ball_id,
                "ball_speed_mph": ball_speed_mph,
                "ball_rpm": ball_rpm,
                "oil_pattern": oil_pattern,
                "oil_condition": oil_condition,
                "axis_angle_deg": axis_angle_deg
            },
            "ball": ball_info,
            "output": {
                # ===== AGENT #9: Physics Integrator =====
                "agent_9": {
                    "initial_speed_mph": convert_to_native(sim.initial_speed_mph),
                    "initial_rpm": convert_to_native(sim.initial_rpm),
                    "final_speed_mph": convert_to_native(sim.final_speed_mph),
                    "final_rpm": convert_to_native(sim.final_rpm),
                    "final_distance_ft": convert_to_native(sim.final_distance_ft),
                    "max_board_reached": convert_to_native(sim.max_board_reached),
                    "energy_lost_pct": convert_to_native(sim.energy_lost_pct),
                    "breakpoint_board": convert_to_native(sim.breakpoint_board),
                    "entry_angle_deg": convert_to_native(sim.entry_angle_deg),
                    "success": convert_to_native(sim.success),
                },

                # ===== AGENT #10: Flare =====
                "agent_10": {
                    "flare_distance_inches": convert_to_native(flare.flare_distance_inches),
                    "track_width_inches": convert_to_native(flare.track_width_inches),
                    "revolutions_total": convert_to_native(flare.revolutions_total),
                    "grit_condition": flare.grit_condition,
                    "saturation_pct": convert_to_native(flare.saturation_pct),
                },

                # ===== AGENT #11: Saturation =====
                "agent_11": {
                    "saturation_pct_initial": convert_to_native(saturation.saturation_pct_initial),
                    "saturation_pct_final": convert_to_native(saturation.saturation_pct_final),
                    "oil_absorbed_cc": convert_to_native(saturation.oil_absorbed_cc),
                    "absorption_rate_pct_per_ft": convert_to_native(saturation.absorption_rate_pct_per_ft),
                    "friction_coefficient_initial": convert_to_native(saturation.friction_coefficient_initial),
                    "friction_coefficient_final": convert_to_native(saturation.friction_coefficient_final),
                    "saturation_trajectory": [convert_to_native(x) for x in saturation.saturation_trajectory],
                },

                # ===== AGENT #12: Gyroscopic Precession =====
                "agent_12": {
                    "entry_angle_deg": convert_to_native(gyroscopic.entry_angle_deg),
                    "spin_axis_angle_deg": convert_to_native(gyroscopic.spin_axis_angle_deg),
                    "lateral_velocity_ft_s": convert_to_native(gyroscopic.lateral_velocity_ft_s),
                    "breakpoint_board": convert_to_native(gyroscopic.breakpoint_board),
                    "breakpoint_distance_ft": convert_to_native(gyroscopic.breakpoint_distance_ft),
                    "precession_rate_deg_per_ft": convert_to_native(gyroscopic.precession_rate_deg_per_ft),
                    "hook_amount_boards": convert_to_native(gyroscopic.hook_amount_boards),
                },

                # ===== AGGREGATED RESULTS FOR UI =====
                "summary": {
                    "entry_angle_deg": convert_to_native(entry_angle),
                    "breakpoint_board": convert_to_native(breakpoint),
                    "hook_amount_boards": convert_to_native(hook_amount),
                    "impact_board": convert_to_native(impact_board),
                    "strike_chance_pct": convert_to_native(strike_chance),
                    "final_speed_mph": convert_to_native(sim.final_speed_mph),
                    "final_rpm": convert_to_native(sim.final_rpm),
                    "distance_ft": convert_to_native(sim.final_distance_ft),
                },

                # ===== Trajectory for visualization =====
                "trajectory": [convert_to_native(t) for t in trajectory_vis]
            },
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(convert_to_native(response))

    except Exception as e:
        print(f"Error in /api/simulate: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/defaults', methods=['GET'])
def get_defaults():
    """Get default simulation parameters"""
    return jsonify({
        "ball_speed_mph": 18.0,
        "ball_rpm": 300,
        "oil_pattern": "house_shot",
        "oil_condition": "fresh",
        "axis_angle_deg": 45.0
    })

if __name__ == '__main__':
    print("Starting Bowling Visualizer MVP Backend...")
    print("API endpoints:")
    print("  GET  /api/health       - Health check")
    print("  GET  /api/defaults     - Get default parameters")
    print("  POST /api/simulate     - Run simulation")
    print("\nServer running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
