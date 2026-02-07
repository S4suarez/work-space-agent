# AK (AmeriKooler) Quote CSV Field Definitions

**CSV Location:** `C:/Users/bnmsu/ak_quotes_data.csv`

## Field Reference

| Field | Description | Example |
|-------|-------------|---------|
| PDF_Filename | Original uploaded PDF filename | `26-02170-quote.pdf` |
| AK Vendor Extract | Always "AmeriKooler" | `AmeriKooler` |
| Quote # | AK quote number (XX-XXXXX format) | `26-02170` |
| SHIP TO ZIP | Delivery zip code (from freight dest) | `36067` |
| State | Destination state (from freight dest) | `AL` |
| Customer Job | Project name from quote | `Big Star AB172969` |
| Dimensions and Basic Description | Overall dims with type/location | `6'-0" x 20'-0" x 7'-6" Outdoor Cooler` |
| Floor(s) | Floor specification | `NSF vinyl screed` or `Floorless` |
| Doors | Access door specifications | `(1) Standard 36" x 76" Left hinged flush door` |
| Net Price | Single combined price (box+freight+accessories) | `$10,498.00` |
| Quote Date | Quote creation date | `01/23/2026` |
| Good Thru | Expiration date (quote date + 30 days) | `02/22/2026` |
| Type | Cooler or Freezer | `Cooler` |
| Display Doors | Glass door info or None | `None` or `Glass Doors By Others - Net Opening: 123.125" x 75"` |
| Pass Thru Doors | Pass-through door count | `0` |
| Shape | Box shape | `Rectangular` |
| Location | Indoor or Outdoor | `Outdoor` |
| Combo | Combination box (Y/N) | `N` |
| Accessories | Listed accessories (semicolon-separated) | `(120) Rain roof membrane...; (7) DRAIN HOOD...` |
| Revision | Quote revision number if present | `` or `1` |
| Lead Time | Manufacturing lead time | `3 weeks` |

## Data Rules

- **Unique Identifier**: Quote # + Quote Date as composite key
- **Append Mode**: Always append new records, never overwrite existing data
- **Numeric Fields**: Must be properly formatted before CSV write
- **Currency Field**: Net Price formatted as `$X,XXX.00`
- **Date Fields**: Use MM/DD/YYYY format
- **Good Thru**: Calculated as Quote Date + 30 days (AK quotes valid 30 days)

## CSV Header Row

```csv
PDF_Filename,AK Vendor Extract,Quote #,SHIP TO ZIP,State,Customer Job,Dimensions and Basic Description,Floor(s),Doors,Net Price,Quote Date,Good Thru,Type,Display Doors,Pass Thru Doors,Shape,Location,Combo,Accessories,Revision,Lead Time
```

## Key Differences from CCI CSV

| Feature | CCI CSV | AK CSV |
|---------|---------|--------|
| Vendor field | `CCI Vendor Extract` | `AK Vendor Extract` |
| ID field | `Tag #` (CC359210) | `Quote #` (26-02170) |
| Pricing | Walk-In Price + Freight Estimate + Subtotal | Net Price (single) |
| Weight | `Est. Box Weight` | Not available |
| Sq. Ft. | `Approx. Sq. Ft.` | Not available |
| Reach-In | `Reach-In` field | Not tracked |
| Accessories | Not tracked | `Accessories` field |
| Revision | Not tracked | `Revision` field |
| Lead Time | Not tracked | `Lead Time` field |

## Data Purpose

This data will be used for:
- Historical quote analysis
- Cost optimization studies
- Regional freight pattern analysis
- Size vs. cost efficiency studies
- Vendor comparison (AK vs CCI)
- Seasonal pricing trends
- Customer cost-saving recommendations
