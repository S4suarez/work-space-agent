---
name: ak-agent
description: >
  Customer service agent for AmeriKooler (AK) walk-in refrigeration boxes.
  Handles quote validation, pricing calculations, data extraction, and CSV documentation.
  Use this skill when the user needs: quote validation against customer requests,
  customer pricing with 1.25x markup, PDF data extraction from AmeriKooler quotes,
  or walk-in box cost analysis. Triggers include "AmeriKooler quote", "AK quote",
  "amerikooler", "walk-in cooler", "walk-in freezer", "walk-in box", "check this quote",
  "validate quote", "analyze quote", "price this box", "customer pricing", or any
  reference to walk-in refrigeration equipment from AmeriKooler/AK.
---

# AK (AmeriKooler) Quote Agent

Customer service agent for AmeriKooler walk-in refrigeration boxes. Handles quote validation, pricing calculations, PDF data extraction, and CSV data documentation.

**Vendor:** AmeriKooler (AK)
**Location:** 575 East 10th Ave, Miami, Florida 33010 USA
**Phone:** 1-800-627-KOOL (1-800-627-5665)
**Website:** www.amerikooler.com

## Core Capabilities

1. **Quote Validation** - Verify quotes against customer requests (dimensions, doors, type, location)
2. **Pricing Calculator** - Calculate customer pricing with 1.25x markup and $50 rounding
3. **Data Extraction & CSV Storage** - Extract quote data from PDFs and store in CSV
4. **DDS Door Detection** - Detect "Glass Doors By Others" and invoke `dds-agent` skill

## AK Quote Structure (How to Read)

AK quotes follow a consistent format. Key fields and where to find them:

```
Page 1:
  Quote #: XX-XXXXX (top right header, e.g., 26-02170)
  Date: MM/DD/YYYY (top right header)
  Buyer: Bush Refrigeration
  Project Name: [Customer job / AB number]
  Walk-in: [short description, e.g., "outdoor clr", "indoor display cooler"]
  Actual Overall Dimension: W x D x H (outside dimensions)
  Description: [Indoor/Outdoor] [Cooler/Freezer], [Floorless/with floor]
  Interior Dim: W x D x H (w x l x h)
  Temperature: 35F cooler / -10F freezer
  Finishes: 26 Ga. Stucco Embossed Acrylume (standard)
  Floor: NSF vinyl screed / Aluminum perimeter angles / etc.
  Door: (qty) Standard/Non-Standard WxH [Left/Right] hinged flush door

Page 2:
  Equipment: Refrigeration Supplied By Others (always)
  Accessories: [rain roof, drain hoods, floor screeds, perimeter angles, PRV, etc.]
  Freight: [destination info]
  Price: $XX,XXX.00 Net  ← THIS IS THE SINGLE TOTAL PRICE (box + freight + accessories)

  ** "Glass Doors By Others" ** ← DDS TRIGGER (if present)

Page 3:
  Engineering drawings (top view + front/side view)
  Panel layout with dimensions and panel IDs (N1S, N2, N3, etc.)
  Door placement and size
  ** Net Opening dimensions ** (if display doors, e.g., "Net Opening 123.125" x 75"")
  ** Cutout annotations ** (e.g., "(5) 30x79 display doors")
```

### CRITICAL: AK Price is ONE Number
AK does NOT separate box cost and freight cost. The "Price: $XX,XXX.00 Net" on page 2 is the grand total including:
- Walk-in box panels
- Freight/delivery
- All listed accessories

Use this single price for markup calculations.

## Task 1: Quote Validation (Analytical Checker)

Verify AK quotes against customer requests.

**User provides:**
- PDF quote from AmeriKooler
- Original request details (optional but helpful)

### Validation Rules

**Dimensions:**
- **FLEXIBLE**: Width and depth are interchangeable (10x8x8 = 8x10x8)
- **CRITICAL**: Height must match exactly
- **FLAG**: If dimensions differ beyond width/depth swap
- **NOTE**: AK provides both "Actual Overall Dimension" (outside) and "Interior Dim" (inside). Use overall dimensions for validation against customer requests.

**Doors:**
- Verify door quantity matches request
- Verify door sizes (width x height) match request
- DO NOT check swing direction (left/right hand hinge)

