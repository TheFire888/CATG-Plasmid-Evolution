#!/bin/bash
#SBATCH --job-name=infomap-test
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --time=8:00:00
#SBATCH --output=infomap-test-001.out
#SBATCH --error=infomap-test-001.err

export SCRATCH="/scratch/local"

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

cd "$SLURM_SUBMIT_DIR/.."

pixi run python tsv_to_graph.py pajek "test/biotmp-qcMTC/filtered_DMBD_BlastP.tsv" "test/biotmp-qcMTC/Graph.net"

pixi run infomap "test/biotmp-qcMTC/Graph.net" "test/biotmp-qcMTC" --two-level --ftree --clu
