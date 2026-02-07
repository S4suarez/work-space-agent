---
name: turbo-air-refrigeration
description: Complete data management system for Turbo Air commercial refrigeration specifications and pricing. Use this skill when users need to manage, update, or query Turbo Air refrigeration system data, including condensing units, evaporators, pricing updates from OEM price lists, model number corrections, system configuration lookups, pricing calculations, or generating quotes. Triggers include "Turbo Air", "TA pricing", "refrigeration systems", "condensing unit", "evaporator", "OEM price list", "update pricing", or any refrigeration equipment data management tasks.
license: Proprietary - Internal Use Only
---

# Turbo Air Refrigeration Data Management

Complete system for managing Turbo Air commercial refrigeration equipment specifications, pricing, and configurations.

## Overview

This skill provides tools and workflows for managing a database of 88+ Turbo Air refrigeration system configurations, including:
- Cooler systems (0.5 - 10 HP)
- Freezer systems (1 - 10 HP)  
- Multiple evaporator configurations per system
- Pricing calculations including warranty costs
- Model number updates for regulatory compliance

## Quick Start

Load the current data:
```python
from TA_refrigeration_data_manager import TurboAirDataManager
manager = TurboAirDataManager()
manager.df = pd.read_csv('Turbo_Air_Refrigeration_Systems.csv')
```

## Core Workflows

### 1. Update Pricing from OEM Price List

When Turbo Air releases new pricing (typically quarterly):

**Trigger phrases:** "update Turbo Air pricing", "new OEM price list", "pricing changes"

**Process:**
1. Load OEM Excel file (format: `_0101BU2026.xlsx`)
2. Extract condensing unit pricing: Base Price (Col B) + Warranty (Col I)
3. Extract evaporator pricing: Price (Col B)
4. Calculate: `Total Cost = Condensing Total + (Evaporator × Qty)`
5. Update model numbers if OEM list shows changes
6. Export updated files and change report

**Script:** Use `scripts/update_pricing_from_oem.py` as template

**Important:** Always create backup before pricing updates.

### 2. Update Model Numbers

When regulatory changes or product updates require model number changes:

**Trigger phrases:** "update model numbers", "new refrigerant", "A suffix", "remove timer"

**Common updates:**
- Scroll compressor designation: Add "A" suffix (e.g., `TS015MR404A2` → `TS015MR404A2A`)
- Timer removal: Remove "-T" suffix (e.g., `TS020MR404A2-T` → `TS020MR404A2`)
- Evaporator suffix changes: M/X → C (e.g., `LED052BENM` → `LED052BENC`)

**Usage:**
```python
manager.update_model_numbers(
    old_model='TS015MR404A2',
    new_model='TS015MR404A2A',
    model_type='condensing'
)
```

### 3. Query Systems

Filter and retrieve system configurations:

```python
# By horsepower and type
systems = manager.get_systems_by_capacity(min_hp=2, max_hp=5, box_type='cooler')

# By specific criteria
freezers_2hp = manager.filter_systems(box_type='freezer', horsepower=2)

# By evaporator quantity
dual_evap = manager.filter_systems(evaporator_qty=2)
```

### 4. Generate Reports

Export data for different teams:

```python
# Sales team - cooler pricing
coolers = manager.filter_systems(box_type='cooler')
coolers.to_excel('cooler_pricing_salesteam.xlsx', index=False)

# Service team - all freezer specs
freezers = manager.filter_systems(box_type='freezer')
freezers.to_excel('freezer_specs_service.xlsx', index=False)
```

## Data Structure

### Key Fields

**System Identification:**
- `system_id`: Unique identifier (auto-generated)
- `box_type`: 'cooler' or 'freezer'
- `brand`: Always 'Turbo Air'

**Equipment:**
- `condensing_unit_model`: Model number (e.g., TS020MR404A2A)
- `horsepower`: Motor HP (0.5 to 10)
- `evaporator_model`: Evaporator coil model (ADR or LED series)
- `evaporator_qty`: Number of coils (1, 2, or 3)
- `btu_rating_448a`: Cooling capacity in BTU/hr

**Pricing:**
- `total_system_cost`: Complete system price (condensing + evaporators)
- `price_update_date`: Last pricing update
- `model_update_date`: Last model number change

### Model Nomenclature

See `references/model-nomenclature.md` for complete guide.

**Condensing Units:**
- `TS###MR404A#[A]` - Coolers (Medium temp)
- `TS###XR404A#[A]` - Freezers (Low temp)

**Evaporators:**
- `ADR###AEN[C/M/X]` - Standard air defrost coils
- `LED###BEN[C/M/X]` - LED-lit electric defrost coils

## Pricing Calculations

Always use OEM list formula:
```
Condensing Unit Total = Base Price + Warranty Cost
Total System = Condensing Total + (Evaporator × Quantity)
```

See `references/pricing-calculation.md` for detailed examples.

## Best Practices

1. **Always backup before updates:** Use built-in backup functionality
2. **Verify OEM list format:** Column positions may change
3. **Check model number mappings:** Ensure horsepower matches correctly
4. **Review incomplete records:** Flag systems needing additional info
5. **Document all changes:** Export update history after major changes
6. **Validate calculations:** Spot-check pricing against OEM list

## References

For additional details, see:
- `references/model-nomenclature.md` - Model numbering system explained
- `references/pricing-calculation.md` - Pricing formulas and examples
- `references/common-updates.md` - Typical update scenarios and workflows
