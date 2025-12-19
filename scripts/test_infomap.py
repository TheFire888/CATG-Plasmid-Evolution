from pathlib import Path
import psutil
import threading
import time
import os
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )
from infomap import Infomap


def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.info(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(30)

threading.Thread(target=log_memory, daemon=True).start()

output_dir = Path("test/4267.24-09-2025_14:09:34")
markov_time = 0.1
input_path = str(output_dir / "graph.net")
output_name = str(output_dir
                  / f"clustered_graph_{markov_time}.ftree")

im = Infomap(two_level=True,
             num_trials=3,
             out_name=output_name,
             markov_time=markov_time,
             variable_markov_time=True)
logging.info("Lendo arquivo de entrada...")
im.read_file(input_path)
logging.info("Iniciando agrupamento...")
im.run()
logging.info("Salvando arquivo de saída...")
im.write_flow_tree(f"{output_name}")

