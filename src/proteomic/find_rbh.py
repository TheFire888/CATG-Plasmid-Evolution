"""
Esse módulo é uma interface de linha de comando para filtrar
os Reciprocal Best Hits de um output do DIAMOND.
"""

from collections import defaultdict
import click
from file_read_backwards import FileReadBackwards


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def find_rbh(input_file, output_file):
    """
    Filtra os RBH em um arquivo de saída do DIAMOND

    Args:
        input_file (str): Arquivo do DIAMOND a ser filtrado.
        output_file (str): Arquivo de saída, apenas com os RBH.
    """
    best_hits = defaultdict(dict)
    with FileReadBackwards(input_file, encoding="utf-8") as f_in:
        for line in f_in:
            qseq_gene_id, sseq_gene_id = line.split()[:2]
            qseq_contig, sseq_contig = qseq_gene_id.rsplit("_", 1)[0], sseq_gene_id.rsplit("_", 1)[0]
            if (qseq_contig == sseq_contig) and (qseq_gene_id != sseq_gene_id):
                continue
            best_hits[qseq_gene_id][sseq_contig] = sseq_gene_id
    with FileReadBackwards(input_file, encoding="utf-8") as f_in, open(output_file, 'w', encoding="utf-8") as f_out:
        for line in f_in:
            qseq_gene_id, sseq_gene_id = line.split()[:2]
            qseq_contig, sseq_contig = qseq_gene_id.rsplit("_", 1)[0], sseq_gene_id.rsplit("_", 1)[0]
            if (qseq_contig in best_hits[sseq_gene_id]) and (best_hits[sseq_gene_id][qseq_contig] == qseq_gene_id):
                f_out.write(line + "\n")


if __name__ == "__main__":
    find_rbh()
