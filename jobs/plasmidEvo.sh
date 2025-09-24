#!/bin/bash
#SBATCH --job-name=plasmidEvo
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=out/plasmidEvo%j.out
#SBATCH --error=err/plasmidEvo%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"
pixi reinstall
pixi run build

WORKDIR="test/${SLURM_JOB_ID}.$(date +'%d-%m-%Y_%T')"
mkdir ${WORKDIR}
SAMPLE_PATH="${WORKDIR}/sample.fna" 

pixi run seqkit sample -p 0.1 "data/genbank_plasmid_seqs.fna" > ${SAMPLE_PATH}
pixi run plasmid-evo ${SAMPLE_PATH} ${WORKDIR}


