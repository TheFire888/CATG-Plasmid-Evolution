#!/bin/bash

SAMPLE_SIZE=$1
INPUT_FILE=$2
OUTPUT_FILE=$3
WORKDIR=$(mktemp -d biotmpXXXXX)

cleanup() {
    echo "Limpando arquivos temporários em ${WORKDIR}"
    rm -rf "${WORKDIR}"
}
trap cleanup EXIT

# Gera uma amostra aleatória de N sequências presentes no arquivo FASTA. Reescrito para grandes bancos de dados.
seqkit sample -p 0.1 ${INPUT_FILE} | seqkit head -n ${SAMPLE_SIZE} > "${WORKDIR}/plasmid_sample.fna"

# Encontra as CDS na amostra.
pyrodigal -i "${WORKDIR}/plasmid_sample.fna" -a "${WORKDIR}/proteins.faa" -p meta -j0

# Faz a contagem de genes por plasmídeo, útil para determinar wGRR
awk -F'_' '/^>/ {sub(">", "", $1); print $1 }' "${WORKDIR}/proteins.faa" | sort | uniq -c | awk '{print $2 "\t" $1}' > "${WORKDIR}/gene_count.tsv"

# Cria um arquivo binário para trabalhar com o DIAMOND
diamond makedb --in "${WORKDIR}/proteins.faa" -d "${WORKDIR}/DMND_DB" --quiet

# Cria um arquivo .tsv correspondente ao formato gerado pelo BLAST
diamond blastp -q "${WORKDIR}/proteins.faa" -d "${WORKDIR}/DMND_DB" -o "${WORKDIR}/DMND_BlastP.tsv" --very-sensitive --quiet

# Encontra os best hits que não são auto-hits e cria uma chave canônica para cada tupla
awk -F'\t' '$1 != $2' "${WORKDIR}/DMND_BlastP.tsv" | sort -k1,1 -k12,12gr | awk -F'\t' '!seen[$1]++' | awk -F'\t' '{
    g1=$1; g2=$2; score=$12;
    if (g1 < g2) { print g1 "\t" g2 "\t" score; }
    else         { print g2 "\t" g1 "\t" score; }
}' | sort -k1,1 -k2,2 > "${WORKDIR}/best_hits.tsv"

# Cria um arquivo .tsv com os Reciprocal Best Hits, Average Aminoacid Identity e wGRR
# python RBH.py "${WORKDIR}/DMND_BlastP.tsv" "${OUTPUT_FILE}"

echo "Análise finalizada, salvo em '${OUTPUT_FILE}'"
