"""
Turbo Air Refrigeration - Example Update Scenarios
Run these examples to perform common monthly updates
"""

from TA_refrigeration_data_manager import TurboAirDataManager
import pandas as pd

# Load the organized data
manager = TurboAirDataManager()
manager.df = pd.read_csv('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.csv')

print("="*70)
print("TURBO AIR REFRIGERATION - UPDATE EXAMPLES")
print("="*70)

# ============================================================================
# SCENARIO 1: OEM Announces 3% Price Increase on All Products
# ============================================================================
print("\n📊 SCENARIO 1: 3% Price Increase Across All Systems")
print("-" * 70)

# Before prices
print("Before update:")
print(f"  Average system cost: ${manager.df['total_system_cost'].mean():,.2f}")

# Uncomment to apply:
# manager.update_pricing(percentage_change=3.0)
print("  (Commented out - remove comment to apply)")

# ============================================================================
# SCENARIO 2: Differential Pricing by System Type
# ============================================================================
print("\n📊 SCENARIO 2: Different Increases for Coolers vs Freezers")
print("-" * 70)

# Coolers: 2.5% increase
# Freezers: 4% increase (higher material costs)

print("Cooler systems: 2.5% increase")
# manager.update_pricing(percentage_change=2.5, filter_criteria={'box_type': 'cooler'})

print("Freezer systems: 4% increase")
# manager.update_pricing(percentage_change=4.0, filter_criteria={'box_type': 'freezer'})
print("  (Commented out - remove comment to apply)")

# ============================================================================
# SCENARIO 3: Update Specific Model Line
# ============================================================================
print("\n📊 SCENARIO 3: Update Only TS020 Series")
print("-" * 70)

ts020_systems = manager.df[manager.df['condensing_unit_model'].str.contains('TS020')]
print(f"  Found {len(ts020_systems)} TS020 series systems")
print(f"  Current avg price: ${ts020_systems['total_system_cost'].mean():,.2f}")

# Apply 5% increase
# for model in ts020_systems['condensing_unit_model'].unique():
#     manager.update_pricing(model_number=model, percentage_change=5.0)
print("  (Commented out - remove comment to apply)")

# ============================================================================
# SCENARIO 4: Flat Rate Adjustment
# ============================================================================
print("\n📊 SCENARIO 4: Add $150 Surcharge to All Systems")
print("-" * 70)

print("  Adding material surcharge...")
# manager.update_pricing(price_adjustment=150)
print("  (Commented out - remove comment to apply)")

# ============================================================================
# SCENARIO 5: Regulatory Change - Model Number Update
# ============================================================================
print("\n📊 SCENARIO 5: Update Models for New Refrigerant Regulations")
print("-" * 70)

# Example: EPA requires transition from 404A to 448A refrigerant
print("  Updating 404A2 models to 448A compliance...")

# Find all 404A2 models
old_models = manager.df[manager.df['condensing_unit_model'].str.contains('404A2')]['condensing_unit_model'].unique()
print(f"  Found {len(old_models)} different 404A2 models to update")

# Update each model (example - don't run without verification)
# for old_model in old_models:
#     new_model = old_model.replace('404A2', '448A')
#     manager.update_model_numbers(old_model, new_model, model_type='condensing')
print("  (Commented out - remove comment to apply)")

# ============================================================================
# SCENARIO 6: Complex Update - By Horsepower and Type
# ============================================================================
print("\n📊 SCENARIO 6: Price Increase Based on Capacity")
print("-" * 70)

# Small systems (< 2 HP): 2% increase
# Medium systems (2-5 HP): 3% increase  
# Large systems (> 5 HP): 4% increase

small = manager.df[manager.df['horsepower'] < 2]
medium = manager.df[(manager.df['horsepower'] >= 2) & (manager.df['horsepower'] <= 5)]
large = manager.df[manager.df['horsepower'] > 5]

print(f"  Small systems (<2 HP): {len(small)} units - 2% increase")
print(f"  Medium systems (2-5 HP): {len(medium)} units - 3% increase")
print(f"  Large systems (>5 HP): {len(large)} units - 4% increase")

# Apply tiered pricing
# manager.df.loc[manager.df['horsepower'] < 2, 'total_system_cost'] *= 1.02
# manager.df.loc[(manager.df['horsepower'] >= 2) & (manager.df['horsepower'] <= 5), 'total_system_cost'] *= 1.03
# manager.df.loc[manager.df['horsepower'] > 5, 'total_system_cost'] *= 1.04
print("  (Commented out - remove comment to apply)")

# ============================================================================
# SCENARIO 7: Export Updated Price Lists for Different Teams
# ============================================================================
print("\n📊 SCENARIO 7: Generate Department-Specific Reports")
print("-" * 70)

# Sales team needs cooler pricing
coolers = manager.filter_systems(box_type='cooler')
# coolers.to_excel('/mnt/user-data/outputs/cooler_pricing_salesteam.xlsx', index=False)
print(f"  Cooler systems: {len(coolers)} configurations ready for export")

# Service team needs freezer specs
freezers = manager.filter_systems(box_type='freezer')
# freezers.to_excel('/mnt/user-data/outputs/freezer_specs_service.xlsx', index=False)
print(f"  Freezer systems: {len(freezers)} configurations ready for export")

# Management needs high-capacity systems
large_systems = manager.get_systems_by_capacity(min_hp=6)
# large_systems.to_excel('/mnt/user-data/outputs/large_capacity_systems.xlsx', index=False)
print(f"  Large capacity systems: {len(large_systems)} configurations ready for export")

print("  (Commented out - remove comment to apply)")

# ============================================================================
# SCENARIO 8: Monthly Update Workflow
# ============================================================================
print("\n📊 SCENARIO 8: Standard Monthly Update Workflow")
print("-" * 70)
print("""
Standard monthly workflow:
1. Backup current data
2. Load OEM price sheet
3. Apply percentage or fixed adjustments
4. Review changes
5. Export to all formats
6. Save update history

Example code:
-----------
# 1. Backup
manager.export_data('backup_YYYYMMDD.csv')

# 2. Apply updates (from OEM notification)
manager.update_pricing(percentage_change=2.8)

# 3. Review
stats = manager.get_summary_stats()
print(stats['price_range'])

# 4. Export
manager.export_data('refrigeration_systems_current.xlsx', format='excel')
manager.export_update_history('updates_YYYYMMDD.json')
""")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("CURRENT DATA STATUS")
print("="*70)
stats = manager.get_summary_stats()
for key, value in stats.items():
    print(f"{key.replace('_', ' ').title()}: {value}")

print("\n✅ Example scenarios ready!")
print("💡 Tip: Uncomment the code blocks you want to run")
print("📁 All exports will be saved to /mnt/user-data/outputs/")
