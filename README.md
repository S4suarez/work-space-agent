# Work Space Agent

**First Upload: February 6, 2026**

This is my first push to GitHub! This repository contains my AI agent framework for Bush Refrigeration operations.

## Overview

A 3-layer architecture that separates concerns to maximize reliability:

1. **Layer 1: Directives** - SOPs written in Markdown (`directives/`)
2. **Layer 2: Orchestration** - AI decision-making and routing
3. **Layer 3: Execution** - Deterministic Python scripts (`execution/`)

## Skills

Custom Claude Code skills for refrigeration industry workflows:

| Skill | Description |
|-------|-------------|
| `ak-agent` | AmeriKooler walk-in box quote validation and pricing |
| `cci-leer-quote-agent` | CCI/Carroll/LEER quote validation and pricing |
| `dds-agent` | DDS display door pricing, freight quotes, net openings |
| `refrigeration-system-engineer` | Equipment selection and BTU calculations |
| `turbo-air-refrigeration` | Turbo Air equipment data management |

## Directory Structure

```
├── CLAUDE.md              # Agent instructions
├── directives/            # SOP markdown files
├── execution/             # Python scripts
├── references/            # Reference data files
└── skills/                # Claude Code custom skills
    ├── ak-agent/
    ├── cci-leer-quote-agent/
    ├── dds-agent/
    ├── refrigeration-system-engineer/
    └── turbo-air-refrigeration/
```

## Author

Bush Refrigeration - Camden, NJ
