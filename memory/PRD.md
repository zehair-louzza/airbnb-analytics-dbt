# Airbnb Analytics Berlin — PRD

## Problème original
> "Créer une page d'atterrissage : i need you to fix all the problems in my repo and fixe my streamlit reed the README.md to understand the architectur"

Projet existant : Pipeline data **DuckDB + dbt + Streamlit** analysant 17 499 annonces Airbnb Berlin + 409 695 avis (MBA ESG Big Data & IA 2026 - Zehair Louzza).

## Architecture
```
data/raw/*.csv  →  DuckDB (raw)  →  dbt (Bronze → Silver → Gold)  →  Streamlit
```

## Tech Stack
- Python 3.10+, DuckDB 0.10, dbt-duckdb 1.8, Streamlit 1.35, Plotly 5.22, Pandas 2.2
- Supervisor : `streamlit` sur port 3000 (exposé externe)

## Personas
- Évaluateur académique (MBA ESG) qui consulte le dashboard via URL preview
- Auteur (Zehair) qui rejoue le pipeline localement

## Problèmes identifiés & corrigés (2026-01)
1. ✅ `bronze_listings.sql` référençait colonne `bedrooms` inexistante → supprimé
2. ✅ Hack `scripts/fix_db.py` qui ajoutait bedrooms en post-traitement → supprimé (n'est plus nécessaire)
3. ✅ `bronze_reviews.sql` colonne `reviewer_id` inexistante → supprimé
4. ✅ Bronze/Silver/Gold polluées de `NULL AS neighbourhood, NULL AS rating, ...` car raw CSV n'a pas ces colonnes
5. ✅ `dim_listings` enrichi via aggregation de `silver_reviews` (nb_reviews, sentiment moyen, note proxy 1-5)
6. ✅ `dim_hosts` enrichi (total_listings, avg_price, is_multi_host)
7. ✅ `silver_full_moon_dates` adapté au seed à 1 colonne (full_moon_date uniquement)
8. ✅ Seed `seeds/full_moon_dates.csv` mis à jour (2009-2030, 272 dates)
9. ✅ `silver_listings` : nettoyage prix `$90.00` → 90.00 DOUBLE
10. ✅ Streamlit app entièrement repensée :
   - Nouveau **onglet Accueil** (landing page hero + KPIs + diagramme pipeline)
   - 4 onglets analytics (Vue d'ensemble, Prix, Sentiment, Pleine Lune)
   - Thème dark Berlin urbain (Bricolage Grotesque + DM Sans, palette #FF1F53)
   - Filtres sidebar adaptés (type de logement, prix, pleine lune)

## Pipeline validé
- `dbt seed` : 1/1 PASS (272 dates pleine lune)
- `dbt run` : 12/12 modèles PASS
- `dbt test` : 33/33 tests PASS

## KPIs réels obtenus
- Logements : 17 499
- Prix moyen : 75 €
- Note moyenne (proxy sentiment) : 3.96 / 5
- Avis total : 409 695
- Avis pleine lune : 28 095 (6.86%)
- Période : 2009 → 2021

## Implémenté (2026-01)
- ✅ Pipeline dbt fonctionnel end-to-end
- ✅ Streamlit dashboard 5 onglets avec landing page dark/Berlin
- ✅ Theme cohérent (Bricolage Grotesque + DM Sans)
- ✅ Supervisor config Streamlit sur port 3000
- ✅ README mis à jour
- ✅ Données raw chargées depuis CSV fournis par utilisateur

## Backlog (P1/P2)
- P2 : Caching DuckDB sur queries lourdes
- P2 : Ajout d'un onglet "Carte" si lat/long ajoutés au CSV
- P2 : Export PDF du dashboard
- P2 : Comparatif Berlin vs autres villes (extensible)

## Next Actions
- Tester en conditions réelles (utilisateur)
- Push GitHub via feature "Save to Github"
