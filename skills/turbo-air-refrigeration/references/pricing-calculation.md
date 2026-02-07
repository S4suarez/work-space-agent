# Turbo Air Pricing Calculations

## Standard Pricing Formula

### Complete System Cost

```
Total System Cost = Condensing Unit Total + (Evaporator Cost × Quantity)

Where:
  Condensing Unit Total = Base Price + Warranty Cost
  Evaporator Cost = Unit price from OEM list
  Quantity = Number of evaporator coils (1, 2, or 3)
```

## OEM Price List Format

### Condensing Units
Located in rows ~178-234 of OEM Excel file

**Columns:**
- Column A (0): Model Number
- Column B (1): Base Price
- Column I (8): Warranty Cost

**Example from price list:**
```
Model: TS020MR404A2A
Base Price (Col B): $2,470
Warranty (Col I): $319
Total: $2,789
```

### Evaporators
Located in rows ~9-82 of OEM Excel file

**Columns:**
- Column A (0): Model Number
- Column B (1): Price

**Example from price list:**
```
Model: LED114BENC
Price (Col B): $2,051
```

## Calculation Examples

### Example 1: Single Evaporator System

**Configuration:**
- Box Type: Cooler
- Condensing Unit: TS020MR404A2A (2 HP)
- Evaporator: LED114BENC × 1

**Calculation:**
```
Condensing Unit:
  Base: $2,470
  Warranty: $319
  Total: $2,789

Evaporator:
  Price: $2,051
  Qty: 1
  Total: $2,051

System Total: $2,789 + $2,051 = $4,840
```

### Example 2: Dual Evaporator System

**Configuration:**
- Box Type: Cooler
- Condensing Unit: TS050MR404A2A (5 HP)
- Evaporator: ADR171AENC × 2

**Calculation:**
```
Condensing Unit:
  Base: $3,279
  Warranty: $388
  Total: $3,667

Evaporator:
  Price: $1,840
  Qty: 2
  Total: $3,680

System Total: $3,667 + $3,680 = $7,347
```

### Example 3: Triple Evaporator System

**Configuration:**
- Box Type: Cooler
- Condensing Unit: TS100MR404A3 (10 HP)
- Evaporator: ADR352AENC × 3

**Calculation:**
```
Condensing Unit:
  Base: $9,525
  Warranty: $885
  Total: $10,410

Evaporator:
  Price: $2,800
  Qty: 3
  Total: $8,400

System Total: $10,410 + $8,400 = $18,810
```

## Historical Pricing Comparison

### January 2026 vs Previous Pricing

**Average Changes by System Type:**
```
Cooler Systems:
  Previous Average: $5,000
  New Average: $5,697
  Change: +13.9%

Freezer Systems:
  Previous Average: $5,329
  New Average: $6,161
  Change: +15.6%

Overall:
  Previous Average: $5,810
  New Average: $6,621
  Change: +14.0%
```

### Price Increases by Horsepower Range

**Small Systems (0.5 - 1.5 HP):**
- Typical Increase: 10-11%
- Range: $322 - $415

**Medium Systems (2 - 5 HP):**
- Typical Increase: 10-12%
- Range: $421 - $620

**Large Systems (6 - 10 HP):**
- Typical Increase: 13-16%
- Range: $1,169 - $2,295

## Cost Breakdown Analysis

### Component Cost Percentages

**Typical 2 HP Cooler System:**
```
Total System: $4,840
  
Condensing Unit: $2,789 (57.6%)
  Base: $2,470 (51.0%)
  Warranty: $319 (6.6%)
  
Evaporator: $2,051 (42.4%)
```

**Typical 5 HP Cooler with Dual Evaporators:**
```
Total System: $7,347

Condensing Unit: $3,667 (49.9%)
  Base: $3,279 (44.6%)
  Warranty: $388 (5.3%)
  
Evaporators: $3,680 (50.1%)
  Unit Price: $1,840
  Quantity: 2
```

### Observations

1. **Warranty costs:** Range from 5-10% of total system cost
2. **Multi-evaporator systems:** Evaporator costs can exceed condensing unit costs
3. **Larger systems:** Higher percentage in condensing unit (more expensive compressors)
4. **Small systems:** More balanced split between components

## Pricing Update Workflow

### When OEM Releases New Pricing

1. **Load OEM Excel File**
   - Typically named like `_0101BU2026.xlsx` (effective date format)
   - Verify sheet name is 'NEW MODELS'

2. **Extract Condensing Unit Prices**
   ```python
   condensing_df = pd.read_excel(
       file, 
       skiprows=178, 
       nrows=57, 
       usecols=[0, 1, 8]
   )
   condensing_df['total_cost'] = base + warranty
   ```

3. **Extract Evaporator Prices**
   ```python
   evap_df = pd.read_excel(
       file,
       skiprows=9,
       nrows=74,
       usecols=[0, 1]
   )
   ```

4. **Calculate System Prices**
   ```python
   for system in all_systems:
       condensing_cost = lookup_condensing(system.model)
       evap_cost = lookup_evaporator(system.evap_model)
       system.total_cost = condensing_cost + (evap_cost * system.qty)
   ```

5. **Validate Results**
   - Spot check 5-10 calculations manually
   - Verify price increases are reasonable (typically 5-20%)
   - Check for any systems with missing pricing

6. **Export Updated Data**
   - Main CSV/Excel files
   - Pricing change report
   - Update summary document

## Common Pricing Issues

### Issue 1: Model Not Found in OEM List

**Cause:** Model number mismatch between database and OEM list

**Solutions:**
- Check for "-T" suffix (remove if present)
- Check for missing "A" suffix (add if it's a scroll model)
- Verify horsepower matches (1.5 HP = 015, not 15)

### Issue 2: Evaporator Shows as "LED" or "PENDING"

**Cause:** Incomplete specifications in database

**Solution:**
- Contact Turbo Air for complete model number
- Typically occurs on 7.5 HP and 10 HP systems
- Cannot calculate pricing without complete evaporator model

### Issue 3: Unusual Price Increase (>25%)

**Cause:** Possible model number change or data entry error

**Solution:**
- Verify model number is correct
- Check if model was upgraded (different generation)
- Compare with similar HP systems
- Spot check against OEM list manually

### Issue 4: Missing Warranty Cost

**Cause:** Column I empty in OEM list

**Solution:**
- Check neighboring models for typical warranty cost
- Contact Turbo Air if pattern unclear
- Use average warranty percentage (~6-7% of base price) as estimate

## Quality Assurance Checks

After any pricing update:

1. **Range Check:** Verify min/max prices are reasonable
2. **Change Distribution:** Review histogram of price changes
3. **Outlier Detection:** Flag any changes >20% for manual review
4. **Missing Data:** Identify any systems without updated pricing
5. **Calculation Audit:** Manually verify 10 random systems
6. **Historical Comparison:** Compare trends with previous updates
