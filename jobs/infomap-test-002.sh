#!/bin/bash
#SBATCH --job-name=infomap-test
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --time=5:00:00
#SBATCH --output=infomap-test-002.out
#SBATCH --error=infomap-test-002.err

export SCRATCH="/scratch/local"

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

cd "$SLURM_SUBMIT_DIR/.."

pixi run infomap "test/biotmp-qcMTC/Graph.net" "test/infomap-test" \
    --two-level --ftree --clu --markov-time 5
