# Work Space Agent

**First Upload: February 6, 2026**

This is my first push to GitHub! This repository contains my AI agent framework for Bush Refrigeration operations.

## Overview

A 3-layer architecture that separates concerns to maximize reliability:

1. **Layer 1: Directives** - SOPs written in Markdown (inside each skill's `skill.md`)
2. **Layer 2: Orchestration** - AI decision-making and routing
3. **Layer 3: Execution** - Deterministic Python scripts (inside each skill's `execution/` or `scripts/`)

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
├── README.md              # This file
└── skills/                # Claude Code custom skills
    ├── ak-agent/
    │   ├── skill.md       # Directives/SOP
    │   ├── execution/     # Python scripts
    │   └── references/    # Reference data
    ├── cci-leer-quote-agent/
    ├── dds-agent/
    ├── refrigeration-system-engineer/
    └── turbo-air-refrigeration/
```

## Local Setup

Skills are backed up here but **must also exist** in `~/.claude/skills/` for Claude Code to use them.

To restore skills to a new machine:
```bash
cp -r skills/* ~/.claude/skills/
```

## Author

Bush Refrigeration - Camden, NJ
