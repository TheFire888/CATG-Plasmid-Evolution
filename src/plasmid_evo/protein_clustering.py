"""
Este módulo encapsula a lógica para realizar o agrupamento de proteínas
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

class DiamondClustering:
    """
    Executa um agrupamento all-versus-all com DIAMOND.
    """

    def __init__(self, params: dict = {}):
        """
        Inicializa o agrupador com parâmetros configuráveis.

        Args:
            params (dict, optional): Dicionário de configuração.
        """
        if not shutil.which("diamond"):
            raise FileNotFoundError("O executável 'diamond' não foi "
                                    "encontrado no PATH.")

        self.threads = params.get("threads", 16)

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

    def vertex_cover(self, output_dir: Path) -> None:
        """
        Orquestra o processo de agrupamento completo.

        Args:
            output_dir (Path): O objeto Path do diretório de saída.
        """
        logging.info("Iniciando agrupamento com DIAMOND")

        hits_tsv = output_dir / "rbh_hits.tsv"
        edges_tsv = output_dir / "proteins_edges.tsv"
        prot_list = output_dir / "proteins_list_rbh.txt"
        final_out = output_dir / "diamond_protein_clustering_rbh.tsv"

        logging.info(f"Criando banco de proteínas e filtrando...")
        
        seen_proteins = set()
        with open(hits_tsv, "r") as f_in, \
             open(edges_tsv, "w") as f_out, \
             open(prot_list, "w") as f_list:

            for line in f_in:
                parts = line.strip().split("\t")
                if len(parts) < 2: continue

                p1, p2 = parts[0], parts[1]
                f_out.write(f"{p1}\t{p2}\t1\n")

                for p in (p1, p2):
                    if p not in seen_proteins:
                        f_list.write(f"{p}\n")
                        seen_proteins.add(p)

        cmd = [
            "diamond", "greedy-vertex-cover",
            "--threads", str(self.threads),
            "--db", str(prot_list),
            "--out", str(final_out),
            "--edges", str(edges_tsv),
            "--edge-format", "triplet",
            "--header", "simple",
            "--connected-component-depth", "0",
            "--log", "--verbose"
        ]
        
        logging.info("Iniciando greedy-vertex-cover...")
        self._run_command(cmd)

        logging.info("Agrupamento de proteínas concluído.")


if __name__ == "__main__":
    dc = DiamondClustering()
    dc.vertex_cover(Path("test/"))
