#!/bin/bash
#SBATCH --job-name=protein_clu_rbh
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=18GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=out/protein_clu%j.out
#SBATCH --error=err/protein_clu%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="test/6790.17-12-2025_10:51:03"

awk -v OFS='\t' '{print $1, $2, $4}' "${WORKDIR}/rbh_hits.tsv" > "${WORKDIR}/rbh_hits_filtered.tsv"

seqkit fx2tab -ni "${WORKDIR}/proteins.faa" > "${WORKDIR}/proteins_list.txt"

pixi run diamond greedy-vertex-cover \
    --threads 16 \
    --db "${WORKDIR}/proteins_list.txt" \
    --out "${WORKDIR}/diamond_protein_clustering_rbh" \
    --header "simple" \
    --edge-format "triplet" \
    --edges "${WORKDIR}/rbh_hits_filtered.tsv"

