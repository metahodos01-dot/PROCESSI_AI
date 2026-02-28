import pandas as pd
from reportlab.pdfgen import canvas
import os

target_dir = os.path.join(os.path.dirname(__file__), "enterprise_docs")

# 1. Excel (Sales Data)
df = pd.DataFrame({
    'Prodotto': ['Widget A', 'Widget B', 'Super Widget'],
    'Fatturato 2024': [15000, 25000, 120000],
    'Responsabile': ['Marco Rossi', 'Giulia Bianchi', 'Luca Neri'],
    'Note': ['Lancio ritardato', 'Miglior venditore Q3', 'Prodotto di punta aziendale']
})
excel_path = os.path.join(target_dir, "vendite_2024.xlsx")
df.to_excel(excel_path, index=False)
print(f"Created {excel_path}")

# 2. PDF (Company Policy)
pdf_path = os.path.join(target_dir, "policy_aziendale.pdf")
c = canvas.Canvas(pdf_path)
c.drawString(100, 800, "POLICY AZIENDALE SULLE FERIE - 2025")
c.drawString(100, 780, "Tutti i dipendenti hanno diritto a 22 giorni di ferie remunerate all'anno.")
c.drawString(100, 760, "Le richieste di ferie superiori a 2 settimane consecutive devono essere")
c.drawString(100, 740, "approvate dal responsabile HR (Dr.ssa Anna Verdi) con almeno 30 giorni di preavviso.")
c.drawString(100, 700, "NOTE SULLO SMART WORKING:")
c.drawString(100, 680, "Lo smart working è concesso per un massimo di 2 giorni alla settimana,")
c.drawString(100, 660, "preferibilmente martedì e giovedì.")
c.save()
print(f"Created {pdf_path}")
