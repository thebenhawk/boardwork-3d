# Agent Mapping — Lane Renderer v7

Which part of `index.html` belongs to which agent, so this work can be lifted
into the physics pipeline instead of living only in a browser file.

Status key: **OWNED** = this renderer is currently the reference implementation ·
**SEAM** = placeholder here, agent replaces it · **FEEDS** = produces an input the agent needs

---

## Agent #2 — Oil Pattern  ·  OWNED

The largest share of this work. This renderer is now further along than the
agent spec, and the spec needs revising.

| Piece | Where | Note |
|---|---|---|
| Kegel sheet decoder | `tools/parse_pdf.py` | `T.OIL = LOADS × MICS × boards`; `nL → 40-n`, `nR → n` |
| Zone/units decoder | `tools/parse_tsv.py` | per-board × per-zone matrix; better than load rows |
| Machine-file decoder | `tools/build_db.py` | fixed-offset `.txt` blocks; last resort |
| Pattern database | `data/kegel_patterns.json` | 11 patterns, all sheet-validated |
| Matrix builder | `buildMatrix()` | 39 boards × 714 one-inch steps, µL per cell |
| Buffer carry | `buildMatrix()`, `buffer` param | MODELLED, not on the sheet |
| Cross-section sampling | `drawProfile()` | µL per board at any station |

**Spec change required.** Agent #2 is specified as a *0.0–1.0 density matrix with
bilinear interpolation*. That is wrong in two ways:
1. Oil is a **volume**, not a normalized density. Depletion, absorption and
   carrydown only conserve if cells hold µL. Normalized density cannot be
   conserved through a transition model.
2. Grid resolution is **1 inch down-lane × 1 board across** — not an arbitrary
   grid needing bilinear interpolation. Boards are physically discrete. Interpolation
   is only needed *along* the lane, and nearest-cell is adequate at 1 in.

Agent #2 should be re-specified to load `kegel_patterns.json` and emit the µL matrix.

## Agent #4 — Contact Patch  ·  FEEDS

- `TRACK_HALF_BD = 1.5` — the ~3-board contact strip the ball rides.
  This is currently a constant. Agent #4 should compute it from ball weight,
  coverstock and the oil film under the patch, then feed it back here.
- The renderer already samples oil per 1-inch step along the track, which is the
  exact input Agent #4 needs (`oil under patch at this station`).

## Agent #5 — Friction & Torque  ·  FEEDS

- µL per cell at the contact patch is the friction driver. Two numbers this
  renderer produces that Agent #5 needs:
  - **local oil volume** at the ball's position each step
  - **cumulative oil absorbed into the coverstock** (`meta.absorbed`), which
    changes effective grit as the ball soaks — listed in the project's
    Common Mistakes as #6.

## Agent #9 — Physics Integrator  ·  SEAM

`pathBoardAt()` is a **placeholder**: a cubic Hermite from the breakpoint to the
pocket. Only two things about it are real —
- the endpoints (laydown board 20, breakpoint board, pocket 17.5 RH / 22.5 LH)
- the tangent at 60 ft, fixed to exactly 6° by construction

Everything between is not physics. Agent #9 replaces this function wholesale.
The renderer consumes it through one interface: `board = f(feet)`. Keep that
signature and nothing else needs to change.

## Agent #11 — Saturation  ·  OWNED (partial)

`applyShots()` splits oil taken from the lane three ways:

| Fraction | Const | Destination |
|---|---|---|
| absorbed into coverstock | `F_ABS = 0.15` | leaves the lane — Agent #11's accumulator |
| squeezed sideways | `F_LAT = 0.30` | boards flanking the track |
| pushed down lane | `F_DOWN = 0.55` | carrydown, decays at `0.004`/inch (~20 ft travel) |

Mass conserves exactly: `on-lane + absorbed + off-end = fresh volume`.
Agent #11 currently owns only the absorbed term. It should also own the
boot-shaped saturation footprint on the ball, which this renderer does not model.

## Agent #14 — Visualization  ·  OWNED

- Piecewise down-lane scale (`ZONES`): approach 1.8 px/in, surface 3.2, pin deck 9.15.
  Pin deck matches the across-boards scale so **pins and the ball render as true circles**.
  Any uniform scale makes them ellipses.
- USBC geometry from `claude_lane-geometry-spec.md`: 39 boards, arrow arc
  (board 20 furthest downlane at 16 ft), range finders, exact pin coordinates.
- Oil drawn via `putImageData` at native matrix resolution then blitted —
  28k `fillRect` calls per lane was far too slow to drag a slider against.
- Two independent lanes, each with its own matrix, pattern and wear state.

## Proposed new agent — Oil Transition

`applyShots()` does not belong to any agent in the current architecture. It is
its own concern: how a pattern degrades over a session. It depends on #9 (where
the ball actually goes) and feeds #5 (friction) and #11 (saturation).

Suggested slot: **Agent #15 — Oil Transition**, Phase 2, after #11.
Its constants (`TAKE`, `F_ABS`, `F_LAT`, `F_DOWN`, `CARRY_DECAY`) are currently
tuned by eye to produce plausible transition, **not fitted to measured data**.
That is the single largest piece of unvalidated physics in this build.

---

## Not yet touched by any agent

- Pin carry prediction — pins render at true 4.75" belly diameter and the 1-3
  contact geometry is drawn (6.00" centre-to-centre, 1.25" clear gap vs an 8.5"
  ball), but nothing computes carry.
- Flare rings (Agent #10) — not in this renderer at all.
- Track migration across shots — the ball's own oil ring.
