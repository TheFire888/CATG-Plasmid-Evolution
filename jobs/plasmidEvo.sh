#!/bin/bash
#SBATCH --job-name=plasmidEvo
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --time=32:00:00
#SBATCH --output=out/plasmidEvo%j.out
#SBATCH --error=err/plasmidEvo%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="test/${SLURM_JOB_ID}.$(date +'$d-$m-$Y_%T')"
mkdir ${WORKDIR}
SAMPLE_PATH="${WORKDIR}/sample.fna" 

pixi run seqkit sample -p 0.2 "data/genbank_plasmid_seqs.fna" > ${SAMPLE_PATH}
pixi run plasmid-evo ${WORKDIR} ${SAMPLE_PATH}


