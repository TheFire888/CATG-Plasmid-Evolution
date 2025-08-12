from collections import defaultdict
import sys
import click

def find_RBH(file_in, file_out):
    best_hits = defaultdict(dict)
    with open(file_in, 'r') as f_in:
        for line in f_in:
            qseq_id, sseq_id = line.split()[:2]
            qseq_name, sseq_name = qseq_id.rsplit("_", 1)[0], sseq_id.rsplit("_", 1)[0]
            if qseq_name != sseq_name:
                best_hits[qseq_id][sseq_name] = sseq_id
    with open(file_in, 'r') as f_in, open(file_out, 'w') as f_out:
        for line in f_in:
            qseq_id, sseq_id = line.split()[:2]
            qseq_name, sseq_name = qseq_id.rsplit("_", 1)[0], sseq_id.rsplit("_", 1)[0]
            if (qseq_name in best_hits[sseq_id]) and (best_hits[sseq_id][qseq_name] == qseq_id):
                f_out.write(line)

if __name__ == "__main__":
    f_in = sys.argv[1]
    f_out = sys.argv[2]
    find_RBH(f_in, f_out)
