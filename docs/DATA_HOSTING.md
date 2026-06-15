# Hebergement cloud des donnees brutes

## Pourquoi ?

Les 4 fichiers CSV sont heberges sur **GitHub Releases `v1.0-data`** et telecharges automatiquement
par `scripts/load_data.py` lors de la premiere execution. Aucune action manuelle n'est requise
pour un usage standard.

```
data/raw/hosts.csv                 <- telecharge depuis GitHub Releases v1.0-data
data/raw/listings.csv              <- telecharge depuis GitHub Releases v1.0-data
data/raw/reviews.csv               <- telecharge depuis GitHub Releases v1.0-data (~112 MB)
seeds/seed_full_moon_dates.csv     <- telecharge depuis GitHub Releases v1.0-data
```

> `reviews.csv` pese ~112 MB et depasse la limite GitHub de 100 MB par fichier — raison principale
> de l'hebergement sur Releases.

---

## Utilisation standard (aucune configuration)

```bash
python scripts/load_data.py
```

Le script :
1. Verifie si chaque fichier CSV existe localement
2. Si absent → telecharge depuis GitHub Releases `v1.0-data` avec barre de progression
3. Charge les fichiers dans DuckDB (couche Bronze)
4. Au prochain appel, les fichiers presents → pas de retelechargement

---

## Surcharger l'URL de reviews.csv

Si vous souhaitez utiliser une autre source pour `reviews.csv` (S3, Hugging Face, Dropbox,
Cloudflare R2, Google Drive lien direct, etc.), trois options sont disponibles par ordre de priorite :

### Option A — Argument CLI `--reviews-url` (recommande)

```bash
python scripts/load_data.py --reviews-url "https://example.com/reviews.csv"
```

### Option B — Variable d'environnement `REVIEWS_URL`

```bash
# macOS / Linux
export REVIEWS_URL="https://example.com/reviews.csv"
python scripts/load_data.py

# Windows PowerShell
$env:REVIEWS_URL="https://example.com/reviews.csv"
python scripts/load_data.py
```

### Option C — Modifier la constante dans le script

Editer `scripts/load_data.py` et changer la valeur de `RELEASE_BASE_URL` :

```python
RELEASE_BASE_URL = "https://votre-serveur.com/data"
```

---

## Re-uploader les donnees sur GitHub Releases (admin uniquement)

Cette section est utile uniquement si vous forkez le projet et devez re-heberger les CSV.

1. Ouvrez le repo : `https://github.com/zehair-louzza/airbnb-analytics-dbt`
2. Cliquez **Releases** → **Create a new release**
3. Configurez :
   - **Tag** : `v1.0-data`
   - **Release title** : `Donnees brutes Airbnb Berlin (v1.0)`
4. Glissez-deposez les 4 fichiers CSV dans la zone d'upload
5. Cliquez **Publish release**

---

## Options avancees de load_data.py

```bash
python scripts/load_data.py --help

# Arguments disponibles :
#   --data-dir DIR       Dossier destination des CSV (default: ./data/raw)
#   --db-path PATH       Chemin DuckDB (default: ./data/airbnb.duckdb)
#   --reviews-url URL    URL de telechargement pour reviews.csv
#   --no-download        Desactive le telechargement automatique
#   --verify             Affiche un apercu des tables apres chargement
```
