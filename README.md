# Airbnb Analytics Platform - Berlin

> Pipeline de donnees end-to-end : **DuckDB + dbt + Streamlit**  
> Projet MBA ESG - Management Operationnel - Big Data & AI (2026)

---

## Table des matieres

- [Apercu du projet](#apercu-du-projet)
- [Architecture Medallion](#architecture-medallion)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Modeles dbt](#modeles-dbt)
- [KPIs et metriques metier](#kpis-et-metriques-metier)
- [Dashboard Streamlit](#dashboard-streamlit)
- [Installation et execution](#installation-et-execution)
- [Livrable](#livrable)

---

## Apercu du projet

Ce projet realise une **plateforme analytique complete** sur les annonces Airbnb de Berlin (17 499 logements). Il couvre l'integralite du cycle de vie de la donnee :

1. **Ingestion** des donnees brutes (CSV Inside Airbnb)
2. **Transformation** en couches Bronze / Silver / Gold via dbt
3. **Stockage** analytique dans DuckDB (base locale haute performance)
4. **Visualisation** interactive via une application Streamlit

L'analyse porte sur des **KPIs metier avances** incluant le taux d'occupation, le ratio prix/qualite, les multi-annonces par hote, et une analyse originale de l'effet de la **Pleine Lune** sur les avis clients.

---

## Architecture Medallion

```
Source CSV (Inside Airbnb)
        |
        v
+------------------+
|   BRONZE Layer   |  Ingestion brute
|  bronze_listings |  (DuckDB schema: main_bronze)
+------------------+
        |
        v
+------------------+
|   SILVER Layer   |  Nettoyage, typage, enrichissement
| silver_listings  |
| silver_reviews   |
| silver_hosts     |
| silver_full_moon_dates |
+------------------+
        |
        v
+------------------+
|    GOLD Layer    |  Agregations metier, KPIs finaux
|  dim_listings    |
|  dim_hosts       |
|  fact_reviews    |
| full_moon_reviews|
+------------------+
        |
        v
+------------------+
| Streamlit App    |  Dashboard interactif
+------------------+
```

---

## Stack technique

| Composant | Role | Version |
|-----------|------|---------|
| **DuckDB** | Base de donnees analytique locale | >= 0.9 |
| **dbt-duckdb** | Transformation et documentation SQL | >= 1.6 |
| **Streamlit** | Application web interactive | >= 1.28 |
| **Python** | Orchestration et scripts d'ingestion | >= 3.10 |
| **Plotly** | Visualisations interactives | >= 5.0 |
| **Pandas** | Manipulation de donnees | >= 2.0 |
| **GitHub** | Versioning et collaboration | - |

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
|   `-- full_moon_dates.csv
|-- scripts/
|   `-- load_data.py
|-- streamlit/
|   `-- app.py
|-- dbt_project.yml
|-- profiles.yml
`-- requirements.txt
```

---

## Modeles dbt

### Bronze - Ingestion brute
- **bronze_listings** : Chargement des annonces (id, listing_url, name, room_type, minimum_nights, host_id, price, created_at, updated_at)
- **bronze_hosts** : Chargement des hotes
- **bronze_reviews** : Chargement des avis avec sentiment pre-classifie
- **bronze_full_moon_dates** : Chargement du seed des dates de pleine lune

### Silver - Nettoyage et standardisation
- **silver_listings** : Nettoyage du prix (retire `$`, cast en DOUBLE), cap minimum_nights a 30
- **silver_reviews** : Standardisation dates, derivation `sentiment_score` (-1 / 0 / +1)
- **silver_hosts** : Cast types, flag `is_superhost` boolean
- **silver_full_moon_dates** : Calcul `full_moon_date_plus_1` (J+1)

### Gold - Agregations metier
- **dim_listings** : Listings enrichis avec aggregations reviews (nb_avis, sentiment moyen, note proxy /5)
- **dim_hosts** : Hotes enrichis (total_listings, avg_price, is_multi_host)
- **fact_reviews** : Avis joints aux listings + hosts + sentiment
- **full_moon_reviews** : Avis emis dans la fenetre J / J+1 d'une pleine lune

> **Note** : la note moyenne `review_scores_rating` est derivee du sentiment moyen
> (mapping `[-1, +1]` -> `[1, 5]`) car la version raw des CSV ne contient pas la note Airbnb d'origine.

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

L'application propose **5 onglets** :

### 1. Accueil (Landing Page)
- Hero section immersif (Berlin Fernsehturm, theme dark urbain)
- KPIs cles anime au survol (Logements, Prix, Note, Avis, Superhosts...)
- Diagramme du pipeline Bronze -> Silver -> Gold
- Presentation du projet et des angles d'analyse

### 2. Vue d'ensemble
- Repartition par type de logement (bar + donut chart)
- Statistiques par type (prix, note, nb avis, nuits min)
- Top 10 hotes par nombre d'annonces

### 3. Analyse des prix
- Distribution des prix (histogramme, capped a 500EUR)
- Boxplot prix par type de logement
- Quartiles (Min, Q1, Mediane, Q3, Max)
- Correlation prix vs note (scatter)

### 4. Avis & Sentiment
- KPIs sentiment (% positifs / neutres / negatifs)
- Volume d'avis par mois (line chart, 60 derniers mois)
- Repartition du sentiment (donut)
- Sentiment moyen par type de logement
- Echantillon des derniers avis

### 5. Pleine Lune
- KPIs pleine lune (volume, sentiment compare)
- Avis pleine lune par type de logement
- Sentiment des avis pleine lune
- Evolution annuelle des avis lunaires
- Echantillon des avis pleine lune

### Filtres globaux (sidebar)
- Type de logement (multi-select)
- Prix moyen EUR/nuit (slider)
- Pleine lune uniquement (checkbox)

---

## Installation et execution

### Prerequis

```bash
python >= 3.10
dbt-duckdb >= 1.8
streamlit >= 1.35
```

### Donnees attendues

Placez les CSV bruts dans `data/raw/` :
- `listings.csv` (colonnes : id, listing_url, name, room_type, minimum_nights, host_id, price, created_at, updated_at) — **versionne dans le repo**
- `hosts.csv` (colonnes : id, name, is_superhost, created_at, updated_at) — **versionne dans le repo**
- `reviews.csv` (colonnes : listing_id, date, reviewer_name, comments, sentiment) — **heberge cloud, telecharge auto**

> **Note** : `reviews.csv` non compresse pese ~112 MB et depasse la limite de fichier GitHub (100 MB).
> Il est donc heberge sur **GitHub Releases** et **telecharge automatiquement** par `scripts/load_data.py`
> lors du premier `make ingest`. Voir [`docs/DATA_HOSTING.md`](docs/DATA_HOSTING.md) pour la configuration de l URL.

Le seed `seeds/full_moon_dates.csv` contient les dates de pleine lune (2009-2030).

### 1. Installer les dependances

```bash
pip install -r requirements.txt
```

### 2. Charger les donnees brutes dans DuckDB (couche Bronze raw)

```bash
python scripts/load_data.py --data-dir ./data/raw --db-path ./data/airbnb.duckdb
```

### 3. Executer le pipeline dbt

```bash
dbt deps
dbt seed
dbt run
dbt test
```

### 4. Lancer le dashboard

```bash
streamlit run streamlit/app.py
```

Ou en une commande grace au Makefile :

```bash
make all          # install + ingest + seed + run + test
make dashboard    # lance Streamlit
```

Ouvrir : http://localhost:8501

---

## Livrable

Soumis sous l'intitule **MBAESG_EVALUATION_MANAGEMENT_OPERATIONNEL_2026**  
a l'adresse : axel@logbrain.fr

---

## Auteur

**Auteur : Zehair Louzza**

Projet realise dans le cadre du **MBA ESG Big Data & AI** - Promotion 2026  
Cours : Management Operationnel

---

## Licence

MIT License - MBA ESG 2026
