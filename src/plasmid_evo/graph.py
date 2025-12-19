"""
Este módulo constrói uma representação de grafo a partir dos resultados
de RBH e a exporta para formatos de análise de redes.
"""
from collections import defaultdict
from pathlib import Path
import csv
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

class GeneGraph:
    """
    Constrói e exporta um grafo de genes e contigs a partir de um
    arquivo de hits filtrados.

    O grafo contém dois tipos de nós (genes e contigs) e dois tipos de arestas:
    1. Arestas entre genes, com peso normalizado pelo autohit (self-hit).
    2. Arestas entre um contig e seus genes, com peso 1.0.
    """

    def __init__(self, params: dict = None):
        """
        Inicializa o construtor de grafos.

        Args:
            params (dict, optional): Dicionário de configuração.
                                     (Reservado para futuras extensões).
        """
        if params is None:
            params = {}
        # Futuros parâmetros podem ser adicionados aqui.

    def _get_contig_from_gene(self, gene_id: str) -> str:
        """Extrai o nome do contig a partir do ID do gene."""
        if "_" in gene_id:
            return gene_id.rsplit("_", 1)[0]
        return None

    def _collect_autohits(self, input_path: Path):
        """
        Primeira passagem: lê o arquivo para coletar os bitscores dos autohits.
        """
        autohits = defaultdict()
        logging.info("Coletando autohits para normalização de peso...")
        with open(input_path, 'r', newline='', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if row[0] == row[1]:
                    try:
                        autohits[row[0]] = float(row[2])
                    except ValueError:
                        continue

        return autohits

    def _find_nodes(self, input_path: Path):
        """
        Segunda passagem: lê o arquivo para determinar os nós do grafo
        """
        nodes = set()
        logging.info("Mapeando nós para IDs...")
        with open(input_path, 'r', newline='', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if len(row) < 2:
                    continue
                qseq_gene_id, sseq_gene_id = row[0], row[1]
                nodes.add(qseq_gene_id)
                nodes.add(sseq_gene_id)
                if '_' in qseq_gene_id:
                    nodes.add(qseq_gene_id.rsplit('_', 1)[0])

        node_to_id = {node: i+1 for i, node in enumerate(sorted(list(nodes)))}

        return node_to_id

    def _calculate_weight(self, bitscore: float, autohit: float):
        weight = bitscore / autohit
        return weight

    def _write_pajek(self, input_path: Path, output_dir: Path):
        logging.info("Escrevendo arquivo de saída...")
        output_file = output_dir / "graph.net"
        node_to_id = self._find_nodes(input_path)
        autohits = self._collect_autohits(input_path)
        with open(output_file, 'w', encoding="utf-8") as f_out:
            f_out.write(f"*Vertices {len(node_to_id)}\n")
            for node, node_id in node_to_id.items():
                f_out.write(f'{node_id} "{node}"\n')

            f_out.write("*Edges\n")
            contig_genes_edges = set()
            with open(input_path, 'r', newline='', encoding="utf-8") as f_in:
                reader = csv.reader(f_in, delimiter='\t')
                for row in reader:
                    qseq_gene_id, sseq_gene_id = row[0], row[1]
                    bitscore = float(row[2])

                    if qseq_gene_id != sseq_gene_id:
                        try:
                            weight = self._calculate_weight(bitscore,
                                                            autohits[qseq_gene_id])
                            source_id = node_to_id[qseq_gene_id]
                            target_id = node_to_id[sseq_gene_id]
                            f_out.write(f"{source_id} {target_id} {weight}\n")

                        except KeyError:
                            continue
                        except ValueError:
                            continue

                    if '_' in qseq_gene_id:
                        qseq_contig = qseq_gene_id.rsplit('_', 1)[0]
                        qedge = (qseq_contig, qseq_gene_id)
                        if qedge not in contig_genes_edges:
                            try:
                                source_id = node_to_id[qseq_contig]
                                target_id = node_to_id[qseq_gene_id]
                                f_out.write(f"{source_id} {target_id} 1.0\n")
                                contig_genes_edges.add(qedge)
                            except KeyError:
                                continue

    def _write_ncol(self, input_path: Path, output_dir: Path):
        output_file = output_dir / "graph.ncol"
        autohits = self._collect_autohits(input_path)
        contig_genes_edges = set()
        with (
                open(input_path, 'r', encoding="utf-8") as tsv_file,
                open(output_file, 'w', encoding="utf-8") as ncol_file
                ):
            reader = csv.reader(tsv_file, delimiter='\t')
            for row in reader:
                qseq_gene_id, sseq_gene_id = row[0], row[1]
                bitscore = float(row[2])
                qseq_contig = qseq_gene_id.rsplit("_", 1)[0]

                if qseq_gene_id != sseq_gene_id:
                    try:
                        weight = bitscore / autohits[qseq_gene_id]
                        ncol_file.write(f"{qseq_gene_id}\t{sseq_gene_id}\t{weight}\n")
                    except KeyError:
                        logging.info(f"Aviso: Autohit não encontrado para {qseq_gene_id}. Ignorando a aresta.")
                        continue

                qedge = (qseq_contig, qseq_gene_id)
                if qedge not in contig_genes_edges:
                    ncol_file.write(f"{qseq_contig}\t{qseq_gene_id}\t1.0\n")
                    contig_genes_edges.add(qedge)

    def generate(self, output_dir: Path,
                 file_format: str = "pajek") -> Path:
        """
        Orquestra a criação e exportação do grafo.

        Args:
            input_file (str): Caminho para o arquivo de
                              entrada com os hits (RBH).
            output_dir (Path): Diretório para salvar o arquivo de saída.
            file_format (str): O formato do arquivo de saída ('pajek' ou 'ncol').

        Returns:
            Path: O caminho para o arquivo de grafo gerado.
        """
        input_path = output_dir / "rbh_hits.tsv"

        logging.info(f"Exportando o grafo para o formato {file_format}...")
        match file_format:
            case "pajek":
                output_path = output_dir / "graph.net"
                self._write_pajek(input_path, output_dir)
            case "ncol":
                output_path = output_dir / "graph.ncol"
                self._write_ncol(input_path, output_dir)
            case _:
                raise ValueError(f"Formato de saída desconhecido: "
                                 f"'{file_format}'. "
                                 "Use 'pajek' ou 'ncol'.")

        logging.info(f"Arquivo salvo em: {output_path}")
        return output_path


if __name__ == "__main__":
    gg = GeneGraph()
    gg.generate(Path("test/"))
