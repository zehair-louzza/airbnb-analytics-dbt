# PROJET COMPLET — Airbnb Analytics Berlin
## Architecture Medallion avec DuckDB, dbt & Streamlit

**Auteur :** LOUZZA Zehair  
**MBA ESG — Big Data & IA 2026**  
**Date :** 14 juin 2026

---

## 1. Vue d'ensemble

Plateforme analytique complète pour les données Airbnb Berlin avec :
- Architecture **Medallion** (Bronze → Silver → Gold)
- Moteur **DuckDB** (in-process SQL OLAP)
- Transformations **dbt** (data build tool)
- Dashboard **Streamlit** multi-onglets
- Integration **Pleine Lune** (seed_full_moon_dates.csv)

---

## 2. Architecture du Pipeline

```
data/ (CSV sources)
  ├── hosts.csv
  ├── listings.csv  
  ├── reviews.csv
  └── seed_full_moon_dates.csv
        ↓
seeds/ (dbt seeds)
  └── seed_full_moon_dates.csv
        ↓
BRONZE (raw ingestion)
  ├── bronze_hosts
  ├── bronze_listings
  ├── bronze_reviews
  └── bronze_full_moon_dates ← NOUVEAU
        ↓
SILVER (cleaned & typed)
  ├── silver_hosts
  ├── silver_listings
  ├── silver_reviews
  └── silver_full_moon_dates ← NOUVEAU
        ↓
GOLD (business marts)
  ├── dim_hosts
  ├── dim_listings
  ├── fact_reviews
  └── full_moon_reviews ← NOUVEAU
```

---

## 3. Résultats dbt

| Commande | Résultat |
|---|---|
| `dbt seed` | PASS (4 seeds) |
| `dbt run` | PASS (12 modeles) |
| `dbt test` | PASS (33 tests) |

---

## 4. Modèles Gold

### dim_hosts
- Dimension hôtes avec métriques
- COALESCE pour valeurs manquantes

### dim_listings
- Dimension annonces avec prix, quartier, type

### fact_reviews
- Table de faits des avis
- Jointures hosts + listings

### full_moon_reviews ← NOUVEAU
- Croisement avis × dates de pleine lune
- Analyse comportementale lunaire
- Filtre dashboard "Pleine lune uniquement"

---

## 5. Dashboard Streamlit

URL locale : http://localhost:8501  
URL tunnel : https://v4rwhw37-8501.uks1.devtunnels.ms/

Onglets :
1. Vue d ensemble
2. Analyse des hotes
3. Analyse des prix
4. Analyse des avis (avec filtre pleine lune)
5. Heatmap temporelle

---

## 6. Git History

Branches :
- `main` — branche principale (34 commits)
- `clean-branch` — version propre sans CSV

Commits cles :
- fix: add bronze_full_moon_dates model
- fix: replace NVL with COALESCE, fix CAST
- chore: exclude large CSV data files

---

## 7. Commandes de Reproduction

```bash
# Setup
cd airbnb-analytics-dbt
pip install dbt-duckdb streamlit

# Pipeline
dbt deps
dbt seed
dbt run
dbt test

# Dashboard
streamlit run streamlit/app.py
```

---

## 8. Tests Passes

- not_null sur toutes les cles primaires
- unique sur host_id, listing_id, review_id
- accepted_values sur room_type
- Referential integrity Bronze → Silver → Gold

---

*Projet realise dans le cadre du MBA ESG Big Data & IA — 2026*
