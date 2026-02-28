from agno.agent import Agent
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools

# 1. Creiamo un Agente specializzato nella ricerca web
web_researcher = Agent(
    name="Web Researcher",
    role="Esperto di ricerca web e reperimento informazioni",
    instructions=[
        "Utilizza DuckDuckGo per cercare le informazioni più recenti e accurate.",
        "Riassumi i link più rilevanti.",
        "Rispondi sempre in italiano."
    ],
    tools=[DuckDuckGoTools()], # Qui forniamo allo strumento la capacità di cercare su internet
)

# 2. Creiamo un Agente specializzato nell'analisi e sintesi
content_writer = Agent(
    name="Content Writer",
    role="Scrittore di contenuti tech",
    instructions=[
        "Analizza i dati forniti dal ricercatore web.",
        "Scrivi un breve articolo o post per LinkedIn chiaro e accattivante sui risultati.",
        "Aggiungi un tocco di ironia e usa emoji."
    ],
)

# 3. Creiamo un "Team Leader" che orchestra i due agenti
team_leader = Team(
    name="Team Leader",
    role="Direttore editoriale",
    members=[web_researcher, content_writer],
    instructions=[
        "Il tuo compito è rispondere alla richiesta dell'utente coordinando il tuo team.",
        "Prima chiedi al 'Web Researcher' di trovare le informazioni necessarie.",
        "Poi passa le informazioni al 'Content Writer' per far scrivere l'articolo finale.",
        "Restituisci all'utente solo il risultato finale del Content Writer."
    ],
    markdown=True,
)

# 4. Eseguiamo il Team!
if __name__ == "__main__":
    print("🚀 Avvio del Team Agno...\n")
    # Puoi cambiare l'argomento qui sotto!
    argomento = "Quali sono state le notizie più importanti sull'Intelligenza Artificiale della settimana scorsa?"
    
    print(f"Argomento: {argomento}\n")
    print("Attendere la risposta dell'Agente Team Leader (che delegherà ai ricercatori e scrittori)...\n")
    
    # Esegue il leader
    team_leader.print_response(argomento, stream=True)
