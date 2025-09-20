#!/bin/bash
#SBATCH --job-name=plasmidEvo
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --time=32:00:00
#SBATCH --output="out/plasmidEvo_$(date +'%d%m%Y_%T').out"
#SBATCH --error="err/plasmidEvo_$(date +'%d%m%Y_%T').err"

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR=$(mktemp -d "test/$(date +'$d-$m-$Y_%T')")
SAMPLE_PATH="${WORKDIR}/sample.fna" 

pixi run seqkit sample -p 0.2 "data/genbank_plasmid_seqs.fna" > ${SAMPLE_PATH}
pixi run plasmid-evo ${WORKDIR} ${SAMPLE_PATH}


