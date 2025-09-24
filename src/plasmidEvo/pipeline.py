"""
Este módulo realiza toda a pipeline necessária para o plasmidEvo
"""
from pathlib import Path

from plasmidEvo.prediction import ProteinPredictor
from plasmidEvo.alignment import DiamondAligner
from plasmidEvo.filtering import RBHFilter
from plasmidEvo.graph import GeneGraph
from plasmidEvo.clustering import GeneClusterer
# from .analysis import AnalysisEngine


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
        # self.analyzer = AnalysisEngine()

    # TODO: Adicionar "resume"
    def run(self, input_fasta: str, output_dir: str) -> None:
        """
        Executa a sequência completa de análise.

        Args:
            input_fasta: Caminho para o arquivo FASTA de entrada.
            output_dir: Diretório onde os resultados serão salvos.
        """
        print("--- Iniciando pipeline plasmidEvo ---")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.predictor.predict(input_fasta, output_path)
        self.aligner.align(output_path)
        self.rbh_filter.diamond_filter(output_path)
        self.graph_builder.generate(output_path)
        self.clusterer.cluster(output_path)
        # self.analyzer.generate_report(output_path)

        print("--- Pipeline concluída. "
              f"Resultados salvos em {output_path} ---")
