from multiprocessing.pool import ThreadPool
from pyrodigal import GeneFinder
#from needletail import parse_fastx_file
import Bio.SeqIO
#import click
import sys

def find_genes(seq):
    return (seq.id, GeneFinder(meta=True).find_genes(bytes(seq.seq)))

def translate_genes(input_seqs, f_out):
    with (
            ThreadPool() as pool,
            open(f_out, "w") as f_out
        ):
        for seq_id, pred_genes in pool.imap(find_genes, input_seqs):
            for gene_id, gene in enumerate(pred_genes):
                f_out.write(f">{seq_id}_{gene_id+1}" + "\n")
                f_out.write(gene.translate() + "\n")

if __name__ == "__main__":
    f_in = sys.argv[1]
    f_out = sys.argv[2]
    input_seqs = Bio.SeqIO.parse(f_in, "fasta")
    translate_genes(input_seqs, f_out)
    
