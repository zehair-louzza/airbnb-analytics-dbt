"""
Script d ingestion des donnees Airbnb dans DuckDB
Etape 1 du pipeline : chargement couche Bronze

Usage:
    python scripts/load_data.py --data-dir ./data/raw
    python scripts/load_data.py --reviews-url <URL>     # Surcharge l URL de telechargement

Les fichiers CSV attendus dans data/raw/ :
    - hosts.csv                        (versionne dans le repo)
    - listings.csv                     (versionne dans le repo)
    - seed_full_moon_dates.csv         (versionne dans le repo)
    - reviews.csv  OU  reviews.csv.gz  (telecharge automatiquement depuis GitHub Releases)

Le fichier reviews.csv (~112 MB) depasse la limite GitHub (100 MB / fichier).
Il est donc heberge en cloud (GitHub Releases) et telecharge a la volee si absent.

Configuration de l URL :
    1. Argument CLI :  --reviews-url <URL>
    2. Variable env :  REVIEWS_URL=<URL> python scripts/load_data.py
    3. Defaut       :  voir REVIEWS_DOWNLOAD_URL ci-dessous
"""

import argparse
import logging
import os
import sys
import urllib.request
from pathlib import Path

import duckdb

# ============================================================
# CONFIGURATION
# ============================================================
# URL par defaut du fichier reviews.csv (GitHub Releases)
# A remplacer par votre propre URL apres avoir uploade le fichier :
#   https://github.com/<USER>/<REPO>/releases/download/<TAG>/<FILENAME>
REVIEWS_DOWNLOAD_URL = os.environ.get(
    "REVIEWS_URL",
    "https://github.com/zehair-louzza/airbnb-analytics-dbt-new/releases/download/v1.0-data/reviews.csv",
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# HELPERS
# ============================================================
def download_file(url: str, dest_path: str) -> bool:
    """Telecharge un fichier depuis une URL avec barre de progression."""
    logger.info(f"Telechargement depuis : {url}")
    logger.info(f"Destination          : {dest_path}")

    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
    try:
        last_pct = [-1]

        def _report(block_num: int, block_size: int, total_size: int) -> None:
            if total_size <= 0:
                return
            downloaded = block_num * block_size
            pct = min(int(downloaded * 100 / total_size), 100)
            if pct != last_pct[0] and pct % 5 == 0:
                mb_done = downloaded / 1_048_576
                mb_total = total_size / 1_048_576
                sys.stderr.write(
                    f"\r  {pct:3d}%  |  {mb_done:6.1f} / {mb_total:6.1f} MB"
                )
                sys.stderr.flush()
                last_pct[0] = pct

        urllib.request.urlretrieve(url, dest_path, reporthook=_report)
        sys.stderr.write("\n")
        size_mb = os.path.getsize(dest_path) / 1_048_576
        logger.info(f"Telechargement OK ({size_mb:.1f} MB)")
        return True
    except Exception as exc:
        sys.stderr.write("\n")
        logger.error(f"Echec du telechargement : {exc}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False


def ensure_reviews_file(data_dir: str, url: str) -> str | None:
    """
    Verifie la presence de reviews.csv ou reviews.csv.gz dans data_dir.
    Telecharge depuis l URL si aucun n existe.
    Retourne le chemin du fichier ou None en cas d echec.
    """
    csv_path = os.path.join(data_dir, "reviews.csv")
    gz_path = os.path.join(data_dir, "reviews.csv.gz")

    if os.path.exists(csv_path):
        logger.info(f"reviews.csv deja present : {csv_path}")
        return csv_path
    if os.path.exists(gz_path):
        logger.info(f"reviews.csv.gz deja present : {gz_path}")
        return gz_path

    logger.info("reviews.csv absent en local. Telechargement depuis le cloud...")
    # On telecharge sous le nom de la fin de l URL (csv ou gz)
    fname = url.split("/")[-1].split("?")[0]
    if not fname.startswith("reviews.csv"):
        fname = "reviews.csv"
    dest = os.path.join(data_dir, fname)

    if download_file(url, dest):
        return dest
    return None


# ============================================================
# DUCKDB INGESTION
# ============================================================
def create_database(db_path: str) -> duckdb.DuckDBPyConnection:
    """Cree ou ouvre la base DuckDB."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = duckdb.connect(db_path)
    logger.info(f"Connexion DuckDB etablie : {db_path}")
    return conn


def load_hosts(conn: duckdb.DuckDBPyConnection, data_dir: str) -> int:
    """Charge les donnees des hotes depuis hosts.csv."""
    hosts_path = os.path.join(data_dir, "hosts.csv")
    if not os.path.exists(hosts_path):
        logger.warning(f"Fichier introuvable : {hosts_path}")
        return 0

    conn.execute(
        """
        CREATE OR REPLACE TABLE raw_hosts AS
        SELECT *
        FROM read_csv_auto(?, header=True)
        """,
        [hosts_path],
    )
    count = conn.execute("SELECT COUNT(*) FROM raw_hosts").fetchone()[0]
    logger.info(f"raw_hosts charge : {count:,} lignes")
    return count


def load_listings(conn: duckdb.DuckDBPyConnection, data_dir: str) -> int:
    """Charge les annonces depuis listings.csv."""
    listings_path = os.path.join(data_dir, "listings.csv")
    if not os.path.exists(listings_path):
        logger.warning(f"Fichier introuvable : {listings_path}")
        return 0

    conn.execute(
        """
        CREATE OR REPLACE TABLE raw_listings AS
        SELECT *
        FROM read_csv_auto(?, header=True)
        """,
        [listings_path],
    )
    count = conn.execute("SELECT COUNT(*) FROM raw_listings").fetchone()[0]
    logger.info(f"raw_listings charge : {count:,} lignes")
    return count


def load_reviews(conn: duckdb.DuckDBPyConnection, data_dir: str, reviews_url: str) -> int:
    """
    Charge les avis depuis reviews.csv ou reviews.csv.gz.
    Telecharge depuis le cloud (GitHub Releases) si fichier absent.
    DuckDB gere le .gz nativement via read_csv_auto.
    """
    source = ensure_reviews_file(data_dir, reviews_url)
    if source is None:
        logger.error(
            "Impossible de charger reviews. Verifiez votre connexion ou l URL :\n"
            f"  {reviews_url}"
        )
        return 0

    conn.execute(
        """
        CREATE OR REPLACE TABLE raw_reviews AS
        SELECT *
        FROM read_csv_auto(?, header=True, ignore_errors=True)
        """,
        [source],
    )
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


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Charge les CSV Airbnb dans DuckDB (couche Bronze)."
    )
    parser.add_argument(
        "--data-dir",
        default="./data/raw",
        help="Dossier des CSV (default: ./data/raw)",
    )
    parser.add_argument(
        "--db-path",
        default="./data/airbnb.duckdb",
        help="Chemin vers la base DuckDB (default: ./data/airbnb.duckdb)",
    )
    parser.add_argument(
        "--reviews-url",
        default=REVIEWS_DOWNLOAD_URL,
        help=(
            "URL cloud du fichier reviews.csv (par defaut : variable REVIEWS_URL "
            "ou constante REVIEWS_DOWNLOAD_URL dans le script)"
        ),
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("AIRBNB ANALYTICS - Ingestion Bronze")
    logger.info("=" * 60)
    logger.info(f"Source       : {args.data_dir}")
    logger.info(f"Base DuckDB  : {args.db_path}")
    logger.info(f"Reviews URL  : {args.reviews_url}")

    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    conn = create_database(args.db_path)

    total = 0
    total += load_hosts(conn, args.data_dir)
    total += load_listings(conn, args.data_dir)
    total += load_reviews(conn, args.data_dir, args.reviews_url)

    verify_tables(conn)
    conn.close()

    logger.info(f"Ingestion terminee. {total:,} lignes chargees au total.")
    logger.info("Prochaine etape : dbt seed && dbt run")


if __name__ == "__main__":
    main()
