from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Tuple, Iterable
import threading
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

import Bio.SeqIO
from Bio.SeqRecord import SeqRecord
from pyrodigal import GeneFinder
import click

def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.debug(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(60)

threading.Thread(target=log_memory, daemon=True).start()

def _find_genes_in_sequence(
        seq_record: SeqRecord) -> Tuple[str, Iterable[GeneFinder]]:
    gene_finder = GeneFinder(meta=self.meta)
    genes = gene_finder.find_genes(bytes(seq_record.seq))
    return seq_record.id, genes

def predict(input_fasta: str, output_dir: Path) -> None:
    """
    Lê um arquivo FASTA, prevê os genes/proteínas e salva os resultados.

    Gera dois arquivos:
    1. Um FASTA (.faa) com as sequências de proteínas traduzidas.
    2. Um TSV (.tsv) com a contagem de genes por contig.

    Args:
        input_fasta (str): O caminho para o arquivo FASTA de entrada.
        output_dir (Path): O objeto Path do diretório de saída.

    Returns:
        Path: O caminho para o arquivo FASTA de proteínas gerado.
    """
    input_path = Path(input_fasta)
    output_proteins_path = output_dir / "proteins.faa"
    output_counts_path = output_dir / "gene_counts.tsv"

    logging.info(f"Iniciando predição de proteínas para: {input_path.name}")

    fasta_parser = Bio.SeqIO.parse(input_path, "fasta")

    with (
        ThreadPool(self.threads) as pool,
        open(output_proteins_path, "w", encoding="utf-8") as f_out,
        open(output_counts_path, "w", encoding="utf-8") as f_count,
    ):
        f_count.write("contig_id\tgene_count\n")

        # pool.imap processa os resultados conforme eles ficam prontos
        for seq_id, pred_genes in pool.imap(
            self._find_genes_in_sequence, fasta_parser
        ):
            f_count.write(f"{seq_id}\t{len(pred_genes)}\n")
            for i, gene in enumerate(pred_genes, 1):
                header = (
                    f">{seq_id}_{i} "
                    f"strand={gene.strand} start={gene.begin} "
                    f"end={gene.end} "
                    f"partial_begin={int(gene.partial_begin)} "
                    f"partial_end={int(gene.partial_end)}"
                )
                f_out.write(header + "\n")
                f_out.write(gene.translate(include_stop=False) + "\n")

    logging.info(f"Proteínas salvas em: {output_proteins_path}")

@click.command()
@click.argument('input_fasta', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--threads', '-t', default=1, help='Número de threads.')
def main(input_fasta, output_dir, threads):
    predict(input_fasta, Path(output_dir))

if __name__ == "__main__":
    main()
