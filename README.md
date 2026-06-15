# Airbnb Analytics Platform — Berlin

> Pipeline de donnees end-to-end : **DuckDB + dbt + Streamlit**  
> Projet MBA ESG — Big Data & IA | Management Operationnel 2026

**Auteur :** LOUZZA Zehair  
**Livrable :** `MBAESG_EVALUATION_MANAGEMENT_OPERATIONNEL_2026`  
**Contact evaluation :** axel@logbrain.fr

---

## Table des matieres

- [Vue d'ensemble](#vue-densemble)
- [Architecture Medallion](#architecture-medallion)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Modeles dbt](#modeles-dbt)
- [KPIs et metriques metier](#kpis-et-metriques-metier)
- [Dashboard Streamlit](#dashboard-streamlit)
- [Resultats dbt](#resultats-dbt)
- [Installation — Guide VS Code](#installation--guide-vs-code)
- [Commandes de reference](#commandes-de-reference)
- [Problemes frequents](#problemes-frequents)

---

## Vue d'ensemble

Plateforme analytique complete sur les annonces Airbnb de Berlin (17 499 logements). Elle couvre l'integralite du cycle de vie de la donnee :

1. **Ingestion** des donnees brutes (CSV Inside Airbnb) — telechargement automatique depuis GitHub Releases
2. **Transformation** en couches Bronze / Silver / Gold via dbt
3. **Stockage** analytique dans DuckDB (base locale haute performance)
4. **Visualisation** interactive via une application Streamlit multi-onglets

L'analyse porte sur des **KPIs metier avances** incluant le taux d'occupation, le ratio prix/qualite, les multi-annonces par hote, et une analyse originale de l'effet de la **Pleine Lune** sur les avis clients.

---

## Architecture Medallion

```
Source CSV (Inside Airbnb)
        |
        v
+----------------------+
|     BRONZE Layer     |  Ingestion brute (DuckDB schema: main_bronze)
|  bronze_listings     |
|  bronze_hosts        |
|  bronze_reviews      |
|  bronze_full_moon_dates |
+----------------------+
        |
        v
+----------------------+
|     SILVER Layer     |  Nettoyage, typage, enrichissement
|  silver_listings     |
|  silver_reviews      |
|  silver_hosts        |
|  silver_full_moon_dates |
+----------------------+
        |
        v
+----------------------+
|      GOLD Layer      |  Agregations metier, KPIs finaux
|  dim_listings        |
|  dim_hosts           |
|  fact_reviews        |
|  full_moon_reviews   |
+----------------------+
        |
        v
+----------------------+
|   Streamlit App      |  Dashboard interactif — http://localhost:8501
+----------------------+
```

---

## Stack technique

| Composant | Role | Version |
|-----------|------|---------|
| **DuckDB** | Base de donnees analytique locale | >=1.1.0, <2.0.0 |
| **dbt-duckdb** | Transformation et documentation SQL | >=1.9.0, <2.0.0 |
| **Streamlit** | Application web interactive | >=1.35.0, <2.0.0 |
| **Python** | Orchestration et scripts d'ingestion | >=3.10 |
| **Plotly** | Visualisations interactives | >=5.22.0 |
| **Pandas** | Manipulation de donnees | >=2.2.3 |
| **GitHub** | Versioning, collaboration, hebergement data | — |

---

## Structure du projet

```
airbnb-analytics-dbt/
|-- models/
|   |-- bronze/
|   |   |-- bronze_listings.sql
|   |   `-- schema.yml
|   |-- silver/
|   |   |-- silver_listings.sql
|   |   |-- silver_reviews.sql
|   |   |-- silver_hosts.sql
|   |   |-- silver_full_moon_dates.sql
|   |   `-- schema.yml
|   `-- gold/
|       |-- dim_listings.sql
|       |-- dim_hosts.sql
|       |-- fact_reviews.sql
|       |-- full_moon_reviews.sql
|       `-- schema.yml
|-- seeds/
|   `-- seed_full_moon_dates.csv
|-- scripts/
|   `-- load_data.py           <- ingestion + telechargement auto
|-- streamlit/
|   `-- app.py                 <- dashboard Streamlit
|-- docs/
|   `-- DATA_HOSTING.md        <- configuration hebergement donnees
|-- .vscode/
|   `-- settings.json          <- interpreteur Python VS Code
|-- dbt_project.yml
|-- profiles.yml
|-- Makefile
`-- requirements.txt
```

---

## Modeles dbt

### Bronze — Ingestion brute

| Modele | Description |
|---|---|
| `bronze_listings` | Annonces brutes (id, listing_url, name, room_type, minimum_nights, host_id, price) |
| `bronze_hosts` | Hotes bruts |
| `bronze_reviews` | Avis avec sentiment pre-classifie |
| `bronze_full_moon_dates` | Dates de pleine lune depuis le seed |

### Silver — Nettoyage et standardisation

| Modele | Transformations cles |
|---|---|
| `silver_listings` | Nettoyage prix (retire `$`, cast DOUBLE), cap minimum_nights a 30 |
| `silver_reviews` | Standardisation dates, derivation `sentiment_score` (-1 / 0 / +1) |
| `silver_hosts` | Cast types, flag `is_superhost` boolean |
| `silver_full_moon_dates` | Calcul `full_moon_date_plus_1` (J+1) |

### Gold — Agregations metier

| Modele | Description |
|---|---|
| `dim_listings` | Listings enrichis — nb_avis, sentiment moyen, note proxy /5 |
| `dim_hosts` | Hotes enrichis — total_listings, avg_price, is_multi_host |
| `fact_reviews` | Avis joints aux listings + hosts + sentiment |
| `full_moon_reviews` | Avis emis dans la fenetre J / J+1 d'une pleine lune |

> **Note** : `review_scores_rating` est derivee du sentiment moyen (mapping `[-1, +1]` -> `[1, 5]`)
> car les CSV raw ne contiennent pas la note Airbnb d'origine.

---

## KPIs et metriques metier

| KPI | Definition | Valeur Berlin |
|-----|-----------|---------------|
| Logements | Nombre total d'annonces actives | 17 499 |
| Prix moyen/nuit | Mediane du prix par nuit (EUR) | 75 EUR |
| Note moyenne | Score moyen sur 5 | 4.14 / 5 |
| Avis total | Nombre total d'avis collectes | 409 695 |
| Multi-annonces | % d'hotes avec > 1 annonce | 38.4% |
| Superhosts | % d'hotes avec statut superhost | 13.6% |
| Taux d'occupation | % logements avec >= 10 avis (proxy) | 35.8% |
| Prix / Qualite | Ratio prix moyen / note moyenne | 18.2 EUR/pt |
| Avis pleine lune | % avis emis en periode lunaire | 100.0% |
| Nuits min moy | Duree minimum moyenne de sejour | 5.7 nuits |

---

## Dashboard Streamlit

L'application propose **5 onglets** accessibles sur `http://localhost:8501` :

### 1. Vue d'ensemble
- Repartition par type de logement (bar + donut chart)
- Statistiques par type (prix, note, nb avis, nuits min)
- Top 10 hotes par nombre d'annonces

### 2. Analyse des prix
- Distribution des prix (histogramme, capped a 500 EUR)
- Boxplot prix par type de logement
- Quartiles (Min, Q1, Mediane, Q3, Max)
- Correlation prix vs note (scatter)

### 3. Avis & Sentiment
- KPIs sentiment (% positifs / neutres / negatifs)
- Volume d'avis par mois (line chart)
- Repartition du sentiment (donut)
- Sentiment moyen par type de logement
- Echantillon des derniers avis

### 4. Pleine Lune
- KPIs pleine lune (volume, sentiment compare)
- Avis pleine lune par type de logement
- Evolution annuelle des avis lunaires
- Echantillon des avis pleine lune

### Filtres globaux (sidebar)
- Type de logement (multi-select)
- Prix EUR/nuit (slider)
- Pleine lune uniquement (checkbox)

---

## Resultats dbt

| Commande | Resultat |
|---|---|
| `dbt seed` | ✅ PASS (4 seeds) |
| `dbt run` | ✅ PASS (12 modeles) |
| `dbt test` | ✅ PASS (33 tests) |

Tests executes :
- `not_null` sur toutes les cles primaires
- `unique` sur host_id, listing_id, review_id
- `accepted_values` sur room_type
- Integrite referentielle Bronze → Silver → Gold

---

## Installation — Guide VS Code

### Prerequis

- Python 3.10 → 3.13 : [python.org/downloads](https://www.python.org/downloads/)
- Git : [git-scm.com](https://git-scm.com/)
- VS Code avec l'extension **Python** (Microsoft)

### Etape 1 — Cloner le projet

```powershell
git clone https://github.com/zehair-louzza/airbnb-analytics-dbt.git
cd airbnb-analytics-dbt
```

Puis dans VS Code : **File → Open Folder** → selectionner le dossier `airbnb-analytics-dbt`.

> ⚠️ Ne pas telecharger en ZIP — Git est obligatoire pour les mises a jour.

### Etape 2 — Creer l'environnement virtuel

```powershell
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux
```

### Etape 3 — Selectionner l'interpreteur Python dans VS Code

> ⚠️ Obligatoire pour eviter les faux avertissements Pylance (`reportMissingImports`)

1. `Ctrl+Shift+P` → `Python: Select Interpreter`
2. Selectionner **`.venv`** : `Python 3.x.x ('.venv': venv)  .\.venv\Scripts\python.exe`

Ou creer `.vscode/settings.json` pour que VS Code retienne le choix automatiquement :

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true
}
```

### Etape 4 — Installer les dependances

```powershell
pip install -r requirements.txt
```

### Etape 5 — Telecharger et ingerer les donnees

```powershell
python scripts/load_data.py
```

Le script telecharge automatiquement les 4 CSV depuis GitHub Releases `v1.0-data` si absents :

| Fichier | Taille | Destination |
|---|---|---|
| `hosts.csv` | ~800 KB | `data/raw/hosts.csv` |
| `listings.csv` | ~2.8 MB | `data/raw/listings.csv` |
| `reviews.csv` | ~112 MB | `data/raw/reviews.csv` |
| `seed_full_moon_dates.csv` | ~3 KB | `seeds/seed_full_moon_dates.csv` |

Pour surcharger l'URL de `reviews.csv` :

```powershell
python scripts/load_data.py --reviews-url "https://example.com/reviews.csv"
```

Voir [`docs/DATA_HOSTING.md`](docs/DATA_HOSTING.md) pour la configuration complete.

### Etape 6 — Construire les modeles dbt

```powershell
dbt deps
dbt seed
dbt run
dbt test       # optionnel
```

Resultat attendu : tous les modeles en vert ✅ `Completed successfully`.

### Etape 7 — Lancer le dashboard

```powershell
streamlit run streamlit/app.py
```

Ouvrir : **http://localhost:8501**

### Raccourci Makefile

```powershell
make all        # install + ingest + dbt seed + run + test
make dashboard  # lance Streamlit uniquement
```

### Les fois suivantes

```powershell
.venv\Scripts\activate
streamlit run streamlit/app.py
```

---

## Commandes de reference

```powershell
# Mise a jour du projet
git pull origin main
pip install -r requirements.txt

# Push apres modifications
git add .
git commit -m "description des changements"
git pull origin main --rebase
git push origin main

# Re-ingestion complete
Remove-Item .\data\raw\listings.csv
python scripts/load_data.py
dbt seed && dbt run
```

---

## Problemes frequents

| Symptome | Cause | Solution |
|---|---|---|
| `reportMissingImports: duckdb` dans VS Code | Mauvais interpreteur Python | `Ctrl+Shift+P` → `Python: Select Interpreter` → choisir `.venv` |
| `SyntaxError: unterminated string literal` | Ancien fichier local (ZIP) | Remplacer le fichier par la version GitHub |
| KPIs affichent `<NA>` dans Streamlit | `listings.csv` incomplet (1 000 lignes) | `Remove-Item .\data\raw\listings.csv` puis `python scripts/load_data.py` |
| `No options to select` dans le filtre Quartier | Colonne `neighbourhood` absente | Verifier colonnes : `Get-Content .\data\raw\listings.csv \| Select-Object -First 1` |
| `git push` rejected (fetch first) | Commits distants non integres | `git pull origin main --rebase` puis `git push origin main` |
| `dbt run` echoue | DuckDB vide | Lancer `python scripts/load_data.py` d'abord |

---

## Licence

MIT License — MBA ESG Big Data & AI 2026  
**Auteur : Zehair Louzza**
