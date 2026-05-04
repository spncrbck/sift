from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from typing import Optional

from .recipe_parser import parse_recipe, extract_text_from_image, extract_text_from_pdf
from .html_renderer import render_recipe

app = FastAPI(title="Sift")


@app.post("/convert")
async def convert(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    pdf: Optional[UploadFile] = File(None),
):
    if text and text.strip():
        raw = text
    elif image:
        raw = extract_text_from_image(await image.read())
    elif pdf:
        raw = extract_text_from_pdf(await pdf.read())
    else:
        raise HTTPException(status_code=400, detail="Provide text, image, or PDF.")

    recipe = parse_recipe(raw)
    html = render_recipe(recipe)
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in recipe.title)
    filename = f"{safe_title or 'recipe'}.html"

    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
