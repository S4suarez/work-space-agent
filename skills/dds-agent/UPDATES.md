# DDS Agent Updates

## Recent Changes (2026-02-01)

### Pricing Calculator Enhancements

**1. Freight Cost Integration**
- Agent now asks for freight cost at the beginning of EVERY pricing request
- Options: Exact freight cost OR estimated ($250 × quantity)
- If user doesn't provide exact cost, defaults to estimated

**2. Markup Application**
- 1.25× markup applied to BOTH door cost AND freight cost
- Each is calculated and marked up separately

**3. Rounding to Nearest $50**
- Door cost (after markup) rounded to nearest $50
- Freight cost (after markup) rounded to nearest $50
- Provides clean customer quotes

**4. Itemized Customer Quote Format**
```
DDS Doors Cost: $X,XXX.00
DDS Freight:    $XXX.00
--------------------------------------------------
Total:          $X,XXX.00
```

### New Execution Script

**File:** `execution/calculate_pricing.py`

**Usage:**
```bash
python calculate_pricing.py --base-cost 1001.08 --quantity 2 --freight 500
```

**Parameters:**
- `--base-cost`: Base cost per door/window before markup
- `--quantity`: Total number of doors/windows
- `--freight`: Freight cost (exact or estimated)
- `--json`: Optional flag to output as JSON

**Example Output:**
```
DDS CUSTOMER QUOTE
DDS Doors Cost: $2,500.00
DDS Freight:    $600.00
Total:          $3,100.00
```

### Updated Workflow

1. User requests pricing
2. Agent asks: "Do you have an exact freight cost, or should I estimate?"
3. Agent calculates base cost from pricing.md
4. Agent applies 10% upcharge if needed (1-2 door orders)
5. Agent runs pricing calculator script
6. Agent provides itemized customer quote

### Files Modified

- `skill.md` - Updated Task 3 (Door Pricing) section
- `execution/calculate_pricing.py` - New pricing calculator script (created)
- `UPDATES.md` - This file (created)
