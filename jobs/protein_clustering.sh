#!/bin/bash
#SBATCH --job-name=protein_clu
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=128GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=out/protein_clu%j.out
#SBATCH --error=err/protein_clu%j.err

log_memory() {
    local parent_pid=$1
    while kill -0 "$parent_pid" 2>/dev/null; do
        pids=$(pgrep -P "$parent_pid" | tr '\n' ',')$parent_pid

        mem_kb=$(ps -o rss= -p "$pids" 2>/dev/null | awk '{s+=$1} END {print s}')

        if [ -n "$mem_kb" ]; then
            mb=$(awk "BEGIN {printf \"%.2f\", $mem_kb/1024}")
            echo "[$(date +%T)] Total: $mb MB"
        fi
        sleep 30
    done
}

log_memory $$ &

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"

# awk -v OFS='\t' '{print $1, $2, 1}' "${WORKDIR}/rbh_hits.tsv" > "${WORKDIR}/proteins_edges.tsv"
# 
# echo "proteins_edges.tsv done!"
# 
# awk '{ if (!seen[$1]++) print $1; if (!seen[$2]++) print $2 }' "${WORKDIR}/rbh_hits.tsv" > "${WORKDIR}/proteins_list.txt"
# 
# echo "proteins_list.txt done!"

pixi run diamond greedy-vertex-cover \
    --verbose \
    --connected-component-depth 0 \
    --threads 16 \
    --db "${WORKDIR}/proteins_list.txt" \
    --out "${WORKDIR}/protein_clusters.tsv" \
    --memory-limit 50G \
    --edge-format "triplet" \
    --edges "${WORKDIR}/proteins_edges.tsv"

