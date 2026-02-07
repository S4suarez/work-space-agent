# DDS Net Opening Calculations

## Goal
Provide net cooler opening dimensions for a given door configuration, always showing both with and without wall panels.

## Inputs
- Number of doors
- Door width (default: 30" if not specified)

## Process
1. Determine door width (default 30")
2. Look up dimensions in `references/net-openings.md`
3. Always provide BOTH scenarios:
   - **Without Wall Panels** — net opening only
   - **With Wall Panels** — minimum rough opening including panels (30" wide only table)

## Output Format
```
For X doors (30" wide):

WITHOUT WALL PANELS:
Net Opening Width: XX' X-X/X"

WITH WALL PANELS INCLUDED:
Minimum Rough Opening Width: XX' X"
```

## Reference Data
- Load `references/dds-net-openings.md` for dimension lookup tables
- Available widths: 24", 26", 28", 30" (without panels)
- With-panels table is for 30" wide doors only

## Edge Cases
- Default to 30" wide doors unless user specifies otherwise
- Heights available: 67", 75", 79" (79" is most common)
- If user requests with-panels dimensions for non-30" doors, note that the with-panels table only covers 30" wide
- Maximum 30 doors in lookup table; for larger counts, inform user data is unavailable

## Tools
- No execution scripts needed — this is a reference lookup task
