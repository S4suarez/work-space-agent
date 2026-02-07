#!/usr/bin/env python3
"""
CCI/LEER Walk-In Quote Pricing Calculator

Applies 1.25x markup with $50 rounding for customer quotes.

CCI Pricing Rules:
  - BASE: (Walk-In + Freight) combined, then x1.25, round to $50
  - OPTIONS: Each option individually x1.25, round to $50
  - Options are NEVER combined with base pricing
"""

import argparse
import json
import sys


def round_to_nearest_50(amount):
    """Round amount to nearest $50."""
    return round(amount / 50) * 50


def calculate_base_pricing(walkin_price, freight):
    """
    Calculate customer base pricing for CCI/LEER walk-in quote.

    CCI Rule: Walk-In + Freight combined FIRST, then x1.25, then round to $50.

    Args:
        walkin_price: Base walk-in box price from CCI quote
        freight: Freight estimate from CCI quote

    Returns:
        dict with base pricing breakdown
    """
    base_subtotal = walkin_price + freight
    raw_markup = base_subtotal * 1.25
    customer_base = round_to_nearest_50(raw_markup)

    return {
        "walkin_price": walkin_price,
        "freight": freight,
        "base_subtotal": base_subtotal,
        "raw_markup": raw_markup,
        "customer_base_quote": customer_base,
    }


def calculate_option_pricing(name, price):
    """
    Calculate customer pricing for a single option.

    Each option is marked up individually: price x1.25, round to $50.

    Args:
        name: Option description
        price: Option price from CCI quote

    Returns:
        dict with option pricing breakdown
    """
    raw_markup = price * 1.25
    customer_price = round_to_nearest_50(raw_markup)

    return {
        "name": name,
        "leer_price": price,
        "raw_markup": raw_markup,
        "customer_price": customer_price,
    }


def format_currency(amount):
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def print_quote(base, options):
    """Print formatted customer quote."""
    print()
    print("=" * 50)
    print("CCI/LEER QUOTE PRICING")
    print("=" * 50)

    print()
    print("VENDOR COST:")
    print("-" * 50)
    print(f"  Walk-In Box:        {format_currency(base['walkin_price']):>14}")
    print(f"  Freight Estimate:   {format_currency(base['freight']):>14}")
    print(f"                      {'-' * 14}")
    print(f"  Vendor Cost:        {format_currency(base['base_subtotal']):>14}")
    print()
    print(f"  >>> CUSTOMER PRICE (1.25x):  {format_currency(base['customer_base_quote'])} <<<")
    print(f"                      {'=' * 14}")

    if options:
        print()
        print("OPTIONAL ADD-ONS (priced separately):")
        print("-" * 50)
        for opt in options:
            print(f"  {opt['name']}:")
            print(f"    Vendor Cost:      {format_currency(opt['leer_price']):>14}")
            print(f"    Customer Price (1.25x): {format_currency(opt['customer_price']):>10}")
            print()

    print("=" * 50)

    # Calculation details
    print()
    print("Calculation Details:")
    print(f"  Walk-In Price:        {format_currency(base['walkin_price'])}")
    print(f"  Freight Estimate:     {format_currency(base['freight'])}")
    print(f"  Vendor Cost:          {format_currency(base['base_subtotal'])}")
    print(f"  x1.25:               {format_currency(base['raw_markup'])}")
    print(f"  Rounded ($50):       {format_currency(base['customer_base_quote'])}")
    if options:
        for opt in options:
            print(f"  Option '{opt['name']}':")
            print(f"    Vendor Cost:        {format_currency(opt['leer_price'])}")
            print(f"    x1.25:              {format_currency(opt['raw_markup'])}")
            print(f"    Rounded ($50):      {format_currency(opt['customer_price'])}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Calculate CCI/LEER customer pricing with 1.25x markup"
    )
    parser.add_argument(
        "--walkin-price",
        type=float,
        required=True,
        help="Walk-in box price from CCI quote",
    )
    parser.add_argument(
        "--freight",
        type=float,
        required=True,
        help="Freight estimate from CCI quote",
    )
    parser.add_argument(
        "--options",
        type=str,
        default="[]",
        help='JSON array of options: [{"name":"desc","price":550}]',
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text",
    )

    args = parser.parse_args()

    # Parse options
    try:
        options_input = json.loads(args.options)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON for --options: {args.options}", file=sys.stderr)
        sys.exit(1)

    # Calculate base pricing
    base = calculate_base_pricing(args.walkin_price, args.freight)

    # Calculate option pricing
    options = []
    for opt in options_input:
        if "name" not in opt or "price" not in opt:
            print(
                f"Error: Each option must have 'name' and 'price' keys: {opt}",
                file=sys.stderr,
            )
            sys.exit(1)
        options.append(calculate_option_pricing(opt["name"], float(opt["price"])))

    if args.json:
        result = {"base": base, "options": options}
        print(json.dumps(result, indent=2))
    else:
        print_quote(base, options)


if __name__ == "__main__":
    main()
