#!/bin/bash

#SBATCH --job-name=DMND-benchmark
#SBATCH --ntasks=8
#SBATCH --time=16:00:00 

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') #####################\n"

cd "$SLURM_SUBMIT_DIR/.."

bash "scripts/DMND_Benchmark.sh"
