# BTU Calculation Guide

## Standard BTU Requirements

BTU (British Thermal Unit) requirements for walk-in boxes are based on:
- Box type (cooler vs freezer)
- External dimensions (width × depth in feet)
- Standard insulation (4" for coolers, 6" for freezers)
- Typical usage patterns

## BTU Table Explanation

### Cooler BTU Requirements

Coolers maintain 35-40°F and require less BTU per square foot.

**Small coolers (6×6 to 8×8):**
- Range: 5,198 - 6,876 BTU
- Typical: ~900 BTU per square foot

**Medium coolers (8×10 to 10×16):**
- Range: 7,758 - 11,547 BTU  
- Typical: ~900 BTU per square foot

**Large coolers (10×18 to 12×20):**
- Range: 12,475 - 15,082 BTU
- Typical: ~850 BTU per square foot

### Freezer BTU Requirements

Freezers maintain 0°F to -10°F and require ~17% more BTU than equivalent coolers.

**Small freezers (6×6 to 8×8):**
- Range: 6,097 - 7,772 BTU
- ~17% higher than coolers

**Medium freezers (8×10 to 10×16):**
- Range: 8,638 - 12,273 BTU
- ~12-13% higher than coolers

**Large freezers (10×18 to 12×20):**
- Range: 13,155 - 15,554 BTU
- ~10-11% higher than coolers

## Size Matching Rules

### Exact Match
If box dimensions exactly match a table entry (e.g., 8×10), use that BTU value.

### Rounding Up
If dimensions fall between table values:
- Find the next larger size in BOTH dimensions
- Use that BTU value
- Never round down

**Example:**
- Box: 9×11
- Not in table
- Next larger: 10×12 (9,805 BTU for cooler)
- Use 9,805 BTU

### Non-Square Dimensions
Table assumes width × depth order doesn't matter (8×10 = 10×8).

If given 10×8, look up as 8×10.

### Sizes Beyond Table
For boxes larger than 12×20:
- Estimate based on square footage ratio
- Add ~850 BTU per additional square foot for coolers
- Add ~1,000 BTU per additional square foot for freezers
- Recommend consulting engineer for very large boxes

**Example:**
- Box: 14×20 = 280 sq ft
- Largest table: 12×20 = 240 sq ft (15,082 BTU cooler)
- Additional: 40 sq ft × 850 = 34,000 BTU
- Estimated: 15,082 + 34,000 = 49,082 BTU
- Note: This is an estimate; recommend professional load calculation

## Factors NOT in Standard Table

The standard BTU table assumes:
- Normal traffic (door opened 30-40 times/day)
- Standard product load
- Moderate climate
- Proper insulation

**Factors that increase BTU requirements (not in table):**
- High traffic areas (restaurants, busy stores)
- Hot/humid climates
- Poor insulation
- Large door openings
- Frequent restocking
- High product temperature at loading
- Glass doors (add 10-20%)

**When to add safety factor:**
- High-traffic locations: add 15-20%
- Hot climates: add 10-15%
- Glass doors: add 10-20%
- Combination of factors: add 20-30%

For this skill, **use standard table values only** unless user specifies special conditions.

## Sizing Philosophy

### Always Meet or Exceed
- System capacity must be ≥ required BTU
- Never select undersized equipment
- Slight oversizing (10-20%) is acceptable

### Consequences of Undersizing
- Compressor runs continuously
- Cannot maintain temperature
- Shortened equipment life
- Product spoilage
- Energy waste

### Consequences of Oversizing
- Short cycling (bad for compressor)
- Higher initial cost
- Inconsistent temperatures
- Usually prefer 0-20% oversizing maximum

### Optimal Sizing
Target: System capacity 100-120% of required BTU

**Example:**
- Required: 8,000 BTU
- Optimal: 8,000 - 9,600 BTU
- Acceptable: 8,000 - 10,000 BTU
- Avoid: < 8,000 BTU (too small) or > 12,000 BTU (too large)

## BTU vs Tonnage

Refrigeration often specified in "tons":
- 1 ton = 12,000 BTU/hr
- 0.5 ton = 6,000 BTU
- 1.5 ton = 18,000 BTU

**Small systems (< 1 ton):**
- 0.5 HP ≈ 0.5 ton ≈ 6,000 BTU
- 0.75 HP ≈ 0.75 ton ≈ 9,000 BTU
- 1 HP ≈ 0.8 ton ≈ 10,000 BTU

**Medium systems (1-2 tons):**
- 1.5 HP ≈ 1.2 tons ≈ 14,000 BTU
- 2 HP ≈ 1.4 tons ≈ 16,500 BTU
- 2.5 HP ≈ 1.5 tons ≈ 18,000 BTU

## External vs Internal Dimensions

### CRITICAL: Always Use External Dimensions

**Why external dimensions:**
- Consistency across calculations
- Accounts for wall thickness (insulation)
- Standard BTU table is calibrated for external
- Matches how boxes are specified in construction

**Internal vs External:**
- Typical wall: 4-6 inches thick
- External 8×10 ≈ Internal 7.33×9.33
- BTU difference: Significant (~10-15%)

**Example:**
- Box external: 8×10
- Box internal: ~7.33×9.33 (assuming 4" walls)
- Using external 8×10: 7,758 BTU (cooler) ✓ CORRECT
- Using internal 7.33×9.33: Would undersize by ~12%

### If Only Internal Given
**DO NOT PROCEED** - Ask for external dimensions.

If user insists on using internal:
```
Internal dimensions of 8×10 suggest external of ~8.66×10.66
Round up to 10×12 for safety: 9,805 BTU
Note: This is conservative estimate. Please confirm external dimensions.
```

## Verification Examples

### Example 1: Standard Cooler
```
Box: 8×10 cooler (external)
Lookup: 8×10 cooler = 7,758 BTU
Selected system: 9,888 BTU
Margin: 27% over requirement ✓ GOOD
```

### Example 2: In-Between Size
```
Box: 9×11 cooler (external)
Not in table
Next larger: 10×12 = 9,805 BTU
Selected system: 9,888 BTU  
Margin: 1% over requirement ✓ ACCEPTABLE (very tight, but meets)
```

### Example 3: Large Freezer
```
Box: 12×18 freezer (external)
Lookup: 12×18 freezer = 14,571 BTU
Selected system: 16,245 BTU
Margin: 11% over requirement ✓ GOOD
```

### Example 4: Oversized
```
Box: 6×8 cooler (external)
Lookup: 6×8 cooler = 5,955 BTU
Selected system: 9,888 BTU
Margin: 66% over requirement ⚠️ OVERSIZED
Note: May be acceptable if no smaller system available
Check for better match
```
