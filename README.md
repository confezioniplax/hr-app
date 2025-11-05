# HR-App (Access & HR Management)

**HR-App** è una web application completa per la **gestione del personale**, delle **certificazioni** e dei **documenti aziendali**.  
Permette al reparto HR e alla direzione di monitorare in modo centralizzato tutti i dati dei dipendenti, gli allegati, le scadenze e gli accessi.  
Include autenticazione sicura, interfaccia web moderna e automazione all’avvio su Windows.

---

## 🧩 Funzionalità principali

### 👷‍♂️ Personale HR e Direzione
- Gestione **anagrafiche dipendenti** (creazione, modifica, disattivazione)
- Gestione **certificazioni** con allegati PDF/immagini/Word
  - Salvataggio automatico su disco in `Certificazioni/<CF>/<TIPO>_<DATA>.ext`
  - Scaricamento automatico dell’**ultima versione** di ogni certificazione
- Gestione **documenti aziendali**:
  - Caricamento, categorizzazione per anno e frequenza
  - Download diretto e gestione storica
- Visualizzazione **KPI e scadenze** (in scadenza, scadute, mancanti)
- Gestione **reparti e ruoli**
- Invio automatico **email di promemoria scadenze**

### 👨‍💼 Dipendente
- Visualizzazione dei propri dati anagrafici e certificazioni
- Accesso rapido tramite QR code personale
- Consultazione dei propri registri di presenza e documenti

---

## ⚙️ Architettura

L’app è basata su **FastAPI** e **Jinja2** per il rendering HTML.  
Il backend gira su **Uvicorn**, con database **MySQL**.

### Struttura progetto

```
app/
 ├─ main.py                 → entrypoint FastAPI
 ├─ routers/                → API e viste web (FastAPI routers)
 ├─ services/               → logica applicativa (es. HRService)
 ├─ repo/                   → accesso ai dati e query SQL
 ├─ templates/              → interfacce HTML (Jinja2)
 ├─ sql/                    → script SQL e query MySQL
 └─ static/                 → immagini, JS, CSS
```

---

## 🧠 Requisiti

- **Python 3.10+**
- **MySQL Server**
- **Git** installato
- (Opzionale ma consigliato) **Visual Studio Code**
- **Windows 10/11** o **VM Windows Server**

---

## 🚀 Installazione e avvio manuale

### 1️⃣ Clona il repository
```powershell
git clone git@github.com:confezioniplax/hr-app.git
cd hr-app
```

### 2️⃣ Crea e attiva l’ambiente virtuale
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
```

### 3️⃣ Installa le dipendenze
```powershell
pip install -r requirements.txt
```

### 4️⃣ Configura il database
Assicurati che il server MySQL sia attivo e poi esegui lo script:
```
app/sql/sql_executions.sql
```
per creare le tabelle necessarie.

### 5️⃣ Avvia l’app
```powershell
uvicorn app.main:app --reload
```

Apri il browser su **http://localhost:8000**

---

## 🖥️ Avvio automatico all’accensione (Windows)

Per far partire l’app automaticamente quando la VM o il PC si accende:

1. Crea (o verifica di avere) il file:
   ```
   C:\Users\Plax\Desktop\Apps\hr-app\start_hr_app.bat
   ```
2. Aggiungi questo contenuto:
   ```bat
   @echo off
   set APPDIR=C:\Users\Plax\Desktop\Apps\hr-app
   set VENV=%APPDIR%\.venv

   cd /d %APPDIR%
   call "%VENV%\Scripts\activate.bat"

   :: Installa requirements solo se modificati
   if exist "%APPDIR%\requirements_installed.txt" (
       for %%A in ("%APPDIR%\requirements.txt") do set RQTIME=%%~tA
       for %%B in ("%APPDIR%\requirements_installed.txt") do set INSTTIME=%%~tB
       if "!RQTIME!" gtr "!INSTTIME!" (
           pip install -r "%APPDIR%\requirements.txt"
           copy /y "%APPDIR%\requirements.txt" "%APPDIR%\requirements_installed.txt" >nul
       )
   ) else (
       pip install -r "%APPDIR%\requirements.txt"
       copy /y "%APPDIR%\requirements.txt" "%APPDIR%\requirements_installed.txt" >nul
   )

   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. Apri **Utilità di pianificazione (Task Scheduler)**  
   → Crea nuova attività → **Avvio all’accensione del computer**  
   → Programma:  
   ```
   C:\Windows\System32\cmd.exe
   ```
   → Argomenti:
   ```
   /c "C:\Users\Plax\Desktop\Apps\hr-app\start_hr_app.bat"
   ```

Ora l’app si avvia automaticamente ad ogni accensione.

---

## 📁 Struttura file salvati

- **Certificazioni:**  
  `C:\Certificazioni\<CodiceFiscale>\<Tipo>_<Data>.pdf`

- **Documenti aziendali:**  
  `C:\DocumentiAziendali\<Categoria>\<Anno>\<Titolo>.<ext>`

---

## 📧 Notifiche automatiche

Il sistema può inviare email automatiche per:
- certificazioni in scadenza o scadute
- riepiloghi periodici HR (configurabili nel service `send_expiring_certs_email_if_needed`)

---

## 🧰 Tecnologie principali

| Componente | Tecnologia |
|-------------|-------------|
| Backend | FastAPI (Python) |
| Database | MySQL |
| Frontend | Jinja2 + Bootstrap 5 |
| Server | Uvicorn |
| Email | SMTP (configurabile in `settings.py`) |
| Scheduling | Windows Task Scheduler |

---

## 🛡️ Licenza

MIT License  
(c) 2025 [Riccardo Leonelli / PLAX Packaging S.r.l.]
