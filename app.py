"""
Enterprise RAG - Backend FastAPI
"""
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.pgvector import PgVector

# ─── Config ───────────────────────────────────────────────────────────────────
DB_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_xujFI96zlkSr@ep-delicate-base-agzt2gjt-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require")
DOCS_DIR = Path(__file__).parent / "enterprise_docs"
DOCS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".txt", ".csv"}

# ─── Agno Setup ───────────────────────────────────────────────────────────────
knowledge_base = Knowledge(
    vector_db=PgVector(table_name="enterprise_documents", db_url=DB_URL),
    max_results=5,
)

rag_agent = Agent(
    name="Assistente Aziendale",
    role=(
        "Sei l'assistente AI aziendale. Ricerca SEMPRE le informazioni nei documenti ufficiali "
        "prima di rispondere. Se l'informazione non è nei documenti, di' chiaramente che non è "
        "disponibile nella knowledge base e usa la ricerca web solo per informazioni generali. "
        "Rispondi sempre in italiano e indica le fonti."
    ),
    knowledge=knowledge_base,
    tools=[DuckDuckGoTools()],
    search_knowledge=True,
    markdown=True,
)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(title="Enterprise RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str


# --- Onboarding Demo Models ---
class OnboardingRequest(BaseModel):
    nome_dipendente: str
    ruolo: str
    seniority: str

class OnboardingResponse(BaseModel):
    plan_text: str

# --- Hiring Demo Models ---
class JDRequest(BaseModel):
    role: str
    brief: str

class JDResponse(BaseModel):
    jd_text: str

class CVScoreRequest(BaseModel):
    jd_text: str
    cv_text: str

class CVScoreResult(BaseModel):
    match_score: int
    candidato_ideale: bool
    punti_forza: list[str]
    gap_formativi: list[str]
    motivazione_sintesi: str


@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        response_text = ""
        # Collects streamed chunks into a string
        for chunk in rag_agent.run(req.message, stream=True):
            if hasattr(chunk, "content") and chunk.content:
                response_text += chunk.content
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato non supportato. Usa: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    dest = DOCS_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Ingest into vector DB
    try:
        knowledge_base.insert(path=str(dest), upsert=True)
    except Exception as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Errore durante indicizzazione: {e}")

    return {"message": f"✅ '{file.filename}' caricato e indicizzato con successo!", "filename": file.filename}


@app.get("/api/documents")
async def list_documents():
    files = []
    for f in DOCS_DIR.iterdir():
        if f.suffix.lower() in ALLOWED_EXTENSIONS:
            files.append({
                "name": f.name,
                "size_kb": round(f.stat().st_size / 1024, 1),
                "ext": f.suffix.lower(),
            })
    return {"documents": sorted(files, key=lambda x: x["name"])}


# ─── Hiring Demo Endpoints ────────────────────────────────────────────────────

# Agent for Hiring tasks
hiring_agent = Agent(
    name="HR Assistant",
    role="Sei un Senior HR Assistant per l'azienda MetàHodòs. Sei specializzato nel creare Job Description perfette e analizzare CV in modo oggettivo.",
    markdown=False
)

hiring_scorer_agent = Agent(
    name="HR Scorer",
    role="Sei un motore di validazione CV. Valuta il CV rispetto alla JD e fornisci un'analisi strutturata.",
    output_schema=CVScoreResult,
)


@app.post("/api/hiring/generate-jd", response_model=JDResponse)
async def generate_jd(req: JDRequest):
    try:
        prompt = f"""
        Scrivi una Job Description per il ruolo di '{req.role}'.
        
        Briefing e requisiti dell'azienda:
        {req.brief}
        
        Regole:
        1. Formatta la risposta per essere letta bene, senza markdown eccessivo, ma usando elenchi puntati semplici.
        2. Includi le sezioni: "Chi siamo", "Cosa farai", "Cosa cerchiamo in te", "Cosa offriamo (Benefit)".
        3. Adotta il tono di voce aziendale di MetàHodòs: innovativo, inclusivo, professionale ma fresco.
        """
        
        response = hiring_agent.run(prompt)
        text_content = getattr(response, "content", str(response))
        return JDResponse(jd_text=text_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/hiring/score-cv", response_model=CVScoreResult)
async def score_cv(req: CVScoreRequest):
    try:
        prompt = f"""
        Ecco la Job Description (JD):
        {req.jd_text}
        
        Ecco il CV del candidato:
        {req.cv_text}
        
        Restituisci l'analisi strutturata (score da 0 a 100, ecc.).
        """
        
        response = hiring_scorer_agent.run(prompt)
        # Assuming Agno automatically parses response_model into response.content
        result_content = getattr(response, "content", None)
        if not result_content:
            raise ValueError("Empty response from AI")
            
        return result_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Onboarding Demo Endpoints ────────────────────────────────────────────────

onboarding_agent = Agent(
    name="Onboarding Tutor",
    role=(
        "Sei il Tutor AI per l'onboarding in MetàHodòs. "
        "Attingi SEMPRE alla policy aziendale per formare il nuovo dipendente su regole d'ufficio, "
        "sicurezza informatica (es. VPN, 1Password, policy 'Zero Allucinazioni') e benefit in base al ruolo e seniority. "
        "Crea un piano di 5 giorni realistico e accogliente."
    ),
    knowledge=knowledge_base,
    search_knowledge=True,
    markdown=False
)

@app.post("/api/onboarding/generate-plan", response_model=OnboardingResponse)
async def generate_onboarding_plan(req: OnboardingRequest):
    try:
        prompt = f"""
        Crea un piano di Onboarding di 5 giorni per:
        - Nome: {req.nome_dipendente}
        - Ruolo: {req.ruolo}
        - Livello: {req.seniority}
        
        Usa la tua knowledge base (leggi la policy aziendale). Include nel piano:
        1. Giorno 1: Benvenuto, setup IT (sicurezza, VPN) e cultura MetàHodòs.
        2. Giorno 2-3: Regole di condotta, procedure del ruolo.
        3. Giorno 4-5: Shadowing e setup AI.
        
        Rispondi con un output leggibile, organizzato in paragrafi o elenchi puntati semplici (senza eccessivo markdown tecnico).
        """
        response = onboarding_agent.run(prompt)
        text_content = getattr(response, "content", str(response))
        return OnboardingResponse(plan_text=text_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/static", StaticFiles(directory="static"), name="static")
