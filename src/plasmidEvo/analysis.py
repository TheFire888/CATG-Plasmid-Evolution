"""
Esse módulo encapsula toda as análises do plasmidEvo, usando anotações,
fluxo e gerando um banco de dados com os principais resultados.
"""

import subprocess
import shutil
import re
from pathlib import Path
import os

import polars as pl


class AnalysisEngine:
    """
    Executa as análises necessárias para gerar um relatório da
    hierarquia.

    Esta classe gerencia a criação do banco de dados a partir dos
    valores gerados pelos passos anteriores.
    """

    def __init__(self, params: dict = None):
        if not shutil.which("apptainer"):
            raise FileNotFoundError("O executável 'apptainer' não foi "
                                    "encontrado no PATH.")

        if params is None:
            params = {}

        self.applications = params.get("applications",
                                       "Pfam,NCBIfam,CDD,HAMAP")
        self.data_dir = params.get("data_dir")
        self.num_cpu = params.get("num_cpu", 16)

    def _run_command(self, command: list):
        """
        (Método privado) Executa um comando de subprocesso
        e lida com erros.
        """
        try:
            subprocess.run(
                command, check=True, capture_output=True,
                text=True, encoding="utf-8"
            )
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {' '.join(command)}")
            print(f"Stderr: {e.stderr}")
            raise

    def annotate_genes(self, output_dir: Path) -> None:
        """
        Realiza a anotação dos genes preditos e salva os resultados
        no diretório de saída.

        Args:
            output_dir (Path): O objeto Path do diretório de saída.
        """
        print("--- Iniciando anotação dos genes ---")
        protein_path = output_dir / "proteins.faa"
        output_annotations_path = output_dir / "annotations"

        sif_path = (Path(os.path.expanduser("~"))
                    / "images"
                    / "interproscan.sif"
                    )

        data_bind_host = self.data_dir / "data"
        data_bind_container = "/opt/interproscan/data"
        bind_mount = f"{data_bind_host}:{data_bind_container}"

        output_annotations_path.mkdir(parents=True, exist_ok=True)

        interpro_args = [
            "/opt/interproscan/interproscan.sh",
            "--input", str(protein_path),
            "--applications", str(self.applications),
            "--iprlookup",
            "--goterms",
            "--pathways",
            "--cpu", str(self.num_cpu),
            "--output-dir", str(output_annotations_path)
        ]

        annotation_cmd = [
            "apptainer",
            "--silent",
            "exec",
            "-B", bind_mount,
            str(sif_path),
        ] + interpro_args

        self._run_command(annotation_cmd)

    def convert_flow_tree_to_lazyframe(self, output_dir: Path) -> None:
        """
        Converte um arquivo de saída do Infomap, .ftree, para um banco
        de dados rico em informação.
        """
        ftree_file = output_dir / 'clustered_graph_5.ftree'

        # TODO: Continue a partir daqui !!!

        with open(ftree_file, 'r', encoding="utf-8") as f_in:
            modules = []
            flow = []
            nodes = []

            line_start = re.compile(r'^[0-9]+:')

            for line in f_in:
                if not line_start.match(line):
                    continue
                line_parts = line.split()
                module_id = int(line_parts[0].split(':')[0])
                node_flow = float(line_parts[1])
                node_name = line_parts[2].strip('"')

                modules.append(module_id)
                flow.append(node_flow)
                nodes.append(node_name)

            data = {
                    "module_id": modules,
                    "node_flow": flow,
                    "node_name": nodes
                    }
            raw_lf = pl.LazyFrame(data)

            processed_lf = raw_lf.with_columns(
                pl.when(pl.col("node_name").str.contains("_"))
                .then(pl.lit("gene"))
                .otherwise(pl.lit("contig"))
                .alias("type")
                .cast(pl.Categorical))

            return processed_lf
