#!/bin/bash

#SBATCH --job-name=annotation
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=100GB
#SBATCH --cpus-per-task=48
#SBATCH --time=64:00:00
#SBATCH --output=out/annotation%j.out
#SBATCH --error=err/annotation%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
DATADIR="/home/lleal/programs/plasmidEvo/data/interproscan-5.75-106.0"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

apptainer --silent exec         -B "data/interproscan-5.75-106.0/data:/opt/interproscan/data"         "$HOME/images/interproscan.sif"         /opt/interproscan/interproscan.sh --cpu 4 --applications Pfam,CDD,HAMAP --input rslts/sample.faa --output-dir rslts/test

apptainer --silent exec \
    -B "${DATADIR}/data:/opt/interproscan/data" \
    "$HOME/images/interproscan.sif" \
    "/opt/interproscan/interproscan.sh" \
    --input "${WORKDIR}/proteins.faa" \
    --applications NCBIfam \
    --disable-precalc \
    --verbose \
    --cpu 48 \
    --output-dir "${WORKDIR}/annotations" \