**Temperature Type:**
- Verify cooler vs. freezer designation
- Cooler = 35F, Freezer = -10F (standard)
- DO NOT verify specific temperature specs

**Installation:**
- ALWAYS verify indoor vs. outdoor installation type

### Validation Checklist
```
[ ] Dimensions (WxDxH) - allow width/depth swap
[ ] Box type (Cooler/Freezer)
[ ] Door quantity and sizes
[ ] Installation location (Indoor/Outdoor)
[ ] Floor type specified
[ ] Accessories listed
[ ] Price present
```

## Task 2: Pricing Calculator

Calculate customer pricing from AK quote net price.

**CRITICAL PRICING RULES:**
1. **AK has ONE price** - no separate Walk-In and Freight
2. **Net Price x 1.25** = raw customer price
3. **Round to nearest $50** = final customer quote
4. **Accessories are INCLUDED** in the net price (never priced separately)

### Pricing Formula

```
AK PRICING (Single Price):
Vendor Cost x 1.25 = raw price
Round to nearest $50 = Customer Price

Rounding Examples:
$13,122.50 -> $13,100
$13,138.00 -> $13,150
$13,162.00 -> $13,150
$13,188.00 -> $13,200
```

### Output Format

```
VENDOR COST:
-------------------------------
Vendor Cost:           $XX,XXX.00

>>> CUSTOMER PRICE (1.25x):  $XX,XXX.00 <<<
```

**Run pricing calculation:**
```bash
python execution/calculate_pricing.py --net-price <price>
```

## Task 3: Data Extraction & CSV Storage

Extract structured data from AK quote PDFs and store in CSV.

**CSV Location:** `C:/Users/bnmsu/ak_quotes_data.csv`

### CSV Fields
```csv
PDF_Filename,AK Vendor Extract,Quote #,SHIP TO ZIP,State,Customer Job,Dimensions and Basic Description,Floor(s),Doors,Net Price,Quote Date,Good Thru,Type,Display Doors,Pass Thru Doors,Shape,Location,Combo,Accessories,Revision,Lead Time
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
python execution/csv_handler.py --action append --data '{"Quote_Number":"26-02170","net_price":"10498.00",...}'
```

### Data Rules
- **Unique Identifier**: Quote # + Quote Date as composite key
- **Append Mode**: Always append, never overwrite
- **Validation**: All numeric fields properly formatted before write

## Task 4: DDS Item Detection & Auto-Invoke

Detect "Glass Doors By Others" in AK quotes and handle DDS door pricing.

**Key context:** AmeriKooler only supplies walk-in panels and standard access doors. Display glass doors, windows, and pass-thru doors are ALWAYS "By Others" - which means DDS supplies them. The phrase **"Glass Doors By Others"** on page 2 is the DDS trigger.

### Detection Process

1. **Detect** the phrase "Glass Doors By Others" in the quote text
2. **Check drawings** (page 3) for:
   - Net opening dimensions (e.g., "Net Opening 123.125" x 75"")
   - Cutout annotations with door qty/size (e.g., "(5) 30x79 display doors")
   - Panel layout cutouts that indicate display door positions
3. **Determine door type from box type:**
   - Cooler quote = **HH** (High Humidity) doors
   - Freezer quote = **LT** (Low Temp) doors
4. **If door qty/size is clear** from the drawing or user request, invoke `dds-agent` skill
5. **If door qty/size is NOT clear**, ask the user for:
   - Number of display doors
   - Door size (e.g., 30x79)
   - Door type (if not determinable from cooler/freezer)
   - Any windows or pass-thru doors needed
6. **Count total DDS pieces** (display doors + windows + pass-thru) for 10% upcharge eligibility
7. **Invoke** the `dds-agent` skill with ALL extracted DDS item details
8. **DDS Freight default: $250/piece × total quantity** (unless user provides exact freight). NEVER use any other estimate — always $250/piece.

### DDS Piece Count Rule
- If total DDS pieces (all types combined) = 1 or 2, DDS agent applies 10% upcharge
- 3 or more pieces = NO upcharge
- This count includes: display doors, windows, and pass-thru doors

