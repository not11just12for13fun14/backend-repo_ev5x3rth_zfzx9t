import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import ArticleInput, Article, LayoutTemplate

app = FastAPI(title="SamacharAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SamacharAI backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# ---- Utility: simple mock generation for now ----
# In a real deployment, you can swap this for an LLM provider.
def generate_article_from_input(inp: ArticleInput) -> Article:
    # Very light, deterministic mock to keep demo self-contained
    body = []
    if inp.bullets:
        body.append("Key developments:")
        for i, b in enumerate(inp.bullets, 1):
            body.append(f"{i}. {b}")
    body.append(
        "This story has been crafted in a {tone} tone for a {audience} audience,"
        .format(tone=inp.tone, audience=inp.audience)
        + " emphasizing clarity, context, and accuracy."
    )
    content = "\n\n".join(body)

    # headline and subhead suggestions
    base = inp.title.strip()
    headlines = [
        base,
        f"{base}: What You Need to Know",
        f"Explained | {base}",
    ]
    subheads = [
        "Context, impact, and what comes next",
        "A clear breakdown for busy readers",
    ]

    return Article(
        title=inp.title,
        content=content,
        language=inp.language,
        tone=inp.tone,
        audience=inp.audience,
        headlines=headlines,
        subheads=subheads,
    )

# ---- Endpoints ----

@app.post("/api/generate", response_model=Article)
def generate_article(inp: ArticleInput):
    article = generate_article_from_input(inp)
    # Persist the generated article
    if db is None:
        # Still return article so frontend can demo even without DB
        return article
    try:
        doc_id = create_document("article", article.model_dump())
        return article
    except Exception as e:
        # Log and still return
        return article

class SaveLayoutRequest(BaseModel):
    template: LayoutTemplate

@app.post("/api/layout/save")
def save_layout(req: SaveLayoutRequest):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    tid = create_document("layouttemplate", req.template.model_dump())
    return {"id": tid, "ok": True}

@app.get("/api/layout/templates")
def list_layouts(limit: int = 20):
    if db is None:
        return []
    docs = get_documents("layouttemplate", {}, limit)
    # Normalize _id to string
    for d in docs:
        if isinstance(d.get("_id"), ObjectId):
            d["id"] = str(d.pop("_id"))
    return docs
