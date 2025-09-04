#!/bin/bash

# run:
# $ ./proteomic_analyze.sh N f_in

set -e

SAMPLE_SIZE=$1
INPUT_FILE=$2
WORKDIR=$(mktemp -d "test/biotmp-XXXXX")

echo "Iniciando trabalho em ${WORKDIR}" >&2

NUM_SEQS=$(pixi run seqkit sample -p ${SAMPLE_SIZE} "${INPUT_FILE}" 2>&1 > "${WORKDIR}/plasmid_sample.fna" | grep -oP '\b[0-9]+\b')

MAX_TARGET_SEQS=$(echo "${NUM_SEQS}" | awk '{print int($1 * 0.5)}')

echo "Realizando predição de genes..." >&2
pixi run python src/proteomic/protein_predictor.py \
    "${WORKDIR}/plasmid_sample.fna" \
    "${WORKDIR}/proteins.faa" \
    "${WORKDIR}/gene_count.tsv"

echo "Realizando busca all-versus-all..." >&2
pixi run diamond makedb \
    --in "${WORKDIR}/proteins.faa" \
    -d "${WORKDIR}/DMND_DB"

pixi run diamond blastp \
    -q "${WORKDIR}/proteins.faa" \
    -d "${WORKDIR}/DMND_DB" \
    -o "${WORKDIR}/DMND_BlastP.tsv" \
    --very-sensitive \
    --outfmt 6 qseqid sseqid pident bitscore \
    --max-target-seqs $MAX_TARGET_SEQS \
    --query-cover 75 \
    --subject-cover 75 \
    --min-score 30

echo "Filtrando Reciprocal Best Hits..." >&2
pixi run python src/proteomic/find_rbh.py \
    "${WORKDIR}/DMND_BlastP.tsv" \
    "${WORKDIR}/filtered_DMBD_BlastP.tsv" \

echo "Gerando grafo..." >&2
pixi run python src/proteomic/tsv_to_graph.py pajek\
    "${WORKDIR}/filtered_DMBD_BlastP.tsv" \
    "${WORKDIR}/Graph.net"

echo "Agrupando comunidades..." >&2
pixi run infomap \
    "${WORKDIR}/Graph.net" \
    "${WORKDIR}" \
    --two-level \
    --ftree \
    --clu

echo "Análise finalizada, salvo em '${WORKDIR}'" >&2
