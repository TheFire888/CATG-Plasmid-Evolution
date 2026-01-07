#!/bin/bash

#SBATCH --job-name=annotation
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=out/annotation%j.out
#SBATCH --error=err/annotation%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/test/7149.07-01-2026_11:53:50"
cd $WORKDIR

DATADIR="/home/lleal/programs/plasmidEvo/ips_data"

pixi run nextflow run ebi-pf-team/interproscan6 \
  -r 6.0.0 \
  -profile apptainer \
  --datadir ${DATADIR} \
  --input ${WORKDIR}/proteins.faa \
   --applications Pfam,NCBIFAM,PANTHER,SUPERFAMILY
