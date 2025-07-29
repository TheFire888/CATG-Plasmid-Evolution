from collections import defaultdict

def count(f_in, f_out):
    max_genes = defaultdict(int)
    with open(f_in, 'r') as f_in:
        for line in f_in:
            if line.startswith(">"):
                l = line.rsplit("_", 1)
                plasmid = l[0]
                gene_id = int(l[1])
                if max_genes[plasmid] < gene_id:
                    max_genes[plasmid] = gene_id
    with open(f_out, 'w') as f_out:
        for plasmid, max_id in max_genes.items():
        f_out.write(f"{plasmid} \t {max_id} \n")

if __name__ == "__main__":
    f_in = sys.argv[1]
    f_out = sys.argv[2]
    count(f_in, f_out)


