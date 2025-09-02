"""
Interpreta o output do DIAMOND como uma rede de interações genéticas,
construindo um grafo no formato Pajek.
"""

from collections import defaultdict
import csv
import click


def discover_data(input_file):
    """
    Primeira passagem: lê o arquivo para descobrir todos os nós únicos
    (genes e plasmídeos) e para mapear cada gene ao seu bitscore de autohit.

    Args:
        input_file (str): arquivo de entrada com os hits

    Returns:
        Retorna um conjunto de nós e um defaultdict de autohits.
    """
    nodes = set()
    autohits = defaultdict(lambda: 1.0)

    with open(input_file, 'r', newline='', encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if len(row) >= 4 and row[0] == row[1]:
                try:
                    autohits[row[0]] = float(row[3])
                except ValueError:
                    continue

    with open(input_file, 'r', newline='', encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if len(row) < 2:
                continue
            source_gene = row[0]
            target_gene = row[1]
            nodes.add(source_gene)
            nodes.add(target_gene)
            if '_' in source_gene:
                nodes.add(source_gene.rsplit('_', 1)[0])
            if '_' in target_gene:
                nodes.add(target_gene.rsplit('_', 1)[0])

    node_to_id = {node: i + 1 for i, node in enumerate(list(nodes))}
    return node_to_id, autohits


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def generate_pajek_file(input_file, output_file):
    """
    Gera um arquivo Pajek de um grafo bipartido com arestas em uma das
    partições, onde os contigs se conectam aos seus genes com peso 1.0
    e os genes se conectam entre si com peso igual a razão do bitscore
    dividido pelo bitscore do próprio gene.

    Args:
        input_file (str): arquivo de entrada com os hits
        output_file (str): arquivo de saída, formato Pajek
    """
    node_to_id, autohits = discover_data(input_file)

    with open(output_file, 'w', encoding="utf-8") as netfile:
        netfile.write(f"*Vertices {len(node_to_id)}\n")
        for node_name, node_id in node_to_id.items():
            netfile.write(f'{node_id} "{node_name}"\n')

        netfile.write("*Edges\n")

        with open(input_file, 'r', newline='', encoding="utf-8") as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            for row in reader:
                if len(row) < 4 or row[0] == row[1]:
                    continue
                source_gene, target_gene, weight_str = row[0], row[1], row[3]
                try:
                    weight = float(weight_str) / autohits[source_gene]
                    source_id = node_to_id[source_gene]
                    target_id = node_to_id[target_gene]
                    netfile.write(f"{source_id} {target_id} {weight}\n")
                except (ValueError, KeyError):
                    continue

        for node_name in node_to_id:
            if '_' in node_name:
                try:
                    weight = autohits[node_name]
                    plasmid_name = node_name.rsplit('_', 1)[0]

                    if plasmid_name in node_to_id:
                        gene_id = node_to_id[node_name]
                        plasmid_id = node_to_id[plasmid_name]
                        netfile.write(f"{gene_id} {plasmid_id} {weight}\n")
                except (IndexError, KeyError):
                    continue


if __name__ == '__main__':
    generate_pajek_file()
