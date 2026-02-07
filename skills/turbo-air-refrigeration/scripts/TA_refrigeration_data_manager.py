"""
Turbo Air Refrigeration Specifications Data Manager
Handles organization, manipulation, and updates for Turbo Air refrigeration system data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json


class TurboAirDataManager:
    """
    Manages commercial refrigeration specifications data with capabilities for:
    - Data organization and validation
    - Model number updates
    - Pricing adjustments
    - Regulatory compliance tracking
    """
    
    def __init__(self, data_file=None):
        """Initialize the data manager with optional data file"""
        self.df = None
        self.update_history = []
        
        if data_file:
            self.load_data(data_file)
    
    def load_raw_data(self, raw_data):
        """
        Load and structure raw refrigeration data
        
        Parameters:
        -----------
        raw_data : list of dict
            Raw data from TSV/CSV format
        """
        self.df = pd.DataFrame(raw_data)
        self._standardize_columns()
        self._clean_data()
        self._add_metadata_columns()
        
        print(f"✓ Loaded {len(self.df)} refrigeration system configurations")
        return self.df
    
    def _standardize_columns(self):
        """Standardize column names and data types"""
        # Rename columns to snake_case for consistency
        column_mapping = {
            'boxType': 'box_type',
            'referBrand': 'brand',
            'horsePower': 'horsepower',
            'referModelNumber': 'condensing_unit_model',
            'evapCoil': 'evaporator_model',
            'qtyEvapCoil': 'evaporator_qty',
            'referSysTotalCost': 'total_system_cost',
            'btu448A': 'btu_rating_448a'
        }
        self.df.rename(columns=column_mapping, inplace=True)
        
        # Convert data types
        self.df['horsepower'] = pd.to_numeric(self.df['horsepower'], errors='coerce')
        self.df['evaporator_qty'] = pd.to_numeric(self.df['evaporator_qty'], errors='coerce')
        self.df['btu_rating_448a'] = pd.to_numeric(self.df['btu_rating_448a'], errors='coerce')
        
        # Clean up cost field (remove commas and convert to float)
        if self.df['total_system_cost'].dtype == 'object':
            self.df['total_system_cost'] = self.df['total_system_cost'].str.replace(',', '').astype(float)
    
    def _clean_data(self):
        """Clean and validate data"""
        # Handle missing values
        self.df['evaporator_model'] = self.df['evaporator_model'].fillna('PENDING')
        
        # Add validation flags
        self.df['has_complete_data'] = ~(
            self.df['evaporator_model'].isna() | 
            self.df['total_system_cost'].isna() |
            self.df['btu_rating_448a'].isna()
        )
    
    def _add_metadata_columns(self):
        """Add metadata columns for tracking and analysis"""
        self.df['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        self.df['price_update_date'] = None
        self.df['model_update_date'] = None
        self.df['notes'] = ''
        
        # Create unique system ID
        self.df['system_id'] = (
            self.df['box_type'].str[:3].str.upper() + '_' +
            self.df['condensing_unit_model'] + '_' +
            self.df['evaporator_model'] + '_' +
            self.df['evaporator_qty'].astype(str)
        )
    
    def get_summary_stats(self):
        """Get summary statistics of the dataset"""
        stats = {
            'total_configurations': len(self.df),
            'cooler_systems': len(self.df[self.df['box_type'] == 'cooler']),
            'freezer_systems': len(self.df[self.df['box_type'] == 'freezer']),
            'unique_condensing_units': self.df['condensing_unit_model'].nunique(),
            'unique_evaporators': self.df['evaporator_model'].nunique(),
            'horsepower_range': f"{self.df['horsepower'].min()} - {self.df['horsepower'].max()} HP",
            'price_range': f"${self.df['total_system_cost'].min():,.2f} - ${self.df['total_system_cost'].max():,.2f}",
            'incomplete_records': (~self.df['has_complete_data']).sum()
        }
        return stats
    
    def update_pricing(self, model_number=None, price_adjustment=None, 
                      percentage_change=None, filter_criteria=None):
        """
        Update pricing for specific models or groups
        
        Parameters:
        -----------
        model_number : str, optional
            Specific condensing unit model to update
        price_adjustment : float, optional
            Dollar amount to add/subtract
        percentage_change : float, optional
            Percentage to increase/decrease (e.g., 5.5 for 5.5% increase)
        filter_criteria : dict, optional
            Dictionary of column:value pairs to filter records
        """
        # Create filter mask
        mask = pd.Series([True] * len(self.df))
        
        if model_number:
            mask &= self.df['condensing_unit_model'] == model_number
        
        if filter_criteria:
            for column, value in filter_criteria.items():
                mask &= self.df[column] == value
        
        # Apply pricing update
        old_prices = self.df.loc[mask, 'total_system_cost'].copy()
        
        if price_adjustment is not None:
            self.df.loc[mask, 'total_system_cost'] += price_adjustment
        elif percentage_change is not None:
            self.df.loc[mask, 'total_system_cost'] *= (1 + percentage_change / 100)
        
        # Update metadata
        self.df.loc[mask, 'price_update_date'] = datetime.now().strftime('%Y-%m-%d')
        self.df.loc[mask, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Log the update
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'update_type': 'pricing',
            'records_affected': mask.sum(),
            'model_number': model_number,
            'price_adjustment': price_adjustment,
            'percentage_change': percentage_change,
            'filter_criteria': filter_criteria
        }
        self.update_history.append(update_record)
        
        print(f"✓ Updated {mask.sum()} records")
        if len(old_prices) > 0:
            print(f"  Average old price: ${old_prices.mean():,.2f}")
            print(f"  Average new price: ${self.df.loc[mask, 'total_system_cost'].mean():,.2f}")
        
        return mask.sum()
    
    def update_model_numbers(self, old_model, new_model, model_type='condensing'):
        """
        Update model numbers (for regulatory changes or product updates)
        
        Parameters:
        -----------
        old_model : str
            Current model number
        new_model : str
            New model number
        model_type : str
            'condensing' or 'evaporator'
        """
        column = 'condensing_unit_model' if model_type == 'condensing' else 'evaporator_model'
        
        mask = self.df[column] == old_model
        records_affected = mask.sum()
        
        self.df.loc[mask, column] = new_model
        self.df.loc[mask, 'model_update_date'] = datetime.now().strftime('%Y-%m-%d')
        self.df.loc[mask, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Update system IDs
        self.df.loc[mask, 'system_id'] = (
            self.df.loc[mask, 'box_type'].str[:3].str.upper() + '_' +
            self.df.loc[mask, 'condensing_unit_model'] + '_' +
            self.df.loc[mask, 'evaporator_model'] + '_' +
            self.df.loc[mask, 'evaporator_qty'].astype(str)
        )
        
        # Log the update
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'update_type': 'model_number',
            'records_affected': records_affected,
            'old_model': old_model,
            'new_model': new_model,
            'model_type': model_type
        }
        self.update_history.append(update_record)
        
        print(f"✓ Updated {records_affected} records from {old_model} to {new_model}")
        return records_affected
    
    def filter_systems(self, **criteria):
        """
        Filter systems based on criteria
        
        Example:
        --------
        filter_systems(box_type='cooler', horsepower=2)
        filter_systems(brand='Turbo Air', evaporator_qty=2)
        """
        mask = pd.Series([True] * len(self.df))
        
        for column, value in criteria.items():
            if column in self.df.columns:
                mask &= self.df[column] == value
        
        return self.df[mask]
    
    def get_systems_by_capacity(self, min_hp=None, max_hp=None, box_type=None):
        """Get systems within a horsepower range"""
        mask = pd.Series([True] * len(self.df))
        
        if min_hp is not None:
            mask &= self.df['horsepower'] >= min_hp
        if max_hp is not None:
            mask &= self.df['horsepower'] <= max_hp
        if box_type:
            mask &= self.df['box_type'] == box_type
        
        return self.df[mask].sort_values('horsepower')
    
    def export_data(self, filename, format='csv'):
        """Export data to file"""
        if format == 'csv':
            self.df.to_csv(filename, index=False)
        elif format == 'excel':
            self.df.to_excel(filename, index=False, sheet_name='Refrigeration_Systems')
        elif format == 'json':
            self.df.to_json(filename, orient='records', indent=2)
        
        print(f"✓ Data exported to {filename}")
    
    def export_update_history(self, filename):
        """Export update history log"""
        with open(filename, 'w') as f:
            json.dump(self.update_history, f, indent=2)
        print(f"✓ Update history exported to {filename}")
    
    def add_notes(self, system_id, note):
        """Add notes to specific system configurations"""
        mask = self.df['system_id'] == system_id
        current_note = self.df.loc[mask, 'notes'].iloc[0] if mask.any() else ''
        
        new_note = f"{current_note}\n{datetime.now().strftime('%Y-%m-%d')}: {note}".strip()
        self.df.loc[mask, 'notes'] = new_note
        
        print(f"✓ Note added to {system_id}")


def main():
    """Example usage and data loading"""
    
    # Raw data from your input
    raw_data = [
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 0.5, 'referModelNumber': 'TS006MR404A2-T', 'evapCoil': 'ADR060AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '2,929', 'btu448A': 6998},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 0.75, 'referModelNumber': 'TS008MR404A2-T', 'evapCoil': 'ADR089AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,132', 'btu448A': 9404},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 0.75, 'referModelNumber': 'TS008MR404A2-T', 'evapCoil': 'LED052BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,377', 'btu448A': 9404},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1, 'referModelNumber': 'TS010MR404A2-T', 'evapCoil': 'ADR112AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,426', 'btu448A': 9888},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1, 'referModelNumber': 'TS010MR404A2-T', 'evapCoil': 'LED072BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,632', 'btu448A': 9888},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015MR404A2-T', 'evapCoil': 'ADR060AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,075', 'btu448A': 13981},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015MR404A2-T', 'evapCoil': 'ADR125AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,746', 'btu448A': 13981},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015MR404A2-T', 'evapCoil': 'LED081BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,864', 'btu448A': 13981},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015MR404A3-T', 'evapCoil': 'ADR060AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,131', 'btu448A': 13981},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015MR404A3-T', 'evapCoil': 'ADR125AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,802', 'btu448A': 13981},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015MR404A3-T', 'evapCoil': 'LED081BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,920', 'btu448A': 13981},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020MR404A2-T', 'evapCoil': 'ADR137AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,956', 'btu448A': 16540},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020MR404A2-T', 'evapCoil': 'ADR089AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,330', 'btu448A': 16540},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020MR404A2-T', 'evapCoil': 'LED114BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,380', 'btu448A': 16540},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020MR404A3-T', 'evapCoil': 'ADR137AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '3,987', 'btu448A': 16540},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020MR404A3-T', 'evapCoil': 'ADR089AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,361', 'btu448A': 16540},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020MR404A3-T', 'evapCoil': 'LED114BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,411', 'btu448A': 16540},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025MR404A2-T', 'evapCoil': 'ADR171AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,251', 'btu448A': 18163},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025MR404A2-T', 'evapCoil': 'ADR112AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,644', 'btu448A': 18163},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025MR404A2-T', 'evapCoil': 'LED124BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,756', 'btu448A': 18163},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025MR404A3-T', 'evapCoil': 'ADR171AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,276', 'btu448A': 18163},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025MR404A3-T', 'evapCoil': 'ADR112AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,669', 'btu448A': 18163},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025MR404A3-T', 'evapCoil': 'LED124BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,781', 'btu448A': 18163},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030MR404A2-T', 'evapCoil': 'ADR258AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,681', 'btu448A': 26470},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030MR404A2-T', 'evapCoil': 'ADR125AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,115', 'btu448A': 26470},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030MR404A2-T', 'evapCoil': 'LED176BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,159', 'btu448A': 26470},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030MR404A3-T', 'evapCoil': 'ADR258AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,727', 'btu448A': 26470},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030MR404A3-T', 'evapCoil': 'ADR125AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,161', 'btu448A': 26470},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030MR404A3-T', 'evapCoil': 'LED176BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,205', 'btu448A': 26470},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A2-T', 'evapCoil': 'ADR325AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,500', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A2-T', 'evapCoil': 'ADR137AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,840', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A2-T', 'evapCoil': 'ADR089AENX', 'qtyEvapCoil': 3, 'referSysTotalCost': '5,839', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A2-T', 'evapCoil': 'LED225BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,853', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A3-T', 'evapCoil': 'ADR325AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,356', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A3-T', 'evapCoil': 'ADR137AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,666', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A3-T', 'evapCoil': 'ADR089AENX', 'qtyEvapCoil': 3, 'referSysTotalCost': '5,695', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 4, 'referModelNumber': 'TS040MR404A3-T', 'evapCoil': 'LED225BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,709', 'btu448A': 34140},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A2-T', 'evapCoil': 'ADR392AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '6,086', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A2-T', 'evapCoil': 'ADR171AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '6,343', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A2-T', 'evapCoil': 'ADR137AENX', 'qtyEvapCoil': 3, 'referSysTotalCost': '7,035', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A2-T', 'evapCoil': 'LED273BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '6,544', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A2-T', 'evapCoil': 'LED124BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '7,353', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A3-T', 'evapCoil': 'ADR392AENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '6,042', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A3-T', 'evapCoil': 'ADR171AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '6,299', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A3-T', 'evapCoil': 'ADR137AENX', 'qtyEvapCoil': 3, 'referSysTotalCost': '6,098', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A3-T', 'evapCoil': 'LED273BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '6,500', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 5, 'referModelNumber': 'TS050MR404A3-T', 'evapCoil': 'LED124BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '7,309', 'btu448A': 42347},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 6, 'referModelNumber': 'TS060MR404A3-T', 'evapCoil': 'ADR191AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '7,126', 'btu448A': 50513},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 6, 'referModelNumber': 'TS060MR404A3-T', 'evapCoil': 'ADR137AENX', 'qtyEvapCoil': 3, 'referSysTotalCost': '7,694', 'btu448A': 50513},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 6, 'referModelNumber': 'TS060MR404A3-T', 'evapCoil': 'LED176BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '8,440', 'btu448A': 50513},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 7.5, 'referModelNumber': 'TS075MR404A3-T', 'evapCoil': 'ADR258AENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '10,871', 'btu448A': 73100},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 7.5, 'referModelNumber': 'TS075MR404A3-T', 'evapCoil': 'ADR171AENX', 'qtyEvapCoil': 3, 'referSysTotalCost': '11,774', 'btu448A': 73100},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 7.5, 'referModelNumber': 'TS075MR404A3-T', 'evapCoil': 'LED', 'qtyEvapCoil': None, 'referSysTotalCost': None, 'btu448A': 73100},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 10, 'referModelNumber': 'TS100MR404A3-T', 'evapCoil': 'ADR352AENX', 'qtyEvapCoil': 3, 'referSysTotalCost': '16,515', 'btu448A': 96333},
        {'boxType': 'cooler', 'referBrand': 'Turbo Air', 'horsePower': 10, 'referModelNumber': 'TS100MR404A3-T', 'evapCoil': 'LED', 'qtyEvapCoil': None, 'referSysTotalCost': None, 'btu448A': 96333},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 1, 'referModelNumber': 'TS010XR404A2', 'evapCoil': 'LED052BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,068', 'btu448A': 4270},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015XR404A2', 'evapCoil': 'LED072BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,264', 'btu448A': 5746},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 1.5, 'referModelNumber': 'TS015XR404A3', 'evapCoil': 'LED072BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,255', 'btu448A': 5746},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020XR404A2', 'evapCoil': 'LED081BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,344', 'btu448A': 6720},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020XR404A2', 'evapCoil': 'LED036BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,793', 'btu448A': 6720},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020XR404A3', 'evapCoil': 'LED081BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,344', 'btu448A': 6720},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2, 'referModelNumber': 'TS020XR404A3', 'evapCoil': 'LED036BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '4,793', 'btu448A': 6720},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025XR404A2', 'evapCoil': 'LED090BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,655', 'btu448A': 8445},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025XR404A2', 'evapCoil': 'LED052BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,285', 'btu448A': 8445},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025XR404A3', 'evapCoil': 'LED090BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,655', 'btu448A': 8445},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 2.5, 'referModelNumber': 'TS025XR404A3', 'evapCoil': 'LED052BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,285', 'btu448A': 8445},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030XR404A2', 'evapCoil': 'LED114BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,899', 'btu448A': 9032},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030XR404A2', 'evapCoil': 'LED052BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,369', 'btu448A': 9032},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030XR404A3', 'evapCoil': 'LED114BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '4,899', 'btu448A': 9032},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3, 'referModelNumber': 'TS030XR404A3', 'evapCoil': 'LED052BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,369', 'btu448A': 9032},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3.5, 'referModelNumber': 'TS035XR404A2', 'evapCoil': 'LED124BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,415', 'btu448A': 10930},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3.5, 'referModelNumber': 'TS035XR404A2', 'evapCoil': 'LED072BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,573', 'btu448A': 10930},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3.5, 'referModelNumber': 'TS035XR404A3', 'evapCoil': 'LED124BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,415', 'btu448A': 10930},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 3.5, 'referModelNumber': 'TS035XR404A3', 'evapCoil': 'LED072BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '5,573', 'btu448A': 10930},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 4.5, 'referModelNumber': 'TS045XR404A2', 'evapCoil': 'LED157BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,878', 'btu448A': 13490},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 4.5, 'referModelNumber': 'TS045XR404A2', 'evapCoil': 'LED072BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '6,065', 'btu448A': 13490},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 4.5, 'referModelNumber': 'TS045XR404A3', 'evapCoil': 'LED157BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '5,878', 'btu448A': 13490},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 4.5, 'referModelNumber': 'TS045XR404A3', 'evapCoil': 'LED072BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '6,065', 'btu448A': 13490},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 5.5, 'referModelNumber': 'TS055XR404A2', 'evapCoil': 'LED176BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '6,247', 'btu448A': 16245},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 5.5, 'referModelNumber': 'TS055XR404A2', 'evapCoil': 'LED081BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '6,469', 'btu448A': 16245},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 5.5, 'referModelNumber': 'TS055XR404A3', 'evapCoil': 'LED176BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '6,247', 'btu448A': 16245},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 5.5, 'referModelNumber': 'TS055XR404A3', 'evapCoil': 'LED081BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '6,469', 'btu448A': 16245},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 6, 'referModelNumber': 'TS060XR404A3', 'evapCoil': 'LED225BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '6,645', 'btu448A': 19880},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 6, 'referModelNumber': 'TS060XR404A3', 'evapCoil': 'LED114BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '7,480', 'btu448A': 19880},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 7.5, 'referModelNumber': 'TS075XR404A3', 'evapCoil': 'LED244BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '10,118', 'btu448A': 24460},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 7.5, 'referModelNumber': 'TS075XR404A3', 'evapCoil': 'LED124BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '11,300', 'btu448A': 24460},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 10, 'referModelNumber': 'TS100XR404A3', 'evapCoil': 'LED273BENM', 'qtyEvapCoil': 1, 'referSysTotalCost': '12,039', 'btu448A': 31540},
        {'boxType': 'freezer', 'referBrand': 'Turbo Air', 'horsePower': 10, 'referModelNumber': 'TS100XR404A3', 'evapCoil': 'LED157BENX', 'qtyEvapCoil': 2, 'referSysTotalCost': '13,164', 'btu448A': 31540}
    ]
    
    # Initialize manager and load data
    manager = TurboAirDataManager()
    df = manager.load_raw_data(raw_data)
    
    print("\n" + "="*70)
    print("TURBO AIR REFRIGERATION DATA SUMMARY")
    print("="*70)
    stats = manager.get_summary_stats()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    return manager


if __name__ == "__main__":
    manager = main()
    
    # Export the organized data
    manager.export_data('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.csv', format='csv')
    manager.export_data('/mnt/user-data/outputs/Turbo_Air_Refrigeration_Systems.xlsx', format='excel')
    
    print("\n✓ Turbo Air data organization complete!")
    print("  Files saved: Turbo_Air_Refrigeration_Systems.csv, Turbo_Air_Refrigeration_Systems.xlsx")
