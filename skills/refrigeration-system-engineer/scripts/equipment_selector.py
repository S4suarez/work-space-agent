"""
Refrigeration System Engineer - Equipment Selection
Automated equipment selection for walk-in coolers and freezers
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class RefrigerationSystemEngineer:
    """
    Main class for refrigeration equipment selection and cost analysis
    """
    
    def __init__(self, btu_table_path: str):
        """Initialize with BTU requirements table"""
        self.btu_table = pd.read_csv(btu_table_path)
        self.markup_multiplier = 1.25  # 25% markup
        
    def calculate_btu_requirement(self, 
                                  box_type: str, 
                                  width: float, 
                                  depth: float) -> Tuple[int, str, bool]:
        """
        Calculate BTU requirement for given box
        
        Returns: (btu_required, box_size, is_exact_match)
        """
        # Format box size
        box_size = f"{int(width)}x{int(depth)}"
        
        # Try exact match
        match = self.btu_table[
            (self.btu_table['boxType'] == box_type) &
            (self.btu_table['boxSize'] == box_size)
        ]
        
        if len(match) > 0:
            return match.iloc[0]['requiredBTU'], box_size, True
        
        # Try reversed dimensions (8x10 = 10x8)
        box_size_rev = f"{int(depth)}x{int(width)}"
        match = self.btu_table[
            (self.btu_table['boxType'] == box_type) &
            (self.btu_table['boxSize'] == box_size_rev)
        ]
        
        if len(match) > 0:
            return match.iloc[0]['requiredBTU'], box_size_rev, True
        
        # No exact match - need to round up
        # Parse all sizes and find next larger
        table_sizes = self.btu_table[
            self.btu_table['boxType'] == box_type
        ]['boxSize'].values
        
        # Extract width and depth from each size
        candidates = []
        for size_str in table_sizes:
            try:
                w, d = map(int, size_str.split('x'))
                # Size must be larger in BOTH dimensions
                if w >= width and d >= depth:
                    candidates.append((w, d, w * d, size_str))
            except:
                continue
        
        if len(candidates) == 0:
            # Box larger than table - estimate
            raise ValueError(f"Box size {width}x{depth} exceeds standard table. "
                           f"Manual calculation required.")
        
        # Sort by area and take smallest
        candidates.sort(key=lambda x: x[2])
        next_size = candidates[0][3]
        
        match = self.btu_table[
            (self.btu_table['boxType'] == box_type) &
            (self.btu_table['boxSize'] == next_size)
        ]
        
        return match.iloc[0]['requiredBTU'], next_size, False
    
    def determine_evaporator_quantity(self, width: float, depth: float) -> int:
        """
        Determine required number of evaporator coils
        
        Rule: 2 coils if either dimension > 30 feet
        """
        return 2 if (width > 30 or depth > 30) else 1
    
    def select_equipment(self,
                        vendor_data: pd.DataFrame,
                        box_type: str,
                        required_btu: int,
                        required_evap_qty: int,
                        vendor_name: str = "Vendor") -> Optional[Dict]:
        """
        Select appropriate equipment from vendor data
        
        Returns dict with equipment details or None if no match
        """
        
        # Filter by box type
        candidates = vendor_data[vendor_data['box_type'] == box_type].copy()
        
        if len(candidates) == 0:
            return None
        
        # Filter by evaporator series (ADR for cooler, LED for freezer)
        if box_type == 'cooler':
            candidates = candidates[
                candidates['evaporator_model'].str.startswith('ADR', na=False)
            ]
        else:  # freezer
            candidates = candidates[
                candidates['evaporator_model'].str.startswith('LED', na=False)
            ]
        
        # Filter by evaporator quantity
        candidates = candidates[
            candidates['evaporator_qty'] == required_evap_qty
        ]
        
        # Filter by BTU capacity (NEVER go under)
        candidates = candidates[
            candidates['btu_rating_448a'] >= required_btu
        ]
        
        if len(candidates) == 0:
            return None
        
        # Sort by BTU (smallest that meets requirement) then cost
        candidates = candidates.sort_values(
            ['btu_rating_448a', 'total_system_cost']
        )
        
        # Get best option
        best = candidates.iloc[0]
        
        # Calculate customer pricing
        vendor_cost = best['total_system_cost']
        customer_price = vendor_cost * self.markup_multiplier
        markup_amount = customer_price - vendor_cost
        
        return {
            'vendor': vendor_name,
            'condensing_unit_model': best['condensing_unit_model'],
            'horsepower': best['horsepower'],
            'evaporator_model': best['evaporator_model'],
            'evaporator_qty': int(best['evaporator_qty']),
            'system_btu': int(best['btu_rating_448a']),
            'vendor_cost': float(vendor_cost),
            'customer_price': float(customer_price),
            'markup_amount': float(markup_amount),
            'meets_requirement': best['btu_rating_448a'] >= required_btu,
            'oversizing_pct': ((best['btu_rating_448a'] - required_btu) / required_btu * 100)
        }
    
    def generate_recommendation(self,
                               box_type: str,
                               width: float,
                               depth: float,
                               vendor_systems: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate complete equipment recommendation
        
        vendor_systems: dict of {vendor_name: dataframe}
        """
        
        # Step 1: Calculate BTU requirement
        required_btu, box_size_used, is_exact = self.calculate_btu_requirement(
            box_type, width, depth
        )
        
        # Step 2: Determine evaporator quantity
        required_evap_qty = self.determine_evaporator_quantity(width, depth)
        
        # Step 3: Select equipment from each vendor
        vendor_options = {}
        for vendor_name, vendor_data in vendor_systems.items():
            selection = self.select_equipment(
                vendor_data,
                box_type,
                required_btu,
                required_evap_qty,
                vendor_name
            )
            if selection:
                vendor_options[vendor_name] = selection
        
        return {
            'box_specifications': {
                'type': box_type,
                'external_width': width,
                'external_depth': depth,
                'box_size': f"{int(width)}x{int(depth)}",
                'box_size_used_for_btu': box_size_used,
                'is_exact_match': is_exact
            },
            'btu_requirements': {
                'required_btu': required_btu,
                'evaporator_qty_needed': required_evap_qty,
                'dual_coil_reason': 'Dimension exceeds 30 feet' if required_evap_qty == 2 else None
            },
            'vendor_options': vendor_options,
            'recommendation': self._pick_best_option(vendor_options) if vendor_options else None
        }
    
    def _pick_best_option(self, vendor_options: Dict) -> str:
        """Pick recommended vendor based on price"""
        if not vendor_options:
            return None
        
        # Sort by customer price
        sorted_vendors = sorted(
            vendor_options.items(),
            key=lambda x: x[1]['customer_price']
        )
        
        best_vendor = sorted_vendors[0][0]
        
        if len(sorted_vendors) > 1:
            price_diff = sorted_vendors[1][1]['customer_price'] - sorted_vendors[0][1]['customer_price']
            return f"{best_vendor} (${price_diff:,.0f} less than next option)"
        
        return best_vendor
    
    def format_recommendation(self, recommendation: Dict) -> str:
        """Format recommendation as readable text"""
        
        output = []
        
        # Header
        box_specs = recommendation['box_specifications']
        output.append(f"Walk-In {box_specs['type'].title()} Equipment Selection")
        output.append("=" * 60)
        output.append("")
        
        # Box specifications
        output.append("Box Specifications:")
        output.append(f"  Type: {box_specs['type'].title()}")
        output.append(f"  External Dimensions: {box_specs['external_width']}' × {box_specs['external_depth']}'")
        
        btu_req = recommendation['btu_requirements']
        output.append(f"  Required BTU: {btu_req['required_btu']:,} BTU")
        
        if not box_specs['is_exact_match']:
            output.append(f"  Note: Using {box_specs['box_size_used_for_btu']} table value (rounded up)")
        
        if btu_req['evaporator_qty_needed'] == 2:
            output.append(f"  Note: {btu_req['dual_coil_reason']} - using dual evaporator configuration")
        
        output.append("")
        
        # Vendor options
        vendor_opts = recommendation['vendor_options']
        
        if not vendor_opts:
            output.append("❌ No suitable equipment found for these requirements")
            return "\n".join(output)
        
        # Show each vendor option
        for i, (vendor_name, equipment) in enumerate(vendor_opts.items(), 1):
            prefix = "RECOMMENDED " if vendor_name == recommendation['recommendation'].split()[0] else ""
            output.append(f"{prefix}Option {i} - {vendor_name.upper()}:")
            output.append(f"  Condensing Unit: {equipment['condensing_unit_model']} ({equipment['horsepower']} HP)")
            output.append(f"  Evaporator{'s' if equipment['evaporator_qty'] > 1 else ''}: "
                         f"{equipment['evaporator_model']} × {equipment['evaporator_qty']}")
            output.append(f"  System Capacity: {equipment['system_btu']:,} BTU "
                         f"({'✓' if equipment['meets_requirement'] else '✗'} "
                         f"{equipment['oversizing_pct']:.1f}% over requirement)")
            output.append("")
            output.append("  Pricing:")
            output.append(f"    Vendor Cost: ${equipment['vendor_cost']:,.2f}")
            output.append(f"    Customer Price: ${equipment['customer_price']:,.2f}")
            output.append(f"    Markup: ${equipment['markup_amount']:,.2f} (25%)")
            output.append("")
        
        # Recommendation
        if recommendation['recommendation']:
            output.append(f"💡 RECOMMENDATION: {recommendation['recommendation']}")
        
        return "\n".join(output)


def example_usage():
    """Example of how to use the RefrigerationSystemEngineer"""
    
    # Initialize engineer
    engineer = RefrigerationSystemEngineer('BTU_Requirements_Standard.csv')
    
    # Load vendor data (example - would come from skills)
    turbo_air_data = pd.read_csv('Turbo_Air_Refrigeration_Systems.csv')
    
    # Single box recommendation
    recommendation = engineer.generate_recommendation(
        box_type='cooler',
        width=8,
        depth=10,
        vendor_systems={'Turbo Air': turbo_air_data}
    )
    
    # Format and display
    print(engineer.format_recommendation(recommendation))


if __name__ == "__main__":
    example_usage()
