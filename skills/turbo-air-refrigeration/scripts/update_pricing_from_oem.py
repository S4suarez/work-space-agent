"""
Turbo Air Pricing Update - January 2026 OEM Price List
=======================================================
Updates total_system_cost based on new OEM pricing:
- Condensing Unit Cost = Column B (base) + Column I (warranty)
- Evaporator Cost = Column B × quantity
- Total System Cost = Condensing Cost + (Evaporator Cost × Qty)

Also updates model numbers:
- Scroll compressor models now end with "A" (e.g., TS015MR404A2A)
- Using "without timer" models (no -T suffix)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('/mnt/user-data/outputs')
from TA_refrigeration_data_manager import TurboAirDataManager

print("="*80)
print("TURBO AIR PRICING UPDATE - JANUARY 2026 OEM PRICE LIST")
print("="*80)

# ============================================================================
# STEP 1: Load OEM Pricing Data
# ============================================================================
print("\n📥 Loading OEM price list...")

# Load condensing units (rows 178-234 based on our exploration)
condensing_df = pd.read_excel(
    '/mnt/user-data/uploads/_0101BU2026.xlsx',
    sheet_name='NEW MODELS',
    header=None,
    skiprows=178,
    nrows=57,
    usecols=[0, 1, 8]  # Model, Base Price, Warranty
)
condensing_df.columns = ['model', 'base_price', 'warranty']
condensing_df = condensing_df[condensing_df['model'].notna()]
condensing_df = condensing_df[condensing_df['model'].str.startswith('TS', na=False)]

# Calculate total condensing unit cost
condensing_df['condensing_total_cost'] = condensing_df['base_price'] + condensing_df['warranty']

print(f"✓ Loaded {len(condensing_df)} condensing unit prices")
print(f"  Sample: {condensing_df.head(3)[['model', 'base_price', 'warranty', 'condensing_total_cost']].to_string(index=False)}")

# Load evaporators (rows 9-82 based on our exploration)
evap_df = pd.read_excel(
    '/mnt/user-data/uploads/_0101BU2026.xlsx', 
    sheet_name='NEW MODELS',
    header=None,
    skiprows=9,
    nrows=74,
    usecols=[0, 1]  # Model, Price
)
evap_df.columns = ['model', 'price']
evap_df = evap_df[evap_df['model'].notna()]
evap_df = evap_df[(evap_df['model'].str.startswith('ADR', na=False)) | 
                  (evap_df['model'].str.startswith('LED', na=False))]

print(f"✓ Loaded {len(evap_df)} evaporator prices")
print(f"  Sample: {evap_df.head(3).to_string(index=False)}")

# ============================================================================
# STEP 2: Load Current Turbo Air System Data
# ============================================================================
print("\n📂 Loading current Turbo Air system data...")

manager = TurboAirDataManager()
manager.df = pd.read_csv('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.csv')

print(f"✓ Loaded {len(manager.df)} system configurations")

# Create backup
backup_filename = f"Turbo_Air_BACKUP_Pricing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
manager.export_data(f'/mnt/user-data/outputs/{backup_filename}', format='csv')
print(f"✓ Backup created: {backup_filename}")

# ============================================================================
# STEP 3: Update Condensing Unit Model Numbers
# ============================================================================
print("\n" + "="*80)
print("UPDATING CONDENSING UNIT MODEL NUMBERS")
print("="*80)

# Create model number mapping based on OEM list
# Scroll compressor models need "A" suffix added
model_updates = []

# Check which models need the "A" suffix
for idx, row in manager.df.iterrows():
    current_model = row['condensing_unit_model']
    
    # Skip freezer models (XR) for now, handle separately
    if 'XR' in current_model:
        # Check if model exists in OEM list with "A" suffix
        if current_model + 'A' in condensing_df['model'].values:
            model_updates.append({
                'old': current_model,
                'new': current_model + 'A',
                'reason': 'Added A suffix for scroll compressor'
            })
    elif 'MR' in current_model:
        # Cooler models - check if needs "A" suffix
        # Models like TS015MR404A2 should become TS015MR404A2A
        if current_model + 'A' in condensing_df['model'].values:
            model_updates.append({
                'old': current_model,
                'new': current_model + 'A',
                'reason': 'Added A suffix for scroll compressor'
            })

# Remove duplicates
unique_updates = {}
for update in model_updates:
    if update['old'] not in unique_updates:
        unique_updates[update['old']] = update['new']

print(f"\nFound {len(unique_updates)} model numbers to update:")
for old, new in list(unique_updates.items())[:10]:
    print(f"  {old:25} → {new}")
    
# Apply updates
updated_count = 0
for old_model, new_model in unique_updates.items():
    count = manager.update_model_numbers(old_model, new_model, model_type='condensing')
    updated_count += count
    
print(f"\n✓ Updated {updated_count} condensing unit model numbers")

# ============================================================================
# STEP 4: Calculate New System Pricing
# ============================================================================
print("\n" + "="*80)
print("CALCULATING NEW SYSTEM PRICING")
print("="*80)

price_changes = []
systems_updated = 0
systems_not_found = 0

for idx, row in manager.df.iterrows():
    condensing_model = row['condensing_unit_model']
    evap_model = row['evaporator_model']
    evap_qty = row['evaporator_qty']
    old_price = row['total_system_cost']
    
    # Find condensing unit price
    condensing_match = condensing_df[condensing_df['model'] == condensing_model]
    if len(condensing_match) == 0:
        # Try without -T if it exists
        if '-T' in condensing_model:
            condensing_model_alt = condensing_model.replace('-T', '')
            condensing_match = condensing_df[condensing_df['model'] == condensing_model_alt]
        
    # Find evaporator price
    evap_match = evap_df[evap_df['model'] == evap_model]
    
    if len(condensing_match) > 0 and len(evap_match) > 0 and pd.notna(evap_qty):
        # Calculate new price
        condensing_cost = float(condensing_match.iloc[0]['condensing_total_cost'])
        evap_cost = float(evap_match.iloc[0]['price'])
        new_price = condensing_cost + (evap_cost * evap_qty)
        
        # Update the dataframe
        manager.df.at[idx, 'total_system_cost'] = new_price
        manager.df.at[idx, 'price_update_date'] = datetime.now().strftime('%Y-%m-%d')
        manager.df.at[idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        price_changes.append({
            'system_id': row['system_id'],
            'condensing_unit': condensing_model,
            'evaporator': evap_model,
            'evap_qty': evap_qty,
            'old_price': old_price,
            'new_price': new_price,
            'change': new_price - old_price,
            'change_pct': ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
        })
        systems_updated += 1
    else:
        systems_not_found += 1
        if len(condensing_match) == 0:
            print(f"⚠️  Condensing unit not found in OEM list: {condensing_model}")
        if len(evap_match) == 0:
            print(f"⚠️  Evaporator not found in OEM list: {evap_model}")

print(f"\n✓ Successfully updated: {systems_updated} systems")
print(f"⚠️  Could not find pricing for: {systems_not_found} systems")

# ============================================================================
# STEP 5: Pricing Summary Statistics
# ============================================================================
print("\n" + "="*80)
print("PRICING CHANGE SUMMARY")
print("="*80)

if len(price_changes) > 0:
    changes_df = pd.DataFrame(price_changes)
    
    print(f"\nOverall Statistics:")
    print(f"  Systems Updated: {len(changes_df)}")
    print(f"  Average Old Price: ${changes_df['old_price'].mean():,.2f}")
    print(f"  Average New Price: ${changes_df['new_price'].mean():,.2f}")
    print(f"  Average Change: ${changes_df['change'].mean():,.2f} ({changes_df['change_pct'].mean():.2f}%)")
    print(f"  Min Change: ${changes_df['change'].min():,.2f} ({changes_df['change_pct'].min():.2f}%)")
    print(f"  Max Change: ${changes_df['change'].max():,.2f} ({changes_df['change_pct'].max():.2f}%)")
    
    print(f"\n📊 Sample of Price Changes:")
    print("-" * 80)
    sample = changes_df.head(15)[['condensing_unit', 'evaporator', 'evap_qty', 'old_price', 'new_price', 'change']]
    sample['old_price'] = sample['old_price'].apply(lambda x: f"${x:,.2f}")
    sample['new_price'] = sample['new_price'].apply(lambda x: f"${x:,.2f}")
    sample['change'] = sample['change'].apply(lambda x: f"${x:,.2f}")
    print(sample.to_string(index=False))
    
    # Breakdown by box type
    cooler_changes = [pc for pc in price_changes if 'MR' in pc['condensing_unit']]
    freezer_changes = [pc for pc in price_changes if 'XR' in pc['condensing_unit']]
    
    if len(cooler_changes) > 0:
        cooler_df = pd.DataFrame(cooler_changes)
        print(f"\n📦 Cooler Systems:")
        print(f"  Count: {len(cooler_df)}")
        print(f"  Avg Change: ${cooler_df['change'].mean():,.2f} ({cooler_df['change_pct'].mean():.2f}%)")
        
    if len(freezer_changes) > 0:
        freezer_df = pd.DataFrame(freezer_changes)
        print(f"\n🧊 Freezer Systems:")
        print(f"  Count: {len(freezer_df)}")
        print(f"  Avg Change: ${freezer_df['change'].mean():,.2f} ({freezer_df['change_pct'].mean():.2f}%)")

# ============================================================================
# STEP 6: Export Updated Data
# ============================================================================
print("\n" + "="*80)
print("EXPORTING UPDATED DATA")
print("="*80)

# Export main files
manager.export_data('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.csv', format='csv')
manager.export_data('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.xlsx', format='excel')

# Export pricing change report
if len(price_changes) > 0:
    changes_df = pd.DataFrame(price_changes)
    report_filename = f"TA_Pricing_Changes_{datetime.now().strftime('%Y%m%d')}.xlsx"
    changes_df.to_excel(f'/mnt/user-data/outputs/{report_filename}', index=False)
    print(f"✓ Pricing change report: {report_filename}")

print(f"✓ Updated: Turbo_Air_Refrigeration_Systems.csv")
print(f"✓ Updated: Turbo_Air_Refrigeration_Systems.xlsx")

# ============================================================================
# STEP 7: Final Summary
# ============================================================================
print("\n" + "="*80)
print("✅ PRICING UPDATE COMPLETE")
print("="*80)

final_stats = manager.get_summary_stats()
print(f"\nFinal System Status:")
print(f"  Total Configurations: {final_stats['total_configurations']}")
print(f"  Price Range: {final_stats['price_range']}")
print(f"  Systems with Updated Pricing: {systems_updated}")
print(f"  Systems Needing Review: {systems_not_found}")

print(f"\nBackup: {backup_filename}")
print("\n" + "="*80)
