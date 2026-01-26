import subprocess
import shutil
import threading
import psutil
import time
import os
from pathlib import Path
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

import click

def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.debug(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(60)

threading.Thread(target=log_memory, daemon=True).start()

def run_command(command: list):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        logging.error(f"Erro ao executar o comando: {' '.join(command)}")
        raise

max_target_seqs = 5000
query_cover = 80
subject_cover = 80
min_score = 30
out_columns = ["qseqid", "sseqid", "bitscore"]
out_format = ["6"] + out_columns

def align(output_dir: Path, threads) -> None:
    logging.info("Iniciando alinhamento all-versus-all com DIAMOND")
    protein_path = output_dir / "split"
    db_path = output_dir / "proteins.dmnd"
    for file in protein_path.iterdir():
        output_tsv_path = output_dir / 'diamond_results' / f"diamond_results.{file.stem}.tsv"

        logging.info(f"Executando a busca {file.stem} DIAMOND blastp...")
        blastp_cmd = [
            "diamond", "blastp",
            "-q", str(file),
            "-d", str(db_path),
            "-o", str(output_tsv_path),
            "--fast",
            "--outfmt", *out_format,
            "--max-target-seqs", str(max_target_seqs),
            "--query-cover", str(query_cover),
            "--subject-cover", str(subject_cover),
            "--min-score", str(min_score),
            "--threads", str(threads),
            "--bin", str(64),
            "--block-size", str(0.5),
        ]
        run_command(blastp_cmd)

        logging.info(f"Alinhamento {file.stem} concluído.")


@click.command()
@click.argument('output_dir', type=click.Path(exists=True))
@click.option('--threads', '-t', default=1, help='Número de threads.')
def main(output_dir, threads):
    align(Path(output_dir), threads)

if __name__ == "__main__":
    main()
