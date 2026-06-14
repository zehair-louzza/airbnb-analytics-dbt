# Recap - Airbnb Analytics Platform Berlin

## 1. Presentation du Projet

Plateforme analytique Airbnb Berlin avec architecture Medallion (Bronze/Silver/Gold).
Stack: dbt + DuckDB + Streamlit.

## 2. Architecture

- Bronze: donnees brutes CSV via dbt seed
- Silver: modeles stg_listings, stg_reviews (nettoyage)
- Gold: mart_listings_by_neighbourhood, mart_review_trends, mart_host_performance

## 3. Modeles dbt

| Couche | Modele | Description |
|--------|--------|-------------|
| Silver | stg_listings | Listings nettoyes |
| Silver | stg_reviews | Reviews normalisees |
| Gold | mart_listings_by_neighbourhood | Prix/note par quartier |
| Gold | mart_review_trends | Tendances mensuelles |
| Gold | mart_host_performance | Performance hosts |

## 4. Dashboard Streamlit

Application multi-onglets (app.py):
- Vue Globale: KPIs (total listings, prix moyen, note moyenne)
- Analyse Quartier: carte + tableaux interactifs
- Tendances Avis: graphique temporel
- Performance Hosts: top hosts, revenus estimes

## 5. Commandes

```bash
dbt deps && dbt seed && dbt run && dbt test
streamlit run app.py
```

## 6. Erreurs et Corrections

| Erreur | Solution |
|--------|----------|
| NVL not found | Utiliser COALESCE |
| git push rejected | git fetch + reset --hard origin/main |
| UPPER on boolean | Caster en VARCHAR avant UPPER |

## 7. Etat Actuel

- [x] Architecture Medallion implementee
- [x] Modeles dbt operationnels
- [x] Dashboard Streamlit fonctionnel
- [x] Documentation complete
- [ ] Deploiement Streamlit Cloud
- [ ] CI/CD GitHub Actions

## 8. Informations Academiques

**Etablissement:** MBA ESG Paris
**Cours:** Management Operationnel
**Promotion:** Big Data & AI 2026
**Soumis a:** axel@logbrain.fr
**Reference:** MBAESG_EVALUATION_MANAGEMENT_OPERATIONNEL_2026

---

*Document genere le 14/06/2026 - LOUZZA Zehair*