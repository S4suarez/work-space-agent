---
name: refrigeration-system-engineer
description: Equipment selection and cost analysis agent for walk-in cooler and freezer refrigeration systems. Use this skill when users need to select refrigeration equipment based on box dimensions, calculate BTU requirements, compare vendor options (Turbo Air, future ABCO), or generate equipment recommendations with pricing. Triggers include "select refrigeration equipment", "size refrigeration system", "walk-in cooler equipment", "walk-in freezer", "BTU calculation", "equipment quote", "refrigeration system", vendor spec sheets, or box dimension analysis.
license: Proprietary - Internal Use Only
---

# Refrigeration System Engineer

Automated equipment selection and cost analysis for walk-in cooler and freezer refrigeration systems.

## Overview

This skill analyzes walk-in box specifications and recommends appropriate refrigeration equipment from available vendors (currently Turbo Air, future ABCO). It handles:

- BTU load calculations based on box dimensions
- Equipment selection meeting capacity requirements
- Multi-vendor pricing comparison
- Single and dual evaporator configurations
- Customer pricing with markup
- Combination cooler/freezer systems

## Core Workflow

### Step 1: Receive Box Specifications

**Input sources:**
- External dimensions from other agents
- Vendor spec sheets (Excel, CSV, PDF)
- Direct user input

**Required information:**
- Box type (cooler, freezer, or both)
- External dimensions: Width × Depth (in feet)
- For combo boxes: separate dimensions for each section

**CRITICAL:** Use ONLY external dimensions, never internal dimensions.

### Step 2: Calculate BTU Requirements

Use `assets/BTU_Requirements_Standard.csv` to lookup required BTU:

```python
import pandas as pd

# Load BTU table
btu_table = pd.read_csv('BTU_Requirements_Standard.csv')

# Format box size as "WxD" (e.g., "8x10")
box_size = f"{width}x{depth}"

# Lookup BTU requirement
required_btu = btu_table[
    (btu_table['boxType'] == box_type) & 
    (btu_table['boxSize'] == box_size)
]['requiredBTU'].values[0]
```

**If exact size not found:** Round UP to next larger size in table to avoid undersizing.

### Step 3: Determine Evaporator Quantity

**Rule:** If either dimension (width OR depth) exceeds 30 feet, use 2 evaporator coils.

```python
evap_qty_needed = 2 if (width > 30 or depth > 30) else 1
```

### Step 4: Select Equipment from Vendors

> **CRITICAL SELECTION RULE:** Always select the **SMALLEST system that meets the BTU requirement**. This means the system with the lowest BTU rating that is still ≥ required BTU. Do NOT skip to larger systems - iterate through options in ascending BTU order and select the FIRST one that qualifies.

**For each available vendor** (currently Turbo Air, future ABCO):

Call the appropriate vendor skill to get equipment data, then filter:

```python
# Example for Turbo Air
from turbo_air_refrigeration import query_systems

# Get all systems matching box type
systems = query_systems(box_type=box_type)

# Filter by BTU requirement (NEVER go under)
suitable_systems = systems[systems['btu_rating_448a'] >= required_btu]

# Filter by evaporator quantity
if evap_qty_needed == 2:
    suitable_systems = suitable_systems[suitable_systems['evaporator_qty'] == 2]

# CRITICAL: Sort by BTU capacity ASCENDING to get smallest suitable system
suitable_systems = suitable_systems.sort_values('btu_rating_448a', ascending=True)

# Get FIRST option (smallest that meets requirement) - NOT a random or larger one
recommended = suitable_systems.iloc[0]
```

**Equipment selection rules (in priority order):**
1. **ALWAYS select the SMALLEST system that meets BTU requirement** - this is the most cost-effective option for the customer
2. **Never select equipment with BTU < required BTU** - undersizing causes equipment failure
3. **Never skip to a larger system when a smaller one qualifies** - verify by checking ALL systems between required BTU and selected system
4. **Coolers use ADR evaporators** (air defrost)
5. **Freezers use LED evaporators** (electric defrost with LED lighting)
6. **Match evaporator quantity to box size** (2 coils if >30ft dimension)

### Step 5: Calculate Customer Pricing

Apply 1.25× markup to vendor cost, then round to nearest $50:

```python
import math

vendor_cost = system['total_system_cost']
raw_price = vendor_cost * 1.25
customer_price = round(raw_price / 50) * 50  # Round to nearest $50
markup_amount = customer_price - vendor_cost
```

**Rounding Examples:**
```
$4,744.00 -> $4,750
$5,180.00 -> $5,200
$6,331.25 -> $6,350
$8,448.75 -> $8,450
```

