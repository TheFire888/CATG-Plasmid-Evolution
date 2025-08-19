#!/bin/bash

LOGFILE="bench_log.txt"
PLASMID_COUNT=5583

for i in $(seq 1 10); do
    X=$(awk "BEGIN {print $i * 0.1}")
    MAX_TARGET=$(awk "BEGIN {print int($PLASMID_COUNT * $X)}")

    echo "Executando com X = $X (max-target-seqs = $MAX_TARGET)..."

    START_TIME=$(date +%s.%N)
    pixi run diamond blastp \ 
        -q "data/gene_sample.faa" \ 
        -d "data/DMND_DB" \ 
        --multiprocessing \ 
        --mp-init \ 
        --tmpdir "$TMPDIR" \ 
        --parallel-tmpdir "$PTMPDIR"

    pixi run diamond blastp \ 
        -q "data/gene_sample.faa" \ 
        -d "data/DMND_DB" \ 
        -o "test/DMND_BlastP_$i.tsv" \ 
        --ultra-sensitive \ 
        --outfmt 6 qseqid sseqid pident qcovhsp scovhsp bitscore \ 
        --max-target-seqs "$MAX_TARGET" \ 
        --multiprocessing \ 
        --tmpdir "$TMPDIR" \ 
        --parallel-tmpdir "$PTMPDIR"
    END_TIME=$(date +%s.%N)

    DURATION=$(awk "BEGIN {print $END_TIME - $START_TIME}")

    echo "$X | $DURATION" >> "$LOGFILE"
done

echo "Benchmark concluído. Resultados salvos em $LOGFILE"

