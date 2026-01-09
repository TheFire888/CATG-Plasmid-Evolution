#!/bin/bash
#SBATCH --job-name=alignment
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=out/alignment%j.out
#SBATCH --error=err/alignment%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/scratch/local/lleal/plasmid_evo"
SCRIPTSDIR="scripts/"
mkdir -p ${WORKDIR}

pixi run diamond makedb \
    --in "${WORKDIR}/proteins.faa" \
    -d "${WORKDIR}/DMND_DB"

pixi run diamond blastp \
    -q "${WORKDIR}/proteins.faa" \
    -d "${WORKDIR}/DMND_DB" \
    -o "${WORKDIR}/diamond_results.tsv" \
    --sensitive \
    --outfmt 6 qseqid sseqid bitscore \
    --max-target-seqs 50000 \
    --query-cover 75 \
    --subject-cover 75 \
    --min-score 30 \
    --threads 16
