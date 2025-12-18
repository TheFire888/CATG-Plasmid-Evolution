"""
Este módulo encapsula a lógica para realizar o alinhamento all-versus-all
usando a ferramenta DIAMOND.
"""

import subprocess
import shutil
from pathlib import Path
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

class DiamondAligner:
    """
    Executa um alinhamento all-versus-all com DIAMOND.

    Esta classe gerencia a criação do banco de dados DIAMOND a partir de
    um arquivo de proteínas, executa a busca `blastp` e carrega os
    dados.
    """

    def __init__(self, params: dict = {}):
        """
        Inicializa o alinhador com parâmetros configuráveis.

        Args:
            params (dict, optional): Dicionário de configuração.
                Chaves esperadas:
                'max_target_seqs' (int): Número máximo de alinhamentos
                                         por query.
                'query_cover' (int): Cobertura mínima da query (0-100).
                'subject_cover' (int): Cobertura mínima do subject (0-100).
                'min_score' (int): Bitscore mínimo.
                'threads' (int): Número de threads a serem usadas.
        """
        if not shutil.which("diamond"):
            raise FileNotFoundError("O executável 'diamond' não foi "
                                    "encontrado no PATH.")

        self.max_target_seqs = params.get("max_target_seqs", 1000)
        self.query_cover = params.get("query_cover", 75)
        self.subject_cover = params.get("subject_cover", 75)
        self.min_score = params.get("min_score", 30)
        self.threads = params.get("threads", 4)
        self.out_columns = ["qseqid", "sseqid", "bitscore"]
        self.out_format = ["6"] + self.out_columns
        # TODO: Adicionar parâmetro de sensibilidade

    def _run_command(self, command: list):
        """
        (Método privado) Executa um comando de subprocesso
        e lida com erros.
        """
        try:
            subprocess.run(
                command, check=True, capture_output=True,
                text=True, encoding="utf-8"
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao executar o comando: {' '.join(command)}")
            logging.error(f"Stderr: {e.stderr}")
            raise

    def align(self, output_dir: Path) -> None:
        """
        Orquestra o processo de alinhamento completo.

        Args:
            output_dir (Path): O objeto Path do diretório de saída.
        """
        logging.info("Iniciando alinhamento all-versus-all com DIAMOND")
        protein_path = output_dir / "proteins.faa"
        db_path = output_dir / f"{protein_path.stem}.dmnd"
        output_tsv_path = output_dir / "diamond_results.tsv"

        # Etapa 1: Criar o banco de dados DIAMOND
        logging.info(f"Criando banco de dados DIAMOND em: {db_path}")
        makedb_cmd = [
            "diamond", "makedb",
            "--in", str(protein_path),
            "-d", str(db_path)
        ]
        self._run_command(makedb_cmd)

        # Etapa 2: Executar a busca BLASTp
        logging.info("Executando a busca DIAMOND blastp...")
        blastp_cmd = [
            "diamond", "blastp",
            "--quiet",
            "-q", str(protein_path),
            "-d", str(db_path),
            "-o", str(output_tsv_path),
            "--sensitive",
            "--outfmt", *self.out_format,
            "--max-target-seqs", str(self.max_target_seqs),
            "--query-cover", str(self.query_cover),
            "--subject-cover", str(self.subject_cover),
            "--min-score", str(self.min_score),
            "--threads", str(self.threads),
        ]
        self._run_command(blastp_cmd)

        logging.info("Alinhamento concluído.")


if __name__ == "__main__":
    da = DiamondAligner()
    da.align(Path("test/"))
