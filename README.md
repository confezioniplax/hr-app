# HR-App (Access & HR Management)

HR-App è una web application completa per la **gestione del personale** e dei **registri di accesso** aziendali.  
Consente al reparto HR e alla direzione di monitorare ingressi, certificazioni e dati anagrafici, integrando un sistema di autenticazione sicuro e un’interfaccia web moderna.

---

## 🧩 Funzionalità principali

### 👷‍♂️ Personale HR e Direzione
- Gestione anagrafica dipendenti (inserimento, modifica, eliminazione)
- Gestione certificazioni (creazione, scadenze, stato)
- Visualizzazione accessi e presenze
- Generazione di report e KPI
- Gestione dei reparti e ruoli

### 👨‍💼 Dipendente
- Visualizzazione dei propri dati anagrafici e certificazioni
- Accesso tramite QR code
- Consultazione dei propri registri di presenza

---

## ⚙️ Architettura

L’applicazione è costruita con **FastAPI** e **Jinja2** per il rendering HTML.  
Il backend gira su **Uvicorn** e si collega a un database **MySQL**.

### Struttura principale

- `app/main.py` → entrypoint FastAPI  
- `app/templates/` → template HTML (Jinja2)  
- `app/repo/` e `app/services/` → logica applicativa  
- `app/sql/sql_executions.sql` → script di creazione tabelle  
- `app/routers/` → gestione delle rotte API e viste  

---

## 🧠 Requisiti

- **Python 3.10+**
- **MySQL**
- **Visual Studio Code** (consigliato)
- **Git** installato
- (Opzionale) **Docker** per il deploy containerizzato

---

## 🚀 Installazione e avvio

### 1️⃣ Clona il repository
```powershell
git clone git@github.com:confezioniplax/hr-app.git
cd hr-app

python -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1


pip install -r requirements.txt

5️⃣ Configura il database

Assicurati che il tuo server MySQL sia attivo.
Esegui lo script SQL in:

app/sql/sql_executions.sql


per creare le tabelle necessarie.


6️⃣ Avvia l’applicazione

In Visual Studio Code:

Apri la cartella del progetto

Premi F5 (Debug > Start Debugging)

Oppure da terminale:

uvicorn app.main:app --reload