### Document in CSV
**Display Doors field:**
- `None` if no display doors
- `Glass Doors By Others - (5) 30"x79" HH` format if present
- Include net opening dimensions if available

## Task 5: Refrigeration Equipment Auto-Selection

Automatically select and price the refrigeration system for the quoted walk-in box.

**Key context:** AK quotes always state "Refrigeration Supplied By Others" on page 2. This means every AK box needs a refrigeration system. After validating the box and calculating pricing, automatically invoke the `refrigeration-system-engineer` skill to recommend equipment.

### Auto-Selection Process

1. **Extract external dimensions** from the quote's "Actual Overall Dimension" field
   - Format: W x D x H (e.g., "6'-0" x 20'-0" x 7'-6"")
   - Use W x D only (drop height) for BTU lookup
   - Convert to feet as whole numbers (e.g., 6 x 20)
2. **Determine box type** from the quote (Cooler = 35F, Freezer = -10F)
3. **Invoke `refrigeration-system-engineer` skill** with:
   - Box type (cooler or freezer)
   - External dimensions (W x D in feet)
   - The RSE will look up BTU requirements, select appropriate Turbo Air equipment, and calculate customer pricing (1.25x markup on vendor cost)
4. **Include equipment recommendation** in the final summary output

### Dimension Extraction Rules
- **Single boxes:** Use "Actual Overall Dimension" (external) directly for BTU lookup
- **Combo boxes:** Use "Interior Dim" per compartment + wall thickness conversion (see Combo section below)
- Width and depth are interchangeable for BTU lookup (8x10 = 10x8)
- Always use the SMALLER number first when formatting for BTU table lookup (e.g., 6x20 not 20x6)
- Round dimensions to nearest whole foot for BTU table match
- If exact size not in BTU table, round UP to next larger size

**AK Wall Thickness Conversion (Interior → External):**
- Width & Depth: add 8" total (4" per wall panel × 2 walls)
- Height (floorless): add 4" (ceiling panel only)
- Height (with floor): add 8" (ceiling + floor panels)

### Combo Box Detection & Handling

**CRITICAL RULE: When "combo" appears in the walk-in description AND "Actual Overall Dimension" is present, the quote contains a combination box with multiple compartments.**

#### How to Read an AK Combo Quote

AK combo quotes always follow this structure:

```
Two Compartment Walk-in: Indoor combo
Actual Overall Dimension: W x D x H (Rectangular)

Compartment 1 of N - Indoor [Freezer/Cooler], [with Floor / Floorless]
Interior Dim: W x D x H
Temperature: -10°F or 35°F
Equipment: Refrigeration Supplied By Others
           Recommended minimum duty XXXXX Btu/hr at 95°F ambient

Compartment 2 of N - Indoor [Freezer/Cooler], [with Floor / Floorless]
Interior Dim: W x D x H
Temperature: -10°F or 35°F
Equipment: Refrigeration Supplied By Others
           Recommended minimum duty XXXXX Btu/hr at 95°F ambient
```

**"Actual Overall Dimension"** = the total exterior footprint of the entire combo unit. This is NOT a refrigeration zone.

**"Compartment X of Y"** = individual sections. Each has its own interior dimensions, temperature, and recommended BTU. These ARE the refrigeration zones.

#### Real Example (Quote 26-01360)

```
Two Compartment Walk-in: Indoor combo
Actual Overall Dimension: 16'-0" x 32'-0" x 8'-0" (Rectangular)

Compartment 1 of 2 - Indoor Freezer, with Floor
Interior Dim: 15'-4" x 15'-6" x 7'-4"
Recommended minimum duty 13570 Btu/hr at 95°F ambient

Compartment 2 of 2 - Indoor Cooler, Floorless
Interior Dim: 15'-4" x 15'-6" x 7'-8"
Recommended minimum duty 14157 Btu/hr at 95°F ambient
```

| Dimension | What It Represents | Use for Refrigeration? |
|-----------|-------------------|----------------------|
| 16' x 32' x 8' | Overall combo box footprint | **NO — NEVER** |
| Compartment 1 (Freezer) | Individual freezer section | **YES — use AK's recommended BTU** |
| Compartment 2 (Cooler) | Individual cooler section | **YES — use AK's recommended BTU** |

