"""
Script para processar e filtrar arquivos no formato .ftree.
"""

import re
import click


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_path", type=click.Path())
def process_ftree(input_path, output_path):
    """
    Lê um arquivo .ftree e escreve os contigs encontrados diretamente
    em um arquivo de saída.
    """
    with (
            open(input_path, 'r', encoding="utf-8") as infile,
            open(output_path, 'w', encoding="utf-8") as outfile
            ):

        outfile.write("# Module_ID, Contig\n")
        line_start_pattern = re.compile(r'^[0-9]+:')
        contig_filter_pattern = re.compile(r'_\d+$')
        contigs = 0

        for line in infile:
            if not line_start_pattern.match(line):
                continue

            parts = line.split()
            if len(parts) >= 3:
                module_id = parts[0].split(':')[0]
                name = parts[2].strip('"')

                if not contig_filter_pattern.search(name):
                    outfile.write(f"{module_id}\t{name}\n")
                    contigs += 1

        return contigs


if __name__ == "__main__":
    print(process_ftree())
