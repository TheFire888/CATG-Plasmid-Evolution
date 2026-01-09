#!/bin/bash
#SBATCH --job-name=predictor
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=16
#SBATCH --time=4:00:00
#SBATCH --output=out/predictor%j.out
#SBATCH --error=err/predictor%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/scratch/local/lleal/plasmid_evo"
SCRIPTSDIR="scripts/"
SAMPLE_PATH="data/genbank_plasmid_seqs.fna" 
rm -rf "${WORKDIR}/*"
mkdir -p ${WORKDIR}

pixi run python "${SCRIPTSDIR}/predictor.py" "${SAMPLE_PATH}" "${WORKDIR}" -t 16
