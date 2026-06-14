# Makefile - Airbnb Analytics Platform
# Automatisation du pipeline complet

.PHONY: help install setup ingest seed run test docs dashboard clean all

# Variables
PYTHON = python
DATA_DIR = ./data/raw
DB_PATH = ./data/airbnb.duckdb

## help: Affiche l aide
help:
	@echo "Commandes disponibles:"
	@echo ""
	@echo "  make install    - Installe les dependances Python"
	@echo "  make setup      - Installe les dependances + packages dbt"
	@echo "  make ingest     - Charge les CSV dans DuckDB (Bronze)"
	@echo "  make seed       - Charge les seeds dbt (full_moon_dates)"
	@echo "  make run        - Execute les modeles dbt (Bronze/Silver/Gold)"
	@echo "  make test       - Lance les tests de qualite dbt"
	@echo "  make docs       - Genere la documentation dbt"
	@echo "  make dashboard  - Lance l application Streamlit"
	@echo "  make clean      - Supprime les artefacts dbt"
	@echo "  make all        - Pipeline complet (install + ingest + seed + run + test)"
	@echo ""

## install: Installe les dependances Python
install:
	@echo "Installation des dependances..."
	pip install -r requirements.txt
	@echo "OK"

## setup: Install + packages dbt
setup: install
	@echo "Installation des packages dbt..."
	dbt deps
	@echo "Setup termine."

## ingest: Charge les CSV dans DuckDB
ingest:
	@echo "Ingestion des donnees CSV -> DuckDB..."
	$(PYTHON) scripts/load_data.py --data-dir $(DATA_DIR) --db-path $(DB_PATH) --verify
	@echo "Ingestion terminee."

## seed: Charge les seeds dbt
seed:
	@echo "Chargement des seeds dbt..."
	dbt seed
	@echo "Seeds charges."

## run: Execute les modeles dbt
run:
	@echo "Execution des modeles dbt (Bronze -> Silver -> Gold)..."
	dbt run
	@echo "Modeles executes."

## test: Lance les tests dbt
test:
	@echo "Lancement des tests de qualite..."
	dbt test
	@echo "Tests termines."

## docs: Genere et ouvre la documentation dbt
docs:
	@echo "Generation de la documentation dbt..."
	dbt docs generate
	dbt docs serve

## dashboard: Lance l application Streamlit
dashboard:
	@echo "Demarrage du dashboard Streamlit..."
	@echo "Ouvrez votre navigateur sur http://localhost:8501"
	streamlit run streamlit/app.py

## clean: Supprime les artefacts
clean:
	@echo "Nettoyage..."
	dbt clean
	@rm -rf target/
	@rm -rf dbt_packages/
	@echo "Nettoyage termine."

## all: Pipeline complet
all: setup ingest seed run test
	@echo ""
	@echo "Pipeline complet termine !"
	@echo "Lancez : make dashboard"

## ci: Pipeline CI sans les tests unitaires (pour GitHub Actions)
ci: install seed run test
	@echo "CI pipeline complete."
