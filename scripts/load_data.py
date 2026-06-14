"""
Script d ingestion des donnees Airbnb dans DuckDB
Etape 1 du pipeline : chargement couche Bronze

Usage:
    python scripts/load_data.py --data-dir ./data/raw

Les fichiers CSV attendus dans data/raw/ :
    - hosts.csv
    - listings.csv
    - reviews.csv
"""

import duckdb
import os
import argparse
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


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
        SELECT *
        FROM read_csv_auto(?, header=True)
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
        SELECT *
        FROM read_csv_auto(?, header=True)
    """, [listings_path])

    count = conn.execute("SELECT COUNT(*) FROM raw_listings").fetchone()[0]
    logger.info(f"raw_listings charge : {count:,} lignes")
    return count


def load_reviews(conn: duckdb.DuckDBPyConnection, data_dir: str) -> int:
    """Charge les avis depuis reviews.csv ou reviews.csv.gz (DuckDB gere le gzip nativement)."""
    reviews_path = os.path.join(data_dir, "reviews.csv")
    gz_path = os.path.join(data_dir, "reviews.csv.gz")

    if os.path.exists(reviews_path):
        source = reviews_path
    elif os.path.exists(gz_path):
        source = gz_path
        logger.info(f"Fichier compresse detecte : {gz_path}")
    else:
        logger.warning(f"Aucun fichier reviews trouve dans {data_dir}")
        return 0

    conn.execute("""
        CREATE OR REPLACE TABLE raw_reviews AS
        SELECT *
        FROM read_csv_auto(?, header=True, ignore_errors=True)
    """, [source])

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
    """Affiche un apercu d une table."""
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
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("AIRBNB ANALYTICS - Ingestion Bronze")
    logger.info("=" * 50)
    logger.info(f"Source     : {args.data_dir}")
    logger.info(f"Base DuckDB: {args.db_path}")

    # Connexion
    conn = create_database(args.db_path)

    # Chargement
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
