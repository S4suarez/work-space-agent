#!/usr/bin/env python3
"""
CCI/LEER Quote PDF Data Extractor

Extracts structured data from CCI/Carroll Coolers/LEER quote PDFs.
Outputs JSON matching the CSV schema for downstream storage.

NOTE: Regex patterns will need refinement as real PDFs are processed.
Update patterns here and document changes in the directive/UPDATES.md.
"""

import argparse
import json
import re
import sys
from datetime import datetime

try:
    from pypdf import PdfReader
except ImportError:
    print(
        "Error: pypdf is required. Install with: pip install pypdf",
        file=sys.stderr,
    )
    sys.exit(1)


def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        sys.exit(1)


def extract_tag_number(text):
    """Extract CCI tag/quote number (e.g., CC359210)."""
    patterns = [
        r"(?:Tag|Quote|Ref)[\s#:]*([A-Z]{2}\d{5,7})",
        r"\b(CC\d{5,7})\b",
        r"(?:Quote\s*Number|Tag\s*Number)[\s:]*(\S+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_dimensions(text):
    """
    Extract dimensions (WxDxH) from quote text.
    Returns tuple (width, depth, height) as strings with units.
    """
    patterns = [
        r"(\d+)['\s]*[xX×]\s*(\d+)['\s]*[xX×]\s*(\d+)['\s]*",
        r"(\d+)\s*ft?\s*[xX×]\s*(\d+)\s*ft?\s*[xX×]\s*(\d+)\s*ft?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1), match.group(2), match.group(3)
    return None, None, None


def extract_type(text):
    """Determine if cooler or freezer."""
    freezer_indicators = [
        r"\bfreezer\b",
        r"\blow\s*temp\b",
        r"\bLT\b",
        r"-\d+\s*[°]?\s*[fF]",
    ]
    cooler_indicators = [
        r"\bcooler\b",
        r"\bhigh\s*humid\b",
        r"\bHH\b",
        r"\b35\s*[°]?\s*[fF]\b",
    ]

    freezer_count = sum(
        1 for p in freezer_indicators if re.search(p, text, re.IGNORECASE)
    )
    cooler_count = sum(
        1 for p in cooler_indicators if re.search(p, text, re.IGNORECASE)
    )

    if freezer_count > cooler_count:
        return "Freezer"
    elif cooler_count > freezer_count:
        return "Cooler"
    return None


def extract_location(text):
    """Determine indoor or outdoor installation."""
    if re.search(r"\boutdoor\b", text, re.IGNORECASE):
        return "Outdoor"
    if re.search(r"\bindoor\b", text, re.IGNORECASE):
        return "Indoor"
    return None


def extract_doors(text):
    """
    Extract door specifications.
    Returns list of door descriptions.
    """
    doors = []
    # Match patterns like (HD1) 34" x 76 1/4" or (HD1) 34"x76.25"
    pattern = r"\(HD\d+\)\s*(\d+[\s\d/]*\"?\s*[xX×]\s*\d+[\s\d/]*\"?[^,\n]*)"
    matches = re.findall(pattern, text)
    for m in matches:
        doors.append(f"(HD{len(doors)+1}) {m.strip()}")

    if not doors:
        # Try simpler door pattern
        pattern = r"(?:door|entry)[\s:]*(\d+\"?\s*[xX×]\s*\d+[\s\d/]*\"?)"
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            doors.append(m.strip())

    return doors


def extract_display_doors(text):
    """
    Extract glass display door callouts (GD1, GD2, etc.).
    Returns list of dicts with quantity, size, model.
    """
    display_doors = []
    pattern = r"\(GD(\d+)\)\s*\((\d+)\)\s*(\d+\"?\s*[xX×]\s*\d+\"?)\s*(DDS\s*\d+\w*)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    for m in matches:
        display_doors.append(
            {
                "callout": f"GD{m[0]}",
                "quantity": int(m[1]),
                "size": m[2].strip(),
                "model": m[3].strip(),
            }
        )
    return display_doors


def extract_prices(text):
    """Extract Walk-In Price, Freight, and Subtotal."""
    result = {}

    # Walk-In Price
    pattern = r"(?:Walk[\s-]*In|Box)[\s]*(?:Price|Cost)?[\s:]*\$?([\d,]+\.?\d*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        result["walkin_price"] = match.group(1).replace(",", "")

    # Freight
    pattern = r"(?:Freight|Shipping)[\s]*(?:Estimate|Cost)?[\s:]*\$?([\d,]+\.?\d*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        result["freight"] = match.group(1).replace(",", "")

    # Subtotal
    pattern = r"(?:Sub[\s-]*total|Total)[\s:]*\$?([\d,]+\.?\d*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        result["subtotal"] = match.group(1).replace(",", "")

    return result


def extract_dates(text):
    """Extract quote date and good-thru date."""
    result = {}

    # Quote date
    pattern = r"(?:Quote\s*Date|Date)[\s:]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        result["quote_date"] = match.group(1)

    # Good thru
    pattern = r"(?:Good\s*Thru|Valid\s*(?:Through|Until)|Expires?)[\s:]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        result["good_thru"] = match.group(1)

    return result


def extract_floor(text):
    """Extract floor specification."""
    pattern = r"(?:Floor|Flooring)[\s:]*([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Look for floorless
    if re.search(r"\bfloorless\b", text, re.IGNORECASE):
        return "Floorless"
    return None


def extract_ship_to_zip(text):
    """Extract shipping zip code."""
    pattern = r"(?:Ship\s*To|Delivery|Destination)[\s:]*.*?(\d{5}(?:-\d{4})?)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def extract_sq_ft(text):
    """Extract approximate square footage."""
    pattern = r"(?:Approx|Sq\.?\s*Ft\.?|Square\s*F(?:oo|ee)t)[\s:]*(\d+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def extract_weight(text):
    """Extract estimated box weight."""
    pattern = r"(?:Weight|Est\.?\s*(?:Box\s*)?Weight)[\s:]*(\d+[\d,]*)\s*(?:lbs?|pounds?)?"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).replace(",", "")
    return None


def extract_options(text):
    """Extract options/add-ons from quote."""
    options = []
    # Look for options section
    pattern = r"(?:Option|Add[\s-]*On|Upgrade)[\s:]*([^\n]+?)[\s]*\$?([\d,]+\.?\d*)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    for name, price in matches:
        if price:
            options.append({"name": name.strip(), "price": price.replace(",", "")})
    return options


def determine_shape(width, depth):
    """Determine if box is square or rectangular."""
    if width and depth:
        try:
            w, d = int(width), int(depth)
            return "Square" if w == d else "Rectangular"
        except ValueError:
            pass
    return None


def extract_all(pdf_path):
    """
    Extract all quote data from PDF.
    Returns dict with all fields matching CSV schema.
    """
    import os

    text = extract_text_from_pdf(pdf_path)
    filename = os.path.basename(pdf_path)

    width, depth, height = extract_dimensions(text)
    box_type = extract_type(text)
    prices = extract_prices(text)
    dates = extract_dates(text)
    doors = extract_doors(text)
    display_doors = extract_display_doors(text)
    options = extract_options(text)

    # Build dimension description
    dim_desc = None
    if width and depth and height:
        type_suffix = f" {box_type}" if box_type else ""
        dim_desc = f"{width}' x {depth}' x {height}'{type_suffix}"

    # Format display doors for CSV
    dd_str = "None"
    if display_doors:
        dd_parts = []
        for dd in display_doors:
            dd_parts.append(
                f"{dd['callout']}: ({dd['quantity']}) {dd['size']} {dd['model']}"
            )
        dd_str = "; ".join(dd_parts)

    # Count pass-thru doors
    pass_thru = len(re.findall(r"\bpass[\s-]*thru\b", text, re.IGNORECASE))

    result = {
        "PDF_Filename": filename,
        "CCI_Vendor_Extract": "LEER",
        "Tag_Number": extract_tag_number(text),
        "Ship_To_Zip": extract_ship_to_zip(text),
        "State": None,  # Derived from context or zip lookup
        "Customer_Job": None,  # Derived from context
        "Dimensions_Description": dim_desc,
        "Width": width,
        "Depth": depth,
        "Height": height,
        "Floors": extract_floor(text),
        "Doors": "; ".join(doors) if doors else None,
        "Door_Count": len(doors),
        "Walk_In_Price": prices.get("walkin_price"),
        "Freight_Estimate": prices.get("freight"),
        "Subtotal": prices.get("subtotal"),
        "Approx_Sq_Ft": extract_sq_ft(text),
        "Est_Box_Weight": extract_weight(text),
        "Good_Thru": dates.get("good_thru"),
        "Quote_Date": dates.get("quote_date"),
        "Type": box_type,
        "Display_Doors": dd_str,
        "Display_Doors_Detail": display_doors,
        "Pass_Thru_Doors": str(pass_thru),
        "Shape": determine_shape(width, depth),
        "Location": extract_location(text),
        "Combo": "N",  # Default, update if combo detected
        "Reach_In": "N",  # Default, update if reach-in detected
        "Options": options,
        "Raw_Text": text[:2000],  # First 2000 chars for debugging
    }

    # Check for combo box
    if re.search(r"\bcombo\b", text, re.IGNORECASE):
        result["Combo"] = "Y"

    # Check for reach-in
    if re.search(r"\breach[\s-]*in\b", text, re.IGNORECASE):
        result["Reach_In"] = "Y"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Extract data from CCI/LEER quote PDFs"
    )
    parser.add_argument(
        "--pdf-path",
        type=str,
        required=True,
        help="Path to the CCI/LEER quote PDF file",
    )
    parser.add_argument(
        "--raw-text",
        action="store_true",
        help="Also output raw extracted text for debugging",
    )

    args = parser.parse_args()

    result = extract_all(args.pdf_path)

    if not args.raw_text:
        result.pop("Raw_Text", None)

    print(json.dumps(result, indent=2))

    # Summary of what was found vs missing
    missing = [k for k, v in result.items() if v is None]
    if missing:
        print(f"\nWARNING: Missing fields: {', '.join(missing)}", file=sys.stderr)

    # Flag display doors for DDS agent
    if result.get("Display_Doors_Detail"):
        print(
            f"\nDISPLAY DOORS DETECTED: {len(result['Display_Doors_Detail'])} callout(s) found.",
            file=sys.stderr,
        )
        print("Invoke dds-agent skill for door pricing.", file=sys.stderr)


if __name__ == "__main__":
    main()
