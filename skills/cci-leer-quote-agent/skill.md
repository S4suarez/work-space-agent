---
name: cci-leer-quote-agent
description: >
  Customer service agent for CCI/Carroll Coolers/LEER walk-in refrigeration boxes.
  Handles quote validation, pricing calculations, data extraction, and CSV documentation.
  Use this skill when the user needs: quote validation against customer requests,
  customer pricing with 1.25x markup, PDF data extraction from CCI/LEER quotes,
  or walk-in box cost analysis. Triggers include "CCI quote", "Carroll Coolers quote",
  "LEER quote", "walk-in cooler", "walk-in freezer", "walk-in box", "check this quote",
  "validate quote", "analyze quote", "price this box", "customer pricing", or any
  reference to walk-in refrigeration equipment from CCI/Carroll/LEER.
---

# CCI/LEER Quote Agent

Customer service agent for CCI/Carroll Coolers/LEER walk-in refrigeration boxes. Handles quote validation, pricing calculations, PDF data extraction, and CSV data documentation.

## Core Capabilities

1. **Quote Validation** - Verify quotes against customer requests (dimensions, doors, type, location)
2. **Pricing Calculator** - Calculate customer pricing with 1.25x markup and $50 rounding
3. **Data Extraction & CSV Storage** - Extract quote data from PDFs and store in CSV
4. **DDS Door Detection** - Auto-invoke `dds-agent` skill when display doors are found

## Task 1: Quote Validation (Analytical Checker)

Verify CCI/LEER quotes against customer requests.

**User provides:**
- PDF quote from CCI/Carroll/LEER
- Original request details (optional but helpful)

### Validation Rules

**Dimensions:**
- **FLEXIBLE**: Width and depth are interchangeable (10x8x8 = 8x10x8)
- **CRITICAL**: Height must match exactly
- **FLAG**: If dimensions differ beyond width/depth swap

**Doors:**
- Verify door quantity matches request
- Verify door sizes (width x height) match request
- DO NOT check swing direction (left/right hand hinge)

**Temperature Type:**
- Verify cooler vs. freezer designation
- DO NOT verify specific temperature specs (35F vs -10F)

**Installation:**
- ALWAYS verify indoor vs. outdoor installation type

### Validation Checklist
```
[ ] Dimensions (WxDxH) - allow width/depth swap
[ ] Box type (Cooler/Freezer)
[ ] Door quantity and sizes
[ ] Installation location (Indoor/Outdoor)
[ ] Floor type specified
[ ] Options listed (if any)
[ ] All prices present (Walk-In, Freight, Subtotal)
```

## Task 2: Pricing Calculator

Calculate customer pricing from CCI/LEER quote prices.

---
### ⚠️ MANDATORY PRICING RULE ⚠️

**ONLY use SUB TOTAL (WALK-IN + FREIGHT ESTIMATE) as Vendor Cost. NEVER include OPTIONS.**

Options are ALWAYS separate line items and are NEVER included in the base vendor cost or component totals. This rule is absolute and has no exceptions.

---

**CRITICAL PRICING RULES:**
1. **BASE PRICING = Walk-In + Freight ONLY** - marked up together at 1.25x
2. **OPTIONS are priced SEPARATELY** - each option gets individual 1.25x markup
3. **Never combine options with base pricing** - options are usually not selected
4. **Round each price independently** to nearest $50

### Pricing Formula

```
VENDOR COST (Walk-In + Freight ONLY):
Walk-In Price + Freight Estimate = Vendor Cost
Vendor Cost x 1.25 = raw price
Round to nearest $50 = Customer Price

OPTIONS (Each option priced separately):
Option Vendor Cost x 1.25 = raw price
Round to nearest $50 = Customer Price

Rounding Examples:
$15,711.25 -> $15,700
$15,738.00 -> $15,750
$15,762.00 -> $15,750
$15,788.00 -> $15,800
```

### Output Format

```
VENDOR COST:
-------------------------------
Walk-In Box:           $XX,XXX.00
Freight Estimate:      $X,XXX.00
                      ----------
Vendor Cost:          $XX,XXX.00

>>> CUSTOMER PRICE (1.25x):  $XX,XXX.00 <<<

OPTIONAL ADD-ONS (priced separately):
-------------------------------
Option 1: [Description]
  Vendor Cost:        $XXX.00
  Customer Price (1.25x): $XXX.00

Option 2: [Description]
  Vendor Cost:        $XXX.00
  Customer Price (1.25x): $XXX.00
```

