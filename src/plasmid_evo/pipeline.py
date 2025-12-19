"""
Este módulo realiza toda a pipeline necessária para o plasmidEvo
"""
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

from plasmid_evo.prediction import ProteinPredictor
from plasmid_evo.alignment import DiamondAligner
from plasmid_evo.filtering import RBHFilter
from plasmid_evo.graph import GeneGraph
from plasmid_evo.clustering import GeneClusterer
from plasmid_evo.analysis import AnalysisEngine


class PlasmidEvoPipeline:
    """
    Realiza o fluxo de trabalho completo para a análise evolutiva de plasmídeos
    baseado em fluxo gênico.
    """

    def __init__(self, config: dict):
        """
        Inicializa o pipeline e seus componentes a partir de um dicionário de
        configuração.
        """
        self.predictor = ProteinPredictor(config.get('predictor_params', {}))
        self.aligner = DiamondAligner(config.get('aligner_params', {}))
        self.rbh_filter = RBHFilter(config.get('filter_params', {}))
        self.graph_builder = GeneGraph()
        self.clusterer = GeneClusterer(config.get('clusterer_params', {}))
        self.analyzer = AnalysisEngine()

    # TODO: Adicionar "resume"
    def run(self, input_fasta: str, output_dir: str) -> None:
        """
        Executa a sequência completa de análise.

        Args:
            input_fasta: Caminho para o arquivo FASTA de entrada.
            output_dir: Diretório onde os resultados serão salvos.
        """
        logging.info("Iniciando pipeline plasmidEvo")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        def log_memory():
            process = psutil.Process(os.getpid())
            while True:
                mem = process.memory_info().rss / 1024**2
                logging.debug(f"Monitor: {mem:.2f} MB em uso")
                time.sleep(10)

        # Thread secundária para monitoramento de memória
        # Talvez exiga um segundo processo? Preciso ver isso aí, vou assumir que não
        threading.Thread(target=log_memory, daemon=True).start()

        self.predictor.predict(input_fasta, output_path)
        self.aligner.align(output_path)
        self.rbh_filter.diamond_filter(output_path)
        self.graph_builder.generate(output_path)
        self.clusterer.cluster(output_path, 0.1)

        # Executa para diferentes tempos de Markov
        # for markov_time in [0.1, 0.2, 0.5, 1, 2, 4]:
        #     self.clusterer.cluster(output_path, markov_time)
        #     self.analyzer.generate_db(output_path, markov_time)

        logging.info("Pipeline concluída. "
              f"Resultados salvos em {output_path}")
