# 🎮 BD2 - Steam Store Games NoSQL Project

## 📌 Descrizione
Questo progetto, sviluppato per il corso di Basi di Dati 2, ha l’obiettivo di progettare e implementare un sistema basato su database NoSQL per la gestione e analisi di dati relativi ai videogiochi.

Il sistema utilizza MongoDB e si basa sul dataset pubblico Steam Store Games, che include informazioni su giochi, sviluppatori, publisher, generi e piattaforme.

Per supportare operazioni CRUD e simulare scenari realistici, il sistema verrà esteso con dati sintetici relativi a utenti e recensioni.

---

## 🎯 Obiettivi del progetto
- Modellare un database NoSQL con più collection correlate
- Implementare operazioni CRUD su entità dinamiche (utenti e recensioni)
- Realizzare query e join tra collection 
- Gestire indici per migliorare le prestazioni
- Analizzare le performance con benchmark
- Fornire una semplice interfaccia utente per l’interazione

---

## 📊 Dataset
Dataset principale:
- Steam Store Games Dataset  
  https://www.kaggle.com/datasets/nikdavis/steam-store-games

Contiene informazioni su:

- giochi
- sviluppatori
- publisher
- generi
- piattaforme
- rating e statistiche di utilizzo

---

## ⚙️ Tecnologie previste
- MongoDB
- Python (per preprocessing e import dati)
- Backend: Python(framework applicativo da definire)
- Frontend: interfaccia web minimale

---

## Preprocessing dei dati

Il dataset viene preprocessato tramite script Python per renderlo coerente con il modello documentale di MongoDB.

Trasformazioni effettuate:
- gestione dei valori mancanti (developer, publisher)
- conversione dei campi multivalore (genres, platforms, categories, steamspy_tags) in array
- standardizzazione del campo release_date
- conversione dei campi numerici
- trasformazione del campo owners in:
- owners_min
- owners_max
### Output:
- games_cleaned.json → pronto per MongoDB
- games_cleaned.csv → per debug/controllo

---

## Generazione dati sintetici

Per supportare le funzionalità applicative, vengono generati:

- Users
- identificativo univoco
- username
- email
- generi preferiti
- Reviews
- collegamento a utente (user_id)
- collegamento a gioco (appid)
- rating (1–10)
- commento

Questi dati permettono di implementare:

- CRUD completo
- join tra collection (es. recensioni + giochi)

---

## 🧪 Validazione dei dati

È stato implementato uno script di controllo (sanity_check.py) che verifica:

- consistenza tra utenti, giochi e recensioni
- assenza di duplicati
- validità dei riferimenti (user_id, appid)
- correttezza dei tipi di dato


---


## Esecuzione

```bash
pip install -r requirements.txt
python scripts/preprocess.py
python scripts/generate_users.py
python scripts/generate_reviews.py
python scripts/sanity_check.py

```

## 📂 Struttura della repository
``` bash
BD2-SteamStoreGames/
│
├── requirements.txt
├── data/
│   ├── raw/
│   │   └── steam.csv
│   └── processed/
│       ├── games_cleaned.json
│       ├── users_seed.json
│       └── reviews_seed.json
│
├── scripts/
│   ├── preprocess.py
│   ├── generate_users.py
│   ├── generate_reviews.py
│   └── sanity_check.py
│
├── docs/
├── src/
├── README.md
└── .gitignore
```

---

## Strategia di modellazione (NoSQL)

Il progetto adotta un approccio documentale basato su MongoDB:

i dati sono organizzati in documenti JSON
i campi multivalore sono rappresentati come array
le relazioni tra entità saranno gestite tramite riferimenti logici
le join saranno implementate tramite aggregation pipeline ($lookup)

La definizione finale delle collection sarà effettuata nelle fasi successive.

---

## Requisiti del progetto

Il progetto è progettato per soddisfare i requisiti minimi:

- ≥ 5 collection
- CRUD completo
- almeno una join tra collection
- utilizzo di indici e benchmark
- interfaccia utente
- workflow Git completo (issue, branch, PR, review)
- README replicabile

## 🚧 Stato del progetto
- ✔ Setup repository completato
- ✔ Preprocessing dataset completato
- ✔ Generazione dati sintetici completata
- 🔄 In corso: modellazione MongoDB
- ⏳ Da fare: CRUD, query, indici, UI