**Important notes:**
- "Buyouts" (if any) should be included in base subtotal before markup
- Options marked "Accepted?" in quotes are still presented as separate line items
- Always use the execution script for calculations:

```bash
python execution/calculate_pricing.py --walkin-price <price> --freight <freight> --options '[{"name":"desc","price":550}]'
```

## Task 3: Data Extraction & CSV Storage

Extract structured data from CCI/LEER quote PDFs and store in CSV.

**CSV Location:** `C:/Users/bnmsu/cci_quotes_data.csv`

### CSV Fields
```csv
PDF_Filename,CCI Vendor Extract,Tag #,SHIP TO ZIP,State,Customer Job,Dimensions and Basic Description,Floor(s),Doors,Walk-In Price,Freight Estimate,Subtotal,Approx. Sq. Ft.,Est. Box Weight,Good Thru,Quote Date,Type,Display Doors,Pass Thru Doors,Shape,Location,Combo,Reach-In
```

For complete field definitions, load: `references/csv_fields.md`

### Extraction Process

1. Extract text from PDF using `execution/extract_quote_data.py`
2. Parse all required fields using regex patterns
3. Validate data before storage
4. Append to CSV using `execution/csv_handler.py`
5. Confirm storage with record count

**Run extraction:**
```bash
python execution/extract_quote_data.py --pdf-path "/path/to/quote.pdf"
```

**Run CSV append:**
```bash
python execution/csv_handler.py --action append --data '{"tag":"CC359210","walkin_price":"10488.00",...}'
```

### Data Rules
- **Unique Identifier**: Tag # + Quote Date as composite key
- **Append Mode**: Always append, never overwrite
- **Validation**: All numeric fields properly formatted before write

## Task 4: DDS Item Detection & Auto-Invoke

Automatically detect ALL DDS items in a CCI/LEER quote and invoke the `dds-agent` skill for pricing.

**Key context:** CCI/Carroll/LEER only supplies walk-in panels and access doors. Display glass doors, windows, and pass-thru doors are ALWAYS "Supplied by Others" — which means DDS supplies them. Every item marked "by Others" that is a display door, window, or pass-thru door is a DDS item to be quoted.

### Detection Patterns

