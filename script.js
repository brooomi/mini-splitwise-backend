const API_URL = "http://127.0.0.1:8000";

// Ausgaben laden
async function loadExpenses() {
    const groupId = document.getElementById("group").value;
    const res = await fetch(`${API_URL}/groups/${groupId}/expenses`);
    const expenses = await res.json();

    const list = document.getElementById("expense-list");
    list.innerHTML = "";
    expenses.forEach(e => {
        const li = document.createElement("li");
        li.textContent = `${e.description} – ${e.amount} € (von ${e.payer_name})`;
        list.appendChild(li);
    });
}

// Neue Ausgabe hinzufügen
async function addExpense() {
    const groupId = document.getElementById("group").value;
    const payerName = document.getElementById("payer_name").value;
    const description = document.getElementById("description").value;
    const amount = parseFloat(document.getElementById("amount").value);

    if (!payerName || !description || isNaN(amount)) return alert("Alle Felder ausfüllen!");

    await fetch(`${API_URL}/groups/${groupId}/expenses`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            payer_name: payerName,
            description: description,
            amount: amount
        })
    });

    document.getElementById("payer_name").value = "";
    document.getElementById("description").value = "";
    document.getElementById("amount").value = "";

    loadExpenses();
    loadBalance();
}

// Abrechnung laden
async function loadBalance() {
    const groupId = document.getElementById("group").value;
    const res = await fetch(`${API_URL}/groups/${groupId}/balance`);
    const balances = await res.json();

    console.log("Balance vom Backend:", balances); // Debug

    const list = document.getElementById("balance-list");
    list.innerHTML = "";
    balances.forEach(b => {
        const li = document.createElement("li");
        li.textContent = `${b.from} → ${b.to}: ${b.amount} €`;
        list.appendChild(li);
    });
}

// Initial laden
window.onload = () => {
    loadExpenses();
    loadBalance();
};