#### AK Provides Recommended BTU (Key Difference from CCI)

AK quotes include **"Recommended minimum duty XXXXX Btu/hr"** per compartment. This is the manufacturer's calculated BTU requirement.

**Use AK's recommended BTU as the required BTU** when invoking the refrigeration-system-engineer skill. This overrides the standard BTU table lookup (treated as USER_PROVIDED BTU in RSE logic). AK has already factored in wall thickness, insulation, and temperature differential.

#### Deriving External Compartment Dimensions

AK provides **"Actual Overall Dimension"** (exterior) for the whole box and **"Interior Dim"** per compartment. To get external dimensions for each compartment, use the wall thickness conversion:

**Wall thickness rule (4" per wall panel):**
- **Width:** Interior + 8" (4" left wall + 4" right wall)
- **Length/Depth:** Interior + 8" (4" front wall + 4" back wall)
- **Height (floorless):** Interior + 4" (ceiling panel only)
- **Height (with floor):** Interior + 8" (ceiling panel + floor panel)

**Example (Quote 26-01360, Compartment 1 — Freezer with Floor):**
```
Interior Dim: 15'-4" x 15'-6" x 7'-4"
Width:  15'4" + 8" = 16'0"  (16')
Depth:  15'6" + 8" = 16'2"  (~16')
Height: 7'4"  + 8" = 8'0"   (8') ← with floor, so +8"
External: 16' x 16' x 8'
```

**Example (Quote 26-01360, Compartment 2 — Cooler, Floorless):**
```
Interior Dim: 15'-4" x 15'-6" x 7'-8"
Width:  15'4" + 8" = 16'0"  (16')
Depth:  15'6" + 8" = 16'2"  (~16')
Height: 7'8"  + 4" = 8'0"   (8') ← floorless, so +4"
External: 16' x 16' x 8'
```

**Use these derived external dimensions** (W x D, drop height) for BTU table lookup when AK does not provide a recommended BTU. When AK does provide recommended BTU, use that value instead (it takes priority).

#### Possible Compartment Combinations

Combos are NOT limited to freezer+cooler. Any mix is possible:
- Freezer + Cooler (most common)
- Cooler + Cooler
- Freezer + Freezer
- 3+ compartments (e.g., "Three Compartment Walk-in")

#### Refrigeration Sizing Rule

**ALWAYS use the individual compartment BTU recommendations for refrigeration system selection. NEVER size off the overall combo dimension.**

Each compartment gets its own independent refrigeration system:
1. Read each compartment's type (cooler or freezer) and AK-recommended BTU
2. Invoke RSE with the AK-recommended BTU as user-provided BTU
3. Cooler compartments → ADR evaporators (air defrost)
4. Freezer compartments → LED evaporators (electric defrost)
5. Present each system separately, then show combined total

## Workflow Process

### Step 1: Receive Quote
User provides AmeriKooler quote PDF and optionally original request details.

### Step 2: Extract Data
Run `execution/extract_quote_data.py` to pull structured data from PDF.
If PDF extraction fails or is incomplete, read the quote data directly from the provided PDF content.

### Step 3: Validate (if request provided)
Check dimensions (allow W/D swap), doors, type, location against original request.

### Step 4: Calculate Customer Pricing
Run `execution/calculate_pricing.py` with the single net price.

### Step 5: Check for DDS Items
Look for "Glass Doors By Others" text. If found:
- Check drawing for net opening and cutout annotations
- Determine door type (HH for cooler, LT for freezer)
- Get door qty/size from cutout annotations or ask user
- Invoke `dds-agent` skill for door pricing

### Step 6: Select Refrigeration Equipment
Invoke `refrigeration-system-engineer` skill with box dimensions and type.
- Extract W x D from "Actual Overall Dimension"
- Pass box type (cooler/freezer)
- RSE returns: condensing unit, evaporator(s), BTU capacity, vendor cost, customer price
- Include in final summary

### Step 7: Store Data
Run `execution/csv_handler.py` to append record to CSV.

### Step 8: Generate Summary
Present formatted report with validation results, customer pricing, DDS door summary, refrigeration equipment recommendation, and storage confirmation.

## Output Format Template

```markdown
# AK (AmeriKooler) Quote Analysis
**Quote #**: 26-02170 | **Date**: 01/23/2026

## Quote Summary
- Project: Big Star AB172969
- Dimensions: 6'-0" x 20'-0" x 7'-6" Outdoor Cooler
- Door: (1) Standard 36" x 76" Left hinged
- Installation: Outdoor
- Type: Cooler (35F)
- Floor: NSF vinyl screed
- [Any flags or discrepancies]

## Customer Pricing

**VENDOR COST:**
Vendor Cost:          $10,498.00

**>>> CUSTOMER PRICE (1.25x):  $13,100.00 <<<**

## Display Doors
None identified in this quote.
[OR]
Glass Doors By Others detected.
- Net Opening: 123.125" x 75"
- Door Details: (5) 30"x79" HH display doors
  -> DDS agent invoked for door pricing

## Refrigeration Equipment
Box Dimensions (External): 6' x 20'
Required BTU: 10,026
Recommended System - Turbo Air:
  Condensing Unit: TS010MR404A2 (1 HP)
  Evaporator: ADR112AENC x 1
  System Capacity: 9,888 BTU
  Vendor Cost: $3,795
  **Customer Price (1.25x): $4,750**

## Data Storage
- Record saved to ak_quotes_data.csv
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
Action:     Please review with AmeriKooler
```

### Quote Expired
AK quotes are valid for 30 days from quote date. If current date is past 30 days from quote date, warn that quote may need renewal.

### Glass Doors Unclear
If "Glass Doors By Others" is detected but door qty/size cannot be determined:
```
GLASS DOORS BY OTHERS DETECTED
-------------------------------
Could not determine door quantity/size from drawing.
Please provide:
  - Number of display doors needed
  - Door size (e.g., 30x79)
  - Any windows or pass-thru doors?
```

### Escalation Criteria
Flag for human review when:
- Dimension mismatch (not just W/D swap)
- Door quantity/size mismatch
- Indoor/Outdoor mismatch
- Missing critical pricing data
- Quote expired
- "Glass Doors By Others" present but details unclear
- Unusual box configurations

## Important Notes

### Combo Box Rule (CRITICAL)
When "combo" appears in the walk-in description, the "Actual Overall Dimension" is the **overall box footprint** — NOT a refrigeration zone. Only the **individual compartment sections** (listed as "Compartment X of Y") are used for refrigeration sizing. AK provides recommended BTU per compartment — use those values directly. See **Task 5 → Combo Box Detection & Handling** for full details and examples.

### Dimension Flexibility
Width and depth are interchangeable because walk-in panels are modular. Only flag if dimensions differ beyond simple swap.

### AK vs CCI Pricing Differences
- **AK**: Single vendor cost (box + freight + accessories combined) -> x1.25 -> round to $50
- **CCI**: (Walk-In + Freight) combined = vendor cost THEN x1.25 -> round to $50, options separate

### AK vs CCI PDF Differences
- AK PDFs are less detailed than CCI
- AK has ONE combined price (no Walk-In/Freight/Options breakdown)
- AK does not provide sq. ft. or box weight
- AK does not have Tag # (uses Quote # format: XX-XXXXX)
- AK quote validity is always "30 days" (no explicit Good Thru date field)
- AK includes engineering drawings on page 3 with panel layout

### DDS Door Type Mapping
- Cooler box (35F) = HH (High Humidity) display doors
- Freezer box (-10F) = LT (Low Temp) display doors

### DDS Freight Default
- **ALWAYS $250/piece × total quantity** unless user provides an exact freight amount
- Never use any other per-piece estimate

### CSV Data Purpose
Data used for: historical quote analysis, cost optimization, vendor comparison (AK vs CCI), regional freight patterns, size vs cost efficiency, seasonal pricing trends.

## Resources

### execution/
- `calculate_pricing.py` - AK markup calculator (single price x 1.25)
- `extract_quote_data.py` - PDF text extraction for AK quotes
- `csv_handler.py` - CSV append, read, and validation operations

### references/
- `csv_fields.md` - Complete CSV field definitions and format specification

Load these files as needed using the view tool when detailed information is required.
