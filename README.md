# SIFT — Recipe Reformatter

Transform messy recipes into beautifully formatted, color-coded recipe cards with automatic metric conversions.

## Overview

SIFT takes recipe input from screenshots, PDFs, or pasted text and transforms it into a self-contained HTML file that renders beautifully in the browser and prints cleanly to PDF. Every ingredient gets a unique pastel color that appears as a dot in the ingredient list and as a highlight pill in the directions. All volumes are automatically converted to grams using a comprehensive weight chart.

## Features

- Accept screenshot, PDF, or pasted recipe text as input
- Parse recipe into structured data (title, source, time, servings, ingredients, steps)
- Convert all volume measurements to metric (grams) via weight chart lookup
- Generate a single self-contained HTML output file
- Color-code ingredients for visual clarity
- Format with good typography and print-friendly layout
- Support metric + imperial dual amounts in ingredient list

## Output Format

- Single `.html` file with no external dependencies except Google Fonts
- Serif headings (Lora) and sans-serif body text (DM Sans)
- 2-column ingredient grid with colored dots
- Numbered directions with bolded quantities and colored ingredient pills
- Optimized for printing to PDF via browser print dialog
- ~0.5" margins, fits on one page when possible

## Color Palette

Pastel color sets cycle by ingredient index. Each set includes:
- Dot color (ingredient list)
- Pill background color (step highlights)
- Pill text color (contrast for readability)

## Weight Chart

Uses the King Arthur Baking ingredient database with ~325 items. Each entry includes teaspoon, tablespoon, cup, ounce, and gram equivalents. Conversions happen at render time; if no match is found, the metric column shows empty and only imperial amounts display.

## Technical Architecture

### Design Decisions

- **HTML/CSS output** instead of PDF generation — easier to iterate on layout and typography
- **Self-contained** (no external assets except fonts) — single file to download/email
- **No JavaScript in output** — plain HTML + CSS, works offline after first load
- **Python backend** for ingest → conversion → render pipeline
- **Canvas resizing** for images before API calls (keep payload under ~400KB)

## Getting Started

[Instructions coming soon]

## Development

- Develop on feature branches (prefixed with `claude/`)
- Commit with clear, descriptive messages
- Push to your feature branch when changes are complete
