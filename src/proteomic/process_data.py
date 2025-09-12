"""
Esse módulo é uma interface de linha de comando feita para analisar
e avaliar agrupamentos realizados pelo PlasmidEvo.
"""
import re
from collections import defaultdict
from itertools import combinations
import click
import polars as pl


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """
    Ferramenta de linha de comando para analisar e avaliar os agrupamentos
    realizados pelo PlasmidEvo.
    """


@cli.command(name="cgp", help="Usado para comparar pares de genomas.")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
def compare_genome_pairs(input_file):
    """
    Gera um tsv com o número de hits entre dois contigs.
    """
    df = (
        pl.scan_csv(
            input_file,
            separator="\t",
            has_header=False,
            new_columns=["query_gene", "target_gene", "identity", "bitscore"],
        )
        .with_columns(
            query_genome=pl.col("query_gene").str.replace(r"_\d+$", ""),
            target_genome=pl.col("target_gene").str.replace(r"_\d+$", ""),
        )
        .filter(
            pl.col("query_genome") != pl.col("target_genome"),
            pl.col("query_gene") != pl.col("target_gene"),
        )
        .group_by(
            pl.concat_arr(pl.col("query_genome"), pl.col("target_genome"))
            .arr.sort()
            .arr.to_struct(["genome_1", "genome_2"])
            .alias("genome_pair")
        )
        .agg(pl.len().alias("n_shared_genes"))
        .unnest("genome_pair")
        .collect(engine="streaming")
    )

    return df


@cli.command(name="cpm", help="contigs por módulo")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
def process_ftree(input_path):
    """
    Lê um arquivo .ftree e escreve os contigs encontrados diretamente
    em um arquivo de saída.
    """
    with open(input_path, 'r', encoding="utf-8") as infile:
        click.echo("Procurando padrões...")
        line_start_pattern = re.compile(r'^[0-9]+:')

        contigs_per_module = defaultdict(set)

        for line in infile:
            if not line_start_pattern.match(line):
                continue

            parts = line.split()
            module_id = parts[0].split(':')[0]
            name = parts[2].strip('"')
            contigs_per_module[module_id].add(name)

    return contigs_per_module


def evaluate_modules(count_file, ftree_file, rbh_file):
    """
    Calcula uma métrica para cada par de genomas em um módulo.

    A métrica é: hits / (genes_genoma1 + genes_genoma2)
    """
    click.echo("Lendo arquivo de contagem de genes...")
    gene_counts = {}
    with open(count_file, 'r', encoding='utf-8') as f:
        for line in f:
            genome, count = line.strip().split()
            gene_counts[genome] = int(count)

    click.echo("Contando pares de genomas...")
    df_hits = compare_genome_pairs(rbh_file)

    click.echo("Processando arquivo .ftree para obter módulos...")
    contigs_per_module = process_ftree(ftree_file)

    click.echo("Calculando a métrica média para cada módulo...")
    for module_id, genomes in contigs_per_module.items():
        if len(genomes) < 2:
            continue

        module_metrics = []
        for g1, g2 in combinations(genomes, 2):
            genome1, genome2 = sorted((g1, g2))

            hits_row = df_hits.filter(
                (pl.col("genome_1") == genome1) & (pl.col("genome_2") == genome2)
            )

            if not hits_row.is_empty():
                hits = hits_row["n_shared_genes"][0]
                genes_1 = gene_counts.get(genome1, 0)
                genes_2 = gene_counts.get(genome2, 0)

                denominator = genes_1 + genes_2
                if denominator > 0:
                    metric = hits / denominator
                    module_metrics.append(metric)

        if module_metrics:
            average_metric = sum(module_metrics) / len(module_metrics)
            print(f"{module_id}: {average_metric}")


if __name__ == "__main__":
    cli()
