# Boardwork — Two-Lane Oil Pattern Renderer

Renders a USBC-spec lane pair with real Kegel oil pattern data, per-board oil
volume in µL, and a three-way depletion model for how a pattern transitions
over a session.

Open `index.html` — no build step, no dependencies.

## What it does

- **11 oil patterns** from real Kegel sheets, every one validated against the
  sheet's own printed totals
- **Oil as a matrix**: 39 boards × 714 one-inch steps, µL per cell
- **Draggable cross-section** — slide a station down the lane, the chart shows
  µL per board at that distance
- **Two independent lanes** — separate pattern, wear state and breakpoint each
- **Depletion**: oil squeezed sideways, pushed down lane as carrydown, and
  absorbed into the coverstock; mass conserves exactly
- **True geometry**: piecewise down-lane scale keeps the pin deck at 1:1 so pins
  and the ball render as circles, not ellipses

## Pattern database

`data/kegel_patterns.json` — usable standalone by the physics agents.

| Pattern | Dist | Volume | Ratio | Source |
|---|---|---|---|---|
| Bat 37 | 37 ft | 25.20 mL | 2.81:1 | PDF |
| Bear 38 | 38 ft | 29.58 mL | 2.01:1 | PDF |
| Chameleon 39 | 39 ft | 32.94 mL | 2.46:1 | PDF |
| Cheetah 35 | 35 ft | 28.79 mL | 1.56:1 | PDF |
| Dragon 47 | 47 ft | 26.40 mL | 2.65:1 | PDF |
| Regional 37 | 37 ft | 32.65 mL | 3.08:1 | PDF |
| Scorpion 43 | 43 ft | 27.06 mL | 3.10:1 | PDF |
| Shark 48 | 48 ft | 32.44 mL | 2.51:1 | PDF |
| Viper 37 | 37 ft | 25.55 mL | 2.65:1 | PDF |
| Wolf 34 | 34 ft | 31.79 mL | — | TSV zone matrix |
| Badger 50 | 50 ft | 35.71 mL | — | machine .txt, **not sheet-verified** |

Two backend shapes, both supported:
- `src: "loads"` — rows of `[b0, b1, loads, mics, d0, d1]`
- `src: "zones"` — `zoneEnd[]`, `zoneVol[]`, `zoneUnits[][]` over `boards[]`

## Decoding a Kegel sheet

Board notation: `nL` = nth board from the left, `nR` = nth from the right.
With board 39 as the left gutter: `nL → 40-n`, `nR → n`.

Row total oil: `T.OIL = LOADS × MICS × (boards covered)`, in microlitres.
Lengthwise: `µL per board per inch = LOADS × MICS / ((d1-d0) × 12)`.

Rows with `LOADS = 0` inject nothing — that stretch is buffer-only travel.

## Rebuilding the database

```bash
python3 tools/parse_pdf.py    # PDF sheets  -> db_pdf.json
python3 tools/parse_tsv.py    # TSV dumps   -> db_tsv.json
python3 tools/build_db.py     # merge       -> patterns.json
python3 tools/validate.py     # re-check every pattern
```

Source sheets default to `/mnt/project`.

## Validation

Every pattern is checked two ways:
1. **Row level** — each load row's `LOADS × MICS × boards` must equal the T.OIL
   printed on the sheet
2. **Total level** — the rebuilt matrix must sum to the sheet's stated VOLUME

All 11 pass.

## Known gaps

- **Ball path is a placeholder.** Endpoints and the 6° entry tangent are real;
  the curve between is a Hermite, not physics. Agent #9 replaces it.
- **Depletion constants are eyeballed**, not fitted to measured data.
- **Buffer carry is modelled**, not from the sheet — injection often stops well
  short of the stated distance (Regional 37 stops at 28 ft of a stated 37).
- No flare, no pin carry, no track migration.

See `AGENT_MAPPING.md` for which agent owns what.
