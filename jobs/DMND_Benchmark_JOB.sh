#!/bin/bash

#SBATCH --job-name=DMND-benchmark
#SBATCH --ntasks=16
#SBATCH --time=32:00:00 

SCRATCH="/scratch/local"

export PATH="/home/lleal/.pixi/bin:$PATH"
export TMPDIR="$SLURM_SUBMIT_DIR/../test/dmndtmp"
export PTMPDIR="$SCRATCH/$SLURM_JOB_ID"

mkdir -p "$TMPDIR"
mkdir -p "$PTMPDIR"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

cd "$SLURM_SUBMIT_DIR/.."

bash "scripts/DMND_Benchmark.sh"
