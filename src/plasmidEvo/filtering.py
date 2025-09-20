"""
Este módulo fornece a lógica para filtrar Reciprocal Best Hits (RBH)
a partir de um arquivo de resultados de alinhamento do DIAMOND.
"""

from collections import defaultdict
from pathlib import Path
from file_read_backwards import FileReadBackwards


class RBHFilter:
    """
    Filtra um arquivo de resultados do DIAMOND para encontrar os
    Reciprocal Best Hits (RBH), operando diretamente no sistema de arquivos.
    """

    def __init__(self, params: dict = None):
        """
        Inicializa o filtro de RBH.

        Args:
            params (dict, optional): Dicionário de configuração.
                                     (Reservado para futuras extensões).
        """
        if params is None:
            params = {}
        # Futuros parâmetros podem ser adicionados aqui.

    def _get_contig_from_gene(self, gene_id: str) -> str:
        """
        Extrai o nome do contig a partir do ID do gene
        (ex: 'contigA_1' -> 'contigA').
        """
        return gene_id.rsplit("_", 1)[0]

    def diamond_filter(self, output_dir: Path) -> None:
        """
        Aplica o filtro de RBH a um arquivo de hits.

        Este método implementa uma estratégia de duas leituras no arquivo de
        entrada para identificar os pares de RBH de forma eficiente.

        Args:
            output_dir (Path): Diretório onde o arquivo filtrado será salvo.
        """
        print("--- Filtrando Reciprocal Best Hits (RBH) ---")
        input_path = output_dir / "diamond_results.tsv"
        output_path = output_dir / "rbh_hits.tsv"

        best_hits = defaultdict(dict)

        print("Passo 1/2: Mapeando os melhores hits...")
        with FileReadBackwards(input_path, encoding="utf-8") as f_in:
            for line in f_in:
                line_parts = line.split()
                qseq_gene_id, sseq_gene_id = line_parts[0], line_parts[1]

                qseq_contig = self._get_contig_from_gene(qseq_gene_id)
                sseq_contig = self._get_contig_from_gene(sseq_gene_id)

                if (qseq_contig == sseq_contig) and \
                        (qseq_gene_id != sseq_gene_id):
                    continue

                best_hits[qseq_gene_id][sseq_contig] = sseq_gene_id

        print("Passo 2/2: Filtrando e escrevendo os pares de RBH...")
        with (FileReadBackwards(input_path, encoding="utf-8") as f_in,
              open(output_path, "w", encoding="utf-8") as f_out
              ):
            for line in f_in:
                parts = line.split()
                qseq_gene_id, sseq_gene_id = parts[0], parts[1]

                qseq_contig = self._get_contig_from_gene(qseq_gene_id)
                sseq_contig = self._get_contig_from_gene(sseq_gene_id)

                if (
                    qseq_contig in best_hits[sseq_gene_id]
                    and best_hits[sseq_gene_id][qseq_contig] == qseq_gene_id
                ):
                    f_out.write(line + "\n")

        print(f"Filtragem concluída. Pares de RBH salvos em "
              f"{output_path}")
        return output_path


if __name__ == "__main__":
    rbh_filter = RBHFilter()
    rbh_filter.diamond_filter(Path("test/"))
