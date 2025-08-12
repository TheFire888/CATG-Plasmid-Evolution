from collections import defaultdict
import sys
import click

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
@click.option("--min-cov", default=20.0)
def find_RBH(input_file, output_file):
    best_hits = defaultdict(dict)
    with open(input_file, 'r') as f_in:
        for line in f_in:
            qseq_id, sseq_id = line.split()[:2]
            qseq_name, sseq_name = qseq_id.rsplit("_", 1)[0], sseq_id.rsplit("_", 1)[0]
            if qseq_name != sseq_name:
                best_hits[qseq_id][sseq_name] = sseq_id
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            qseq_id, sseq_id = line.split()[:2]
            qseq_name, sseq_name = qseq_id.rsplit("_", 1)[0], sseq_id.rsplit("_", 1)[0]
            if (qseq_name in best_hits[sseq_id]) and (best_hits[sseq_id][qseq_name] == qseq_id):
                f_out.write(line)

if __name__ == "__main__":
    find_RBH()
