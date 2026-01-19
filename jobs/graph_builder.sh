#!/bin/bash
#SBATCH --job-name=graph_builder
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=4
#SBATCH --time=100:00:00
#SBATCH --output=out/graph_builder%j.out
#SBATCH --error=err/graph_builder%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
SCRIPTSDIR="scripts/"

pixi run python "${SCRIPTSDIR}/graph_builder.py" "${WORKDIR}"
