# CCI/LEER Quote Agent Updates

## v1.0 - Initial Release (2026-02-01)

### Skill Created
Initial release of the CCI/LEER Quote Agent skill with four core capabilities.

### Core Capabilities
1. **Quote Validation** - Verify CCI/LEER quotes against customer requests
   - Dimension checking with width/depth swap flexibility
   - Door quantity and size validation
   - Type (cooler/freezer) and location (indoor/outdoor) verification

2. **Pricing Calculator** - Customer pricing with 1.25x markup
   - Base pricing: (Walk-In + Freight) combined then x1.25, round to $50
   - Options pricing: Each option individually x1.25, round to $50
   - Script: `execution/calculate_pricing.py`

3. **Data Extraction & CSV Storage** - PDF parsing and record keeping
   - PDF text extraction via pypdf
   - Regex-based field parsing (will self-anneal with real PDF data)
   - CSV storage at `C:/Users/bnmsu/cci_quotes_data.csv`
   - Duplicate detection via Tag # + Quote Date composite key
   - Scripts: `execution/extract_quote_data.py`, `execution/csv_handler.py`

4. **DDS Door Detection** - Auto-invoke dds-agent for display doors
   - Detects GD# callouts (GD1, GD2, etc.) in quote text
   - Extracts door model, quantity, and size
   - Triggers `dds-agent` skill for door pricing automatically

### Files Created
- `skill.md` - Main skill definition with YAML frontmatter
- `execution/calculate_pricing.py` - CCI markup calculator
- `execution/extract_quote_data.py` - PDF data extractor
- `execution/csv_handler.py` - CSV append/read/count handler
- `references/csv_fields.md` - CSV field definitions
- `UPDATES.md` - This file

### Known Limitations
- PDF extraction patterns are initial estimates; will need refinement with real CCI/LEER quote PDFs
- State field requires manual input or zip code lookup (not yet automated)
- Customer Job field requires manual input from user context
