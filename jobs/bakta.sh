#!/bin/bash

#SBATCH --job-name=bakta
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=100GB
#SBATCH --cpus-per-task=48
#SBATCH --time=64:00:00
#SBATCH --output=out/bakta%j.out
#SBATCH --error=err/bakta%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
BAKTA_DB=""

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

pixi run bakta_proteins --db ${BAKTA_DB} --prefix bakta --output ${WORKDIR} --threads 48 "${WORKDIR}/proteins.faa"
