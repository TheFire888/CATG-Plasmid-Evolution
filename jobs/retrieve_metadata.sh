#!/bin/bash
#SBATCH --job-name=retrieve_metadata
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=1
#SBATCH --time=100:00:00
#SBATCH --output=out/retrieve_metadata%j.out
#SBATCH --error=err/retrieve_metadata%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

bash scripts/retrieve_metadata.sh
