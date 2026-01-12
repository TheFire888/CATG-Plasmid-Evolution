#!/bin/bash
#SBATCH --job-name=protein_clu
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=18GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=out/protein_clu%j.out
#SBATCH --error=err/protein_clu%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"

awk -v OFS='\t' '{print $1, $2, 1}' "${WORKDIR}/rbh_hits.tsv" > "${WORKDIR}/proteins_edges.tsv"

awk '{ if (!seen[$1]++) print $1; if (!seen[$2]++) print $2 }' "${WORKDIR}/diamond_results.tsv" > "${WORKDIR}/proteins_list.txt"

pixi run diamond greedy-vertex-cover \
    --verbose \
    --connected-component-depth 0 \
    --threads 16 \
    --db "${WORKDIR}/proteins_list.txt" \
    --out "${WORKDIR}/diamond_protein_clustering.tsv" \
    --header "simple" \
    --edge-format "triplet" \
    --edges "${WORKDIR}/proteins_edges.tsv"

