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

### Tech Stack

**Backend**: FastAPI (async, high performance)
- Tesseract OCR (free, open-source, no API costs)
- Pydantic for schema validation
- Pillow for image processing
- PyPDF2 for PDF text extraction

**Frontend**: Vanilla HTML/CSS/JS (minimal, fast)
- Single-page upload interface
- No build tools or dependencies
- Client-side form handling + async fetch

**Deployment**: Render (free tier)
- Single Python web service
- Efficient resource usage
- Cold start optimized

### Design Decisions

- **HTML/CSS output** instead of PDF generation — easier to iterate on layout and typography
- **Self-contained** (no external assets except fonts) — single file to download/email
- **No JavaScript in output** — plain HTML + CSS, works offline after first load
- **FastAPI backend** for high-performance async processing
- **Tesseract OCR** (free, no API calls)
- **Lightweight frontend** (no frameworks, vanilla JS)
- **Image optimization** before processing (Pillow resizing to reduce payload)

## Project Structure

```
sift/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── recipe_parser.py        # Extract recipe from screenshot/PDF/text
│   ├── weight_converter.py      # Convert volumes to grams
│   ├── html_renderer.py        # Generate self-contained HTML
│   ├── image_handler.py        # Optimize images with Pillow
│   └── schemas.py              # Pydantic models
├── data/
│   └── weight_chart.json       # King Arthur Baking DB (~325 items)
├── frontend/
│   ├── index.html              # Upload/paste UI
│   ├── style.css               # Print-friendly styles
│   └── script.js               # Form handling + fetch API
├── tests/
│   ├── test_parser.py
│   ├── test_converter.py
│   └── fixtures/               # Sample recipes & expected outputs
├── requirements.txt            # Python dependencies
├── .gitignore
├── Dockerfile                  # Render deployment
├── render.yaml                 # Render configuration
└── README.md
```

## Getting Started

[Instructions coming soon]

## Development

- Develop on feature branches (prefixed with `claude/`)
- Commit with clear, descriptive messages
- Push to your feature branch when changes are complete
