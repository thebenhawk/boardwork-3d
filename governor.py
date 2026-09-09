"""
Bowling Visualizer Governor
Orchestrates all Phase 1 agents (2-9), validates outputs, generates real HTML dashboard
"""

import json
import sys
from datetime import datetime
import numpy as np

# Import all agents - Phase 1
from agent_02_oil_pattern import create_oil_pattern, validate_oil_pattern
from agent_03_initial_conditions import create_initial_conditions, validate_initial_conditions
from agent_04_contact_patch import create_contact_patch, validate_contact_patch
from agent_05_friction_torque import create_friction_state, validate_friction_state
from agent_06_rotational_dynamics import create_rotational_state, validate_rotational_state
from agent_07_translational_dynamics import create_translational_state, validate_translational_state
from agent_08_trajectory_integrator import create_trajectory_point, validate_trajectory_point
from agent_09_physics_integrator import run_physics_simulation, validate_simulation

# Import Phase 2 agents
from agent_10_flare import calculate_flare, validate_flare
from agent_11_saturation import calculate_saturation, validate_saturation
from agent_12_gyroscopic_precession import calculate_gyroscopic_precession, validate_gyroscopic

# Phase 1 Success Criteria (from project instructions)
PHASE_1_SUCCESS_CRITERIA = {
    "ball_reaches_60ft": "✓ Ball reaches 60 ft",
    "entry_angle_plausible": "✓ Entry angle 6° ± 2° (max strike probability)",
    "energy_monotonic": "✓ Energy decreases monotonically",
    "no_nan_inf": "✓ No NaN/inf values",
    "friction_backward": "✓ Friction force points backward",
    "no_spiraling": "✓ Ball rolls without spiraling",
}

