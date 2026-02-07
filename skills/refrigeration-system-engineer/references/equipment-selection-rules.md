# Equipment Selection Rules

## Primary Selection Criteria

### 1. BTU Capacity (Most Critical)

**Rule:** System capacity MUST be ≥ required BTU

```python
if system_btu < required_btu:
    # REJECT - Never select
    continue
```

**Tolerance:**
- Minimum: system_btu ≥ required_btu (0% margin)
- Optimal: system_btu = 1.0 to 1.2 × required_btu (0-20% oversizing)
- Acceptable: system_btu ≤ 1.5 × required_btu (up to 50% oversizing)
- Questionable: system_btu > 1.5 × required_btu (>50% oversizing)

### 2. Evaporator Quantity

**Rule:** Use 2 evaporators if width OR depth exceeds 30 feet

```python
if width > 30 or depth > 30:
    required_evap_qty = 2
else:
    required_evap_qty = 1
```

**Why this matters:**
- Single evaporator can't effectively cool boxes >30ft
- Temperature stratification occurs
- Uneven cooling causes product issues
- Code/health department may require dual coils

**Examples:**
- 8×10 box → 1 evaporator
- 12×20 box → 1 evaporator
- 10×35 box → 2 evaporators (depth >30)
- 32×20 box → 2 evaporators (width >30)

### 3. Evaporator Type

**Coolers use ADR series (Air Defrost):**
- Natural air circulation defrost
- Lower cost
- Adequate for 35-40°F applications
- Models: ADR060AENC, ADR089AENC, ADR112AENC, etc.

**Freezers use LED series (Electric Defrost):**
- Electric heating elements for defrost
- LED lighting included
- Required for 0°F to -10°F applications  
- Models: LED036BENC, LED052BENC, LED072BENC, etc.

**Exception:** 
Rare cases where medium-temp condensing unit paired with low-temp LED coil for special applications. Only select if specifically required by user.

```python
if box_type == 'cooler':
    evaporator_series = 'ADR'
elif box_type == 'freezer':
    evaporator_series = 'LED'
```

### 4. Cost Optimization

Given multiple systems meeting requirements, prefer:
1. Smallest BTU capacity (most efficient)
2. Single evaporator over dual (if box size allows)
3. Lower horsepower (lower operating cost)
4. ADR over LED for coolers (lower equipment cost)

## Selection Algorithm

### Step-by-Step Process

```python
# 1. Filter by box type
candidates = systems[systems['box_type'] == box_type]

# 2. Filter by evaporator series
if box_type == 'cooler':
    candidates = candidates[candidates['evaporator_model'].str.startswith('ADR')]
else:  # freezer
    candidates = candidates[candidates['evaporator_model'].str.startswith('LED')]

# 3. Filter by evaporator quantity
candidates = candidates[candidates['evaporator_qty'] == required_evap_qty]

# 4. Filter by BTU capacity (NEVER go under)
candidates = candidates[candidates['btu_rating_448a'] >= required_btu]

# 5. Sort by BTU capacity (smallest first) and cost
candidates = candidates.sort_values(['btu_rating_448a', 'total_system_cost'])

# 6. Select best option
if len(candidates) > 0:
    recommended = candidates.iloc[0]
else:
    # No exact match, may need to consider:
    # - Different evaporator quantity
    # - Next larger system
    # - Consult user
```

## Special Cases

### Case 1: No System Meets Exact Requirements

**Scenario:** Need 2 evaporators but only single-coil systems available

**Solution:**
1. Look for system with 2× single evaporator capacity
2. Note in recommendation: "Using dual single-coil configuration"
3. Calculate cost as: condensing unit + (2 × evaporator cost)

**Example:**
```
Required: 15,000 BTU with 2 evaporators
Available: 10,000 BTU single evaporator system
Solution: Use 2 complete systems? NO
Better: Find system that supports 2 coils or next size up
```

### Case 2: BTU Significantly Oversized

**Scenario:** Smallest available system is 50%+ oversized

**Solution:**
1. Present the oversized option
2. Note the oversizing percentage
3. Explain potential issues (short cycling)
4. Still recommend it (better than undersizing)

**Example:**
```
Required: 6,000 BTU
Smallest available: 9,888 BTU (65% oversizing)
Recommendation: "System is significantly oversized but no smaller option 
                 available. May experience short cycling."
```

