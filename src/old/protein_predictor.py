"""
Esse módulo é uma interface de linha de comando para predição de genes
em sequências de nucleotídeos por uso do Pyrodigal.
"""

from multiprocessing.pool import ThreadPool
from pyrodigal import GeneFinder
import Bio.SeqIO
import click


def find_genes(seq):
    """
    Encontra os genes em uma sequência de nucleotídeos.

    Args:
        seq (str or buffer): Uma sequência de nucleotídeos para ser
        processada, podendo ser uma string de caracteres ou um objeto
        implementando um protocolo de buffer.

    Returns:
        Genes: Uma lista de todos os genes encontrados no input.
    """
    return (seq.id, GeneFinder(meta=True).find_genes(bytes(seq.seq)))


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
@click.argument("output_count_file", type=click.Path())
def translate_genes(input_file, output_file, output_count_file):
    """
    Lê um arquivo FASTA contendo múltiplas sequências de nucleotídeos e
    gera um arquivo FASTA com os genes preditos e um arquivo .tsv com a
    contagem de genes por contig.

    Args:
        input_file (str): O caminho para o arquivo FASTA de entrada.
        output_file (str): O caminho para o arquivo FASTA de saída com os genes preditos.
        output_count_file (str): O caminho para o arquivo .tsv de saída com a contagem de genes por contig.
    """
    fasta_parser = Bio.SeqIO.parse(input_file, "fasta")
    with (
            ThreadPool() as pool,
            open(output_file, "w", encoding="utf-8") as f_out,
            open(output_count_file, "w", encoding="utf-8") as f_count
            ):

        for seq_id, pred_genes in pool.imap(find_genes, fasta_parser):
            f_count.write(f"{seq_id}\t{len(pred_genes)}\n")
            for gene_id, gene in enumerate(pred_genes):
                f_out.write(
                        f">{seq_id}_{gene_id+1} "
                        f"strand={gene.strand} start={gene.begin} end={gene.end} "
                        f"partial_begin={int(gene.partial_begin)} partial_end={int(gene.partial_end)} "
                        + "\n"
                        )
                f_out.write(gene.translate(include_stop=False) + "\n")


if __name__ == "__main__":
    translate_genes()