**Display Doors (GD# callouts):**
```
(GD1) (6) 30" x 79" DDS 1200 glass doors. Supplied by Others.
(GD2) (3) 36" x 81" DDS 1300 glass doors. Supplied by Others.
```
**Pattern:** `(GDX) (Qty) Width" x Height" DDS Model doors`
**Models:** DDS 1200, DDS 1300, DDS 1300E

**Windows (OO# Buck Openings):**
```
(OO1) Buck Opening 2' 3 5/8" x 6' 4 23/32"
WINDOW BY OTHERS
```
**Pattern:** `(OOX) Buck Opening Width x Height` followed by `WINDOW BY OTHERS`
**Note:** Buck opening dimensions are the rough opening — DDS window sizing is derived from these.

**Pass-Thru Doors:**
Look for pass-thru or entry door callouts marked "by Others" with DDS 1300/1300E models.

### Auto-Invoke Process
1. **Detect** all DDS items: GD# display doors, OO# windows, and pass-thru doors
2. **Extract** quantity, size, and model/type for each callout
3. **Count total DDS pieces** (all types combined) — 10% upcharge applies ONLY for 1-2 pieces; 3+ pieces = no upcharge
4. **Invoke** the `dds-agent` skill with ALL extracted DDS item details for pricing
5. **DDS Freight default: $250/piece × total quantity** (unless user provides exact freight). NEVER use any other estimate — always $250/piece.
6. **Present** combined summary: CCI box pricing + DDS door/window pricing

### Document in CSV
**Display Doors field:**
- `None` if no display doors
- `GD1: (6) 30"x79" DDS 1200` format if present

**Windows** should also be noted in the appropriate CSV field when OO# buck openings are detected.

## Task 5: Refrigeration Equipment Auto-Selection

Automatically select and price the refrigeration system for the quoted walk-in box.

**Key context:** CCI/LEER quotes list refrigeration as "Supplied by Others." Every box needs a refrigeration system. After validating the box and calculating pricing, automatically invoke the `refrigeration-system-engineer` skill to recommend equipment.

### Auto-Selection Process

1. **Extract external dimensions** from the quote's dimension fields
   - CCI quotes show dimensions as W x D x H (e.g., "12' x 10' x 8'")
   - Use W x D only (drop height) for BTU lookup
   - Convert to feet as whole numbers (e.g., 12 x 10)
2. **Determine box type** from the quote (Cooler or Freezer)
3. **Invoke `refrigeration-system-engineer` skill** with:
   - Box type (cooler or freezer)
   - External dimensions (W x D in feet)
   - The RSE will look up BTU requirements, select appropriate Turbo Air equipment, and calculate customer pricing (1.25x markup on vendor cost)
4. **Include equipment recommendation** in the final summary output

### Dimension Extraction Rules
- Use external/overall dimensions, NOT interior dimensions
- Width and depth are interchangeable for BTU lookup (8x10 = 10x8)
- Always use the SMALLER number first when formatting for BTU table lookup (e.g., 10x12 not 12x10)
- Round dimensions to nearest whole foot for BTU table match
- If exact size not in BTU table, round UP to next larger size

### Combo Box Detection & Handling

**CRITICAL RULE: When the word "Combo" appears in the "Dimensions And Basic Description" field, the quote contains a combination box with multiple compartments.**

#### How to Read a Combo Quote

CCI/LEER combo quotes always follow this structure:

```
[Overall Dimension] [Type1] [Insulation1] [Type2] [Insulation2] Combo [Location]
[Type1] [Compartment1 Dimension], [Type2] [Compartment2 Dimension]
```

**Line 1 — Overall box dimension:** The FIRST dimension listed is the total exterior footprint of the entire combo unit. This is NOT a refrigeration zone.

**Line 2 — Individual compartment dimensions:** Each compartment is listed with its type and its own W x D x H. These ARE the refrigeration zones.

#### Real Example (CC359598)

```
24' x 12' x 8' Freezer (-10°) (5 1/2" WR Polyurethane) Cooler (35°) (4" WR Polyurethane) Combo *INDOOR*
Freezer (-10°) 12' x 12' x 8', Cooler (35°) 12' x 12' x 8'
```

| Dimension | What It Represents | Use for Refrigeration? |
|-----------|-------------------|----------------------|
| 24' x 12' x 8' | Overall combo box footprint | **NO — NEVER** |
| 12' x 12' x 8' Freezer | Individual freezer compartment | **YES** |
| 12' x 12' x 8' Cooler | Individual cooler compartment | **YES** |

#### Possible Compartment Combinations

Combos are NOT limited to freezer+cooler. Any mix is possible:
- Freezer + Cooler (most common)
- Cooler + Cooler (e.g., CC359595: 28'x26' cooler + 8'x26' cooler)
- Freezer + Freezer
- Freezer + Cooler + Cooler
- Any other combination of 2+ compartments

#### Refrigeration Sizing Rule

**ALWAYS use the individual compartment dimensions for refrigeration system selection. NEVER use the overall combo dimension.**

Each compartment gets its own independent refrigeration system:
1. Parse each compartment's type (cooler or freezer) and dimensions (W x D)
2. Size each system independently using the compartment dimensions
3. Cooler compartments → ADR evaporators (air defrost)
4. Freezer compartments → LED evaporators (electric defrost)
5. Present each system separately, then show combined total

#### Validation Note
When validating a combo box, the overall dimension should equal the sum of compartment dimensions along the split axis. For example: 24' overall = 12' freezer + 12' cooler along the 24' side.

## Workflow Process

### Step 1: Receive Quote
User provides CCI/Carroll/LEER quote PDF and optionally original request details.

### Step 2: Extract Data
Run `execution/extract_quote_data.py` to pull structured data from PDF.

### Step 3: Validate (if request provided)
Check dimensions (allow W/D swap), doors, type, location against original request.

### Step 4: Calculate Customer Pricing
Run `execution/calculate_pricing.py` for base pricing and each option separately.

### Step 5: Check for ALL DDS Items
Detect GD# display doors, OO# windows (buck openings), and pass-thru doors. Invoke `dds-agent` skill with all detected DDS items for pricing. Count total DDS pieces to determine 10% upcharge eligibility.

### Step 6: Select Refrigeration Equipment
Invoke `refrigeration-system-engineer` skill with box dimensions and type.
- Extract W x D from quote dimensions
- Pass box type (cooler/freezer)
- RSE returns: condensing unit, evaporator(s), BTU capacity, vendor cost, customer price
- Include in final summary

### Step 7: Store Data
Run `execution/csv_handler.py` to append record to CSV.

### Step 8: Generate Summary
Present formatted report with validation results, customer pricing, DDS door summary, refrigeration equipment recommendation, and storage confirmation.

## Output Format Template

```markdown
# CCI/LEER Quote Analysis
**Tag #**: CC359210 | **Date**: 01/23/2026

## Quote Validation
- Dimensions: 12' x 10' x 8' Freezer
- Door Qty: 1 door (34" x 76.25")
- Installation: Indoor
- Type: Freezer (-10)
- [Any flags or discrepancies]

## Customer Pricing

**VENDOR COST:**
Walk-In Box:      $10,488.00
Freight:          $ 2,081.00
                  -----------
Vendor Cost:      $12,569.00

**>>> CUSTOMER PRICE (1.25x):  $15,700.00 <<<**

**OPTIONAL ADD-ONS** (priced separately):
- White Interior Finish
  Vendor Cost:    $550.00
  **Customer Price (1.25x): $700.00**

## Display Doors
None identified in this quote.
[OR]
- GD1: (6) 30"x79" DDS 1200 doors
- GD2: (3) 36"x81" DDS 1300 doors
  -> DDS agent invoked for door pricing

## Refrigeration Equipment
Box Dimensions (External): 12' x 10'
Required BTU: 10,600
Recommended System - Turbo Air:
  Condensing Unit: TS015MR404A2A (1.5 HP)
  Evaporator: ADR125AENC x 1
  System Capacity: 13,981 BTU
  Vendor Cost: $4,144
  **Customer Price (1.25x): $5,180**

## Data Storage
- Record saved to cci_quotes_data.csv
- Total records: [count]
```

## Error Handling

### Missing Data
If critical field missing, flag clearly and ask user for missing information.

### Dimension Mismatch
```
DIMENSION MISMATCH DETECTED
-------------------------------
Requested:  12' x 8' x 8'
Quote:      15' x 8' x 8'
Issue:      Width differs (not just swapped)
Action:     Please review with CCI/LEER
```

### Quote Expired
If Good Thru date < current date, warn that quote may need renewal.

### Escalation Criteria
Flag for human review when:
- Dimension mismatch (not just W/D swap)
- Door quantity/size mismatch
- Indoor/Outdoor mismatch
- Missing critical pricing data
- Quote expired
- Unusual box configurations

## Important Notes

### Combo Box Rule (CRITICAL)
When "Combo" appears in "Dimensions And Basic Description," the first dimension is the **overall box footprint** — NOT a refrigeration zone. Only the **individual compartment dimensions** (listed on the following line) are used for refrigeration sizing. See **Task 5 → Combo Box Detection & Handling** for full details and examples.

### Dimension Flexibility
Width and depth are interchangeable because walk-in panels are modular. Only flag if dimensions differ beyond simple swap.

### Pricing vs DDS
CCI pricing formula differs from DDS:
- **CCI**: Vendor Cost = (Walk-In + Freight) combined THEN x1.25 -> round to $50
- **DDS**: Vendor Cost for doors x1.25 -> round to $50 AND Vendor Cost for freight x1.25 -> round to $50 (separate)
- **DDS Freight Default: ALWAYS $250/piece × total quantity** unless user provides an exact freight amount. Never use any other per-piece estimate.

### Standard Pricing Terminology (ALL Vendors)
Always use these two labels consistently:
- **Vendor Cost** = what we pay the vendor (CCI, AK, DDS, or Turbo Air)
- **Customer Price (1.25x)** = what we charge the customer (vendor cost × 1.25, rounded to $50)

### CSV Data Purpose
Data used for: historical quote analysis, cost optimization, regional freight patterns, size vs cost efficiency, seasonal pricing trends.

### Contact Information
- **CCI/Carroll/LEER**: 800-764-6834
- **Location**: 19705 US Highway 30 W, Carroll, IA 51401-0671
- **Website**: https://leerinc.com/

## Resources

### execution/
- `calculate_pricing.py` - CCI markup calculator with base + options pricing
- `extract_quote_data.py` - PDF text extraction for CCI/LEER quotes
- `csv_handler.py` - CSV append, read, and validation operations

### references/
- `csv_fields.md` - Complete CSV field definitions and format specification

Load these files as needed using the view tool when detailed information is required.
