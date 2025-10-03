"""
Este módulo encapsula a predição de genes usando a biblioteca Pyrodigal.
"""

from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Tuple, Iterable

import Bio.SeqIO
from Bio.SeqRecord import SeqRecord
from pyrodigal import GeneFinder


class ProteinPredictor:
    """
    Prevê proteínas em sequências de nucleotídeos usando Pyrodigal.

    Esta classe gerencia a leitura do FASTA, o processamento em paralelo
    e a escrita dos arquivos de saída (proteínas preditas e contagem de genes).
    """

    def __init__(self, params: dict = None):
        """
        Inicializa o preditor de proteínas.

        Args:
            params (dict, optional): Um dicionário de configuração.
                Chaves esperadas:
                'meta' (bool): Se deve rodar em modo metagenômico.
                               Padrão: True.
                'threads' (int): Número de threads.
                               Padrão: None (usa todos os cores).
        """
        if params is None:
            params = {}
        self.meta = params.get("meta", True)
        self.threads = params.get("threads")

    def _find_genes_in_sequence(
            self, seq_record: SeqRecord) -> Tuple[str, Iterable[GeneFinder]]:
        """
        (Método privado) Executa o `find_genes` em um único
        registro de sequência.
        """
        gene_finder = GeneFinder(meta=self.meta)
        genes = gene_finder.find_genes(bytes(seq_record.seq))
        return seq_record.id, genes

    def predict(self, input_fasta: str, output_dir: Path) -> None:
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

        print(f"Iniciando predição de proteínas para: {input_path.name}")

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

        print(f"Proteínas salvas em: {output_proteins_path}")


# Teste da classe
if __name__ == "__main__":
    pp = ProteinPredictor()
    pp.predict("data/test_seqs.fna", Path("test/"))
