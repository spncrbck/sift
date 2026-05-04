from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from typing import Optional
import logging

from .recipe_parser import parse_recipe, extract_text_from_image, extract_text_from_pdf
from .html_renderer import render_recipe

app = FastAPI(title="Sift")
logger = logging.getLogger(__name__)


@app.post("/convert")
async def convert(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    pdf: Optional[UploadFile] = File(None),
):
    try:
        if text and text.strip():
            logger.info("Processing text input")
            raw = text
        elif image:
            logger.info(f"Processing image: {image.filename}")
            raw = extract_text_from_image(await image.read())
            logger.info(f"OCR complete, extracted {len(raw)} chars")
        elif pdf:
            logger.info(f"Processing PDF: {pdf.filename}")
            raw = extract_text_from_pdf(await pdf.read())
            logger.info(f"PDF extraction complete, extracted {len(raw)} chars")
        else:
            raise HTTPException(status_code=400, detail="Provide text, image, or PDF.")

        logger.info("Parsing recipe...")
        recipe = parse_recipe(raw)
        logger.info(f"Recipe parsed: {recipe.title} ({len(recipe.ingredients)} ingredients, {len(recipe.steps)} steps)")

        logger.info("Rendering HTML...")
        html = render_recipe(recipe)
        safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in recipe.title)
        filename = f"{safe_title or 'recipe'}.html"

        logger.info(f"Success: {filename} ({len(html)} bytes)")
        return Response(
            content=html,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception(f"Error processing recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process recipe: {str(e)}")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
