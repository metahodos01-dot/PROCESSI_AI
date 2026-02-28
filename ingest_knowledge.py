import os
from agno.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder

db_url = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_xujFI96zlkSr@ep-delicate-base-agzt2gjt-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require")

# Crea la Knowledge Base associata a Neon DB (tabella per vettori documentali)
knowledge_base = Knowledge(
    vector_db=PgVector(
        table_name="enterprise_documents",
        db_url=db_url,
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(dimensions=1536),
    ),
    # Agno mapperà in automatico l'estensione del path a PdfReader o ExcelReader
)

def ingest_all():
    docs_dir = os.path.join(os.path.dirname(__file__), "enterprise_docs")
    print(f"Inizio indicizzazione dalla cartella: {docs_dir}\n")
    
    # Inizializziamo eventuali tabelle se è la prima volta
    if hasattr(knowledge_base.vector_db, "create_tables"):
         knowledge_base.vector_db.create_tables()
    elif hasattr(knowledge_base.vector_db, "_create_all_tables"):
         knowledge_base.vector_db._create_all_tables()
         
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.startswith("."):
                continue  # skip hidden
                
            file_path = os.path.join(root, file)
            print(f"Ingerendo: {file}")
            
            # Insert elabora il contenuto del file, lo splitta in chunk, crea gli embeddings
            # e per i PDF userà anche l'OCR grazie a pypdf/pdf2image associati al content type.
            knowledge_base.insert(path=file_path, upsert=True)
            
    print("\n[OK] Indicizzazione completata nel database Postgres su Neon!")

if __name__ == "__main__":
    ingest_all()
