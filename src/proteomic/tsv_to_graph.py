"""
Interpreta o output do DIAMOND como uma rede de interações genéticas,
construindo um grafo no formato desejado. Atualmente suporta ncol e Pajek.
"""

from collections import defaultdict
import csv
import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """
    Ferramentas de linha de comando para gerar arquivos de grafos
    (Pajek e ncol) a partir do output filtrado para RBHs do DIAMOND.
    """
    pass


@cli.command(name="pajek", help="Gera um arquivo no formato Pajek.")
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
    click.echo("Passo 1/4: Coletando autohits...", err=True)
    autohits = defaultdict()
    with open(input_file, 'r', newline='', encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if len(row) >= 4 and row[0] == row[1]:
                try:
                    autohits[row[0]] = float(row[3])
                except ValueError:
                    continue

    click.echo("Passo 2/4: Descobrindo todos os nós...", err=True)
    nodes = set()
    with open(input_file, 'r', newline='', encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if len(row) < 2:
                continue
            qseq_gene_id, sseq_gene_id = row[0], row[1]
            nodes.add(qseq_gene_id)
            nodes.add(sseq_gene_id)
            if '_' in qseq_gene_id:
                nodes.add(qseq_gene_id.rsplit('_', 1)[0])

    click.echo("Passo 3/4: Mapeando nós para IDs...", err=True)
    node_to_id = {node: i + 1 for i, node in enumerate(sorted(list(nodes)))}
    nodes = None

    click.echo("Passo 4/4: Escrevendo arquivo de saída...", err=True)
    with open(output_file, 'w', encoding="utf-8") as netfile:
        netfile.write(f"*Vertices {len(node_to_id)}\n")
        for node, node_id in node_to_id.items():
            netfile.write(f'{node_id} "{node}"\n')

        netfile.write("*Edges\n")
        contig_genes_edges = set()
        with open(input_file, 'r', newline='', encoding="utf-8") as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            for row in reader:
                qseq_gene_id, sseq_gene_id, bitscore = row[0], row[1], float(row[3])

                if qseq_gene_id != sseq_gene_id:
                    try:
                        weight = float(bitscore) / autohits[qseq_gene_id]
                        source_id = node_to_id[qseq_gene_id]
                        target_id = node_to_id[sseq_gene_id]
                        netfile.write(f"{source_id} {target_id} {weight}\n")

                    except KeyError:
                        click.echo(
                            f"Aviso: Autohit para '{qseq_gene_id}' não encontrado. Aresta para '{sseq_gene_id}' será ignorada.",
                            err=True
                        )
                        continue
                    except ValueError:
                        continue

                if '_' in qseq_gene_id:
                    qseq_contig = qseq_gene_id.rsplit('_', 1)[0]
                    qedge = (qseq_contig, qseq_gene_id)
                    if qedge not in contig_genes_edges:
                        try:
                            source_id = node_to_id[qseq_contig]
                            target_id = node_to_id[qseq_gene_id]
                            netfile.write(f"{source_id} {target_id} 1.0\n")
                            contig_genes_edges.add(qedge)
                        except KeyError:
                            continue


@cli.command(name="ncol", help="Gera um arquivo no formato ncol.")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def generate_ncol_file(input_file, output_file):
    """
    Gera um arquivo ncol de um grafo bipartido com arestas em uma das
    partições, onde os contigs se conectam aos seus genes com peso 1.0
    e os genes se conectam entre si com peso igual a razão do bitscore
    dividido pelo bitscore do próprio gene.

    Args:
        input_file (str): arquivo de entrada com os hits
        output_file (str): arquivo de saída, formato Pajek
    """

    autohits = defaultdict()
    contig_genes_edges = set()

    click.echo("Passo 1/2: Coletando autohits...", err=True)
    with open(input_file, 'r', encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if row[0] == row[1]:
                autohits[row[0]] = float(row[3])

    click.echo("Passo 2/2: Escrevendo arquivo de saída...", err=True)
    with (
            open(input_file, 'r', encoding="utf-8") as tsvfile,
            open(output_file, 'w', encoding="utf-8") as ncolfile
            ):

        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            qseq_gene_id, sseq_gene_id, bitscore = row[0], row[1], float(row[3])
            qseq_contig = qseq_gene_id.rsplit("_", 1)[0]

            if qseq_gene_id != sseq_gene_id:
                try:
                    weight = bitscore / autohits[qseq_gene_id]
                    ncolfile.write(f"{qseq_gene_id}\t{sseq_gene_id}\t{weight}\n")
                except KeyError:
                    print(f"Aviso: Autohit não encontrado para {qseq_gene_id}. Ignorando a aresta.")
                    continue

            qedge = (qseq_contig, qseq_gene_id)
            if qedge not in contig_genes_edges:
                ncolfile.write(f"{qseq_contig}\t{qseq_gene_id}\t1.0\n")
                contig_genes_edges.add(qedge)


if __name__ == "__main__":
    cli()
