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
        if params is None:
            params = {}

    def convert_flow_tree_to_lazyframe(self, output_dir: Path, markov_time: float) -> None:
        """
        Converte um arquivo de saída do Infomap, .ftree, para um banco
        de dados rico em informação.
        """
        ftree_file = output_dir / f"clustered_graph_{markov_time}.ftree"

        with open(ftree_file, "r", encoding="utf-8") as f_in:
            modules = []
            flow = []
            nodes = []

            line_start = re.compile(r"^[0-9]+:")

            for line in f_in:
                if not line_start.match(line):
                    continue
                line_parts = line.split()
                module_id = int(line_parts[0].split(":")[0])
                node_flow = float(line_parts[1])
                node_name = line_parts[2].strip('"')

                modules.append(module_id)
                flow.append(node_flow)
                nodes.append(node_name)

            data = {"module_id": modules, "node_flow": flow, "node_name": nodes}
            raw_lf = pl.LazyFrame(data)

            processed_lf = raw_lf.with_columns(
                pl.when(pl.col("node_name").str.contains("_"))
                .then(pl.lit("gene"))
                .otherwise(pl.lit("contig"))
                .alias("type")
                .cast(pl.Categorical)
            )

            return processed_lf

    def generate_db(output_path: Path, markov_time: float):
        ftree_file = output_path / f"clustered_graph_{markov_time}.ftree"
        output_file = output_path / f"database_{markov_time}.ftree"

        infomap_lf = convert_flow_tree_to_lazyframe(ftree_file, markov_time)
        genes_lf = (
            infomap_lf.filter(pl.col("type") == "gene")
            .rename(
                {
                    "module_id": "gene_module",
                    "node_name": "gene",
                    "node_flow": "gene_flow",
                }
            )
            .select(["gene", "gene_module", "gene_flow"])
            .with_columns(pl.col("gene_module").cast(pl.Int64))
        )
        contig_lf = (
            infomap_lf.filter(pl.col("type") == "contig")
            .rename(
                {
                    "module_id": "plasmid_module",
                    "node_name": "plasmid",
                    "node_flow": "plasmid_flow",
                }
            )
            .select(["plasmid", "plasmid_module", "plasmid_flow"])
            .with_columns(
                pl.col("plasmid_module").cast(pl.Int64),
                pl.col("plasmid").cast(pl.Categorical),
            )
        )

        db_lf = (
            genes_lf.with_columns(
                pl.col("gene")
                .str.split("_")
                .list.first()
                .alias("plasmid")
                .cast(pl.Categorical)
            )
            .join(contig_lf, left_on="plasmid", right_on="plasmid", how="inner")
            .select(["plasmid", "gene", "plasmid_module", "gene_module"])
        )

        db_lf.sink_csv(output_file, separator='\t')
