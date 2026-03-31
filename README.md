# 🎮 BD2 - Steam Store Games NoSQL Project

## 📌 Descrizione
Questo progetto, sviluppato per il corso di Basi di Dati 2, ha l’obiettivo di progettare e implementare un sistema basato su database NoSQL per la gestione e analisi di dati relativi ai videogiochi.

Il sistema utilizza MongoDB e si basa sul dataset pubblico Steam Store Games, che include informazioni su giochi, sviluppatori, publisher, generi e piattaforme.

Per supportare operazioni CRUD e simulare scenari realistici, il sistema verrà esteso con dati sintetici relativi a utenti e recensioni.

---

## 🎯 Obiettivi del progetto
- Modellare un database NoSQL con più collection correlate
- Implementare operazioni CRUD su entità dinamiche (utenti e recensioni)
- Realizzare query e join tra collection (tramite aggregation pipeline)
- Gestire indici per migliorare le prestazioni
- Analizzare le performance con benchmark
- Fornire una semplice interfaccia utente per l’interazione

---

## 📊 Dataset
Dataset principale:
- Steam Store Games Dataset  
  https://www.kaggle.com/datasets/nikdavis/steam-store-games

Il dataset verrà preprocessato per:
- normalizzare campi multi-valore (es. generi, piattaforme)
- gestire valori mancanti
- uniformare i tipi di dato

---

## ⚙️ Tecnologie previste
- MongoDB
- Python (per preprocessing e import dati)
- Backend: da definire
- Frontend: interfaccia web minimale

---


## 📂 Struttura della repository

- `docs/` → documentazione del progetto  
- `data/raw/` → dataset originale  
- `data/processed/` → dati trasformati  
- `data/synthetic/` → dati generati  
- `scripts/` → script di import e benchmark  
- `sql/` → schema, query e indici  


---

## 🚧 Stato del progetto
Setup iniziale completato.  
Prossimi passi: analisi dataset e progettazione schema.
