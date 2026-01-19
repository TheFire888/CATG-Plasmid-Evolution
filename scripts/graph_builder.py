from pathlib import Path
import threading
import psutil
import time
import os
import logging
import csv

import click
import graph_tool.all as gt
import polars as pl

logging.basicConfig(level=logging.DEBUG, format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")

def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.debug(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(10)

threading.Thread(target=log_memory, daemon=True).start()

def build_graph(output_dir: Path):
    logging.info("Escrevendo arquivo de saída...")
    input_path = output_dir / 'protein_clusters.tsv'
    ncol_file = output_dir / 'graph.ncol'
    graphml_file = output_dir / 'graph.graphml'

    base_scan = pl.scan_csv(
        input_path,
        separator='\t',
        has_header=False,
        new_columns=["centroid", "protein"]
    ).with_columns(
        contig=pl.col("protein").str.replace(r"_[^_]*$", "")
    ).select(["centroid", "contig"]).unique()

    base_scan.sink_csv(
       ncol_file,
       separator='\t',
       include_header=False
    )

    def edges():
        with open(ncol_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                yield tuple(row)

    graph = gt.Graph(edges(), hashed=True, directed=False)

    graph.save(str(graphml_file))

@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    build_graph(Path(output_dir))

if __name__ == "__main__":
    main()
