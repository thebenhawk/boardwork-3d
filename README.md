# Boardwork 3D — Bowling Ball Physics

Two separate bodies of work live here, built at different times and not yet
connected:

- **Root** — a Flask API (`app.py`) over a set of physics "agent" modules
  (`agent_02`…`agent_12`) and a ball database (`balls_database.py`).
- **[`lane-renderer/`](lane-renderer/)** — a browser-only two-lane oil pattern
  renderer built on real Kegel sheet data, with its own validation suite. See
  [`lane-renderer/README.md`](lane-renderer/README.md) and
  [`lane-renderer/AGENT_MAPPING.md`](lane-renderer/AGENT_MAPPING.md) for what
  it does and where it's meant to feed back into the agents below — that
  mapping isn't duplicated here.

This file replaces an earlier README that described the agent pipeline as
more connected and more validated than it is. What follows was checked
against the code, not against the docstrings.

## The physics agents

`agent_02_oil_pattern.py` through `agent_12_gyroscopic_precession.py` (11
files — there is no standalone `agent_01`; ball properties are just rows in
`balls_database.py`). None of them import each other. The only things that
import agent modules are `app.py` and `governor.py`, and both do the same
thing: import each agent's `create_*`/`calculate_*` and `validate_*`
functions and call them one at a time against that agent's own success
criteria. **Every agent has been validated in isolation. None of them have
been validated as a connected chain**, because nothing chains them —
`governor.py` calls each `validate_*` independently, not agent N's output
into agent N+1's input.

### The one that actually runs an end-to-end simulation doesn't use the chain

`/api/simulate` calls `agent_09_physics_integrator.run_physics_simulation()`
for the trajectory. That function does not call agents 3–8 and does not
import `agent_02` — it's a self-contained ~250-line loop with its own
hardcoded Gaussian oil-density model and its own pattern-length table. The
"12 agent pipeline" framing doesn't describe what actually produces a
trajectory; agent_09 does, alone.

That loop has a structural bug, not a tuning one: velocity initializes as
`[0, speed, 0]` and friction each step is computed as a scalar coefficient
times the (negative) velocity vector — anti-parallel by construction. A
vector that starts with zero lateral component and is only ever scaled by
its own direction stays at zero lateral component forever. Ran it directly:

```
entry_angle_deg   0.0
breakpoint_board  20.0
max_board_reached 20.0
```

for all 600 steps, every input tried. The ball cannot hook in this loop —
there's no mechanism in it that could put a nonzero value into `velocity[0]`.
Lateral motion is Agent #12's job (gyroscopic precession), which is called
separately, after the fact, on the trajectory agent_09 already produced — it
doesn't feed back in.

This is visible in `app.py` itself: the `/api/simulate` handler computes
`entry_angle = gyroscopic.entry_angle_deg if gyroscopic.entry_angle_deg != 0
else sim.entry_angle_deg` and derives `breakpoint`/`hook_amount` from that
patched value. So the API's reported hook numbers come from agent_12's
independent calculation, while the `trajectory` array sent to the frontend
for drawing the ball's actual path is agent_09's raw per-step output —
pinned at board 20.0 the whole way. The reported hook and the drawn path
disagree.

There's also a likely unit bug in the same loop: `friction_force` is built
from `normal_force_n = ball_mass_kg * 9.81 * 1.8` (newtons), and
`accel = friction_force / ball_mass_kg` (m/s²) is added directly to
`velocity`, which is carried in ft/s (`ball_speed_mph * 1.46667`) with no
conversion between the two. If that's not intentional, deceleration is off
by a factor of ~3.28.

### Orphan modules

- **`bowling_physics.py`** (~24 KB) implements all nine Phase-1 agents as
  composed functions (`agent_1_ball_properties` … `agent_9_...`), citing
  Brody Dylan Johnson's rolling-with-slipping equations. Nothing in the repo
  imports it.
- **`bowling_validator.py`** is a second, separate validation framework
  (success criteria + an `AgentValidator` class) that also isn't imported by
  anything.

Neither is wired into `app.py` or `governor.py`. They read as an earlier or
parallel attempt at the same problem, left in place.

## Flask API (`app.py`)

```
GET  /api/health
GET  /api/balls              # optional ?category= filter
GET  /api/balls/<ball_id>
GET  /api/patterns
POST /api/simulate
GET  /api/defaults
```

`python app.py` serves on port 5000. `boardwork_3d_mvp.html` is the
browser frontend; open it directly or serve it over HTTP.

## Ball database

`balls_database.py` — 38 Motiv balls with weight, RG, differential, backend
rating, flare potential, cover type, category. (Fewer than the "50+" the old
README claimed.)

## Web shell (`index.html`)

The GitHub Pages root is a tabbed static shell — Lane Renderer, Arsenal
Builder, Bowler Profile, and a Physics Simulator tab that just explains why
that piece can't run on Pages (it needs the Flask API). Arsenal Builder and
Bowler Profile are new UI-only features: a bag of balls with benchmark/spare
flags and an approximate hook/length shape chart, and a bowler profile with a
heuristic style classification (Stroker/Tweener/Cranker/Power Player) from
rev rate ÷ ball speed. Both persist to this browser's `localStorage` only —
nothing is synced anywhere, and neither is wired into the physics pipeline
yet. See [`BACKLOG.md`](BACKLOG.md) for what's built vs planned.

## Setup

```bash
pip install -r requirements.txt
python app.py                  # Flask API on :5000
open boardwork_3d_mvp.html     # or: python -m http.server 8000
```

For the renderer instead: open [`lane-renderer/index.html`](lane-renderer/index.html)
directly — no build step, no server needed. Its pattern data can be
re-validated with `python lane-renderer/tools/validate.py` (11/11 pass as of
this writing).

## Where the two halves meet

`lane-renderer/` renders a ball path through one function,
`pathBoardAt(lane, feet) -> board`. Per
[`lane-renderer/AGENT_MAPPING.md`](lane-renderer/AGENT_MAPPING.md), that
function is a placeholder: only the endpoints (laydown at board 20, the
breakpoint board, the pocket) and a fixed 6° tangent at 60 ft are real: the
curve between them is a cubic Hermite blend, not physics. Agent #9 is meant
to replace it — but the current `agent_09_physics_integrator.py`, per above,
can't produce a hook at all, so it isn't a drop-in replacement yet. That
function signature — `board = f(feet)` — is the actual seam between these two
bodies of work.

## Honest status

- Oil pattern data (`lane-renderer/`): real, validated against source sheets,
  11/11 passing.
- Agent success-criteria checks: each agent passes its own isolated
  `validate_*`, never checked in combination.
- End-to-end trajectory (`agent_09` via `/api/simulate`): runs without
  crashing, reaches 60 ft, but cannot hook — board and entry angle are
  constant by construction. The hook number in the API response comes from a
  separate calculation, not from the drawn path.
- `bowling_physics.py` and `bowling_validator.py`: complete but unused.
