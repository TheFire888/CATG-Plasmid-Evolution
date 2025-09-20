"""
Esse módulo é uma interface de linha de comando feita para analisar
e avaliar agrupamentos realizados pelo PlasmidEvo.
"""
import re
import click
import polars as pl


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """
    Ferramenta de linha de comando para analisar e avaliar os agrupamentos
    realizados pelo PlasmidEvo.
    """


def convert_flow_tree_to_lazyframe(input_file):
    """
    Converte um arquivo de saída do Infomap, .ftree, para um lazyframe
    polars.
    """
    with open(input_file, 'r', encoding="utf-8") as f_in:
        modules = []
        nodes = []

        line_start = re.compile(r'^[0-9]+:')

        for line in f_in:
            if not line_start.match(line):
                continue
            line_parts = line.split()
            module_id = line_parts[0].split(':')[0]
            node_name = line_parts[2].strip('"')

            modules.append(module_id)
            nodes.append(node_name)

        data = {
                "module_id": modules,
                "node_name": nodes
                }

        return pl.LazyFrame(data)


def convert_blastp_to_lazyframe(input_file):
    """
    Converte um arquivo de saída do DIAMOND, .tsv, para um lazyframe
    polars.
    """
    lf = pl.scan_csv(input_file,
                     separator='\t',
                     has_header=False,
                     columns=[0, 1],
                     new_columns=["gene_A", "gene_B"])
    return lf


def process_flow_lazyframe_as_biological_data(
        lf: pl.LazyFrame) -> pl.LazyFrame:
    """
    Processa um lazyframe gerado a partir de um flow tree com
    dados biológicos
    """
    processed_lf = lf.with_columns(
            pl.when(pl.col("node_name").str.contains("_"))
            .then(pl.lit("gene"))
            .otherwise(pl.lit("contig"))
            .alias("type")
            .cast(pl.Categorical))

    return processed_lf


def get_cluster_stats():
    

if __name__ == "__main__":
    cli()