**Standard terminology (same across ALL agents - AK, CCI, DDS, TA):**
- **Vendor Cost** = what we pay the vendor
- **Customer Price (1.25x)** = vendor cost × 1.25, rounded to nearest $50

### Step 6: Generate Recommendation

**For single box systems:**

Present:
- Box type and external dimensions
- Required BTU from standard table
- Recommended system specifications:
  - Condensing unit model and horsepower
  - Evaporator model(s) and quantity
  - System BTU capacity (must be ≥ required)
  - Vendor cost
  - Customer price (with 1.25× markup)
  - Markup amount

**For multi-vendor comparison:**

Show options from all available vendors side-by-side with same information.

**For combination boxes:**

Treat as two independent systems:
- Calculate separately for cooler section
- Calculate separately for freezer section
- Provide two complete equipment recommendations
- Show individual and total pricing

## Example Outputs

### Example 1: Single Cooler

```
Walk-In Cooler Equipment Selection
===================================

Box Specifications:
  Type: Cooler
  External Dimensions: 8' × 10'
  Required BTU: 7,758 BTU

Recommended System - Turbo Air:
  Condensing Unit: TS010MR404A2 (1 HP)
  Evaporator: ADR112AENC × 1
  System Capacity: 9,888 BTU ✓

  Vendor Cost:              $3,795.00
  >>> Customer Price (1.25x): $4,750.00 <<<
```

### Example 2: Large Freezer (Dual Coils)

```
Walk-In Freezer Equipment Selection
====================================

Box Specifications:
  Type: Freezer
  External Dimensions: 10' × 36'
  Required BTU: 14,023 BTU (using 10×20 table value, rounded up)
  Note: Depth exceeds 30' - using dual evaporator configuration

Recommended System - Turbo Air:
  Condensing Unit: TS060XR404A3A (6 HP)
  Evaporators: LED114BENC × 2
  System Capacity: 19,880 BTU ✓

  Vendor Cost:              $8,599.00
  >>> Customer Price (1.25x): $10,750.00 <<<
```

### Example 3: Combination Box

```
Combination Walk-In Equipment Selection
========================================

COOLER SECTION:
  External Dimensions: 8' × 10'
  Required BTU: 7,758 BTU

  Turbo Air System:
    Condensing Unit: TS010MR404A2 (1 HP)
    Evaporator: ADR112AENC × 1
    Capacity: 9,888 BTU ✓
    Vendor Cost: $3,795.00
    >>> Customer Price (1.25x): $4,750.00 <<<

FREEZER SECTION:
  External Dimensions: 6' × 8'
  Required BTU: 6,863 BTU

  Turbo Air System:
    Condensing Unit: TS025XR404A2A (2.5 HP)
    Evaporator: LED090BENC × 1
    Capacity: 8,445 BTU ✓
    Vendor Cost: $5,183.00
    >>> Customer Price (1.25x): $6,500.00 <<<

TOTAL:
  Combined Vendor Cost:              $8,978.00
  >>> Combined Customer Price (1.25x): $11,250.00 <<<
```

### Example 4: Multi-Vendor Comparison

```
Walk-In Cooler Equipment Selection - Vendor Comparison
=======================================================

Box Specifications:
  Type: Cooler
  External Dimensions: 10' × 12'
  Required BTU: 9,805 BTU

OPTION 1 - TURBO AIR:
  Condensing Unit: TS010MR404A2 (1 HP)
  Evaporator: ADR112AENC × 1
  Capacity: 9,888 BTU ✓
  Vendor Cost: $3,795.00
  >>> Customer Price (1.25x): $4,750.00 <<< ✓ LOWEST PRICE

OPTION 2 - ABCO (future):
  [Would show ABCO equipment here when available]

RECOMMENDATION: Turbo Air offers the most cost-effective solution.
```

## Critical Rules

### ALWAYS Select Smallest Qualifying System
- **This is the #1 rule**: Select the system with the LOWEST BTU rating that still meets the requirement
- Sort all qualifying systems by BTU ascending, then pick the FIRST one
- NEVER skip to a larger system when a smaller one qualifies
- Verify selection by confirming no smaller system in the list meets the BTU requirement
- Example: If required BTU is 14,023, and options are 13,490 / 16,245 / 19,880 / 24,460 → select 16,245 (first one ≥ 14,023)

### NEVER Undersize
- System capacity MUST be ≥ required BTU
- If uncertain, round up to next size
- Better to oversize slightly than undersize

### Evaporator Selection
- **Coolers:** ADR series (air defrost)
- **Freezers:** LED series (electric defrost with lighting)
- **Dual coils:** Required when width OR depth > 30 feet

