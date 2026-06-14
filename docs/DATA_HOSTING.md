# Hebergement cloud des donnees brutes

## Pourquoi ?

Le fichier **`reviews.csv`** pese ~112 MB et depasse la limite GitHub de 100 MB par fichier.
Il est donc heberge en cloud (GitHub Releases) et **telecharge automatiquement** par le script
d'ingestion (`scripts/load_data.py`) la premiere fois que vous lancez le pipeline.

```
data/raw/listings.csv          ← versionne dans le repo
data/raw/hosts.csv             ← versionne dans le repo
data/raw/seed_full_moon_dates.csv ← versionne dans le repo
data/raw/reviews.csv           ← TELECHARGE depuis GitHub Releases
```

## Etape 1 — Uploader reviews.csv sur GitHub Releases (a faire UNE seule fois)

1. Ouvrez votre repo : `https://github.com/<USER>/airbnb-analytics-dbt`
2. Cliquez sur **"Releases"** dans la barre laterale droite (ou allez sur `/releases`)
3. Cliquez sur **"Create a new release"** (ou **"Draft a new release"**)
4. Configurez :
   - **Tag** : `v1.0-data`
   - **Release title** : `Donnees brutes Airbnb Berlin (v1.0)`
   - **Description** : `Fichier reviews.csv (~112 MB) — Inside Airbnb Berlin, 2009-2021`
5. **Glissez-deposez `reviews.csv`** dans la zone "Attach binaries by dropping them here..."
6. Attendez la fin de l'upload (~30 sec - 2 min selon votre connexion)
7. Cliquez sur **"Publish release"**

## Etape 2 — Recuperer l'URL de telechargement

Sur la page de la release, faites un **clic droit > Copier l'adresse du lien** sur l'asset `reviews.csv`.

L'URL aura cette forme :
```
https://github.com/<USER>/airbnb-analytics-dbt/releases/download/v1.0-data/reviews.csv
```

## Etape 3 — Configurer le script

Trois facons (par ordre de priorite) :

### Option A : Modifier la constante dans `scripts/load_data.py`
```python
REVIEWS_DOWNLOAD_URL = "https://github.com/<USER>/airbnb-analytics-dbt/releases/download/v1.0-data/reviews.csv"
```

### Option B : Variable d environnement
```bash
export REVIEWS_URL="https://github.com/<USER>/airbnb-analytics-dbt/releases/download/v1.0-data/reviews.csv"
python scripts/load_data.py
```

### Option C : Argument CLI
```bash
python scripts/load_data.py --reviews-url "https://github.com/<USER>/airbnb-analytics-dbt/releases/download/v1.0-data/reviews.csv"
```

## Etape 4 — Lancer le pipeline

```bash
make all   # download (si absent) + ingest + seed + run + test
```

Le script :
1. Verifie si `data/raw/reviews.csv` existe en local
2. Si absent → telecharge depuis l URL configuree avec barre de progression
3. Charge le fichier dans DuckDB
4. Le pipeline dbt continue normalement

Au prochain `make all`, le fichier sera deja present → pas de retelechargement.

## Alternative — autres clouds

Le script accepte **n importe quelle URL HTTP/HTTPS publique** (S3, Hugging Face, Dropbox direct,
Cloudflare R2, Google Drive avec lien direct, etc.). Il suffit de fournir l URL via `--reviews-url`
ou la variable `REVIEWS_URL`.
