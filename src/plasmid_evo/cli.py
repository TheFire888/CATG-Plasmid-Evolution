"""
Este módulo é a interface de linha de comando de uso do plasmidEvo
"""
from pathlib import Path
import tomllib
import click

from plasmid_evo.pipeline import PlasmidEvoPipeline


def _load_config(config_path) -> dict:
    """
    Carrega um arquivo de configuração TOML e o retorna como um dicionário.
    """
    with open(config_path, 'rb', encoding="utf-8") as file:
        return tomllib.load(file)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_fasta", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_path", type=click.Path())
@click.option("-c", default=Path("./plasmid-evo.toml"),
              type=click.Path(exists=True, dir_okay=False))
def cli(input_fasta, output_path, c):
    """
    plasmidEvo: pipeline para clusterização hierárquica de plasmídeos
    """
    config = _load_config(c)
    pipeline = PlasmidEvoPipeline(config)
    pipeline.run(input_fasta, output_path)


if __name__ == "__main__":
    cli()
