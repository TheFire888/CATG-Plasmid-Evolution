import igraph as ig
from pathlib import Path
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

data_dir = Path('test/6790.17-12-2025_10:51:03')
graph_file = data_dir / 'graph.graphml'
betweenness_file = data_dir / 'betweenness.tsv'

logging.info("Loading graph...")
g = ig.Graph.Read(str(gt_file), format="graphml")
logging.info("Graph loaded")

logging.info("Calculating betweenness...")
vb = g.betweenness()

logging.info(f"Writing results to {betweenness_file}...")

with open(betweenness_file, 'w', encoding="utf-8") as f_out:
    for i, value in enumerate(vb):
        f.write(f"{i}\t{g.vp["name"][i]}\t{value}\n")
