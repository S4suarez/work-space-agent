#!/usr/bin/env python3
"""
DDS Door Pricing Calculator
Applies 1.25x markup and rounds to nearest $50 for customer quotes
"""

import argparse


def round_to_nearest_50(amount):
    """Round amount to nearest $50"""
    return round(amount / 50) * 50


def calculate_door_pricing(base_door_cost, quantity, base_freight_cost):
    """
    Calculate DDS door pricing with markup and rounding

    Args:
        base_door_cost: Base cost per door/window before markup
        quantity: Total number of doors/windows
        base_freight_cost: Base freight cost (exact or estimated)

    Returns:
        dict with itemized pricing
    """
    # Calculate base totals
    total_door_cost_base = base_door_cost * quantity

    # Apply 1.25x markup
    door_cost_with_markup = total_door_cost_base * 1.25
    freight_with_markup = base_freight_cost * 1.25

    # Round to nearest $50
    door_cost_rounded = round_to_nearest_50(door_cost_with_markup)
    freight_rounded = round_to_nearest_50(freight_with_markup)

    # Calculate total
    total = door_cost_rounded + freight_rounded

    return {
        'base_door_cost': base_door_cost,
        'quantity': quantity,
        'total_door_cost_base': total_door_cost_base,
        'door_cost_with_markup': door_cost_with_markup,
        'door_cost_rounded': door_cost_rounded,
        'base_freight_cost': base_freight_cost,
        'freight_with_markup': freight_with_markup,
        'freight_rounded': freight_rounded,
        'total': total
    }


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"


def print_quote(pricing):
    """Print formatted customer quote"""
    print("\n" + "="*50)
    print("DDS CUSTOMER QUOTE")
    print("="*50)
    print(f"\nDDS Doors Cost: {format_currency(pricing['door_cost_rounded'])}")
    print(f"DDS Freight:    {format_currency(pricing['freight_rounded'])}")
    print("-" * 50)
    print(f"Total:          {format_currency(pricing['total'])}")
    print("\n" + "="*50)

    # Optional: Show calculation details
    print("\nCalculation Details:")
    print(f"  Base Cost per Unit: {format_currency(pricing['base_door_cost'])}")
    print(f"  Quantity: {pricing['quantity']}")
    print(f"  Base Door Total: {format_currency(pricing['total_door_cost_base'])}")
    print(f"  Door Cost (1.25x markup): {format_currency(pricing['door_cost_with_markup'])}")
    print(f"  Door Cost (rounded to $50): {format_currency(pricing['door_cost_rounded'])}")
    print(f"  Base Freight: {format_currency(pricing['base_freight_cost'])}")
    print(f"  Freight (1.25x markup): {format_currency(pricing['freight_with_markup'])}")
    print(f"  Freight (rounded to $50): {format_currency(pricing['freight_rounded'])}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Calculate DDS door pricing with markup')
    parser.add_argument('--base-cost', type=float, required=True,
                        help='Base cost per door/window before markup')
    parser.add_argument('--quantity', type=int, required=True,
                        help='Total number of doors/windows')
    parser.add_argument('--freight', type=float, required=True,
                        help='Freight cost (exact or estimated)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON instead of formatted text')

    args = parser.parse_args()

    pricing = calculate_door_pricing(args.base_cost, args.quantity, args.freight)

    if args.json:
        import json
        print(json.dumps(pricing, indent=2))
    else:
        print_quote(pricing)


if __name__ == '__main__':
    main()
