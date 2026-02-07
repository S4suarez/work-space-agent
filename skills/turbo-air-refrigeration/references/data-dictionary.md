# Turbo Air Refrigeration Systems - Data Dictionary

## Table: Turbo Air Refrigeration Systems
**Purpose:** Comprehensive catalog of Turbo Air commercial refrigeration system configurations with pricing and specifications

---

## Field Definitions

### Primary Identification Fields

| Field Name | Type | Description | Example Values | Notes |
|------------|------|-------------|----------------|-------|
| **system_id** | string | Unique identifier for each system configuration | `COO_TS020MR404A2-T_LED114BENM_1` | Auto-generated: {box_type}_{condensing_unit}_{evaporator}_{qty} |
| **box_type** | string | Type of refrigerated space | `cooler`, `freezer` | Determines operating temperature range |
| **brand** | string | Manufacturer brand | `Turbo Air` | Currently all Turbo Air, expandable for multi-brand |

### Equipment Specifications

| Field Name | Type | Description | Example Values | Notes |
|------------|------|-------------|----------------|-------|
| **condensing_unit_model** | string | Condensing unit model number | `TS020MR404A2-T` | Contains refrigerant type (404A/448A) and generation (A2/A3) |
| **horsepower** | float | Condensing unit motor horsepower | `0.5`, `1.5`, `2.0`, `10.0` | Key sizing parameter; ranges from 0.5-10 HP |
| **evaporator_model** | string | Evaporator coil model number | `LED114BENM`, `ADR137AENM` | LED or ADR series; some entries show "PENDING" |
| **evaporator_qty** | integer | Number of evaporator coils in system | `1`, `2`, `3` | Multiple coils for larger capacity needs |
| **btu_rating_448a** | integer | Cooling capacity in BTU/hr at 448A refrigerant | `6998`, `16540`, `96333` | Performance metric for system sizing |

### Pricing Information

| Field Name | Type | Description | Example Values | Notes |
|------------|------|-------------|----------------|-------|
| **total_system_cost** | float | Complete system price in USD | `2929.00`, `5810.33`, `16515.00` | Includes condensing unit + evaporator(s) |
| **price_update_date** | date | Last date pricing was updated | `2026-02-02`, `null` | Tracks when prices changed |

### Metadata & Tracking

| Field Name | Type | Description | Example Values | Notes |
|------------|------|-------------|----------------|-------|
| **last_updated** | date | Most recent modification date | `2026-02-02` | Any change to record updates this field |
| **model_update_date** | date | Last model number change date | `2026-02-02`, `null` | Tracks regulatory/product updates |
| **has_complete_data** | boolean | Data validation flag | `True`, `False` | False if missing critical fields |
| **notes** | string | Free-text notes field | Various | For special cases, compatibility issues, etc. |

---

## Data Patterns & Business Rules

### Model Number Nomenclature
- **TS###XR404A#**: Freezer condensing units
  - `TS` = Turbo Air Series
  - `###` = Horsepower x 10 (e.g., TS020 = 2.0 HP)
  - `X` = Freezer designation
  - `R404A` = Refrigerant type
  - `A2/A3` = Generation/revision

- **TS###MR404A#-T**: Cooler condensing units
  - Same pattern, but `M` = Medium temp (cooler)
  - `-T` = Tropicalized (for hot environments)

### Evaporator Patterns
- **LED###BENM/X**: LED-lit evaporators
  - `###` = Approximate BTU capacity / 100
  - `BENM` = Single coil
  - `BENX` = Multi-coil (when qty > 1)

- **ADR###AENM/X**: Standard evaporators
  - Similar numbering scheme

### Pricing Relationships
- Price increases with horsepower (generally)
- Multiple evaporators cost more than single larger unit
- Freezer systems cost ~15-30% more than equivalent cooler systems
- A3 generation models typically cost slightly more than A2

### Data Quality Notes
- 2 records have incomplete data (missing evaporator model or pricing)
- Some 7.5 HP and 10 HP cooler models show "LED" without full model number
- All systems use 404A refrigerant; future updates may introduce 448A compliance

---

## Key Metrics

**Current Dataset (as of 2026-02-02):**
- Total configurations: 88
- Cooler systems: 55 (62.5%)
- Freezer systems: 33 (37.5%)
- Horsepower range: 0.5 - 10.0 HP
- Price range: $2,929 - $16,515
- Average system cost: $5,810.33
- Unique condensing units: 36
- Unique evaporators: 38

---

## Update Frequency

**Recommended Review Cycles:**
- **Pricing Updates**: Monthly or quarterly (based on OEM notifications)
- **Model Number Updates**: As needed for regulatory changes
- **Data Validation**: Quarterly
- **Full Backup**: Before each update cycle

---

## Related Documentation
- `TA_Usage_Guide.md` - How to use the data manager
- `TA_update_examples.py` - Common update scenarios
- `TA_refrigeration_data_manager.py` - Core management system

---

## Change Log

**2026-02-02**: Initial data organization
- Standardized column names to snake_case
- Added metadata tracking fields
- Created unique system identifiers
- Cleaned pricing data format
- Identified 2 incomplete records for followup
