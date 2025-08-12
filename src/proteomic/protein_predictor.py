from multiprocessing.pool import ThreadPool
from pyrodigal import GeneFinder
import Bio.SeqIO
import sys
import click

def find_genes(seq):
    return (seq.id, GeneFinder(meta=True).find_genes(bytes(seq.seq)))

@click.command(context_setting={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def translate_genes(input_file, output_file):
    fasta_parser = Bio.SeqIO.parse(input_file, "fasta")
    with (
            ThreadPool() as pool,
            open(output_file, "w") as f_out
        ):
        for seq_id, pred_genes in pool.imap(find_genes, fasta_parser):
            for gene_id, gene in enumerate(pred_genes):
                f_out.write(f">{seq_id}_{gene_id+1}" + "\n")
                f_out.write(gene.translate() + "\n")

if __name__ == "__main__":
    translate_genes()
    
