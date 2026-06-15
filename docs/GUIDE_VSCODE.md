# Guide — Demarrage rapide avec VS Code

Guide pas-a-pas pour cloner, installer et lancer l'application Airbnb Analytics sur VS Code.

---

## Prerequis

- **Python 3.10 → 3.13** : [python.org/downloads](https://www.python.org/downloads/)
- **Git** : [git-scm.com](https://git-scm.com/)
- **VS Code** avec l'extension **Python** (Microsoft) installee

---

## Etape 1 — Cloner le projet

Ouvrir VS Code, puis `Ctrl+backtick` pour ouvrir le terminal integre :

```bash
git clone https://github.com/zehair-louzza/airbnb-analytics-dbt.git
cd airbnb-analytics-dbt
```

Puis dans VS Code : **File → Open Folder** → selectionner le dossier `airbnb-analytics-dbt`.

> ⚠️ Ne pas telecharger le projet en ZIP — Git est obligatoire pour les mises a jour (`git pull`).

---

## Etape 2 — Creer un environnement virtuel

```bash
python -m venv .venv
```

Activer l'environnement :

| Systeme | Commande |
|---|---|
| Windows PowerShell | `.venv\Scripts\activate` |
| macOS / Linux | `source .venv/bin/activate` |

VS Code proposera automatiquement de selectionner cet interpreteur — cliquer **Yes**.

---

## Etape 3 — Selectionner l'interpreteur Python dans VS Code

> ⚠️ Cette etape est obligatoire pour eviter les faux avertissements Pylance
> (`reportMissingImports`, `duckdb could not be resolved`, etc.)

1. Appuyer sur `Ctrl+Shift+P`
2. Taper **`Python: Select Interpreter`** → Entree
3. Selectionner l'option contenant **`.venv`** :
   ```
   Python 3.x.x ('.venv': venv)   .\.venv\Scripts\python.exe
   ```

Si `.venv` n'apparait pas dans la liste, cliquer **"Enter interpreter path..."** et coller :
```
C:\chemin\vers\airbnb-analytics-dbt\.venv\Scripts\python.exe
```

Pour que VS Code retienne ce choix automatiquement, creer le fichier `.vscode/settings.json` :

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true
}
```

---

## Etape 4 — Installer les dependances

```bash
pip install -r requirements.txt
```

Packages installes : `dbt-core`, `dbt-duckdb`, `duckdb`, `streamlit`, `plotly`, `pandas`.

---

## Etape 5 — Telecharger et ingerer les donnees

```bash
python scripts/load_data.py
```

Ce script :
- Telecharge automatiquement les 4 CSV depuis GitHub Releases `v1.0-data` (si absents)
- Affiche une barre de progression pour `reviews.csv` (~112 MB)
- Charge les donnees dans `data/airbnb.duckdb` (couche Bronze)

Pour utiliser une URL alternative pour `reviews.csv` :

```bash
python scripts/load_data.py --reviews-url "https://example.com/reviews.csv"
```

---

## Etape 6 — Construire les modeles dbt (Bronze → Silver → Gold)

```bash
dbt deps
dbt seed
dbt run
```

Resultat attendu : tous les modeles en vert ✅ avec `Completed successfully`.

Verification optionnelle :

```bash
dbt test
```

---

## Etape 7 — Lancer l'application Streamlit

```bash
streamlit run streamlit/app.py
```

Le navigateur s'ouvre automatiquement sur **http://localhost:8501**.

---

## Raccourci Makefile

Le projet inclut un `Makefile` pour enchainer toutes les etapes :

```bash
make all        # install + ingest + dbt seed + dbt run + dbt test
make dashboard  # lance Streamlit uniquement
```

---

## Les fois suivantes (projet deja installe)

Si la base DuckDB est deja construite, seules 2 commandes suffisent :

```bash
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

streamlit run streamlit/app.py
```

---

## Mise a jour du projet

```bash
git pull origin main
pip install -r requirements.txt  # si requirements.txt a change
```

---

## Problemes frequents

| Symptome | Cause | Solution |
|---|---|---|
| `reportMissingImports: duckdb` dans VS Code | Mauvais interpreteur Python selectionne | `Ctrl+Shift+P` → `Python: Select Interpreter` → choisir `.venv` |
| `SyntaxError: unterminated string literal` | Ancien fichier local (ZIP) | Remplacer le fichier par la version GitHub |
| KPIs affichent `<NA>` dans Streamlit | `listings.csv` incomplet (1 000 lignes) | Supprimer et re-telecharger via `load_data.py` |
| `No options to select` dans le filtre Quartier | Colonne `neighbourhood` absente du CSV | Verifier les colonnes : `Get-Content .\data\raw\listings.csv \| Select-Object -First 1` |
| `dbt run` echoue | DuckDB pas encore peuple | Lancer `python scripts/load_data.py` d'abord |

---

## Arborescence du projet

```
airbnb-analytics-dbt/
|-- models/          <- modeles dbt (bronze / silver / gold)
|-- seeds/           <- seed CSV pleine lune
|-- scripts/
|   `-- load_data.py <- ingestion + telechargement automatique
|-- streamlit/
|   `-- app.py       <- dashboard Streamlit
|-- docs/
|   |-- DATA_HOSTING.md
|   `-- GUIDE_VSCODE.md  <- ce fichier
|-- .vscode/
|   `-- settings.json    <- interpreteur Python (optionnel)
|-- dbt_project.yml
|-- profiles.yml
|-- Makefile
`-- requirements.txt
```

---

*Auteur : Zehair Louzza — MBA ESG Big Data & AI, Promotion 2026*
