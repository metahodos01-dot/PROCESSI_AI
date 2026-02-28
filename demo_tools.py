import json
from datetime import datetime
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

def get_current_time(timezone: str = "Europe/Rome") -> str:
    """Restituisce l'ora corrente per un dato fuso orario.
    
    Args:
        timezone: Il fuso orario, es. "Europe/Rome" o "America/New_York"
    """
    from datetime import datetime
    import pytz
    
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return f"L'ora corrente a {timezone} è {now.strftime('%H:%M:%S del %d/%m/%Y')}"

def calculate_discount(price: float, discount_percentage: float) -> str:
    """Calcola il prezzo scontato di un prodotto.
    
    Args:
        price: Il prezzo originale
        discount_percentage: La percentuale di sconto (es. 20 per il 20%)
    """
    discount_amount = price * (discount_percentage / 100)
    final_price = price - discount_amount
    return f"Prezzo originale: {price}€. Sconto: {discount_percentage}%. Prezzo finale: {final_price:.2f}€"

# Creiamo un agente con poteri multipli
assistant = Agent(
    name="Super Assistant",
    role="Un assistente super intelligente che usa vari strumenti per risolvere problemi pratici.",
    tools=[
        DuckDuckGoTools(), 
        get_current_time, 
        calculate_discount
    ],
    instructions=[
        "Usa SEMPRE lo strumento appropriato per rispondere alle domande.",
        "Se ti chiedono l'ora, usa la funzione get_current_time.",
        "Se ti chiedono calcoli su sconti, usa calculate_discount.",
        "Se ti chiedono informazioni aggiornate, usa la ricerca web DuckDuckGo.",
        "Spiega sempre come hai ottenuto la risposta."
    ],
    markdown=True
)

if __name__ == "__main__":
    print("\n--- TEST 1: RICERCA WEB & CALCOLO MATEMATICO ---")
    domanda_1 = "Cerca su internet quanto costa l'ultimo iPhone uscito (dacci un prezzo indicativo in euro). Poi calcola quanto costerebbe se ci fosse uno sconto del 15%."
    print(f"Domanda: {domanda_1}\n")
    assistant.print_response(domanda_1, stream=True)
    
    print("\n--- TEST 2: FUNZIONI PYTHON PERSONALIZZATE ---")
    domanda_2 = "Che ore sono adesso a New York? E a Tokyo?"
    print(f"Domanda: {domanda_2}\n")
    assistant.print_response(domanda_2, stream=True)
