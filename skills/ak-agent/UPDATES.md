# AK (AmeriKooler) Agent - Updates Log

## v1.0 - Initial Release (2026-02-02)

### Features
- **Quote Validation**: Verify AK quotes against customer requests (dimensions, doors, type, location)
- **Pricing Calculator**: Single net price x 1.25 markup with $50 rounding
- **PDF Data Extraction**: Regex-based extraction of AK quote fields
- **CSV Data Storage**: Separate CSV at `C:/Users/bnmsu/ak_quotes_data.csv` with 21 columns
- **DDS Door Detection**: Detects "Glass Doors By Others" trigger phrase
- **Net Opening Parsing**: Attempts to read net opening dimensions from engineering drawings
- **Door Cutout Detection**: Parses cutout annotations like "(5) 30x79 display doors"
- **Auto Door Type**: Maps cooler = HH doors, freezer = LT doors for DDS

### Known Limitations
- PDF text extraction via pypdf may not capture all drawing annotations
- Net opening dimensions from drawings may need manual confirmation
- Regex patterns may need refinement with more real-world AK PDFs
- AK does not provide sq. ft. or box weight data

### Files Created
- `skill.md` - Main skill definition with YAML frontmatter
- `execution/calculate_pricing.py` - AK pricing calculator (single price markup)
- `execution/extract_quote_data.py` - AK PDF data extractor
- `execution/csv_handler.py` - CSV storage handler
- `references/csv_fields.md` - CSV field definitions
- `UPDATES.md` - This file

### Architecture Notes
- Mirrors CCI agent structure for consistency
- Separate CSV from CCI (`ak_quotes_data.csv` vs `cci_quotes_data.csv`)
- Same 1.25x markup / $50 rounding as CCI but applied to single net price
- DDS integration via `dds-agent` skill (same as CCI)
- Accessories always included in net price (never separate options)