### Case 3: Between Two Sizes

**Scenario:** System A is 5% undersized, System B is 40% oversized

**Solution:** ALWAYS choose System B (oversized)
- Undersizing is never acceptable
- 40% oversizing is acceptable
- Note the oversizing in recommendation

### Case 4: Combination Box with Asymmetric Sections

**Scenario:** 12×20 cooler + 6×8 freezer

**Solution:**
1. Calculate each section independently
2. Cooler: 15,082 BTU required
3. Freezer: 6,863 BTU required
4. Select different equipment for each
5. Present as two separate systems

## Horsepower Guidelines

### Typical HP to BTU Relationship

**Coolers (Medium Temp):**
- 0.5 HP ≈ 6,000-7,000 BTU
- 0.75 HP ≈ 8,000-9,500 BTU
- 1 HP ≈ 9,500-10,000 BTU
- 1.5 HP ≈ 13,000-14,000 BTU
- 2 HP ≈ 16,000-17,000 BTU
- 3 HP ≈ 26,000-27,000 BTU
- 4 HP ≈ 34,000-35,000 BTU
- 5 HP ≈ 42,000-43,000 BTU

**Freezers (Low Temp):**
- 1 HP ≈ 4,000-4,500 BTU
- 1.5 HP ≈ 5,500-6,000 BTU
- 2 HP ≈ 6,500-7,000 BTU
- 2.5 HP ≈ 8,000-8,500 BTU
- 3 HP ≈ 9,000-9,500 BTU

**Note:** Freezers require higher HP for same BTU due to lower temperatures.

## Configuration Options

### Single Evaporator Configurations

**Pros:**
- Lower cost
- Simpler installation
- Less maintenance
- Adequate for boxes ≤30ft

**Cons:**
- Won't work for large boxes
- Potential temperature variation in larger boxes

**Typical applications:**
- Small to medium boxes (6×6 to 12×20)
- One dimension ≤30ft

### Dual Evaporator Configurations

**Pros:**
- Better temperature distribution
- Required for boxes >30ft
- More even cooling
- Redundancy (one fails, other helps)

**Cons:**
- Higher cost (~50-80% more for evaporators)
- More complex installation
- Higher maintenance

**Typical applications:**
- Large boxes (one dimension >30ft)
- Very long narrow boxes
- High-value product storage

## Quality Checks

Before finalizing selection, verify:

1. ✓ System BTU ≥ required BTU (NEVER less)
2. ✓ Evaporator type matches box type:
   - Cooler → ADR series
   - Freezer → LED series
3. ✓ Evaporator quantity correct:
   - ≤30ft dimension → 1 coil
   - >30ft dimension → 2 coils
4. ✓ Horsepower reasonable for application
5. ✓ Cost is competitive
6. ✓ All specifications clearly documented

## Common Errors to Avoid

### Error 1: Undersizing
```
❌ WRONG: Required 8,000 BTU, selected 7,500 BTU system
✓ CORRECT: Required 8,000 BTU, selected 9,888 BTU system
```

### Error 2: Wrong Evaporator Type
```
❌ WRONG: Cooler with LED evaporator (freezer coil)
✓ CORRECT: Cooler with ADR evaporator
```

### Error 3: Wrong Evaporator Quantity
```
❌ WRONG: 10×35 box with single evaporator (depth >30)
✓ CORRECT: 10×35 box with dual evaporators
```

### Error 4: Using Internal Dimensions
```
❌ WRONG: Internal 8×10 = 7,758 BTU
✓ CORRECT: External 8×10 = 7,758 BTU
(Internal would actually be smaller, leading to undersizing)
```

### Error 5: Rounding BTU Down
```
❌ WRONG: 8.5×11 rounds to 8×10 (7,758 BTU)
✓ CORRECT: 8.5×11 rounds to 10×12 (9,805 BTU)
```

## Vendor-Specific Notes

### Turbo Air
- Complete line from 0.5 to 10 HP
- Both A2 (single phase) and A3 (three phase) available
- Scroll compressor models have "A" suffix
- Current models use "C" suffix evaporators (digital controller)

### ABCO (Future)
- Will have similar selection criteria
- May have different model numbering
- Compare side-by-side on BTU and cost
- Apply same BTU and configuration rules
