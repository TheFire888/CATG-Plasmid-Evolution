"""
Interpreta o output do DIAMOND como uma rede de interações genéticas,
construindo um grafo no formato ncol.
"""

from collections import defaultdict
from file_read_backwards import FileReadBackwards
import csv
import click


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
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

    with open(input_file, 'r', encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if row[0] == row[1]:
                autohits[row[0]] = float(row[3])

    with (
            open(input_file, 'r', encoding="utf-8") as tsvfile,
            open(output_file, 'w', encoding="utf-8") as ncolfile
            ):

        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            qseq_gene_id, sseq_gene_id, bitscore = row[0], row[1], float(row[3])
            qseq_contig, sseq_contig = qseq_gene_id.rsplit("_", 1)[0], sseq_gene_id.rsplit("_", 1)[0]

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
    generate_ncol_file()
