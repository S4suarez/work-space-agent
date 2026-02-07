#!/usr/bin/env python3
"""
AmeriKooler (AK) Quote CSV Handler

Manages CSV data storage for AmeriKooler quote records.
Supports append, read, and count operations.
Checks for duplicates using Quote # + Quote Date as composite key.

Default CSV path: C:/Users/bnmsu/ak_quotes_data.csv
"""

import argparse
import csv
import json
import os
import sys

DEFAULT_CSV_PATH = r"C:\Users\bnmsu\ak_quotes_data.csv"

CSV_HEADERS = [
    "PDF_Filename",
    "AK Vendor Extract",
    "Quote #",
    "SHIP TO ZIP",
    "State",
    "Customer Job",
    "Dimensions and Basic Description",
    "Floor(s)",
    "Doors",
    "Net Price",
    "Quote Date",
    "Good Thru",
    "Type",
    "Display Doors",
    "Pass Thru Doors",
    "Shape",
    "Location",
    "Combo",
    "Accessories",
    "Revision",
    "Lead Time",
]

# Maps JSON keys from extract_quote_data.py to CSV headers
FIELD_MAP = {
    "PDF_Filename": "PDF_Filename",
    "AK_Vendor_Extract": "AK Vendor Extract",
    "Quote_Number": "Quote #",
    "Ship_To_Zip": "SHIP TO ZIP",
    "State": "State",
    "Customer_Job": "Customer Job",
    "Dimensions_Description": "Dimensions and Basic Description",
    "Floors": "Floor(s)",
    "Doors": "Doors",
    "Net_Price": "Net Price",
    "Quote_Date": "Quote Date",
    "Good_Thru": "Good Thru",
    "Type": "Type",
    "Display_Doors": "Display Doors",
    "Pass_Thru_Doors": "Pass Thru Doors",
    "Shape": "Shape",
    "Location": "Location",
    "Combo": "Combo",
    "Accessories": "Accessories",
    "Revision": "Revision",
    "Lead_Time": "Lead Time",
}


def ensure_csv_exists(csv_path):
    """Create CSV file with headers if it doesn't exist."""
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
        print(f"Created new CSV file: {csv_path}", file=sys.stderr)


def check_duplicate(csv_path, quote_number, quote_date):
    """Check if a record with same Quote # + Quote Date already exists."""
    if not os.path.exists(csv_path):
        return False

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Quote #") == quote_number and row.get("Quote Date") == quote_date:
                return True
    return False


def map_data_to_csv_row(data):
    """Map JSON data keys to CSV header format."""
    row = {}
    for json_key, csv_header in FIELD_MAP.items():
        value = data.get(json_key, "")
        if value is None:
            value = ""
        # Format currency field
        if csv_header == "Net Price":
            if value and not str(value).startswith("$"):
                try:
                    value = f"${float(value):,.2f}"
                except (ValueError, TypeError):
                    pass
        row[csv_header] = str(value)
    return row


def append_record(csv_path, data):
    """
    Append a quote record to the CSV file.

    Args:
        csv_path: Path to CSV file
        data: Dict with quote data (JSON keys from extract_quote_data.py)

    Returns:
        tuple (success: bool, message: str)
    """
    ensure_csv_exists(csv_path)

    quote_num = data.get("Quote_Number") or data.get("Quote #", "")
    date = data.get("Quote_Date") or data.get("Quote Date", "")

    # Check for duplicates
    if quote_num and date and check_duplicate(csv_path, quote_num, date):
        return False, f"Duplicate record: Quote #{quote_num} / Date {date} already exists"

    row = map_data_to_csv_row(data)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)

    count = count_records(csv_path)
    return True, f"Record appended. Total records: {count}"


def read_records(csv_path, last_n=10):
    """
    Read recent records from CSV.

    Args:
        csv_path: Path to CSV file
        last_n: Number of most recent records to return

    Returns:
        list of dicts
    """
    if not os.path.exists(csv_path):
        return []

    records = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))

    return records[-last_n:] if last_n else records


def count_records(csv_path):
    """Count total records in CSV (excluding header)."""
    if not os.path.exists(csv_path):
        return 0

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        return sum(1 for _ in reader)


def main():
    parser = argparse.ArgumentParser(description="AmeriKooler Quote CSV Handler")
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["append", "read", "count"],
        help="Action to perform: append, read, or count",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="{}",
        help="JSON data for append action",
    )
    parser.add_argument(
        "--csv-path",
        type=str,
        default=DEFAULT_CSV_PATH,
        help=f"Path to CSV file (default: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument(
        "--last-n",
        type=int,
        default=10,
        help="Number of recent records to read (default: 10)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    if args.action == "append":
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON for --data: {args.data}", file=sys.stderr)
            sys.exit(1)

        success, message = append_record(args.csv_path, data)
        if args.json:
            print(json.dumps({"success": success, "message": message}))
        else:
            status = "OK" if success else "SKIPPED"
            print(f"[{status}] {message}")

        if not success:
            sys.exit(1)

    elif args.action == "read":
        records = read_records(args.csv_path, args.last_n)
        if args.json:
            print(json.dumps(records, indent=2))
        else:
            if not records:
                print("No records found.")
            else:
                print(f"Last {len(records)} record(s):")
                print("-" * 80)
                for i, rec in enumerate(records, 1):
                    quote = rec.get("Quote #", "N/A")
                    date = rec.get("Quote Date", "N/A")
                    desc = rec.get("Dimensions and Basic Description", "N/A")
                    price = rec.get("Net Price", "N/A")
                    print(f"  {i}. Quote #{quote} | {date} | {desc} | {price}")
                print("-" * 80)

    elif args.action == "count":
        count = count_records(args.csv_path)
        if args.json:
            print(json.dumps({"count": count}))
        else:
            print(f"Total records: {count}")


if __name__ == "__main__":
    main()
