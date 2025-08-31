from multiprocessing.pool import ThreadPool
from pyrodigal import GeneFinder
import Bio.SeqIO
import click


def find_genes(seq):
    return (seq.id, GeneFinder(meta=True).find_genes(bytes(seq.seq)))


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
@click.argument("output_count_file", type=click.Path())
def translate_genes(input_file, output_file, output_count_file):
    fasta_parser = Bio.SeqIO.parse(input_file, "fasta")
    with (
            ThreadPool() as pool,
            open(output_file, "w") as f_out,
            open(output_count_file, "w") as f_count
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
                f_out.write(gene.translate() + "\n")

if __name__ == "__main__":
    translate_genes()
