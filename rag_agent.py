from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.openai import OpenAIChat

# Importa GmailTools per inviare e-mail
from agno.tools.gmail import GmailTools

import os
# Connessione al DB Neon
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable is missing")

# Colleghiamo la Knowledge Base al database vettoriale già popolato
knowledge_base = Knowledge(
    vector_db=PgVector(
        table_name="enterprise_documents",
        db_url=db_url,
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(dimensions=1536),
    ),
    # Definisce il numero di frammenti di documento da passare al LLM per rispondere
    max_results=5,
)

    model=OpenAIChat(id="gpt-4o-mini"),
    name="Enterprise RAG Assistant",
    role="Sei l'assistente AI aziendale. Rispondi alle domande aziendali cercando nei documenti (Policy o Vendite). Se ti chiedono di inviare una mail o leggere la posta, usa GmailTools.",
    knowledge=knowledge_base,
    # Aggiungi qui gli strumenti aggiuntivi!
    tools=[DuckDuckGoTools(), GmailTools()],
    # search_knowledge=True fornisce automaticamente lo strumento "search_knowledge_base" all'agente
    search_knowledge=True,
    markdown=True,
)

if __name__ == "__main__":
    print("\n--- TEST: RETRIEVAL DA PDF ED EXCEL ---")
    
    # Domanda 1: inerente al PDF (Policy)
    print("\nDOMANDA: Quanti giorni di ferie ho all'anno e a chi devo chiedere se volessi fare 3 settimane consecutive?")
    rag_agent.print_response("Quanti giorni di ferie ho all'anno e a chi devo chiedere se volessi fare 3 settimane consecutive?", stream=True)
    
    # Domanda 2: inerente al file Excel
    print("\n\nDOMANDA: Chi è stato il miglior venditore nel Q3 e per quale prodotto?")
    rag_agent.print_response("Chi è stato il miglior venditore nel Q3 e per quale prodotto?", stream=True)

    # Domanda 3: inerente al Web aperto (richiede l'uso di DuckDuckGoTools)
    print("\n\nDOMANDA: Quali sono le ultime notizie sul mercato azionario della Apple (AAPL)?")
    rag_agent.print_response("Quali sono le ultime notizie sul mercato azionario della Apple (AAPL)?", stream=True)
