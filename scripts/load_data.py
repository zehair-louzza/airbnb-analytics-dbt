"""
Script d'ingestion des donnees Airbnb dans DuckDB
Etape 1 du pipeline : chargement couche Bronze

Usage:
    python scripts/load_data.py
    python scripts/load_data.py --data-dir ./data/raw --db-path ./data/airbnb.duckdb --verify
    python scripts/load_data.py --reviews-url "https://example.com/reviews.csv"
    REVIEWS_URL="https://example.com/reviews.csv" python scripts/load_data.py

Tous les fichiers CSV sont telecharges automatiquement depuis GitHub Releases v1.0-data
si absents dans leurs dossiers respectifs :
    - data/raw/hosts.csv                  (~800 KB)
    - data/raw/listings.csv               (~2.8 MB)
    - data/raw/reviews.csv                (~111 MB)
    - seeds/seed_full_moon_dates.csv      (~3 KB)
"""

import duckdb
import os
import argparse
import logging
import urllib.request
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# URLs de telechargement depuis GitHub Releases v1.0-data
RELEASE_BASE_URL = (
    "https://github.com/zehair-louzza/airbnb-analytics-dbt"
    "/releases/download/v1.0-data"
)

# (filename -> destination relative to project root, default url)
RELEASE_FILES = {
    "hosts.csv":                 ("data/raw/hosts.csv",             f"{RELEASE_BASE_URL}/hosts.csv"),
    "listings.csv":              ("data/raw/listings.csv",          f"{RELEASE_BASE_URL}/listings.csv"),
    "reviews.csv":               ("data/raw/reviews.csv",           f"{RELEASE_BASE_URL}/reviews.csv"),
    "seed_full_moon_dates.csv":  ("seeds/seed_full_moon_dates.csv", f"{RELEASE_BASE_URL}/seed_full_moon_dates.csv"),
}


def ensure_data_files(data_dir: str, reviews_url: str = None) -> None:
    """
    Verifie la presence de chaque fichier a son emplacement attendu.
    Telecharge automatiquement depuis GitHub Releases v1.0-data si absent.
    Pour reviews.csv, l'URL peut etre surchargee via --reviews-url ou REVIEWS_URL.
    """
    # Resolve reviews URL override: CLI arg > env var > default
    resolved_reviews_url = (
        reviews_url
        or os.environ.get("REVIEWS_URL")
        or RELEASE_FILES["reviews.csv"][1]
    )
    if resolved_reviews_url != RELEASE_FILES["reviews.csv"][1]:
        logger.info(f"reviews.csv : URL surchargee -> {resolved_reviews_url}")

    for filename, (default_dest, default_url) in RELEASE_FILES.items():
        # Pour les 3 CSV Airbnb, on respecte --data-dir ; pour le seed, chemin fixe
        if filename == "seed_full_moon_dates.csv":
            file_path = Path(default_dest)
        else:
            file_path = Path(data_dir) / filename

        # Determine final URL (override only applies to reviews.csv)
        url = resolved_reviews_url if filename == "reviews.csv" else default_url

        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            logger.info(f"{filename} trouve ({size_kb:.0f} KB) : {file_path}")
            continue

        logger.warning(f"{filename} absent - telechargement depuis : {url}")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        def _progress(block_num, block_size, total_size, fname=filename):
            downloaded = block_num * block_size
            if total_size > 0:
                pct = min(downloaded / total_size * 100, 100)
                mb = downloaded / 1_048_576
                total_mb = total_size / 1_048_576
                print(f"  [{fname}] {pct:.1f}%  {mb:.1f}/{total_mb:.1f} MB", end="\r")

        try:
            urllib.request.urlretrieve(url, file_path, _progress)
            print()  # newline apres la progression
            size_kb = file_path.stat().st_size / 1024
            logger.info(f"{filename} telecharge avec succes ({size_kb:.0f} KB) -> {file_path}")
        except Exception as e:
            logger.error(f"Echec du telechargement de {filename} : {e}")
            logger.error(f"Telechargez manuellement depuis : {url}")
            raise