### Pricing
- Always show **Vendor Cost** AND **Customer Price (1.25x)**
- Customer Price = Vendor Cost × 1.25, rounded to nearest $50
- Use `>>> Customer Price (1.25x): $X,XXX.00 <<<` format to make it visually distinct
- Same terminology used across ALL agents (AK, CCI, DDS, TA)

### Combination (Combo) Boxes

**CRITICAL:** When receiving dimensions from a CCI/LEER combo quote, you will receive **individual compartment dimensions** — NOT the overall box dimension. The calling agent (cci-leer-quote-agent) strips out the overall dimension and passes only the compartment sizes.

**Rules:**
- Treat each compartment as a fully independent system
- Calculate BTU separately for each compartment using its own W × D
- Cooler compartments → ADR evaporators (air defrost)
- Freezer compartments → LED evaporators (electric defrost)
- Show individual system pricing AND combined total
- Combos can be any mix: freezer+cooler, cooler+cooler, freezer+freezer, or 3+ compartments

**Example:** A 24'x12'x8' Freezer/Cooler Combo with Freezer 12'x12'x8' and Cooler 12'x12'x8' → size a 12x12 freezer system AND a 12x12 cooler system separately. Never use 24x12 for either.

## BTU Table Coverage

The standard BTU table covers:
- **Coolers:** 6×6 through 12×20 (52 sizes)
- **Freezers:** 6×6 through 12×20 (52 sizes)

**For sizes outside table:**
- Round UP to nearest larger size
- Note the rounding in recommendation
- Never round down

## Working with Vendor Skills

### Turbo Air Integration

```python
# Load Turbo Air data via skill
from TA_refrigeration_data_manager import TurboAirDataManager
manager = TurboAirDataManager()
manager.df = pd.read_csv('Turbo_Air_Refrigeration_Systems.csv')

# Query for suitable systems
systems = manager.filter_systems(box_type=box_type)
systems = systems[systems['btu_rating_448a'] >= required_btu]
systems = systems[systems['evaporator_qty'] == evap_qty_needed]

# Get ADR for coolers, LED for freezers
if box_type == 'cooler':
    systems = systems[systems['evaporator_model'].str.startswith('ADR')]
else:  # freezer
    systems = systems[systems['evaporator_model'].str.startswith('LED')]

# Sort by BTU to get smallest suitable system
systems = systems.sort_values('btu_rating_448a')
recommended = systems.iloc[0] if len(systems) > 0 else None
```

### Future ABCO Integration

When ABCO skill is available, follow same pattern:
1. Query ABCO data
2. Apply same BTU and configuration rules
3. Present both options
4. Highlight lower-cost option

## Reading Vendor Spec Sheets

When processing vendor files (Excel, PDF, CSV):

```python
import pandas as pd
import PyPDF2
import re

# For Excel/CSV
df = pd.read_excel('vendor_spec.xlsx')  # or read_csv
# Look for columns containing: width, depth, size, dimensions
# Extract values

# For PDF
with open('vendor_spec.pdf', 'rb') as file:
    pdf = PyPDF2.PdfReader(file)
    text = pdf.pages[0].extract_text()
    # Use regex to find dimensions: r'(\d+)\s*[x×]\s*(\d+)'
    match = re.search(r'(\d+)\s*[x×]\s*(\d+)', text)
    if match:
        width, depth = int(match.group(1)), int(match.group(2))
```

**Look for:**
- "External dimensions", "Outside dimensions", "OD"
- Size patterns: "8x10", "8'×10'", "8 x 10"
- Width/depth in separate fields
- Box type: "cooler", "freezer", "combo", "split"

**If dimensions not found:**
- Ask user to provide external dimensions
- Do NOT proceed with assumption or internal dimensions

## Quality Checks

Before finalizing recommendation:

1. ✓ BTU requirement looked up from standard table
2. ✓ System capacity ≥ required BTU (NEVER less)
3. ✓ **Selected system is the SMALLEST that meets BTU requirement** (verify no smaller system qualifies)
4. ✓ Evaporator quantity matches box size (2 if >30ft)
5. ✓ Evaporator type matches box type (ADR for cooler, LED for freezer)
6. ✓ Customer price = vendor cost × 1.25, rounded to nearest $50
7. ✓ All specifications clearly stated

## References

See reference files for additional details:
- `references/btu-calculation-guide.md` - BTU calculation methodology
- `references/equipment-selection-rules.md` - Detailed selection criteria
- `references/vendor-comparison.md` - Multi-vendor analysis guidelines
