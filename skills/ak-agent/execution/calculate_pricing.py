#!/usr/bin/env python3
"""
AmeriKooler (AK) Walk-In Quote Pricing Calculator

Applies 1.25x markup with $50 rounding for customer quotes.

AK Pricing Rules:
  - AK provides a SINGLE net price (box + freight + accessories combined)
  - Net Price x 1.25, round to nearest $50 = Customer Quote
  - No separate Walk-In/Freight/Options breakdown
"""

import argparse
import json
import sys


def round_to_nearest_50(amount):
    """Round amount to nearest $50."""
    return round(amount / 50) * 50


def calculate_pricing(net_price):
    """
    Calculate customer pricing for AmeriKooler walk-in quote.

    AK Rule: Single net price x 1.25, then round to $50.

    Args:
        net_price: The single net price from AK quote (includes box + freight + accessories)

    Returns:
        dict with pricing breakdown
    """
    raw_markup = net_price * 1.25
    customer_quote = round_to_nearest_50(raw_markup)

    return {
        "net_price": net_price,
        "raw_markup": raw_markup,
        "customer_quote": customer_quote,
    }


def format_currency(amount):
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def print_quote(pricing):
    """Print formatted customer quote."""
    print()
    print("=" * 50)
    print("AK (AMERIKOOLER) QUOTE PRICING")
    print("=" * 50)

    print()
    print("VENDOR COST:")
    print("-" * 50)
    print(f"  Vendor Cost:         {format_currency(pricing['net_price']):>14}")
    print()
    print(f"  >>> CUSTOMER PRICE (1.25x):  {format_currency(pricing['customer_quote'])} <<<")
    print(f"                       {'=' * 14}")

    print()
    print("=" * 50)

    # Calculation details
    print()
    print("Calculation Details:")
    print(f"  Vendor Cost:          {format_currency(pricing['net_price'])}")
    print(f"  x1.25:               {format_currency(pricing['raw_markup'])}")
    print(f"  Rounded ($50):        {format_currency(pricing['customer_quote'])}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Calculate AmeriKooler customer pricing with 1.25x markup"
    )
    parser.add_argument(
        "--net-price",
        type=float,
        required=True,
        help="Net price from AK quote (single combined price)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text",
    )

    args = parser.parse_args()

    # Calculate pricing
    pricing = calculate_pricing(args.net_price)

    if args.json:
        print(json.dumps(pricing, indent=2))
    else:
        print_quote(pricing)


if __name__ == "__main__":
    main()
