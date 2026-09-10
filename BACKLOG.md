# Backlog

UI-only pass (no backend physics changes). Checked items are built; unchecked
are next. See [`README.md`](README.md) for what's real vs placeholder in the
physics pipeline, and [`lane-renderer/AGENT_MAPPING.md`](lane-renderer/AGENT_MAPPING.md)
for the renderer's own seams.

## Arsenal Builder (`index.html`)

- [x] Ball catalog (from `balls_database.py`, snapshotted inline) with add-to-bag
- [x] Per-ball Benchmark / Spare flags, editable finish (Solid/Pearl/Hybrid
      Reactive, Urethane, Particle, Plastic) — stored in `localStorage`, this
      browser only
- [x] RG, differential, hook potential (0–200, derived as `backendRating*20`)
      shown per ball
- [x] Arsenal shape chart — hook axis (backend rating ÷ 10) × length axis
      (RG normalized), quadrant-labeled. This is a heuristic stand-in, not a
      manufacturer-published ball motion chart — no length data exists in the
      source DB, so it's inferred from RG.
- [ ] Drill layout assignment (layout sheet: pin, PAP, drill angles)
- [ ] Positive Axis Point (PAP) capture per ball
- [ ] Swap the heuristic shape axes for real manufacturer motion-chart data,
      if that ever becomes available

## Bowler Profile (`index.html`)

- [x] Hand, release style (1H/2H/no-thumb), ball speed, rev rate inputs
- [x] Heuristic style classification (rev rate ÷ ball speed ratio → Stroker /
      Tweener / Cranker / Power Player) — a coaching rule of thumb, not an
      official rating; doesn't account for axis rotation or tilt
- [ ] Axis rotation / tilt inputs for a real classification
- [ ] Attach a saved bowler profile to a specific arsenal or session

## Lane Renderer (`lane-renderer/index.html`)

- [x] Ball dropdown from the ball database, showing RG / diff / hook
      potential — **display only**, not wired into the sim (there's no sim to
      wire into yet — see below)
- [x] Fit-to-width zoom control (CSS-scales the canvas, so aspect ratio is
      preserved automatically; mouse/drag coordinates adjusted for the scale)
- [x] Placeholder panels for a ball flare map and a vertical ball oil
      cross-section — empty, labeled "coming soon," not computed
- [ ] Real flare map (Agent #10's track-migration output) drawn on the ball
- [ ] Real oil-on-ball cross-section, fed by Agent #11's per-shot pickup
      (`applyShots()` already computes absorption — see AGENT_MAPPING.md)
- [ ] Once `agent_09` can produce a real path, wire the ball dropdown's
      selected ball into it and replace `pathBoardAt()` — the renderer already
      only needs `board = f(feet)`, so this is the actual integration point

## Physics pipeline (root, not touched in this pass)

- [ ] Fix `agent_09`'s unit mismatch (Newton-based accel added into a
      ft/s-carried velocity with no conversion)
- [ ] Give `agent_09` an actual lateral-motion mechanism — right now friction
      is computed anti-parallel to velocity, which structurally cannot
      produce a hook
- [ ] Only after both of the above: replace lane-renderer's placeholder path
      function with real agent_09 output
