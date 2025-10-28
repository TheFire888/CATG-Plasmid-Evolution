"""
Este módulo fornece a lógica para filtrar Reciprocal Best Hits (RBH)
a partir de um arquivo de resultados de alinhamento do DIAMOND.
"""

from pathlib import Path
import polars as pl


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

    def diamond_filter(self, output_dir: Path) -> None:
        """
        Aplica o filtro de RBH a um arquivo de hits.

        Este método implementa uma estratégia de self-join em um lazyframe
        polars do arquivo de entrada para identificar os pares de RBH
        de forma eficiente.

        Args:
            output_dir (Path): Diretório onde o arquivo filtrado será salvo.
        """
        print("--- Filtrando Reciprocal Best Hits (RBH) ---")
        input_path = output_dir / "diamond_results.tsv"
        output_path = output_dir / "rbh_hits.tsv"

        lf = pl.scan_csv(
            input_path,
            separator='\t',
            has_header=False,
            new_columns=['qseq_gene', 'sseq_gene',
                         'pident', 'bitscore'
                         ],
            schema_overrides=[pl.Categorical, pl.Categorical,
                              pl.Float64, pl.Float64
                              ]
        ).with_columns(
            qseq_contig=(pl.col("qseq_gene").cast(pl.Utf8)
                         .str.replace(r"_[^_]*$", "").cast(pl.Categorical)),
            sseq_contig=(pl.col("sseq_gene").cast(pl.Utf8)
                         .str.replace(r"_[^_]*$", "").cast(pl.Categorical))
        ).filter(  # Garante que teremos os autohits
            (pl.col("qseq_contig") != pl.col("sseq_contig"))
            | (pl.col("qseq_gene") == pl.col("sseq_gene"))
        ).group_by(
            "qseq_gene", "sseq_contig"
        ).first()

        lf.join(
            lf.select(
                pl.col("qseq_gene").alias("reverse_qseq"),
                pl.col("sseq_gene").alias("reverse_sseq")
            ),
            left_on=["qseq_gene", "sseq_gene"],
            right_on=["reverse_sseq", "reverse_qseq"],
            how="inner"
        ).select(
            'qseq_gene', 'sseq_gene', 'pident', 'bitscore'
        ).sink_csv(output_path,
                   separator='\t',
                   include_header=False
                   )

        print(f"Filtragem concluída. Pares de RBH salvos em "
              f"{output_path}")
        return output_path


if __name__ == "__main__":
    rbh_filter = RBHFilter()
    rbh_filter.diamond_filter(Path("test/"))
