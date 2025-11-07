#!/bin/bash
#SBATCH --job-name=graph_tool
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=16
#SBATCH --time=32:00:00
#SBATCH --output=../out/graph_tool.out
#SBATCH --error=../err/graph_tool.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

pixi run python -u src/util/graph_tool_test.py

