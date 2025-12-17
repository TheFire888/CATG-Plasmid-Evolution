#!/bin/bash
#SBATCH --job-name=betweenness
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=out/betweenness%j.out
#SBATCH --error=err/betweenness%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

pixi run python "scripts/calculate_betweenness.py"
