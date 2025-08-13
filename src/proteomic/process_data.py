from itertools import combinations
from collections import defaultdict
from multiprocessing.pool import ThreadPool
from functools import partial
import sys

def calculate_wgrr(gene_counts, pair):
    (p_u, p_v), total_identity = pair
    count_u, count_v = gene_counts.get(p_u), gene_counts.get(p_v)
    min_genes = min(count_u, count_v)
    wgrr = total_identity / min_genes

    return [p_u, p_v, wgrr]

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("rbh_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("count_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path())
def process_wgrr(rbh_file, count_file, output_file):
    with open(count_file, 'r') as count_f:
        gene_counts = {line.split()[0]: int(line.split()[1]) for line in count_f}

    sum_hits = defaultdict(float)
    with open(rbh_file, 'r') as rbh_f:
        for line in rbh_f:
            parts = line.split()[:3]
            qseq_gene_id, sseq_gene_id, identity = parts[0], parts[1], float(parts[2])
            p_u, p_v = qseq_gene_id.rsplit("_", 1)[0], sseq_gene_id.rsplit("_", 1)[0]
            pair_key = tuple(sorted((p_u, p_v)))
            sum_hits[pair_key] += identity

    calculate_wgrr_counted = partial(calculate_wgrr, gene_counts)
    with open(output_file, 'w') as f_out, ThreadPool() as pool:
        results = pool.imap(calculate_wgrr_counted, sum_hits.items())
        for row in results:
            f_out.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")

if __name__ == "__main__":
    process_wgrr()
