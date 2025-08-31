import click
from infomap import Infomap


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def cluster_data(input_file, output_file):
    im = Infomap(num_trials=10)
    im.read_file(input_file)
    im.run()

    with open(output_file + ".label", 'w', encoding="utf-8") as f:
        for node in im.tree:
            if node.is_leaf:
                node_name = im.get_name(node.node_id)
                f.write(f"{node_name},{node.node_id}\n")

    im.write_newick(output_file)


if __name__ == "__main__":
    cluster_data()
