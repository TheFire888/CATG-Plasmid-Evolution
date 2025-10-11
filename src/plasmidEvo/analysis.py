"""
Esse módulo encapsula toda as análises do plasmidEvo, usando anotações,
fluxo e gerando um banco de dados com os principais resultados.
"""

import subprocess
import shutil
import re
from pathlib import Path

import polars as pl


class AnalysisEngine:
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
        Realiza a anotação dos genes preditos

        Args:
            output_dir (Path): O objeto Path do diretório de saída.
        """
        print("--- Iniciando anotação dos genes ---")
        protein_path = output_dir / "proteins.faa"
        output_annotations_path = output_dir / "annotations"

        annotation_cmd = ["interproscan",
                          "--input", str(protein_path),
                          "--applications", str(self.applications),
                          "--iprlookup --goterms --pathways",
                          "--data-dir", str(self.data_dir),
                          "--cpu", str(self.num_cpu),
                          "--outṕut-dir", str(output_annotations_path)
                          ]
        self._run_command(annotation_cmd)


    def convert_flow_tree_to_lazyframe(self, output_dir: Path) -> None:
        """
        Converte um arquivo de saída do Infomap, .ftree, para um banco
        de dados rico em informação.
        """
        ftree_file = output_dir / 'clustered_graph_5.ftree'
        
        # TODO: Continue a partir daqui !!!

        with open(input_file, 'r', encoding="utf-8") as f_in:
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
