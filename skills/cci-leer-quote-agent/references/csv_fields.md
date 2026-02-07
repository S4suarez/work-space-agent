# CCI/LEER Quote CSV Field Definitions

**CSV Location:** `C:/Users/bnmsu/cci_quotes_data.csv`

## Field Reference

| Field | Description | Example |
|-------|-------------|---------|
| PDF_Filename | Original uploaded PDF filename | `Caffe_AB172882-Quote.pdf` |
| CCI Vendor Extract | Always "CCI" or "LEER" or "Carroll" | `LEER` |
| Tag # | CCI quote tag number | `CC359210` |
| SHIP TO ZIP | Delivery zip code | `39740` |
| State | Destination state (derive from context) | `MS` |
| Customer Job | Project/job name | `Caffe AB172882` |
| Dimensions and Basic Description | Full size with type | `12' x 10' x 8' Freezer (-10°)` |
| Floor(s) | Floor specification | `.050 Smooth Aluminium 4 5/8" STD Floor` |
| Doors | Door specifications | `(HD1) 34" x 76 1/4" Overlap Mount, LH` |
| Walk-In Price | Base walk-in box price | `$10,488.00` |
| Freight Estimate | Freight cost | `$2,081.00` |
| Subtotal | Walk-In + Freight + Options | `$12,569.00` |
| Approx. Sq. Ft. | Square footage | `592` |
| Est. Box Weight | Weight in pounds | `3576 lbs` |
| Good Thru | Quote expiration date | `02/22/2026` |
| Quote Date | Quote creation date | `01/23/2026` |
| Type | Cooler or Freezer | `Freezer` |
| Display Doors | Glass door callouts (GD1, GD2, etc.) | `None` or `GD1: (6) 30"x79" DDS 1200` |
| Pass Thru Doors | Pass-through door count | `0` or `2` |
| Shape | Box shape | `Square` or `Rectangular` |
| Location | Indoor or Outdoor | `Indoor` |
| Combo | Combination box (Y/N) | `N` |
| Reach-In | Reach-in configuration (Y/N) | `N` |

## Data Rules

- **Unique Identifier**: Tag # + Quote Date as composite key
- **Append Mode**: Always append new records, never overwrite existing data
- **Numeric Fields**: Must be properly formatted before CSV write
- **Currency Fields**: Walk-In Price, Freight Estimate, Subtotal formatted as `$X,XXX.00`
- **Date Fields**: Use MM/DD/YYYY format

## CSV Header Row

```csv
PDF_Filename,CCI Vendor Extract,Tag #,SHIP TO ZIP,State,Customer Job,Dimensions and Basic Description,Floor(s),Doors,Walk-In Price,Freight Estimate,Subtotal,Approx. Sq. Ft.,Est. Box Weight,Good Thru,Quote Date,Type,Display Doors,Pass Thru Doors,Shape,Location,Combo,Reach-In
```

## Data Purpose

This data will be used for:
- Historical quote analysis
- Cost optimization studies
- Regional freight pattern analysis
- Size vs. cost efficiency studies
- Seasonal pricing trends
- Customer cost-saving recommendations (future feature, 50+ quotes recommended)
