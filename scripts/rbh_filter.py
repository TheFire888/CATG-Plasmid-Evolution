from pathlib import Path
import threading
import psutil
import time
import os
import logging
import duckdb
import click

logging.basicConfig(level=logging.DEBUG, format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")

def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.debug(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(10)

threading.Thread(target=log_memory, daemon=True).start()

def diamond_filter(output_dir: Path) -> None:
    logging.info("Iniciando filtragem RBH via DuckDB (Out-of-Core)")
    input_path = output_dir / "diamond_results.tsv"
    output_path = output_dir / "rbh_hits.tsv"
    tmp_dir = output_dir / "duck_tmp"
    tmp_dir.mkdir(exist_ok=True)

    db = duckdb.connect()
    db.execute(f"SET temp_directory = '{tmp_dir}'")
    db.execute("SET memory_limit = '180GB'") # Ajuste conforme o job

    query = f"""
        COPY (
            WITH raw_hits AS (
                SELECT column0 as q, column1 as s, column2 as b,
                       split_part(column0, '_', 1) as qc,
                       split_part(column1, '_', 1) as sc
                FROM read_csv_auto('{input_path}', sep='\t', header=False)
                WHERE (split_part(column0, '_', 1) != split_part(column1, '_', 1)) 
                   OR (column0 = column1)
            ),
            bh AS (
                SELECT q, s, b FROM raw_hits
                QUALIFY ROW_NUMBER() OVER(PARTITION BY q, sc ORDER BY b DESC) = 1
            )
            SELECT a.q, a.s, a.b 
            FROM bh a
            JOIN bh b ON a.q = b.s AND a.s = b.q
        ) TO '{output_path}' (DELIMITER '\t', HEADER FALSE)
    """
    
    try:
        db.execute(query)
        logging.info(f"Filtragem concluída. Resultados em: {output_path}")
    finally:
        db.close()
        for f in tmp_dir.glob("*"): f.unlink()
        tmp_dir.rmdir()

@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    diamond_filter(Path(output_dir))

if __name__ == "__main__":
    main()
