# Turbo Air Model Nomenclature Guide

## Condensing Unit Model Numbers

### Cooler Models (Medium Temperature)

**Format:** `TS###MR404A#[A][-T]`

**Breakdown:**
- `TS` = Turbo Air Series
- `###` = Horsepower × 10
  - `006` = 0.5 HP
  - `008` = 0.75 HP
  - `010` = 1 HP
  - `015` = 1.5 HP
  - `020` = 2 HP
  - `025` = 2.5 HP
  - `030` = 3 HP
  - `040` = 4 HP
  - `050` = 5 HP
  - `060` = 6 HP
  - `075` = 7.5 HP
  - `100` = 10 HP
- `M` = Medium temperature (cooler designation)
- `R404A` = Refrigerant type (R-404A/R-448A/R-449A compatible)
- `#` = Generation
  - `2` = Single phase (208-230V/60Hz/1Ph)
  - `3` = Three phase (208-230V/60Hz/3Ph)
- `A` = Scroll compressor designation (newer models)
- `-T` = Timer included (older models, being phased out)

**Examples:**
- `TS020MR404A2A` = 2 HP, Medium temp, Single phase, Scroll compressor
- `TS050MR404A3A` = 5 HP, Medium temp, Three phase, Scroll compressor
- `TS030MR404A2-T` = 3 HP, Medium temp, Single phase, With timer (older)

### Freezer Models (Low Temperature)

**Format:** `TS###XR404A#[A]`

