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

    with duckdb.connect() as db:
        tmp_dir = output_dir / "duck_tmp"
        tmp_dir.mkdir(exist_ok=True)
        db.execute(f"SET temp_directory = '{tmp_dir}'")
        db.execute("SET memory_limit = '64GB'") 

        query = f"""
        COPY (
            WITH raw_hits AS (
                SELECT column0 as q_gene, column1 as s_gene, column2 as bitscore,
                       regexp_replace(column0, '_[^_]+$', '') as q_contig,
                       regexp_replace(column1, '_[^_]+$', '') as s_contig
                FROM read_csv_auto('{input_path}', sep='\t', header=False)
                WHERE (regexp_replace(column0, '_[^_]+$', '') != (regexp_replace(column1, '_[^_]+$', ''))) 
                   OR (column0 = column1)
            ),
            best_hits AS (
                SELECT q_gene, s_gene, bitscore FROM raw_hits
                QUALIFY ROW_NUMBER() OVER(PARTITION BY q_gene, s_contig ORDER BY bitscore DESC) = 1
            )
            SELECT fwd.q_gene, fwd.s_gene, fwd.bitscore 
            FROM best_hits fwd
            JOIN best_hits rev ON fwd.q_gene = rev.s_gene AND fwd.s_gene = rev.q_gene
        ) TO '{output_path}' (DELIMITER '\t', HEADER FALSE)
        """
    
        db.execute(query)
        logging.info(f"Filtragem concluída. Resultados em: {output_path}")

        for f in tmp_dir.glob("*"): f.unlink()
        tmp_dir.rmdir()

@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    diamond_filter(Path(output_dir))

if __name__ == "__main__":
    main()
