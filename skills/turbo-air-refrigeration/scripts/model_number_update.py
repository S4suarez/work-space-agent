"""
Turbo Air Model Update - February 2026
=======================================
Update 1: Remove timer designation and update evaporator suffix

Changes:
1. Condensing Units: Remove "-T" suffix (timer removed from all models)
2. Evaporators: Change final letter from M or X to C
"""

from TA_refrigeration_data_manager import TurboAirDataManager
import pandas as pd
from datetime import datetime

# Load the current data
print("="*80)
print("TURBO AIR MODEL UPDATE - FEBRUARY 2026")
print("="*80)
print("\nLoading current Turbo Air data...")

manager = TurboAirDataManager()
manager.df = pd.read_csv('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.csv')

print(f"✓ Loaded {len(manager.df)} system configurations")

# ============================================================================
# STEP 1: Show what will change
# ============================================================================
print("\n" + "="*80)
print("PREVIEW OF CHANGES")
print("="*80)

# Preview condensing unit changes
condensing_units_to_update = manager.df[manager.df['condensing_unit_model'].str.contains('-T', na=False)]
print(f"\n1. CONDENSING UNITS: {len(condensing_units_to_update)} systems will be updated")
print("   Removing '-T' suffix (timer designation)")
print("\n   Sample changes:")
unique_condensing = condensing_units_to_update['condensing_unit_model'].unique()[:5]
for old_model in unique_condensing:
    new_model = old_model.replace('-T', '')
    print(f"   {old_model:25} → {new_model}")

# Preview evaporator changes
evaporators_to_update = manager.df[
    (manager.df['evaporator_model'].str.endswith('M', na=False)) | 
    (manager.df['evaporator_model'].str.endswith('X', na=False))
]
print(f"\n2. EVAPORATORS: {len(evaporators_to_update)} systems will be updated")
print("   Changing final letter M or X to C")
print("\n   Sample changes:")
unique_evaporators = evaporators_to_update['evaporator_model'].unique()[:5]
for old_model in unique_evaporators:
    if old_model.endswith('M'):
        new_model = old_model[:-1] + 'C'
    elif old_model.endswith('X'):
        new_model = old_model[:-1] + 'C'
    else:
        new_model = old_model
    print(f"   {old_model:25} → {new_model}")

# ============================================================================
# STEP 2: Create backup before making changes
# ============================================================================
print("\n" + "="*80)
print("CREATING BACKUP")
print("="*80)

backup_filename = f"Turbo_Air_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
manager.export_data(f'/mnt/user-data/outputs/{backup_filename}', format='csv')
print(f"✓ Backup created: {backup_filename}")

# ============================================================================
# STEP 3: Apply condensing unit updates
# ============================================================================
print("\n" + "="*80)
print("UPDATING CONDENSING UNITS")
print("="*80)

# Get all unique models with -T
models_with_timer = manager.df[manager.df['condensing_unit_model'].str.contains('-T', na=False)]['condensing_unit_model'].unique()

updated_count = 0
for old_model in models_with_timer:
    new_model = old_model.replace('-T', '')
    records = manager.update_model_numbers(old_model, new_model, model_type='condensing')
    updated_count += records
    print(f"  ✓ {old_model:30} → {new_model:30} ({records} records)")

print(f"\n✓ Total condensing unit records updated: {updated_count}")

# ============================================================================
# STEP 4: Apply evaporator updates
# ============================================================================
print("\n" + "="*80)
print("UPDATING EVAPORATORS")
print("="*80)

# Get all unique evaporator models ending in M or X
evaporator_models = manager.df['evaporator_model'].unique()
models_to_update = [m for m in evaporator_models if isinstance(m, str) and (m.endswith('M') or m.endswith('X'))]

updated_count = 0
for old_model in models_to_update:
    if old_model.endswith('M'):
        new_model = old_model[:-1] + 'C'
    elif old_model.endswith('X'):
        new_model = old_model[:-1] + 'C'
    else:
        continue
    
    records = manager.update_model_numbers(old_model, new_model, model_type='evaporator')
    updated_count += records
    print(f"  ✓ {old_model:30} → {new_model:30} ({records} records)")

print(f"\n✓ Total evaporator records updated: {updated_count}")

# ============================================================================
# STEP 5: Verify the changes
# ============================================================================
print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

# Check for any remaining -T suffixes
remaining_timer = manager.df[manager.df['condensing_unit_model'].str.contains('-T', na=False)]
print(f"\n✓ Condensing units with '-T': {len(remaining_timer)} (should be 0)")

# Check for any remaining M or X suffixes
remaining_mx = manager.df[
    (manager.df['evaporator_model'].str.endswith('M', na=False)) | 
    (manager.df['evaporator_model'].str.endswith('X', na=False))
]
print(f"✓ Evaporators ending in M/X: {len(remaining_mx)} (should be 0)")

# Show sample of updated records
print("\n" + "-"*80)
print("Sample of updated records:")
print("-"*80)
sample_cols = ['condensing_unit_model', 'evaporator_model', 'model_update_date']
print(manager.df[sample_cols].head(10).to_string(index=False))

# ============================================================================
# STEP 6: Export updated data
# ============================================================================
print("\n" + "="*80)
print("EXPORTING UPDATED DATA")
print("="*80)

# Export to all formats
manager.export_data('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.csv', format='csv')
manager.export_data('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.xlsx', format='excel')

# Export update history
history_filename = f"TA_Model_Update_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
manager.export_update_history(f'/mnt/user-data/outputs/{history_filename}')

print("✓ Updated files exported:")
print("  - Turbo_Air_Refrigeration_Systems.csv")
print("  - Turbo_Air_Refrigeration_Systems.xlsx")
print(f"  - {history_filename}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("UPDATE COMPLETE - SUMMARY")
print("="*80)

stats = manager.get_summary_stats()
print(f"\nTotal configurations: {stats['total_configurations']}")
print(f"Cooler systems: {stats['cooler_systems']}")
print(f"Freezer systems: {stats['freezer_systems']}")
print(f"Unique condensing units: {stats['unique_condensing_units']}")
print(f"Unique evaporators: {stats['unique_evaporators']}")

print("\n" + "="*80)
print("✅ MODEL UPDATE SUCCESSFUL!")
print("="*80)
print("\nChanges made:")
print("  1. ✓ Removed '-T' suffix from all condensing unit models")
print("  2. ✓ Changed evaporator suffix from M/X to C")
print(f"  3. ✓ Backup saved: {backup_filename}")
print("  4. ✓ Update history logged")
print("\nNext steps:")
print("  - Review the updated Excel file")
print("  - Distribute to sales/service teams")
print("  - Update any external systems or quotation tools")
print("="*80)
