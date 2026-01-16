from pathlib import Path
import threading
import psutil
import time
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

import polars as pl
import click


def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.debug(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(10)


threading.Thread(target=log_memory, daemon=True).start()


def diamond_filter(output_dir: Path) -> None:
    """
    Aplica o filtro de RBH a um arquivo de hits.

    Este método implementa uma estratégia de self-join em um lazyframe
    polars do arquivo de entrada para identificar os pares de RBH
    de forma eficiente.

    Args:
        output_dir (Path): Diretório onde o arquivo filtrado será salvo.
    """
    logging.info("Filtrando Reciprocal Best Hits (RBH)")
    input_path = output_dir / "diamond_results.tsv"
    output_path = output_dir / "rbh_hits.tsv"

    lf = (
        pl.scan_csv(
            input_path,
            separator="\t",
            has_header=False,
            new_columns=["qseq_gene", "sseq_gene", "bitscore"],
            schema_overrides=[pl.Categorical, pl.Categorical, pl.Float64],
            low_memory=True
        )
        .with_columns(
            qseq_contig=(
                pl.col("qseq_gene")
                .cast(pl.Utf8)
                .str.replace(r"_[^_]*$", "")
                .cast(pl.Categorical)
            ),
            sseq_contig=(
                pl.col("sseq_gene")
                .cast(pl.Utf8)
                .str.replace(r"_[^_]*$", "")
                .cast(pl.Categorical)
            ),
        )
        .filter(  # Garante que teremos os autohits
            (pl.col("qseq_contig") != pl.col("sseq_contig"))
            | (pl.col("qseq_gene") == pl.col("sseq_gene"))
        )
        .unique(subset=["qseq_gene", "sseq_contig"], keep="first")
    )

    lf.join(
        lf.select(
            pl.col("qseq_gene").alias("reverse_qseq"),
            pl.col("sseq_gene").alias("reverse_sseq"),
        ),
        left_on=["qseq_gene", "sseq_gene"],
        right_on=["reverse_sseq", "reverse_qseq"],
        how="inner",
    ).select("qseq_gene", "sseq_gene", "bitscore").sink_csv(
        output_path, separator="\t", include_header=False
    )

    logging.info(f"Filtragem concluída. Pares de RBH salvos em " f"{output_path}")
    return output_path


@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    diamond_filter(Path(output_dir))


if __name__ == "__main__":
    main()
