# DDS Door Pricing

## Goal
Calculate door costs using 2026 contract pricing with markup and freight, producing an itemized customer quote.

## Inputs
- Door quantities
- Door types (cooler / freezer / pass-thru / windows)
- Any special options or modifications
- Freight cost (exact or estimated)

## Process

### Step 1: Ask About Freight
**CRITICAL — do this at the start of EVERY pricing request:**
- "Do you have an exact freight cost, or should I estimate?"
- **Exact:** User provides the freight amount
- **Estimated:** Use $250 x total quantity (all doors/windows combined)
- **If user doesn't specify:** Default to estimated

### Step 2: Determine Base Cost
Look up base pricing from `references/dds-pricing.md`:

| Type | Model | Base Price |
|------|-------|-----------|
| Cooler | 1200E HH 30x79 | $1,001.08 |
| Freezer | 1200E LT 30x79 | $1,076.23 |
| Pass-Thru | 1300E HH 30x81 (no lights) | $1,324.74 |

### Step 3: Apply Upcharges
- **10% upcharge** for 1-2 door orders (unless part of a 3+ door lineup) — apply BEFORE markup
- Add any option upcharges from pricing.md

### Step 4: Run Pricing Calculator
```bash
python execution/dds_calculate_pricing.py --base-cost <per_unit_cost> --quantity <qty> --freight <freight_cost>
```

The script handles:
1. Multiply base cost x quantity
2. Apply 1.25x markup to door cost -> round to nearest $50
3. Apply 1.25x markup to freight -> round to nearest $50
4. Sum for total

### Step 5: Format Output
```
DDS Doors Cost: $X,XXX.00 (rounded to nearest $50)
DDS Freight: $XXX.00 (rounded to nearest $50)
────────────────────────
Total: $X,XXX.00
```

## Edge Cases
- NT (Non-Heated) doors are NOT standard — only use if specifically requested for windows
- All 1200E doors include DDS LED and posts (Galv/Black/White)
- For mixed door types (e.g., 5 cooler + 3 freezer), run calculator separately for each type, then combine
- Window pricing uses square footage formula: (W x H) / 144 x price/SF
- Add `--json` flag to calculator for programmatic output

## Tools
- `execution/dds_calculate_pricing.py` — pricing calculator with markup and rounding

## Reference Data
- `references/dds-pricing.md` — complete 2026 pricing including all models, options, and upcharges

## Learned Notes
- Lead time: 8-10 weeks from receipt of PO
- All pricing is FOB Elkton, Kentucky
- 27" deep shelves included at no upcharge
- Handle upgrades (elliptical, sleek line chrome/black) are no upcharge