def create_database(db_path: str) -> duckdb.DuckDBPyConnection:
    """Cree ou ouvre la base DuckDB."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    logger.info(f"Connexion DuckDB etablie : {db_path}")
    return conn


def load_hosts(conn: duckdb.DuckDBPyConnection, data_dir: str) -> int:
    """Charge les donnees des hotes depuis hosts.csv."""
    hosts_path = os.path.join(data_dir, "hosts.csv")
    if not os.path.exists(hosts_path):
        logger.warning(f"Fichier introuvable : {hosts_path}")
        return 0

    conn.execute("""
        CREATE OR REPLACE TABLE raw_hosts AS
        SELECT * FROM read_csv_auto(?, header=True)
    """, [hosts_path])

    count = conn.execute("SELECT COUNT(*) FROM raw_hosts").fetchone()[0]
    logger.info(f"raw_hosts charge : {count:,} lignes")
    return count


def load_listings(conn: duckdb.DuckDBPyConnection, data_dir: str) -> int:
    """Charge les annonces depuis listings.csv."""
    listings_path = os.path.join(data_dir, "listings.csv")
    if not os.path.exists(listings_path):
        logger.warning(f"Fichier introuvable : {listings_path}")
        return 0

    conn.execute("""
        CREATE OR REPLACE TABLE raw_listings AS
        SELECT * FROM read_csv_auto(?, header=True)
    """, [listings_path])

    count = conn.execute("SELECT COUNT(*) FROM raw_listings").fetchone()[0]
    logger.info(f"raw_listings charge : {count:,} lignes")
    return count


def load_reviews(conn: duckdb.DuckDBPyConnection, data_dir: str) -> int:
    """Charge les avis depuis reviews.csv."""
    reviews_path = os.path.join(data_dir, "reviews.csv")
    if not os.path.exists(reviews_path):
        logger.warning(f"Fichier introuvable : {reviews_path}")
        return 0

    conn.execute("""
        CREATE OR REPLACE TABLE raw_reviews AS
        SELECT * FROM read_csv_auto(?, header=True, ignore_errors=True)
    """, [reviews_path])

    count = conn.execute("SELECT COUNT(*) FROM raw_reviews").fetchone()[0]
    logger.info(f"raw_reviews charge : {count:,} lignes")
    return count


def verify_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """Verifie que les tables sont bien chargees."""
    logger.info("--- Verification des tables ---")
    tables = conn.execute("SHOW TABLES").fetchall()
    for table in tables:
        name = table[0]
        count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        logger.info(f"  {name}: {count:,} lignes")


def show_sample(conn: duckdb.DuckDBPyConnection, table: str, n: int = 3) -> None:
    """Affiche un apercu d'une table."""
    logger.info(f"--- Apercu de {table} ({n} lignes) ---")
    df = conn.execute(f"SELECT * FROM {table} LIMIT {n}").fetchdf()
    print(df.to_string())


def main():
    parser = argparse.ArgumentParser(
        description="Charge les CSV Airbnb dans DuckDB (couche Bronze)"
    )
    parser.add_argument(
        "--data-dir",
        default="./data/raw",
        help="Dossier contenant les fichiers CSV (default: ./data/raw)"
    )
    parser.add_argument(
        "--db-path",
        default="./data/airbnb.duckdb",
        help="Chemin vers la base DuckDB (default: ./data/airbnb.duckdb)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Affiche un apercu des tables apres chargement"
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Desactive le telechargement automatique des fichiers manquants"
    )
    parser.add_argument(
        "--reviews-url",
        default=None,
        help=(
            "URL de telechargement pour reviews.csv "
            "(surcharge REVIEWS_URL env var et l'URL par defaut). "
            "Accepte n'importe quelle URL HTTP/HTTPS publique "
            "(GitHub Releases, S3, Hugging Face, Dropbox, etc.)"
        )
    )
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("AIRBNB ANALYTICS - Ingestion Bronze")
    logger.info("=" * 50)
    logger.info(f"Source     : {args.data_dir}")
    logger.info(f"Base DuckDB: {args.db_path}")

    # Auto-download des fichiers manquants (sauf si --no-download)
    if not args.no_download:
        ensure_data_files(args.data_dir, reviews_url=args.reviews_url)

    # Connexion DuckDB
    conn = create_database(args.db_path)

    # Chargement des 3 tables Bronze
    total = 0
    total += load_hosts(conn, args.data_dir)
    total += load_listings(conn, args.data_dir)
    total += load_reviews(conn, args.data_dir)

    # Verification
    verify_tables(conn)

    if args.verify:
        for tbl in ["raw_hosts", "raw_listings", "raw_reviews"]:
            try:
                show_sample(conn, tbl)
            except Exception:
                pass

    conn.close()
    logger.info(f"Ingestion terminee. {total:,} lignes chargees au total.")
    logger.info("Prochaine etape : dbt seed && dbt run")


if __name__ == "__main__":
    main()