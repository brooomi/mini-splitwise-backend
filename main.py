from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# CORS aktivieren, damit Frontend fetch funktioniert
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modell für neue Ausgabe
class Expense(BaseModel):
    payer_name: str
    amount: float
    description: str

# Gruppen mit Testmitgliedern und Testausgaben
groups = {
    1: {
        "name": "Urlaub 2025",
        "members": ["Alice", "Bob", "Charlie"],
        "expenses": [
            {"payer_name": "Alice", "description": "Pizza", "amount": 12},
            {"payer_name": "Bob", "description": "Getränke", "amount": 8}
        ]
    },
    2: {
        "name": "WG",
        "members": ["Alice", "Bob"],
        "expenses": []
    }
}

# GET: Ausgaben einer Gruppe
@app.get("/groups/{group_id}/expenses")
def get_expenses(group_id: int):
    group = groups.get(group_id)
    if group:
        return group["expenses"]
    return []

# POST: Neue Ausgabe hinzufügen
@app.post("/groups/{group_id}/expenses")
def add_expense(group_id: int, expense: Expense):
    group = groups.get(group_id)
    if group:
        group["expenses"].append(expense.dict())

        # Neuen Namen automatisch zur Mitgliederliste hinzufügen
        if expense.payer_name not in group["members"]:
            group["members"].append(expense.payer_name)

        return {"message": "Ausgabe hinzugefügt"}
    return {"error": "Gruppe nicht gefunden"}


# GET: Abrechnung berechnen
@app.get("/groups/{group_id}/balance")
def get_balance(group_id: int):
    group = groups.get(group_id)
    if not group:
        return {"error": "Gruppe nicht gefunden"}

    expenses = group["expenses"]

    # Alle Personen (Mitglieder + Ausgaben-Namen)
    all_names = set(group["members"]) | set(e["payer_name"] for e in expenses)

    # Wie viel hat jeder ausgegeben
    spent = {}
    for e in expenses:
        name = e["payer_name"]
        spent[name] = spent.get(name, 0) + e["amount"]

    # Jeder soll gleich viel zahlen
    total = sum(e["amount"] for e in expenses)
    n = len(all_names)
    share = total / n if n > 0 else 0

    # Berechne Salden
    balances = {name: spent.get(name, 0) - share for name in all_names}

    # Min-Cash-Flow: wer schuldet wem
    debtors = [(name, -b) for name, b in balances.items() if b < 0]
    creditors = [(name, b) for name, b in balances.items() if b > 0]

    settlements = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, d_amount = debtors[i]
        creditor, c_amount = creditors[j]
        paid = min(d_amount, c_amount)
        settlements.append({"from": debtor, "to": creditor, "amount": round(paid, 2)})

        debtors[i] = (debtor, d_amount - paid)
        creditors[j] = (creditor, c_amount - paid)

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return settlements
