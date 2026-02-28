import os
from agno.agent import Agent
from agno.db.postgres import PostgresDb

# DB URL from Neon (puoi impostarlo come variabile d'ambiente o usarlo hardcoded per test)
# Di solito è consigliato usare os.getenv("DATABASE_URL") in produzione.
db_url = "postgresql://neondb_owner:npg_xujFI96zlkSr@ep-delicate-base-agzt2gjt-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require"

# Creiamo lo storage collegato al DB Neon
# Questo creerà automaticamente la tabella 'agent_sessions' se non esiste.
neon_storage = PostgresDb(
    session_table="agent_sessions",
    db_url=db_url
)

# Creiamo l'Agente!
assistant = Agent(
    name="Memory Assistant",
    role="Sei un assistente che si ricorda le cose grazie a un database remoto Postgres.",
    # L'ID della sessione è cruciale per la memoria a lungo termine: è la "stanza" in cui parlate
    session_id="la_mia_prima_sessione",
    db=neon_storage,
    # Questa impostazione è quella che fa la magia passandogli lo storico
    add_history_to_context=True,
    markdown=True
)

if __name__ == "__main__":
    print("\n--- TEST: MEMORIA DB POSTGRES ---")
    print("Saluto iniziale dell'Agente per popolare il DB:\n")
    assistant.print_response("Ciao! Il mio nome è Francesco e il mio colore preferito è il rosso mattone. Non dimenticarlo!", stream=True)
    
    print("\n\n--- SECONDA DOMANDA ---")
    print("Proviamo a vedere se si ricorda tutto leggendo dallo storico salvato nel database Neon:\n")
    assistant.print_response("Come mi chiamo e qual è il mio colore preferito?", stream=True)
