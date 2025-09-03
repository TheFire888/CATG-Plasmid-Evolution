"""
Esse módulo é uma interface de linha de comando para encontrar
agrupamentos em um grafo.
"""

import click
import igraph as ig
from infomap import Infomap


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def infomap_cluster_data(input_file, output_file):
    """
    Aplica o algoritmo do Infomap 10 vezes para encontrar
    agrupamentos em um grafo.

    Args:
        input_file (str): arquivo Pajek de entrada.
        output_file (str): arquivo de saída com os
        agrupamentos encontrados
    """

    im = Infomap(num_trials=10)
    im.read_file(input_file)
    im.run()

    with open(output_file + ".label", 'w', encoding="utf-8") as f:
        for node in im.tree:
            if node.is_leaf:
                node_name = im.get_name(node.node_id)
                f.write(f"{node_name},{node.node_id}\n")

    im.write_newick(output_file)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def leiden_cluster_data(input_file, output_file):
    """
    Aplica o algoritmo do Leidein para encontrar
    agrupamentos em um grafo.

    Args:
        input_file (str): arquivo Pajek de entrada.
        output_file (str): arquivo de saída com os
        agrupamentos encontrados
    """

    click.echo("Loading graph...", err=True)
    g = ig.Graph.Load(input_file, format="pajek")

    click.echo("Clustering data...", err=True)
    community = ig.Graph.community_leiden(g)

    click.echo("Writing output...", err=True)
    with open(output_file, 'w', encoding="utf-8") as f:
        for cluster in community:
            f.write(' '.join(map(str, cluster)) + '\n')


if __name__ == "__main__":
    # infomap_cluster_data()
    leiden_cluster_data()
