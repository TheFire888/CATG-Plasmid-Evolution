#/bin/bash

#SBATCH --job-name=DMND-benchmark
#SBATCH --ntasks=16
#SBATCH --time=32:00:00
#SBATCH --output=DMNDbench_job.out
#SBATCH --error=DMNDbench_job.err

SCRATCH="/scratch/local"

export PATH="/home/lleal/.pixi/bin:$PATH"


echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

cd "$SLURM_SUBMIT_DIR/.."

bash script.sh
