# Setup Guide - Boardwork 3D

## For Windows, macOS, and Linux

### Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click **New repository** (top right)
3. Name it: `boardwork-3d` (or your preferred name)
4. **Do NOT** initialize with README, .gitignore, or license (we have those)
5. Click **Create repository**
6. Copy the HTTPS URL (looks like: `https://github.com/yourusername/boardwork-3d.git`)

### Step 2: Clone and Set Up Locally

```bash
# Download this repository
git clone https://github.com/yourusername/boardwork-3d.git
cd boardwork-3d

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Simulator

```bash
# Start the Flask backend
python app.py
```

You should see:
```
Starting Bowling Visualizer MVP Backend...
Server running on http://localhost:5000
```

### Step 4: Open in Browser

**Option A: Direct** (simplest)
```bash
# macOS
open boardwork_3d_mvp.html

# Windows
start boardwork_3d_mvp.html

# Linux
xdg-open boardwork_3d_mvp.html
```

**Option B: HTTP Server** (more reliable)
```bash
# In a new terminal (with venv activated)
python -m http.server 8000

# Then open: http://localhost:8000/boardwork_3d_mvp.html
```

## Testing the Simulator

### Health Check
Verify the API is working:
```bash
curl http://localhost:5000/api/health
```

You should see:
```json
{"status": "ok", "timestamp": "2026-09-09T..."}
```

### List Available Balls
```bash
curl http://localhost:5000/api/balls | jq '.count'
```

Should return: `50` (or your ball count)

### Run a Simulation
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "ball_id": "jackal_ghost",
    "ball_speed_mph": 18.0,
    "ball_rpm": 300,
    "oil_pattern": "house_shot",
    "oil_condition": "fresh"
  }' | jq '.output.summary'
```

## Pushing to GitHub

```bash
# Set your repo as remote (if not already done)
git remote add origin https://github.com/yourusername/boardwork-3d.git

# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: Boardwork 3D MVP with 12 physics agents"

# Push to GitHub
git branch -M main
git push -u origin main
```

## Troubleshooting

### "Port 5000 already in use"
Flask server didn't shut down. Kill it:
```bash
# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process
```

### "Failed to fetch" in browser
Make sure:
1. Flask server is running (`python app.py`)
2. You're opening the HTML through HTTP or as a file (not both)
3. Both are on `localhost` (same machine)

### "balls.forEach is not a function"
The API response format is wrong. Check:
1. Flask server is running
2. `/api/balls` returns valid JSON with `success: true`

### Python/pip not found
You need Python 3.8+. [Download here](https://www.python.org)

## Next Steps

Once it's working:
1. Try different ball/speed/RPM combinations
2. Compare predictions with your real league data
3. Create additional feature branches for Tier 2 work
4. Share the repo with teammates

## File Structure

```
boardwork-3d/
├── app.py                          # Flask backend (main entry point)
├── balls_database.py               # 50+ Motiv ball specs
├── agent_02_oil_pattern.py        # Oil density interpolation
├── agent_03_initial_conditions.py # Speed/RPM/axis setup
├── agent_04_contact_patch.py      # Friction surface area
├── agent_05_friction_torque.py    # Force calculations
├── agent_06_rotational_dynamics.py # Spin decay
├── agent_07_translational_dynamics.py # Deceleration
├── agent_08_trajectory_integrator.py # Path tracking
├── agent_09_physics_integrator.py # Full simulation
├── agent_10_flare.py              # Track migration
├── agent_11_saturation.py         # Oil absorption
├── agent_12_gyroscopic_precession.py # Spin axis tilt
├── bowling_physics.py             # Physics utilities
├── bowling_validator.py           # Validation helpers
├── governor.py                    # Agent orchestrator
├── boardwork_3d_mvp.html          # Interactive UI (open this!)
├── requirements.txt               # Python dependencies
├── README.md                      # Project overview
├── SETUP.md                       # This file
├── MVP_QUICK_START.md             # Quick reference
└── .gitignore                     # Git ignore rules
```

## Support

- **Documentation**: See README.md for full architecture
- **Quick Reference**: MVP_QUICK_START.md for troubleshooting
- **Issues**: Create a GitHub issue with error message and steps to reproduce

---

**Ready to test?** Run `python app.py` and enjoy!
