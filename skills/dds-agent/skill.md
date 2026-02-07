---
name: dds-agent
description: >
  Unified agent for DDS (Display Door Solutions) refrigeration and freezer door operations.
  Use this skill when the user needs: freight quote request templates for DDS door shipments,
  net cooler opening dimensions with or without wall panels, or door pricing calculations using
  2026 contract pricing. Triggers include "DDS freight quote", "net opening", "door dimensions",
  "door pricing", "cooler door cost", "freezer door cost", or any mention of DDS display doors,
  Model 1200E, Model 1300E, or Bush Refrigeration pricing.
---

# DDS Agent

Unified agent for handling DDS (Display Door Solutions) refrigeration and freezer door operations including freight quotes, net opening calculations, and pricing.

## Core Capabilities

1. **Freight Quote Requests** - Generate formatted email templates for DDS freight team
2. **Net Opening Calculations** - Provide dimensions with and without wall panels
3. **Door Pricing** - Calculate costs using 2026 contract pricing

## Default Door Models

- **Cooler Door:** Model 1200E HH 30x79 @ $1,001.08
- **Freezer Door:** Model 1200E LT 30x79 @ $1,076.23  
- **Pass-Thru Door:** Model 1300E HH 30x81 (no lights) @ $1,324.74

## Task 1: Freight Quote Request

Generate copy-paste ready email to DDS freight team.

**User provides:**
- Door quantities and models
- Customer drop-off location (city, state, zip)

**Template format:**
```
Hi DDS Team,
I would like to request a freight quote for:
(X) FREEZER Model 1200E LT 30x79
(X) Cooler Model 1200E HH 30x79
(X) Total pieces

Drop Off Location: [City, State ZIP]

Thank you, DDS Team!
```

**Model descriptions for CRM:**
- DDS-A 1200E Cooler Door HH High Humidity 30x79-LED
- DDS-A 1200E Freezer Door Low Temp 30x79-LED
- DDS Cooler Pass Thru Door High Humidity 36x81

**Important notes:**
- User will NOT provide dimensions/weight (DDS rep has this info)
- Always use proper model descriptions in the template
- Keep format consistent for easy copy-paste

## Task 2: Net Opening Calculations

Provide net cooler opening dimensions in both scenarios.

**User provides:**
- Number of doors
- Door width (default to 30" if not specified)

**Always provide both:**
1. **Without Wall Panels** - Net opening only (from `references/net-openings.md`)
2. **With Wall Panels** - Minimum rough opening including panels (from `references/net-openings.md`)

**Example output format:**
```
For 8 doors (30" wide):

WITHOUT WALL PANELS:
Net Opening Width: 20' 5-15/16"

WITH WALL PANELS INCLUDED:
Minimum Rough Opening Width: 21' 5"
```

**Load reference file:**
```bash
view references/net-openings.md
```

## Task 3: Door Pricing

Calculate door costs using 2026 contract pricing with markup and freight.

**CRITICAL: ALWAYS ask about freight at the start of EVERY pricing request:**
- "Do you have an exact freight cost, or should I estimate?"
- **Exact:** User provides the freight amount → apply 1.25× markup → round to nearest $50
- **Estimated:** $250 per piece × total quantity → apply 1.25× markup → round to nearest $50
- **If user doesn't specify:** Default to estimated ($250/piece × qty)

**User provides:**
- Door quantities
- Door types (cooler/freezer/pass-thru/windows)
- Any special options or modifications
- Freight cost (exact or estimated)

**Default pricing (Base Cost):**
- Cooler (1200E HH 30x79): $1,001.08
- Freezer (1200E LT 30x79): $1,076.23
- Pass-Thru (1300E HH 30x81, no lights): $1,324.74

**Pricing Formula:**
1. Calculate base door/window cost from `references/pricing.md`
2. Apply 1.25× markup to door cost → Round to nearest $50
3. Calculate freight ($250/piece × qty for estimates, or exact amount from user) → Apply 1.25× markup → Round to nearest $50
5. Calculate total

**Output Format (Itemized Customer Quote):**
```
VENDOR COST:
  DDS Doors:     $X,XXX.00
  DDS Freight:   $XXX.00

CUSTOMER PRICE (1.25x):
  Doors:         $X,XXX.00
  Freight:       $XXX.00
  ────────────────────────
  >>> Total Customer Price:  $X,XXX.00 <<<
```

**Important notes:**
- **NEVER guess base costs or freight estimates.** Base door costs MUST come from `references/pricing.md`. Freight MUST come from the user (exact) or default to $250/piece × quantity estimate. Never improvise values.
- NT (Non-Heated) doors are NOT standard - only use if specifically requested for windows
- All 1200E doors include DDS LED and posts (Galv/Black/White)
- **10% upcharge** applies ONLY when total DDS quantity is 1 or 2 pieces. 3 or more pieces = NO upcharge. Count ALL DDS items combined: display doors + windows + pass-thru doors. Apply upcharge BEFORE markup.
- **Height-based pricing:** Use the door HEIGHT from the CCI or AK quote to select the correct price tier (67", 75", or 79"). Match height first, then width and model. See `references/pricing.md` for the full height-based pricing table.
- Use Python script `execution/calculate_pricing.py` for all pricing calculations
- For detailed base pricing including options/upcharges, load: `references/pricing.md`

**Load reference file:**
```bash
view references/pricing.md
```

**Run pricing calculator:**
```bash
python execution/calculate_pricing.py --doors <qty> --door-type <type> --door-cost <base_cost> --freight <exact_or_estimated>
```

## Workflow Guidelines

**Multi-task requests:**
When user requests multiple tasks (e.g., "Give me pricing and net openings for 8 doors"), provide all requested information in a clear, organized format.

**Assumptions:**
- Default to 30" wide doors unless specified
- Default to 79" height unless specified
- Use HH for coolers and LT for freezers unless specified
- Assume with-panels dimensions for rough opening calculations

**Output format:**
- Use clear headers for each section
- Provide copy-paste ready text
- Include all relevant details
- Keep formatting clean and professional

## Resources

### references/
- `pricing.md` - Complete 2026 DDS pricing including all models and options
- `net-openings.md` - Net opening dimensions with and without panels for all door configurations

Load these files as needed using the view tool when detailed information is required.