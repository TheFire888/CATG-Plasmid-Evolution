#!/bin/bash

# run:
# $ ./proteomic_analyze.sh N f_in

SAMPLE_SIZE=$1
INPUT_FILE=$2
WORKDIR=$(mktemp -d "../test/biotmp-XXXXX")

echo "Iniciando trabalho em ${WORKDIR}"

#cleanup() {
#    echo "Limpando arquivos temporários em ${WORKDIR}"
#    rm -rf "${WORKDIR}"
#}
# trap cleanup EXIT

pixi run seqkit sample -p ${SAMPLE_SIZE} \
    ${INPUT_FILE} > "${WORKDIR}/plasmid_sample.fna"

pixi run python ../src/proteomic/protein_predictor.py \
    "${WORKDIR}/plasmid_sample.fna" \
    "${WORKDIR}/proteins.faa" \
    "${WORKDIR}/gene_count.tsv"

pixi run diamond makedb \
    --in "${WORKDIR}/proteins.faa" \
    -d "${WORKDIR}/DMND_DB"

pixi run diamond blastp \
    -q "${WORKDIR}/proteins.faa" \
    -d "${WORKDIR}/DMND_DB" \
    -o "${WORKDIR}/DMND_BlastP.tsv" \
    --very-sensitive \
    --outfmt 6 qseqid sseqid pident bitscore
    --max-target-seqs  \
    --query-cover 75 \
    --subject-cover 75

pixi run python ../src/proteomic/tsv_to_pajek.py \
    "${WORKDIR}/DMND_BlastP.tsv" \
    "${WORKDIR}/NetworkPajek.net"

pixi run python ../src/proteomic/cluster.py \
    "${WORKDIR}/NetworkPajek.net" \
    "${WORKDIR}/HierarchicalClustering.newick"

echo "Análise finalizada, salvo em '${OUTPUT_FILE}'"
