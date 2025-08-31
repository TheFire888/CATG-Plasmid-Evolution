#!/bin/bash
#SBATCH --job-name=PlasmidEvo
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --time=32:00:00
#SBATCH --output=PlasmidEvo.out
#SBATCH --error=PlasmidEvo.err

SCRATCH="/scratch/local"

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

cd "$SLURM_SUBMIT_DIR/.."

bash ../scripts/proteomic_analyse.sh 0.1 "data/genbank_plasmid_seqs.fna"
