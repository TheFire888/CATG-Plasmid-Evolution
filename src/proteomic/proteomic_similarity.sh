#!/bin/bash

# run:
# $ ./proteomic_similarity.sh N f_in f_out

SAMPLE_SIZE=$1
INPUT_FILE=$2
OUTPUT_FILE=$3
WORKDIR=$(mktemp -d biotmp-XXXXX)

echo "Iniciando trabalho em ${WORKDIR}"

cleanup() {
    echo "Limpando arquivos temporários em ${WORKDIR}"
    rm -rf "${WORKDIR}"
}
trap cleanup EXIT

# Gera uma amostra aleatória de N sequências presentes no arquivo FASTA. Reescrito para grandes bancos de dados.
seqkit sample -p 0.1 ${INPUT_FILE} | seqkit head -n ${SAMPLE_SIZE} > "${WORKDIR}/plasmid_sample.fna"

# Encontra as CDS na amostra.
# Faz a contagem de genes por plasmídeo, útil para determinar wGRR
python protein_predictor.py "${WORKDIR}/plasmid_sample.fna" "${WORKDIR}/proteins.faa" "${WORKDIR}/gene_count.tsv"

# Cria um arquivo binário para trabalhar com o DIAMOND
diamond makedb --in "${WORKDIR}/proteins.faa" -d "${WORKDIR}/DMND_DB" --quiet

# Cria um arquivo .tsv correspondente ao formato gerado pelo BLAST
diamond blastp -q "${WORKDIR}/proteins.faa" -d "${WORKDIR}/DMND_DB" -o "${WORKDIR}/DMND_BlastP.tsv" --ultra-sensitive --quiet --outfmt 6 qseqid sseqid pident qcovhsp scovhsp

# Filtra os Reciprocal Best Hits
python find_RBH.py "${WORKDIR}/DMND_BlastP.tsv" "${WORKDIR}/RBH.tsv"

# Cria um arquivo .tsv com os Reciprocal Best Hits, Average Aminoacid Identity e wGRR
python process_data.py "${WORKDIR}/RBH.tsv" "${WORKDIR}/gene_count.tsv" "${OUTPUT_FILE}"

echo "Análise finalizada, salvo em '${OUTPUT_FILE}'"
