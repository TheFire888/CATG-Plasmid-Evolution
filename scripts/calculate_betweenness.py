import graph_tool.all as gt
from pathlib import Path
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

data_dir = Path('../../test/6790.17-12-2025_10:51:03')
gt_file = data_dir / 'graph.gt.gz'
betweenness_file = data_dir / 'betweenness.tsv'

logging.info("Loading graph...")
g = gt.load_graph(str(gt_file))
logging.info("Graph loaded")

logging.info("Calculating betweenness...")
vb, eb = gt.betweenness(g)

logging.info(f"Writing results to {betweenness_file}...")

with open(betweenness_file, 'w', encoding="utf-8") as f_out:
    for i, value in enumerate(vb):
        f.write(f"{i}\t{g.vp["name"][i]}\t{value}\n")
