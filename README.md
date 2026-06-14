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
- **bronze_listings** : Chargement direct du CSV Inside Airbnb sans transformation

### Silver - Nettoyage et standardisation
- **silver_listings** : Nettoyage prix, cast numeriques, filtrage valeurs nulles
- **silver_reviews** : Standardisation dates, jointure avec listings
- **silver_hosts** : Parsing date d'inscription, flag superhost
- **silver_full_moon_dates** : Seed CSV transforme, calcul full_moon_date_plus_1

### Gold - Agregations metier
- **dim_listings** : Agregation par quartier, prix moyen, note moyenne
- **dim_hosts** : Ratio superhosts, multi-annonces par hote
- **fact_reviews** : Table de faits avec metriques par annonce
- **full_moon_reviews** : Jointure avis x dates lunaires (fenetre J / J+1)

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

L'application propose **4 onglets analytiques** :

### 1. Vue par quartier
- Distribution des logements par quartier (bar chart)
- Prix moyen par quartier
- Top 10 quartiers les plus chers

### 2. Analyse des prix
- Distribution des prix (histogramme)
- Boxplot prix par type de logement
- Correlation prix / note

### 3. Avis et Ratings
- Evolution temporelle des avis
- Distribution des notes
- Top hotes par nombre d'avis

### 4. Pleine Lune
- Avis par quartier en periode lunaire (bar chart colore)
- Repartition par type de logement (pie chart)
- Analyse comportementale des avis lunaires

### Filtres globaux
- Quartier(s) (multi-select)
- Prix moyen EUR/nuit (slider)
- Type de logement (multi-select)
- Pleine lune uniquement (checkbox)

---

## Installation et execution

### Prerequis

```bash
python >= 3.10
dbt-duckdb >= 1.6
streamlit >= 1.28
```

### 1. Installer les dependances

```bash
pip install -r requirements.txt
```

### 2. Charger les donnees brutes

```bash
python scripts/load_data.py
```

### 3. Executer le pipeline dbt

```bash
dbt seed
dbt run
dbt test
```

### 4. Lancer le dashboard

```bash
streamlit run streamlit/app.py --server.port 8501
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
