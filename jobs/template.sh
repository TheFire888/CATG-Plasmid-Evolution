#!/bin/bash

# Esse nome vai aparecer na execução do squeue
#SBATCH --job-name=<job-name>

# Esse é o número de processos
#SBATCH --ntasks=1

# Essa é a memória que seu processo pode usar
#SBATCH --mem=32GB

# Esse é o número de cpus
#SBATCH --cpus-per-task=16

# Essa é a estimativa de tempo. NOTE que seu processo será encerrado após esse tempo limite
#SBATCH --time=32:00:00

# Esses são os arquivos de saída do StdOut e do StdErr, respectivamente
#SBATCH --output=<file>.out
#SBATCH --error=<file>.err

SCRATCH="/scratch/local"

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

cd "$SLURM_SUBMIT_DIR/.."

bash script.sh