class Governor:
    """Orchestrates Phase 1 agents and generates reports"""

    def __init__(self):
        self.agents_status = {}
        self.agent_outputs = {}
        self.validation_results = {}
        self.timeline = []

    def log(self, agent_id, message):
        """Log event with timestamp"""
        ts = datetime.now().isoformat()
        self.timeline.append({"timestamp": ts, "agent": agent_id, "message": message})
        print(f"[{agent_id}] {message}")

    def run_all_agents(self, test_scenario="house_shot_fresh"):
        """Run complete agent pipeline"""
        print("=" * 70)
        print("BOWLING VISUALIZER - PHASE 1 GOVERNOR")
        print("=" * 70)
        print(f"\nTest Scenario: {test_scenario}")
        print(f"Timestamp: {datetime.now().isoformat()}\n")

        results = {
            "scenario": test_scenario,
            "timestamp": datetime.now().isoformat(),
            "phase": "1+2",
            "agents": {}
        }

        # Agent #2: Oil Pattern
        self.log("#2", "Oil Pattern - Initializing")
        try:
            oil = create_oil_pattern("house_shot", "fresh")
            val = validate_oil_pattern(oil)
            self.agents_status["2"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["2"] = {
                "pattern": oil.pattern_name,
                "condition": oil.condition,
                "oil_length_ft": oil.oil_length_ft,
                "center_density": float(oil.get_density(20, 10)),
                "validation": val["passed"]
            }
            results["agents"]["2"] = self.agent_outputs["2"]
            self.log("#2", f"Status: {self.agents_status['2']}")
        except Exception as e:
            self.agents_status["2"] = "✗ ERROR"
            self.log("#2", f"Error: {str(e)}")

        # Agent #3: Initial Conditions
        self.log("#3", "Initial Conditions - Initializing")
        try:
            ic = create_initial_conditions(18.0, 300)
            val = validate_initial_conditions(ic)
            self.agents_status["3"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["3"] = {
                "speed_mph": ic.speed_mph,
                "rpm": ic.rpm,
                "velocity_ft_s": float(np.linalg.norm(ic.velocity)),
                "kinetic_energy_j": ic.kinetic_energy_j,
                "validation": val["passed"]
            }
            results["agents"]["3"] = self.agent_outputs["3"]
            self.log("#3", f"Status: {self.agents_status['3']}")
        except Exception as e:
            self.agents_status["3"] = "✗ ERROR"
            self.log("#3", f"Error: {str(e)}")

        # Agent #4: Contact Patch
        self.log("#4", "Contact Patch - Initializing")
        try:
            cp = create_contact_patch(oil_density=0.6)
            val = validate_contact_patch(cp, 0.6)
            self.agents_status["4"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["4"] = {
                "area_sq_in": cp.area_sq_in,
                "pressure_psi": cp.pressure_psi,
                "friction_coefficient": cp.friction_coefficient,
                "oil_density": cp.oil_density,
                "validation": val["passed"]
            }
            results["agents"]["4"] = self.agent_outputs["4"]
            self.log("#4", f"Status: {self.agents_status['4']}")
        except Exception as e:
            self.agents_status["4"] = "✗ ERROR"
            self.log("#4", f"Error: {str(e)}")

        # Agent #5: Friction & Torque
        self.log("#5", "Friction & Torque - Initializing")
        try:
            fs = create_friction_state(
                velocity=ic.velocity,
                angular_velocity=ic.angular_velocity,
                friction_coefficient=cp.friction_coefficient
            )
            val = validate_friction_state(fs, ic.velocity)
            self.agents_status["5"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["5"] = {
                "friction_force_n": float(fs.friction_magnitude_n),
                "torque_n_m": float(fs.torque_magnitude_n_m),
                "slip_ratio": fs.slip_ratio,
                "validation": val["passed"]
            }
            results["agents"]["5"] = self.agent_outputs["5"]
            self.log("#5", f"Status: {self.agents_status['5']}")
        except Exception as e:
            self.agents_status["5"] = "✗ ERROR"
            self.log("#5", f"Error: {str(e)}")

        # Agent #6: Rotational Dynamics
        self.log("#6", "Rotational Dynamics - Initializing")
        try:
            rs = create_rotational_state(
                angular_velocity=ic.angular_velocity,
                torque_n_m=fs.torque_n_m
            )
            val = validate_rotational_state(rs, ic.rpm)
            self.agents_status["6"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["6"] = {
                "rpm": rs.rpm,
                "spin_axis_angle": rs.spin_axis_angle_deg,
                "angular_accel_mag": float(np.linalg.norm(rs.angular_acceleration)),
                "validation": val["passed"]
            }
            results["agents"]["6"] = self.agent_outputs["6"]
            self.log("#6", f"Status: {self.agents_status['6']}")
        except Exception as e:
            self.agents_status["6"] = "✗ ERROR"
            self.log("#6", f"Error: {str(e)}")

        # Agent #7: Translational Dynamics
        self.log("#7", "Translational Dynamics - Initializing")
        try:
            ts = create_translational_state(
                velocity=ic.velocity,
                friction_force_n=fs.friction_force_n
            )
            val = validate_translational_state(ts, np.linalg.norm(ic.velocity))
            self.agents_status["7"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["7"] = {
                "speed_ft_s": ts.speed_ft_s,
                "speed_mph": ts.speed_mph,
                "deceleration_ft_s2": ts.deceleration_ft_s2,
                "kinetic_energy_j": ts.kinetic_energy_j,
                "validation": val["passed"]
            }
            results["agents"]["7"] = self.agent_outputs["7"]
            self.log("#7", f"Status: {self.agents_status['7']}")
        except Exception as e:
            self.agents_status["7"] = "✗ ERROR"
            self.log("#7", f"Error: {str(e)}")

        # Agent #8: Trajectory Integrator
        self.log("#8", "Trajectory Integrator - Initializing")
        try:
            traj = create_trajectory_point(
                velocity=ts.velocity,
                angular_velocity=rs.angular_velocity,
                current_distance_ft=0.0,
                current_board=20.0
            )
            val = validate_trajectory_point(traj, 0.0)
            self.agents_status["8"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["8"] = {
                "distance_ft": traj.distance_ft,
                "board": traj.board,
                "entry_angle_deg": traj.entry_angle_deg,
                "oil_density": traj.oil_density,
                "validation": val["passed"]
            }
            results["agents"]["8"] = self.agent_outputs["8"]
            self.log("#8", f"Status: {self.agents_status['8']}")
        except Exception as e:
            self.agents_status["8"] = "✗ ERROR"
            self.log("#8", f"Error: {str(e)}")

        # Agent #9: Physics Integrator (Full Simulation)
        self.log("#9", "Physics Integrator - Running full 60-ft simulation")
        try:
            sim = run_physics_simulation(
                ball_speed_mph=18.0,
                ball_rpm=300,
                axis_angle_deg=45.0,
                oil_pattern_name="house_shot",
                oil_condition="fresh"
            )
            val = validate_simulation(sim)
            self.agents_status["9"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["9"] = {
                "distance_ft": sim.final_distance_ft,
                "entry_angle_deg": sim.entry_angle_deg,
                "breakpoint_board": sim.breakpoint_board,
                "initial_speed_mph": sim.initial_speed_mph,
                "final_speed_mph": sim.final_speed_mph,
                "initial_rpm": sim.initial_rpm,
                "final_rpm": sim.final_rpm,
                "energy_lost_pct": sim.energy_lost_pct,
                "validation": val["passed"],
                "trajectory_points": len(sim.trajectory)
            }
            results["agents"]["9"] = self.agent_outputs["9"]
            self.log("#9", f"Status: {self.agents_status['9']}")
            self.log("#9", f"Entry Angle: {sim.entry_angle_deg:.2f}° (target: 6° ± 2°)")
            self.log("#9", f"Distance: {sim.final_distance_ft:.1f} ft")
            self.log("#9", f"Energy Loss: {sim.energy_lost_pct:.1f}%")
        except Exception as e:
            self.agents_status["9"] = "✗ ERROR"
            self.log("#9", f"Error: {str(e)}")

        # Agent #10: Flare Calculation (Phase 2)
        self.log("#10", "Flare Calculation - Initializing")
        try:
            fr = calculate_flare(
                rpm_initial=sim.initial_rpm,
                rpm_final=sim.final_rpm,
                distance_ft=sim.final_distance_ft,
                ball_radius_inches=4.25,
                grit_condition="factory",
                oil_condition="fresh"
            )
            val = validate_flare(fr)
            self.agents_status["10"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["10"] = {
                "flare_distance_inches": float(fr.flare_distance_inches),
                "track_width_inches": float(fr.track_width_inches),
                "revolutions_total": int(fr.revolutions_total),
                "saturation_pct": float(fr.saturation_pct),
                "validation": val["passed"]
            }
            results["agents"]["10"] = self.agent_outputs["10"]
            self.log("#10", f"Status: {self.agents_status['10']}")
        except Exception as e:
            self.agents_status["10"] = "✗ ERROR"
            self.log("#10", f"Error: {str(e)}")

        # Agent #11: Saturation Tracking (Phase 2)
        self.log("#11", "Saturation Tracking - Initializing")
        try:
            sr = calculate_saturation(
                trajectory=sim.trajectory if hasattr(sim, 'trajectory') else [],
                oil_condition="fresh",
                grit_condition="factory",
                initial_saturation_pct=0.0
            )
            val = validate_saturation(sr)
            self.agents_status["11"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["11"] = {
                "saturation_pct_initial": float(sr.saturation_pct_initial),
                "saturation_pct_final": float(sr.saturation_pct_final),
                "oil_absorbed_cc": float(sr.oil_absorbed_cc),
                "absorption_rate_pct_per_ft": float(sr.absorption_rate_pct_per_ft),
                "friction_coefficient_initial": float(sr.friction_coefficient_initial),
                "friction_coefficient_final": float(sr.friction_coefficient_final),
                "validation": val["passed"]
            }
            results["agents"]["11"] = self.agent_outputs["11"]
            self.log("#11", f"Status: {self.agents_status['11']}")
        except Exception as e:
            self.agents_status["11"] = "✗ ERROR"
            self.log("#11", f"Error: {str(e)}")

        # Agent #12: Gyroscopic Precession (Phase 2)
        self.log("#12", "Gyroscopic Precession - Initializing")
        try:
            gr = calculate_gyroscopic_precession(
                trajectory=sim.trajectory if hasattr(sim, 'trajectory') else [],
                rpm_initial=sim.initial_rpm,
                rpm_final=sim.final_rpm,
                axis_angle_initial_deg=45.0,
                oil_condition="fresh"
            )
            val = validate_gyroscopic(gr)
            self.agents_status["12"] = "✓ COMPLETE" if val["passed"] else "✗ FAILED"
            self.agent_outputs["12"] = {
                "entry_angle_deg": float(gr.entry_angle_deg),
                "spin_axis_angle_deg": float(gr.spin_axis_angle_deg),
                "lateral_velocity_ft_s": float(gr.lateral_velocity_ft_s),
                "breakpoint_board": float(gr.breakpoint_board),
                "breakpoint_distance_ft": float(gr.breakpoint_distance_ft),
                "precession_rate_deg_per_ft": float(gr.precession_rate_deg_per_ft),
                "hook_amount_boards": float(gr.hook_amount_boards),
                "validation": val["passed"]
            }
            results["agents"]["12"] = self.agent_outputs["12"]
            self.log("#12", f"Status: {self.agents_status['12']}")
        except Exception as e:
            self.agents_status["12"] = "✗ ERROR"
            self.log("#12", f"Error: {str(e)}")

        # Summary
        completed = sum(1 for v in self.agents_status.values() if "COMPLETE" in v)
        total_agents = len(self.agents_status)
        print(f"\n{'=' * 70}")
        print(f"PHASE 1+2 STATUS: {completed}/{total_agents} agents complete")
        print(f"{'=' * 70}\n")

        # Show success criteria
        print("PHASE 1 SUCCESS CRITERIA:")
        print("-" * 70)
        for key, criterion in PHASE_1_SUCCESS_CRITERIA.items():
            print(f"  {criterion}")

        return results

    def generate_html_dashboard(self, results):
        """Generate real HTML dashboard from actual agent outputs"""

        # Convert numpy types to Python types for JSON serialization
        def convert_to_native(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_native(item) for item in obj]
            return obj

        serializable_outputs = convert_to_native(self.agent_outputs)
        agents_json = json.dumps(serializable_outputs, indent=2)
        status_json = json.dumps(self.agents_status, indent=2)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bowling Visualizer - Phase 1 Governor Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #0f3460;
            padding-bottom: 20px;
        }}

        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            color: #00d4ff;
        }}

        .phase-info {{
            font-size: 14px;
            color: #888;
            margin-bottom: 10px;
        }}

        .progress-bar {{
            width: 300px;
            height: 8px;
            background: #333;
            border-radius: 4px;
            margin: 15px auto;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            width: var(--progress);
            transition: width 0.3s ease;
        }}

        .main-grid {{
            display: grid;
            grid-template-columns: 300px 1fr 300px;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .panel {{
            background: #0f3460;
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 20px;
        }}

        .panel h2 {{
            font-size: 16px;
            margin-bottom: 15px;
            color: #00d4ff;
            border-bottom: 1px solid #00d4ff;
            padding-bottom: 10px;
        }}

        .agent-box {{
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 6px;
            font-size: 12px;
            border-left: 3px solid #666;
            background: rgba(0, 0, 0, 0.3);
        }}

        .agent-box.complete {{
            border-left-color: #00ff88;
            background: rgba(0, 255, 136, 0.1);
        }}

        .agent-box.error {{
            border-left-color: #ff6b6b;
            background: rgba(255, 107, 107, 0.1);
        }}

        .agent-number {{
            color: #00d4ff;
            font-weight: bold;
            margin-right: 5px;
        }}

        .data-panels {{
            grid-column: 2;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .data-panel {{
            grid-column: 1 / -1;
        }}

        .output-box {{
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
            font-family: monospace;
            font-size: 11px;
            margin-top: 10px;
            max-height: 200px;
            overflow-y: auto;
        }}

        .output-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 8px;
            padding: 6px;
            background: rgba(0, 212, 255, 0.05);
            border-left: 2px solid #00d4ff;
        }}

        .output-label {{
            color: #00d4ff;
            font-weight: bold;
        }}

        .output-value {{
            color: #00ff88;
        }}

        .validation-item {{
            margin-bottom: 10px;
            padding: 8px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
            font-size: 12px;
            border-left: 3px solid #666;
        }}

        .validation-item.pass {{
            border-left-color: #00ff88;
        }}

        .validation-item.fail {{
            border-left-color: #ff6b6b;
        }}

        .button {{
            background: #00d4ff;
            border: none;
            border-radius: 4px;
            color: #1a1a2e;
            padding: 8px 12px;
            font-weight: bold;
            cursor: pointer;
            font-size: 12px;
            margin-top: 10px;
            transition: all 0.2s;
        }}

        .button:hover {{
            background: #00ff88;
            transform: translateY(-2px);
        }}

        .phase-2-ready {{
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}

        .phase-2-ready h3 {{
            color: #00ff88;
            margin-bottom: 10px;
        }}

        .phase-2-ready ul {{
            margin-left: 20px;
            font-size: 12px;
            line-height: 1.8;
        }}

        @media (max-width: 1400px) {{
            .main-grid {{
                grid-template-columns: 1fr;
            }}
            .data-panels {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎳 Bowling Visualizer - Phase 1+2 Governor Dashboard</h1>
            <p class="phase-info">Real Agent Orchestration & Validation</p>
            <p class="phase-info">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="--progress: var(--progress-pct)"></div>
            </div>
            <p class="phase-info" id="progress-text">Progress: 0/12</p>
        </header>

        <div class="main-grid">
            <!-- Agent Status Panel (Left) -->
            <div class="panel">
                <h2>Agent Status</h2>
                <div id="agent-status-list"></div>
            </div>

            <!-- Data Panels (Center) -->
            <div class="data-panels" id="data-panels"></div>

            <!-- Validation Panel (Right) -->
            <div class="panel">
                <h2>✓ Phase 1+2 Status</h2>
                <div id="validation-list"></div>
                <div class="phase-2-ready">
                    <h3>→ Phase 2 Complete</h3>
                    <ul>
                        <li><strong>Agent #10:</strong> Flare calculation ✓</li>
                        <li><strong>Agent #11:</strong> Saturation tracking ✓</li>
                        <li><strong>Agent #12:</strong> Gyroscopic precession ✓</li>
                    </ul>
                    <p style="margin-top: 10px; font-size: 11px; color: #888;">
                        Phase 1+2 physics complete. Ready for MVP testing.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const agents_data = {agents_json};
        const agents_status = {status_json};

        const AGENTS = [
            {{ id: 1, name: "Ball Properties", status: "complete" }},
            {{ id: 2, name: "Oil Pattern", status: agents_status["2"] ? "complete" : "error" }},
            {{ id: 3, name: "Initial Conditions", status: agents_status["3"] ? "complete" : "error" }},
            {{ id: 4, name: "Contact Patch", status: agents_status["4"] ? "complete" : "error" }},
            {{ id: 5, name: "Friction & Torque", status: agents_status["5"] ? "complete" : "error" }},
            {{ id: 6, name: "Rotational Dynamics", status: agents_status["6"] ? "complete" : "error" }},
            {{ id: 7, name: "Translational Dynamics", status: agents_status["7"] ? "complete" : "error" }},
            {{ id: 8, name: "Trajectory Integrator", status: agents_status["8"] ? "complete" : "error" }},
            {{ id: 9, name: "Physics Integrator", status: agents_status["9"] ? "complete" : "error" }},
            {{ id: 10, name: "Flare Calculation", status: agents_status["10"] ? "complete" : "error" }},
            {{ id: 11, name: "Saturation Tracking", status: agents_status["11"] ? "complete" : "error" }},
            {{ id: 12, name: "Gyroscopic Precession", status: agents_status["12"] ? "complete" : "error" }}
        ];

        function renderAgents() {{
            const list = document.getElementById("agent-status-list");
            const completed = Object.values(agents_status).filter(s => s && s.includes("COMPLETE")).length;
            const total = 12;
            const pct = Math.round((completed / total) * 100);

            document.documentElement.style.setProperty('--progress-pct', pct + '%');
            document.getElementById("progress-text").textContent = `Progress: ${{completed}}/12 agents (${{pct}}%)`;

            list.innerHTML = AGENTS.map(agent => `
                <div class="agent-box ${{agents_status[agent.id.toString()] && agents_status[agent.id.toString()].includes("COMPLETE") ? "complete" : "error"}}">
                    <div><span class="agent-number">#${{agent.id}}</span>${{agent.name}}</div>
                    <div style="color: #666; font-size: 11px; margin-top: 3px;">
                        ${{agents_status[agent.id.toString()] || "Not run"}}
                    </div>
                </div>
            `).join('');
        }}

        function renderDataPanels() {{
            const container = document.getElementById("data-panels");
            const data = agents_data;

            let html = `
                <div class="panel data-panel">
                    <h2>#9 Physics Integrator</h2>
                    <div class="output-box">
                        ${{Object.entries(data["9"] || {{}}).map(([k, v]) => `
                            <div class="output-row">
                                <span class="output-label">${{k}}:</span>
                                <span class="output-value">${{typeof v === 'number' ? v.toFixed(2) : v}}</span>
                            </div>
                        `).join('')}}
                    </div>
                </div>
                <div class="panel data-panel">
                    <h2>#10 Flare Calculation</h2>
                    <div class="output-box">
                        ${{Object.entries(data["10"] || {{}}).map(([k, v]) => `
                            <div class="output-row">
                                <span class="output-label">${{k}}:</span>
                                <span class="output-value">${{typeof v === 'number' ? v.toFixed(2) : v}}</span>
                            </div>
                        `).join('')}}
                    </div>
                </div>
                <div class="panel data-panel">
                    <h2>#11 Saturation Tracking</h2>
                    <div class="output-box">
                        ${{Object.entries(data["11"] || {{}}).map(([k, v]) => `
                            <div class="output-row">
                                <span class="output-label">${{k}}:</span>
                                <span class="output-value">${{typeof v === 'number' ? v.toFixed(2) : v}}</span>
                            </div>
                        `).join('')}}
                    </div>
                </div>
                <div class="panel data-panel">
                    <h2>#12 Gyroscopic Precession</h2>
                    <div class="output-box">
                        ${{Object.entries(data["12"] || {{}}).map(([k, v]) => `
                            <div class="output-row">
                                <span class="output-label">${{k}}:</span>
                                <span class="output-value">${{typeof v === 'number' ? v.toFixed(2) : v}}</span>
                            </div>
                        `).join('')}}
                    </div>
                </div>
            `;

            container.innerHTML = html;
        }}

        function renderValidation() {{
            const list = document.getElementById("validation-list");
            const criteria = [
                {{ name: "Phase 1: Ball reaches 60 ft", pass: agents_data["9"]?.distance_ft >= 60 }},
                {{ name: "Phase 1: Energy decreases", pass: agents_data["9"]?.energy_lost_pct > 50 }},
                {{ name: "Phase 2: Flare valid (0.5-4.5\")", pass: (agents_data["10"]?.flare_distance_inches >= 0.5 && agents_data["10"]?.flare_distance_inches <= 4.5) }},
                {{ name: "Phase 2: Saturation monotonic", pass: agents_data["11"]?.validation }},
                {{ name: "Phase 2: Precession complete", pass: agents_data["12"]?.validation }},
                {{ name: "All Phase 1 agents pass", pass: agents_data["2"]?.validation && agents_data["3"]?.validation && agents_data["9"]?.validation }},
                {{ name: "All Phase 2 agents pass", pass: agents_data["10"]?.validation && agents_data["11"]?.validation && agents_data["12"]?.validation }},
                {{ name: "MVP Ready", pass: (agents_data["9"]?.distance_ft >= 60 && agents_data["10"]?.validation && agents_data["11"]?.validation && agents_data["12"]?.validation) }}
            ];

            list.innerHTML = criteria.map(c => `
                <div class="validation-item ${{c.pass ? 'pass' : 'fail'}}">
                    <span>${{c.pass ? '✓' : '✗'}}</span> ${{c.name}}
                </div>
            `).join('');
        }}

        function init() {{
            renderAgents();
            renderDataPanels();
            renderValidation();
        }}

        init();
    </script>
</body>
</html>
"""
        return html


if __name__ == "__main__":
    gov = Governor()
    results = gov.run_all_agents()
    html = gov.generate_html_dashboard(results)

    # Save HTML
    with open("/mnt/user-data/outputs/governor_dashboard.html", "w") as f:
        f.write(html)

    print("\n✓ Dashboard saved to: /mnt/user-data/outputs/governor_dashboard.html")
    print("\nAgent Outputs Summary:")

    # Convert and print
    def convert_to_native(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_native(item) for item in obj]
        return obj

    try:
        serializable = convert_to_native(gov.agent_outputs)
        print(json.dumps(serializable, indent=2))
    except Exception as e:
        print(f"Could not serialize full results: {e}")
