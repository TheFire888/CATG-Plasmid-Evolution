#!/bin/bash

#SBATCH --job-name=annotation
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=100GB
#SBATCH --cpus-per-task=48
#SBATCH --time=64:00:00
#SBATCH --output=out/annotation%j.out
#SBATCH --error=err/annotation%j.err

interproscan() {
    local output_dir=""
    local data_dir=""
    local i=1

    # If -help or --help is given, run interproscan.sh --help and exit
    if [[ "$1" == "-help" || "$1" == "--help" ]]; then
        apptainer --silent exec \
            "$HOME/images/interproscan.sif" \
            /opt/interproscan/interproscan.sh --help
        return 0
    fi

    # Show usage if no arguments given
    if [[ $# -eq 0 ]]; then
        echo "Usage:"
        echo "  interproscan --data-dir <path> [interproscan.sh arguments]"
        echo
        echo "Example:"
        echo "  interproscan --data-dir /path/to/data --output-dir /path/to/output \\"
        echo "               --applications Pfam,NCBIfam --disable-precalc \\"
        echo "               --cpu 16 --input /path/to/input.faa"
        echo
        echo "Documentation for interproscan.sh:"
        echo "  https://interproscan-docs.readthedocs.io/en/v5/HowToRun.html"
        return 1
    fi

    # Parse arguments to find output-dir and data-dir
    while [[ $i -le $# ]]; do
        if [[ "${!i}" == "--output-dir" ]] && [[ $((i+1)) -le $# ]]; then
            ((i++))
            output_dir="${!i}"
        elif [[ "${!i}" == "--data-dir" ]] && [[ $((i+1)) -le $# ]]; then
            ((i++))
            data_dir="${!i}"
        fi
        ((i++))
    done

    if [[ -z "$data_dir" ]]; then
        echo "Error: --data-dir is required" >&2
        return 1
    fi

    # Check if output directory exists and is not empty
    if [[ -d "$output_dir" ]] && [[ -n "$(ls -A "$output_dir" 2>/dev/null)" ]]; then
        echo "Error: Output directory '$output_dir' is not empty" >&2
        return 1
    fi

    # Verify data directory exists
    if [[ ! -d "$data_dir" ]]; then
        echo "Error: Data directory '$data_dir' does not exist" >&2
        return 1
    fi

    # Create output directory
    mkdir -p "$output_dir"

    # Filter out --data-dir from arguments since it's not passed to interproscan.sh
    local args=()
    i=1
    while [[ $i -le $# ]]; do
        if [[ "${!i}" == "--data-dir" ]]; then
            ((i++))  # Skip the flag
            ((i++))  # Skip the value
        else
            args+=("${!i}")
            ((i++))
        fi
    done

    # Execute interproscan with proper mounts
    apptainer --silent exec \
        -B "$data_dir/data:/opt/interproscan/data" \
        "$HOME/images/interproscan.sif" \
        /opt/interproscan/interproscan.sh \
        "${args[@]}"
}

export PATH="/home/lleal/.pixi/bin:$PATH"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
DATADIR="/home/lleal/programs/plasmidEvo/data/interproscan-5.75-106.0"

echo -e "\n## Job iniciado em $(date +'%d-%m-%Y as %T') ##\n"

interproscan \
    --input "${WORKDIR}/proteins.faa" \
    --applications Pfam,NCBIfam,CDD,HAMAP,Panther,superfamily \
    --iprlookup --goterms --pathways \
    --data-dir "${DATADIR}" \
    --verbose \
    --cpu 48 \
    --output-dir "${WORKDIR}/annotations" \
