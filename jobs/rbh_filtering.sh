#!/bin/bash
#SBATCH --job-name=rbh_filter
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=100GB
#SBATCH --cpus-per-task=16
#SBATCH --time=100:00:00
#SBATCH --output=out/rbh_filter%j.out
#SBATCH --error=err/rbh_filter%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
SCRIPTSDIR="scripts/"

pixi run python "${SCRIPTSDIR}/rbh_filter.py" "${WORKDIR}"
