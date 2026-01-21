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

def analyse(output_dir: Path):
    graph_ncol = output_dir / 'graph.ncol'

    def edges(tmp_file):
        with open(tmp_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                yield tuple(row)

    # g = gt.Graph(edges(graph_ncol), hashed=True, directed=False)
    g = gt.collection.data["astro-ph"]

    state = gt.minimize_nested_blockmodel_dl(g)

    def save_paths(g, state):
        output_path = output_dir / 'cluster_paths.tsv'
        lvls = state.get_levels()
        avail = []

        with open(output_path, 'w') as f_out:
            for lvl in lvls:
                if lvl.get_N() == 1:
                    break
                avail.append(lvl)

            for i, node in enumerate(g.vp['label']):
                path = [str(i), f"'{node}'"]
                
                r = lvls[0].get_blocks()[i]

                path.append(str(r))
                
                for j in range(1,len(avail)):
                    r = lvls[j].get_blocks()[r]
                    path.append(str(r))

                f_out.write(f"{'\t'.join(path)}\n")

    save_paths(g, state)

@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    analyse(Path(output_dir))

if __name__ == "__main__":
    main()
