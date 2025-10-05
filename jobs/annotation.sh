#!/bin/bash

#SBATCH --job-name=annotation
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=60GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=../out/annotation%j.out
#SBATCH --error=../err/annotation%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

cd "$SLURM_SUBMIT_DIR/.."

interproscan \
    --input "./test/4267.24-09-2025_14\:09\:34/proteins.faa" \
    --applications Pfam,NCBIfam,CDD,HAMAP \
    --iprlookup --goterms --pathways \
    --data-dir interproscan-5.75-106.0 \
    --cpu 16 \
    --output-dir "./lab/4267/annotations" \
