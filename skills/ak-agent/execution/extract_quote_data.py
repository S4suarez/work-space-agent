#!/usr/bin/env python3
"""
AmeriKooler (AK) Quote PDF Data Extractor

Extracts structured data from AmeriKooler quote PDFs.
Outputs JSON matching the CSV schema for downstream storage.

AK PDF Structure:
  Page 1: Quote header, dimensions, door, floor, finishes
  Page 2: Equipment, accessories, freight, price, "Glass Doors By Others"
  Page 3: Engineering drawings with panel layout and net openings

NOTE: Regex patterns will need refinement as real PDFs are processed.
Update patterns here and document changes in UPDATES.md.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta

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


def extract_quote_number(text):
    """
    Extract AK quote number (e.g., 26-02170, 25-36839).
    Format: XX-XXXXX (2 digits, dash, 5 digits)
    """
    patterns = [
        r"Quote\s*#\s*:\s*(\d{2}-\d{5})",
        r"Quote\s*Number\s*:\s*(\d{2}-\d{5})",
        r"\b(\d{2}-\d{5})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_quote_date(text):
    """Extract quote date from header."""
    patterns = [
        r"Date\s*:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            # Try to normalize to MM/DD/YYYY
            try:
                for fmt in ("%m/%d/%Y", "%B %d, %Y", "%B %d,%Y"):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime("%m/%d/%Y")
                    except ValueError:
                        continue
            except Exception:
                pass
            return date_str
    return None


def calculate_good_thru(quote_date_str):
    """Calculate Good Thru date (quote date + 30 days). AK quotes valid for 30 days."""
    if not quote_date_str:
        return None
    try:
        dt = datetime.strptime(quote_date_str, "%m/%d/%Y")
        good_thru = dt + timedelta(days=30)
        return good_thru.strftime("%m/%d/%Y")
    except ValueError:
        return None


def extract_project_name(text):
    """Extract project name from quote."""
    pattern = r"Project\s*Name\s*:\s*(.+?)(?:\n|Quoted)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_revision(text):
    """Extract revision number if present."""
    pattern = r"Revision\s*:\s*(\d+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def extract_lead_time(text):
    """Extract lead time."""
    pattern = r"Lead\s*Time\s*:\s*(\d+\s*weeks?)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def extract_overall_dimensions(text):
    """
    Extract overall (outside) dimensions from AK quote.
    Format: W'-W" x D'-D" x H'-H" (Rectangular/Square)
    Example: 6'-0" x 20'-0" x 7'-6"
    Returns the full dimension string.
    """
    pattern = r"Actual\s*Overall\s*Dimension\s*:\s*([\d'\"x\s\-\.]+(?:\((?:Rectangular|Square)\))?)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_dimensions_parsed(text):
    """
    Extract W, D, H as separate values from overall dimensions.
    Returns tuple (width, depth, height) as strings.
    """
    pattern = r"Actual\s*Overall\s*Dimension\s*:\s*(\d+['\-\"\s\d]*)\s*x\s*(\d+['\-\"\s\d]*)\s*x\s*(\d+['\-\"\s\d]*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip(), match.group(3).strip()
    return None, None, None


def extract_interior_dimensions(text):
    """Extract interior dimensions."""
    pattern = r"Interior\s*Dim\s*:\s*([\d'\"x\s\-\.]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_description(text):
    """Extract description (Indoor/Outdoor Cooler/Freezer, Floorless, etc.)."""
    pattern = r"Description\s*:\s*(.+?)(?:\n|Interior)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_type(text):
    """Determine if cooler or freezer."""
    desc = extract_description(text) or ""
    full_text = desc + " " + text[:2000]

    if re.search(r"\bfreezer\b", full_text, re.IGNORECASE):
        return "Freezer"
    if re.search(r"\bcooler\b", full_text, re.IGNORECASE):
        return "Cooler"
    return None


def extract_location(text):
    """Determine indoor or outdoor installation."""
    desc = extract_description(text) or ""
    full_text = desc + " " + text[:2000]

    if re.search(r"\boutdoor\b", full_text, re.IGNORECASE):
        return "Outdoor"
    if re.search(r"\bindoor\b", full_text, re.IGNORECASE):
        return "Indoor"
    return None


def extract_door(text):
    """
    Extract door specification from AK quote.
    Example: (1) Standard 36" x 76" Left hinged flush door
    """
    pattern = r"Door\s*:\s*(.+?)(?:\n\n|\n[A-Z]|\n1\s*Lead)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        door_text = match.group(1).strip()
        # Clean up multi-line door descriptions
        door_text = re.sub(r"\s+", " ", door_text)
        return door_text
    return None


def extract_door_count(text):
    """Extract number of doors from door specification."""
    door = extract_door(text)
    if door:
        match = re.match(r"\((\d+)\)", door)
        if match:
            return int(match.group(1))
    return 0


def extract_floor(text):
    """Extract floor specification."""
    pattern = r"Floor\s*:\s*(.+?)(?:\n|Door)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Check for floorless in description
    if re.search(r"\bfloorless\b", text, re.IGNORECASE):
        return "Floorless"
    return None


def extract_net_price(text):
    """
    Extract the single net price from AK quote.
    Format: Price: $XX,XXX.00 Net
    """
    pattern = r"Price\s*:\s*\$?([\d,]+\.?\d*)\s*Net"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).replace(",", "")
    # Fallback: just look for Price: $amount
    pattern = r"Price\s*:\s*\$?([\d,]+\.\d{2})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).replace(",", "")
    return None


def extract_freight_destination(text):
    """
    Extract freight destination info.
    Examples: "Delivered to GA-30339", "Freight included to AL-36067"
    """
    patterns = [
        r"(?:Delivered\s+to|Freight\s+included\s+to|freight\s+includes?\s+to)\s+([A-Z]{2}[\-\s]*\d{5})",
        r"(?:Delivered\s+to|Freight\s+included\s+to|freight\s+includes?\s+to)\s+([A-Z]{2}\.\s*\d{5})",
        r"(?:Delivered\s+to|Freight\s+included\s+to|freight\s+includes?\s+to)\s+(.+?)(?:\n|#)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_ship_to_zip(text):
    """Extract shipping zip code from freight destination."""
    dest = extract_freight_destination(text)
    if dest:
        zip_match = re.search(r"(\d{5})", dest)
        if zip_match:
            return zip_match.group(1)
    return None


def extract_state(text):
    """Extract state from freight destination."""
    dest = extract_freight_destination(text)
    if dest:
        state_match = re.search(r"\b([A-Z]{2})\b", dest)
        if state_match:
            return state_match.group(1)
    return None


def extract_accessories(text):
    """
    Extract accessories list from AK quote.
    Accessories are listed on page 2 with quantities.
    """
    accessories = []
    # Look for Accessories section
    pattern = r"Accessories\s*:\s*(.+?)(?=Equipment|Freight|Price|\Z)"
    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    for match in matches:
        # Split by newlines and clean up
        lines = match.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("Accessories"):
                # Clean up the line
                line = re.sub(r"\s+", " ", line)
                if len(line) > 5:  # Skip very short fragments
                    accessories.append(line)
    return accessories


def detect_glass_doors_by_others(text):
    """
    Detect if 'Glass Doors By Others' is present in the quote.
    This is the DDS trigger for AK quotes.
    """
    return bool(re.search(r"Glass\s+Doors?\s+By\s+Others", text, re.IGNORECASE))


def extract_net_opening(text):
    """
    Extract net opening dimensions from drawing annotations.
    Example: Net Opening 123.125" x 75"
    """
    pattern = r"Net\s+Opening\s+([\d\.]+)\s*\"?\s*x\s*([\d\.]+)\s*\"?"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return {
            "width": match.group(1),
            "height": match.group(2),
            "description": f'{match.group(1)}" x {match.group(2)}"',
        }
    return None


def extract_display_door_cutouts(text):
    """
    Extract display door cutout annotations from drawings.
    Example: (5) 30x79 display doors
    """
    cutouts = []
    pattern = r"\((\d+)\)\s*(\d+)\s*x\s*(\d+)\s*(display\s+doors?|glass\s+doors?)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    for m in matches:
        cutouts.append(
            {
                "quantity": int(m[0]),
                "width": m[1],
                "height": m[2],
                "description": f"({m[0]}) {m[1]}x{m[2]} {m[3]}",
            }
        )
    return cutouts


def determine_shape(text):
    """Determine box shape from overall dimensions or explicit label."""
    if re.search(r"\bSquare\b", text):
        return "Square"
    if re.search(r"\bRectangular\b", text):
        return "Rectangular"
    # Try to determine from dimensions
    w, d, h = extract_dimensions_parsed(text)
    if w and d:
        try:
            # Compare just the feet portion
            w_ft = int(re.match(r"(\d+)", w).group(1))
            d_ft = int(re.match(r"(\d+)", d).group(1))
            return "Square" if w_ft == d_ft else "Rectangular"
        except (ValueError, AttributeError):
            pass
    return None


def extract_all(pdf_path):
    """
    Extract all quote data from AK PDF.
    Returns dict with all fields matching CSV schema.
    """
    import os

    text = extract_text_from_pdf(pdf_path)
    filename = os.path.basename(pdf_path)

    quote_date = extract_quote_date(text)
    box_type = extract_type(text)
    overall_dims = extract_overall_dimensions(text)
    description = extract_description(text)
    location = extract_location(text)

    # Build dimension description
    dim_desc = None
    if overall_dims:
        type_str = f" {box_type}" if box_type else ""
        loc_str = f" {location}" if location else ""
        dim_desc = f"{overall_dims}{loc_str}{type_str}"

    # Detect DDS items
    glass_doors_by_others = detect_glass_doors_by_others(text)
    net_opening = extract_net_opening(text)
    door_cutouts = extract_display_door_cutouts(text)

    # Format display doors for CSV
    dd_str = "None"
    if glass_doors_by_others:
        dd_parts = ["Glass Doors By Others"]
        if net_opening:
            dd_parts.append(f"Net Opening: {net_opening['description']}")
        if door_cutouts:
            for cutout in door_cutouts:
                door_temp = "HH" if box_type == "Cooler" else "LT" if box_type == "Freezer" else "?"
                dd_parts.append(f"{cutout['description']} ({door_temp})")
        dd_str = " - ".join(dd_parts)

    # Count pass-thru doors
    pass_thru = len(re.findall(r"\bpass[\s-]*thru\b", text, re.IGNORECASE))

    # Accessories
    accessories = extract_accessories(text)

    result = {
        "PDF_Filename": filename,
        "AK_Vendor_Extract": "AmeriKooler",
        "Quote_Number": extract_quote_number(text),
        "Ship_To_Zip": extract_ship_to_zip(text),
        "State": extract_state(text),
        "Customer_Job": extract_project_name(text),
        "Dimensions_Description": dim_desc,
        "Overall_Dimensions": overall_dims,
        "Interior_Dimensions": extract_interior_dimensions(text),
        "Description": description,
        "Floors": extract_floor(text),
        "Doors": extract_door(text),
        "Door_Count": extract_door_count(text),
        "Net_Price": extract_net_price(text),
        "Quote_Date": quote_date,
        "Good_Thru": calculate_good_thru(quote_date),
        "Type": box_type,
        "Location": location,
        "Display_Doors": dd_str,
        "Display_Doors_By_Others": glass_doors_by_others,
        "Net_Opening": net_opening,
        "Door_Cutouts": door_cutouts,
        "Pass_Thru_Doors": str(pass_thru),
        "Shape": determine_shape(text),
        "Combo": "N",
        "Accessories": "; ".join(accessories) if accessories else "None",
        "Revision": extract_revision(text),
        "Lead_Time": extract_lead_time(text),
        "Freight_Destination": extract_freight_destination(text),
        "Raw_Text": text[:3000],  # First 3000 chars for debugging
    }

    # Check for combo box
    if re.search(r"\bcombo\b", text, re.IGNORECASE):
        result["Combo"] = "Y"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Extract data from AmeriKooler quote PDFs"
    )
    parser.add_argument(
        "--pdf-path",
        type=str,
        required=True,
        help="Path to the AmeriKooler quote PDF file",
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
    critical_fields = [
        "Quote_Number",
        "Net_Price",
        "Quote_Date",
        "Type",
        "Location",
        "Dimensions_Description",
    ]
    missing = [k for k in critical_fields if not result.get(k)]
    if missing:
        print(f"\nWARNING: Missing critical fields: {', '.join(missing)}", file=sys.stderr)

    # Flag Glass Doors By Others for DDS agent
    if result.get("Display_Doors_By_Others"):
        print(
            "\nGLASS DOORS BY OTHERS DETECTED.",
            file=sys.stderr,
        )
        if result.get("Net_Opening"):
            print(
                f"Net Opening: {result['Net_Opening']['description']}",
                file=sys.stderr,
            )
        if result.get("Door_Cutouts"):
            for cutout in result["Door_Cutouts"]:
                print(f"Cutout: {cutout['description']}", file=sys.stderr)
        else:
            print(
                "No door cutout annotations found in drawing. Ask user for door details.",
                file=sys.stderr,
            )
        print("Invoke dds-agent skill for door pricing.", file=sys.stderr)


if __name__ == "__main__":
    main()
