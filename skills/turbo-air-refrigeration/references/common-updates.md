# Common Turbo Air Update Scenarios

## Monthly/Quarterly Updates

### Scenario 1: Standard OEM Price Increase

**When:** Turbo Air announces price increase (typically quarterly)

**Example Request:** "Update all Turbo Air pricing with the new Q1 2026 OEM list"

**Process:**
1. Receive OEM Excel file
2. Create backup of current data
3. Run `update_pricing_from_oem.py` script
4. Review pricing change report
5. Validate spot checks
6. Export updated files
7. Distribute to sales team

**Typical Impact:**
- 86-88 systems updated
- Average increase: 5-15%
- 2-4 systems may need manual review

**Time:** ~5 minutes automated + 10 minutes validation

---

### Scenario 2: Model Number Correction (Regulatory)

**When:** EPA or DOE requires refrigerant or efficiency changes

**Example Request:** "Update all models to remove the timer designation"

**Process:**
1. Identify affected models (check for "-T" suffix)
2. Create backup
3. Run bulk update:
   ```python
   for old_model in models_with_timer:
       new_model = old_model.replace('-T', '')
       manager.update_model_numbers(old_model, new_model, 'condensing')
   ```
4. Verify all changes
5. Export updated data
6. Document changes

**Typical Impact:**
- 50-60 systems updated
- Model numbers simplified
- No pricing changes

**Time:** ~2 minutes automated + 5 minutes validation

---

### Scenario 3: Add Scroll Compressor Designation

**When:** OEM updates model nomenclature for scroll compressors

**Example Request:** "Add the 'A' suffix to all 1.5 HP and 2 HP scroll compressor models"

**Process:**
1. Identify models needing "A" suffix (match against OEM list)
2. Create backup
3. Update systematically by horsepower:
   ```python
   # 1.5 HP models
   manager.update_model_numbers('TS015MR404A2', 'TS015MR404A2A', 'condensing')
   manager.update_model_numbers('TS015MR404A3', 'TS015MR404A3A', 'condensing')
   
   # 2.0 HP models
   manager.update_model_numbers('TS020MR404A2', 'TS020MR404A2A', 'condensing')
   manager.update_model_numbers('TS020MR404A3', 'TS020MR404A3A', 'condensing')
   ```
4. Verify changes
5. Export and document

**Typical Impact:**
- 20-30 systems updated
- Better model identification
- Aligns with OEM nomenclature

**Time:** ~3 minutes

---

## Sales & Quoting

### Scenario 4: Generate Quote for Specific Configuration

**Example Request:** "What's the current price for a 3 HP cooler with dual ADR evaporators?"

**Process:**
```python
# Query by specifications
systems = manager.df[
    (manager.df['horsepower'] == 3) &
    (manager.df['box_type'] == 'cooler') &
    (manager.df['evaporator_model'].str.startswith('ADR')) &
    (manager.df['evaporator_qty'] == 2)
]

# Display options
for idx, row in systems.iterrows():
    print(f"{row['condensing_unit_model']} + {row['evaporator_model']} × {row['evaporator_qty']}")
    print(f"  Price: ${row['total_system_cost']:,.2f}")
```

**Output:**
```
TS030MR404A2 + ADR125AENC × 2
  Price: $5,978.00

TS030MR404A3 + ADR125AENC × 2
  Price: $6,039.00
```

**Time:** ~1 minute

---

### Scenario 5: Export Pricing for Sales Team

**Example Request:** "Give me an Excel file with all cooler systems under 5 HP for the sales team"

**Process:**
```python
# Filter systems
sales_data = manager.df[
    (manager.df['box_type'] == 'cooler') &
    (manager.df['horsepower'] < 5)
]

# Select relevant columns for sales
sales_export = sales_data[[
    'horsepower',
    'condensing_unit_model',
    'evaporator_model',
    'evaporator_qty',
    'total_system_cost',
    'btu_rating_448a'
]]

# Export
sales_export.to_excel('cooler_systems_under_5hp.xlsx', index=False)
```

**Time:** ~1 minute

---

### Scenario 6: Compare Evaporator Options

**Example Request:** "What are the price differences between ADR and LED evaporators for a 2 HP system?"

**Process:**
```python
# Get 2 HP systems
systems_2hp = manager.df[
    (manager.df['horsepower'] == 2) &
    (manager.df['evaporator_qty'] == 1)
]

# Group by evaporator type
adr_systems = systems_2hp[systems_2hp['evaporator_model'].str.startswith('ADR')]
led_systems = systems_2hp[systems_2hp['evaporator_model'].str.startswith('LED')]

print(f"ADR Systems: ${adr_systems['total_system_cost'].mean():,.2f} avg")
print(f"LED Systems: ${led_systems['total_system_cost'].mean():,.2f} avg")
print(f"Difference: ${led_systems['total_system_cost'].mean() - adr_systems['total_system_cost'].mean():,.2f}")
```

