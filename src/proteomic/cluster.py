"""
Esse módulo é uma interface de linha de comando para encontrar
agrupamentos em um grafo.
"""

import click
import igraph as ig
from infomap import Infomap


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """
    Ferramenta de linha de comando para clusterizar grafos
    """
    pass


@cli.command(name="infomap", help="Utiliza o algoritmo Infomap")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
@click.option("--m-time", default=5)
def infomap_cluster_data(input_file, output_file, m_time):
    """
    Aplica o algoritmo do Infomap 10 vezes para encontrar
    agrupamentos em um grafo.

    Args:
        input_file (str): arquivo Pajek de entrada.
        output_file (str): arquivo de saída com os
        agrupamentos encontrados
        m_time (float): tempo de Markov, usado para
        controlar a granularidade
    """
    output_name = "f{output_file}_{m_time}"

    im = Infomap(num_trials=10, two_level=True, out_name=output_name,
                 ftree=True, markov_time=m_time, variable_markov_time=True)
    im.read_file(input_file)
    im.run()


def generate_graph(input_file):
    """
    Gera um grafo baseado no arquivo de entrada (formato ncol)

    Args:
        input_file (str): arquivo de entrada, formato ncol.
    Returns:
        graph: objeto de grafo gerado a partir do arquivo de entrada.

    """
    g = ig.Graph.Load(input_file, format="ncol")
    g.to_undirected(mode="each")
    return g


@cli.command(name="leiden", help="Utiliza o algoritmo Infomap")
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
    g = generate_graph(input_file)

    click.echo("Clustering data...", err=True)
    community = ig.Graph.community_leiden(g)

    click.echo("Writing output...", err=True)
    with open(output_file, 'w', encoding="utf-8") as f:
        for cluster in community:
            node_names = [g.vs[node_id]["name"] for node_id in cluster]
            f.write(' '.join(node_names) + '\n')


if __name__ == "__main__":
    cli()
