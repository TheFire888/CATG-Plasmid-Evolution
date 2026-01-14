#!/bin/bash
#SBATCH --job-name=alignment
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=100GB
#SBATCH --cpus-per-task=32
#SBATCH --time=32:00:00
#SBATCH --output=out/alignment%j.out
#SBATCH --error=err/alignment%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
SCRIPTSDIR="scripts/"

pixi run python "${SCRIPTSDIR}/alignment.py" "${WORKDIR}" -t 32
