# Backlog

UI-only pass (no backend physics changes). Checked items are built; unchecked
are next. See [`README.md`](README.md) for what's real vs placeholder in the
physics pipeline, and [`lane-renderer/AGENT_MAPPING.md`](lane-renderer/AGENT_MAPPING.md)
for the renderer's own seams.

## Ball database (`balls_database.py`)

- [x] Replaced with Motiv's real, current 24-ball catalog (scraped from
      motivbowling.com + BowlerX/BowlersMart) — the original 38-ball version
      was mostly fabricated (invented names that were never real products)
- [x] 7-tier category taxonomy using Motiv's own wording: Heavy Oil,
      Medium-Heavy Oil, Medium Oil, Light-Medium Oil, Light Oil, Entry Level,
      Spare
- [x] Per-weight RG/differential where Motiv publishes it (most balls: 12–16
      lb; a few: 8–10 lb up to 16lb) via `specs_by_weight` / `specsAtWeight()`
- [x] Motiv's own published Length/Backend/Hook indices (0–100 scale) and
      `source_url` per ball
- [ ] A handful of fields are lower-confidence or partial — see inline
      comments in `balls_database.py` (Shadow Tank's coverType is an
      approximation of Motiv's proprietary "MCP," a few balls only have
      RG/diff confirmed at one weight, Sigma Tour Pearl's 14/15lb row is from
      a secondary source)
- [x] `box_grit` / `box_finish` — factory surface, parsed from `coverstock_name`
- [x] `core_symmetric` — parsed from `core_name`, feeds the Shape (Smooth/Sharp)
      half of the arsenal role classification below

## Arsenal Builder (`index.html`)

- [x] Ball catalog (from `balls_database.py`, snapshotted inline) with add-to-bag
- [x] Weight picker per ball (options built from that model's real
      `weightRangeLbs`), RG/diff shown at the selected weight (falls back to
      the nearest weight Motiv actually published, never interpolated)
- [x] Finish is shown as the manufacturer's real, fixed value — not editable
      (an earlier version wrongly let you override it per bag entry)
- [x] Box grit shown per ball (real value, e.g. "1000 LSS")
- [x] Hook potential (0–200, `motivHook × 2` — a rescale of Motiv's own
      published index, not an independent estimate)
- [x] Arsenal shape chart — hook axis × length axis, both Motiv's own
      published Length/Hook indices for the ball's standard weight (real
      manufacturer data, not a derived estimate)
- [x] Auto role badge per ball — Strong/Medium/Weak (Motiv's Hook index) ×
      Smooth/Sharp (core symmetry), the bowling industry's standard
      6-category arsenal system (bowling.com). Benchmark = Medium/Smooth is
      flagged as "benchmark shape." Spare uses the real `category` field, no
      heuristic. Shape is a simplification — real shape also depends on cover
      finish and drilling, which Motiv doesn't publish a number for.
- [x] Manual benchmark pin (★, one per bag) since real bowlers sometimes pick
      by feel rather than strict category — separate from the auto role badge
- [x] Surface-adjustment slider (grit ladder, defaults to each ball's real box
      grit, resettable) — **directional indicator only**: it shows "rougher
      → more hook/less length" or "smoother → more length/less hook" as a
      hint, per bowling.com/bowlerx coaching guidance, but does not change the
      displayed RG/Hook numbers or the chart position, since there's no
      manufacturer-published formula for the exact effect
- [ ] Drill layout assignment (layout sheet: pin, PAP, drill angles)
- [ ] Positive Axis Point (PAP) capture per ball
- [x] Baseline for ball images: a per-ball color picker plus a circular
      monogram avatar in the bag (initials on the picked color) as a stand-in
      until real photos exist. The chart dots use the same color, and the
      pinned benchmark gets a ring in that color too.
- [ ] Real ball images (cropped-to-circle Motiv product photos, or
      user-uploaded photos with crop/zoom) replacing the color/monogram
      placeholder, in the bag and on the shape chart. Would need either
      hotlinking Motiv's own hosted images (not re-hosting copies) or a
      crop/zoom upload UI backed by browser storage (no server to upload to)

## Bowler Profile (`index.html`)

- [x] Hand, release style (1H/2H/no-thumb), ball speed, rev rate inputs
- [x] Heuristic style classification (rev rate ÷ ball speed ratio → Stroker /
      Tweener / Cranker / Power Player) — a coaching rule of thumb, not an
      official rating; doesn't account for axis rotation or tilt
- [ ] Axis rotation / tilt inputs for a real classification
- [ ] Attach a saved bowler profile to a specific arsenal or session

## Lane Renderer (`lane-renderer/index.html`)

- [x] Ball dropdown from the ball database with a weight picker (per-model
      real range), showing RG / diff at that weight / hook potential —
      **display only**, not wired into the sim (there's no sim to wire into
      yet — see below)
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
