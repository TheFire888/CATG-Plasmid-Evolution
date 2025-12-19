from pathlib import Path
from infomap import Infomap
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

output_dir = Path("test/4267.24-09-2025_14:09:34")
markov_time = 0.1
input_path = str(output_dir / "graph.net")
output_name = str(output_dir
                  / f"clustered_graph_{markov_time}.ftree")

logging.info("Iniciando agrupamento...")
im = Infomap(two_level=True,
             num_trials=3,
             out_name=output_name,
             markov_time=markov_time,
             variable_markov_time=True)
im.read_file(input_path)
im.run()
im.write_flow_tree(f"{output_name}")

