# DDS Freight Quote Request

## Goal
Generate a copy-paste ready email template for the DDS freight team requesting a freight quote for door shipments.

## Inputs
- Door quantities and models (cooler, freezer, pass-thru)
- Customer drop-off location (city, state, zip)

## Process
1. Collect door quantities by type from user
2. Map to proper model descriptions:
   - Cooler: DDS-A 1200E Cooler Door HH High Humidity 30x79-LED
   - Freezer: DDS-A 1200E Freezer Door Low Temp 30x79-LED
   - Pass-Thru: DDS Cooler Pass Thru Door High Humidity 36x81
3. Calculate total pieces
4. Format using template below

## Output Template
```
Hi DDS Team,
I would like to request a freight quote for:
(X) FREEZER Model 1200E LT 30x79
(X) Cooler Model 1200E HH 30x79
(X) Total pieces

Drop Off Location: [City, State ZIP]

Thank you, DDS Team!
```

## Edge Cases
- User will NOT provide dimensions/weight — DDS rep has this info
- Always use proper model descriptions in the template
- Keep format consistent for easy copy-paste
- Omit lines for door types with 0 quantity
- If pass-thru doors are included, add them as a separate line item

## Tools
- No execution scripts needed — this is a template generation task