**Time:** ~1 minute

---

## Service & Technical

### Scenario 7: Lookup System by Configuration

**Example Request:** "Customer has a TS050MR404A3 with 2 ADR171 coils, what's the system ID?"

**Process:**
```python
system = manager.df[
    (manager.df['condensing_unit_model'] == 'TS050MR404A3A') &
    (manager.df['evaporator_model'] == 'ADR171AENC') &
    (manager.df['evaporator_qty'] == 2)
]

print(f"System ID: {system.iloc[0]['system_id']}")
print(f"BTU Rating: {system.iloc[0]['btu_rating_448a']}")
print(f"Current Price: ${system.iloc[0]['total_system_cost']:,.2f}")
```

**Time:** ~30 seconds

---

### Scenario 8: Find All Systems Using Specific Component

**Example Request:** "Which systems use the LED114BENC evaporator?"

**Process:**
```python
systems = manager.filter_systems(evaporator_model='LED114BENC')

print(f"Found {len(systems)} systems using LED114BENC:")
for idx, row in systems.iterrows():
    print(f"  {row['condensing_unit_model']} - {row['horsepower']} HP - ${row['total_system_cost']:,.2f}")
```

**Time:** ~30 seconds

---

## Data Management

### Scenario 9: Add Notes to Specific Systems

**Example Request:** "Mark all 7.5 HP systems as requiring extended lead time"

**Process:**
```python
# Find all 7.5 HP systems
systems_75hp = manager.df[manager.df['horsepower'] == 7.5]

# Add note to each
for system_id in systems_75hp['system_id']:
    manager.add_notes(system_id, "Extended lead time - 4-6 weeks")
```

**Time:** ~1 minute

---

### Scenario 10: Identify Incomplete Records

**Example Request:** "Show me all systems that are missing information"

**Process:**
```python
incomplete = manager.df[~manager.df['has_complete_data']]

print(f"Found {len(incomplete)} incomplete records:")
for idx, row in incomplete.iterrows():
    issues = []
    if pd.isna(row['evaporator_model']) or row['evaporator_model'] == 'LED':
        issues.append('Missing evaporator model')
    if pd.isna(row['total_system_cost']):
        issues.append('Missing pricing')
    if pd.isna(row['btu_rating_448a']):
        issues.append('Missing BTU rating')
    
    print(f"{row['condensing_unit_model']}: {', '.join(issues)}")
```

**Time:** ~30 seconds

---

## Reporting

### Scenario 11: Generate Monthly Sales Report

**Example Request:** "Create a report showing systems by price range"

**Process:**
```python
# Define price ranges
ranges = [
    (0, 4000, 'Budget'),
    (4000, 6000, 'Mid-Range'),
    (6000, 10000, 'Premium'),
    (10000, 999999, 'High-End')
]

for min_price, max_price, label in ranges:
    count = len(manager.df[
        (manager.df['total_system_cost'] >= min_price) &
        (manager.df['total_system_cost'] < max_price)
    ])
    print(f"{label} (${min_price:,}-${max_price:,}): {count} systems")
```

**Time:** ~1 minute

---

### Scenario 12: Compare A2 vs A3 Models

**Example Request:** "What's the price difference between single-phase and three-phase systems?"

**Process:**
```python
a2_models = manager.df[manager.df['condensing_unit_model'].str.contains('A2')]
a3_models = manager.df[manager.df['condensing_unit_model'].str.contains('A3')]

print(f"Single Phase (A2):")
print(f"  Count: {len(a2_models)}")
print(f"  Avg Price: ${a2_models['total_system_cost'].mean():,.2f}")

print(f"\nThree Phase (A3):")
print(f"  Count: {len(a3_models)}")
print(f"  Avg Price: ${a3_models['total_system_cost'].mean():,.2f}")

print(f"\nAverage Difference: ${a3_models['total_system_cost'].mean() - a2_models['total_system_cost'].mean():,.2f}")
```

**Time:** ~1 minute

---

## Best Practices

### Always Follow This Order:
1. **Backup** before any update
2. **Preview** changes before applying
3. **Validate** results after update
4. **Export** updated files
5. **Document** what was changed

### Quality Checks:
- Verify price changes are reasonable (5-20% typical)
- Check that model numbers match OEM list format
- Ensure no systems lost data during update
- Spot-check 5-10 random calculations manually
- Export update history log

### Documentation:
- Keep backup files dated
- Export pricing change reports
- Maintain update summary documents
- Log all major changes with reasons
