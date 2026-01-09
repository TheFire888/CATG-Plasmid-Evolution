#!/bin/bash
#SBATCH --job-name=test_infomap
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=16
#SBATCH --time=4:00:00
#SBATCH --output=out/test_infomap%j.out
#SBATCH --error=err/test_infomap%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

pixi run python "scripts/test_infomap.py"

