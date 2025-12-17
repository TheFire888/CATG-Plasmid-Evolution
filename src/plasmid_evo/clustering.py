"""
Esse módulo agrupa os genes e plasmídeos em uma rede para identificar
coisas biológicas legais e tals :3
"""

from pathlib import Path
from infomap import Infomap
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

class GeneClusterer:
    def __init__(self, params: dict = None):
        """
        Inicializa o agrupador de plasmídeos e genes.

        Args:
            params (dict, optional): Dicionário de configuração.
                                     (Reservado para futuras extensões).
        """
        if params is None:
            params = {}
        # Futuros parâmetros podem ser adicionados aqui.

        self.num_trials = params.get("num_trials", 10)
        self.variable_markov_time = params.get("variable_markov_time", True)

    def cluster(self, output_dir: Path, markov_time: float):
        """
        Aplica o algoritmo do Infomap para encontrar os agrupamentos
        no grafo

        Args:
            output_dir (Path): Diretório onde o arquivo de saída será salvo.
        """
        input_path = str(output_dir / "graph.net")
        output_name = str(output_dir
                          / f"clustered_graph_{markov_time}.ftree")
        logging.info("Iniciando agrupamento...")
        im = Infomap(two_level=True,
                     num_trials=self.num_trials,
                     out_name=output_name,
                     markov_time=markov_time,
                     variable_markov_time=self.variable_markov_time)
        im.read_file(input_path)
        im.run()
        im.write_flow_tree(f"{output_name}")


if __name__ == "__main__":
    gc = GeneClusterer()
    gc.cluster(Path("test/"))
