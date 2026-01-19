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

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)


def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.debug(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(10)


threading.Thread(target=log_memory, daemon=True).start()


def edges(graph_path):
    with open(graph_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            yield tuple(row)


def save_betweenness(output_dir: Path):
    graph_path = output_dir / "graph.ncol"
    output_path = output_dir / "betweenness.tsv"

    g = gt.Graph(edges(graph_path), hashed=True, directed=False)

    logging.info("Calculando betweenness...")
    vp, _ = gt.betweenness(g)
    logging.info("Salvando betweenness...")

    with open(output_path, "w", encoding="utf-8") as f_out:
        for i, value in enumerate(vp):
            f_out.write(f"{g.vp['ids'][i]}\t{value}\n")


def save_pagerank(output_dir: Path):
    graph_path = output_dir / "graph.ncol"
    output_path = output_dir / "pagerank.tsv"

    g = gt.Graph(edges(graph_path), hashed=True, directed=False)

    logging.info("Calculando pagerank...")
    pr = gt.pagerank(g)
    logging.info("Salvando pagerank...")

    with open(output_path, "w", encoding="utf-8") as f_out:
        for i, value in enumerate(pr):
            f_out.write(f"{g.vp['ids'][i]}\t{value}\n")


def save_count(output_dir: Path):
    graph_path = output_dir / "graph.ncol"
    output_path = output_dir / "plasmid_count.tsv"

    base_scan = (
        pl.scan_csv(
            graph_path,
            separator="\t",
            has_header=False,
            new_columns=["protein", "plasmid"],
        )
        .select(["protein"])
        .group_by("protein")
        .agg(pl.col("protein").count().alias("count"))
        .sort(pl.col("count"), descending=True)
    )

    logging.info("Salvando count...")
    base_scan.sink_csv(output_path, include_header=False, separator="\t")

@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    save_betweenness(Path(output_dir))
    save_pagerank(Path(output_dir))
    save_count(Path(output_dir))

if __name__ == "__main__":
    main()