**Breakdown:**
- Same as coolers except:
- `X` = Low temperature (freezer designation)
- No `-T` suffix (freezer models don't use timers)

**Examples:**
- `TS020XR404A2A` = 2 HP, Freezer, Single phase, Scroll compressor
- `TS055XR404A3A` = 5.5 HP, Freezer, Three phase, Scroll compressor

### Compressor Types

**Models WITH "A" suffix:**
- Scroll compressors
- Newer product line
- Better efficiency
- Most common in current pricing

**Models WITHOUT "A" suffix:**
- Reciprocating compressors (smaller units)
- Scroll compressors without explicit designation (larger units)
- Mixed in current product line

**Models WITH "-T" suffix:**
- Timer functionality included
- Being phased out
- Not in current OEM pricing lists

## Evaporator Model Numbers

### Standard Air Defrost Coils (ADR Series)

**Format:** `ADR###AEN[C/M/X]`

**Breakdown:**
- `ADR` = Air Defrost, Refrigerant coil
- `###` = Approximate BTU capacity ÷ 100
  - `060` = ~6,000 BTU
  - `089` = ~8,900 BTU
  - `112` = ~11,200 BTU
  - `125` = ~12,500 BTU
  - `137` = ~13,700 BTU
  - `171` = ~17,100 BTU
  - `191` = ~19,100 BTU
  - `258` = ~25,800 BTU
  - `325` = ~32,500 BTU
  - `352` = ~35,200 BTU
  - `392` = ~39,200 BTU
- `A` = Series designation
- `EN` = EC Motor, No frost
- Suffix:
  - `C` = Digital temperature Controller (current standard)
  - `M` = Manual operation with solenoid valve (older)
  - `X` = Multi-coil configuration (older designation for dual/triple coils)

**Examples:**
- `ADR112AENC` = 11,200 BTU, EC motor, Digital controller
- `ADR258AENC` = 25,800 BTU, EC motor, Digital controller

### LED-Lit Electric Defrost Coils (LED Series)

**Format:** `LED###BEN[C/M/X]`

**Breakdown:**
- `LED` = LED-lit Electric Defrost
- `###` = Approximate BTU capacity ÷ 100
  - `036` = ~3,600 BTU
  - `052` = ~5,200 BTU
  - `072` = ~7,200 BTU
  - `081` = ~8,100 BTU
  - `090` = ~9,000 BTU
  - `114` = ~11,400 BTU
  - `124` = ~12,400 BTU
  - `157` = ~15,700 BTU
  - `176` = ~17,600 BTU
  - `225` = ~22,500 BTU
  - `244` = ~24,400 BTU
  - `273` = ~27,300 BTU
- `B` = Series designation
- `EN` = EC Motor, No frost
- Suffix (same as ADR):
  - `C` = Digital controller (current)
  - `M` = Manual with solenoid (older)
  - `X` = Multi-coil configuration (older)

**Examples:**
- `LED052BENC` = 5,200 BTU, LED-lit, EC motor, Digital controller
- `LED176BENC` = 17,600 BTU, LED-lit, EC motor, Digital controller

## Evolution of Model Numbers

### 2024-2025 Transition

**Condensing Units:**
1. Timer removal: `-T` suffix being phased out
2. Scroll compressor: "A" suffix added to designate scroll models
3. Example: `TS020MR404A2-T` → `TS020MR404A2A`

**Evaporators:**
1. Controller upgrade: `M` and `X` → `C` (digital controller standard)
2. Example: `LED052BENM` → `LED052BENC`
3. Example: `ADR112AENX` → `ADR112AENC`

### Why the Changes?

**Timer Removal (-T):**
- Electronic controls replacing mechanical timers
- Improves reliability
- Reduces maintenance
- Cost savings

**Scroll Compressor Designation (A):**
- Clear identification of compressor type
- Important for service and parts
- Efficiency rating differentiation

**Digital Controller (C):**
- More precise temperature control
- Better defrost management
- Diagnostics capability
- Energy efficiency

## Quick Reference by Horsepower

### Coolers (Medium Temp)

| HP | Current Model (1Ph) | Current Model (3Ph) | Common Evaporators |
|----|---------------------|---------------------|-------------------|
| 0.5 | TS006MR404A2 | - | ADR060AENC |
| 0.75 | TS008MR404A2 | - | ADR089AENC, LED052BENC |
| 1.0 | TS010MR404A2 | - | ADR112AENC, LED072BENC |
| 1.5 | TS015MR404A2A | TS015MR404A3A | ADR125AENC, LED081BENC |
| 2.0 | TS020MR404A2A | TS020MR404A3A | ADR137AENC, LED114BENC |
| 2.5 | TS025MR404A2A | TS025MR404A3A | ADR171AENC, LED124BENC |
| 3.0 | TS030MR404A2 | TS030MR404A3 | ADR258AENC, LED176BENC |
| 4.0 | TS040MR404A2 | TS040MR404A3 | ADR325AENC, LED225BENC |
| 5.0 | TS050MR404A2A | TS050MR404A3A | ADR392AENC, LED273BENC |
| 6.0 | - | TS060MR404A3 | ADR191AENX (×2) |
| 7.5 | - | TS075MR404A3 | ADR258AENX (×2) |
| 10 | - | TS100MR404A3 | ADR352AENX (×3) |

### Freezers (Low Temp)

| HP | Current Model (1Ph) | Current Model (3Ph) | Common Evaporators |
|----|---------------------|---------------------|-------------------|
| 1.0 | TS010XR404A2 | - | LED052BENC |
| 1.5 | TS015XR404A2 | TS015XR404A3 | LED072BENC |
| 2.0 | TS020XR404A2A | TS020XR404A3A | LED081BENC |
| 2.5 | TS025XR404A2A | TS025XR404A3A | LED090BENC |
| 3.0 | TS030XR404A2A | TS030XR404A3A | LED114BENC |
| 3.5 | TS035XR404A2A | TS035XR404A3A | LED124BENC |
| 4.5 | TS045XR404A2A | TS045XR404A3A | LED157BENC |
| 5.5 | TS055XR404A2A | TS055XR404A3A | LED176BENC |
| 6.0 | - | TS060XR404A3A | LED225BENC |
| 7.5 | - | TS075XR404A3A | LED244BENC |
| 10 | - | TS100XR404A3 | LED273BENC |
