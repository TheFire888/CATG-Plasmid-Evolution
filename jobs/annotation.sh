#!/bin/bash

#SBATCH --job-name=annotation
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=100GB
#SBATCH --cpus-per-task=32
#SBATCH --time=64:00:00
#SBATCH --output=out/annotation%j.out
#SBATCH --error=err/annotation%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
DATADIR="/home/lleal/programs/plasmidEvo/data/database"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

local-cd-search annotate "${WORKDIR}/proteins.faa" "${WORKDIR}/annotations.tsv" "${DATADIR}"
