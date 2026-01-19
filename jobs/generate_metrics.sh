#!/bin/bash
#SBATCH --job-name=gen_metrics
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=86GB
#SBATCH --cpus-per-task=8
#SBATCH --time=100:00:00
#SBATCH --output=out/gen_metrics%j.out
#SBATCH --error=err/gen_metrics%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
SCRIPTSDIR="scripts/"

pixi run python "${SCRIPTSDIR}/generate_metrics.py" "${WORKDIR}"
