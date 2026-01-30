#!/bin/bash
#SBATCH --job-name=retrieve_metadata
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=1
#SBATCH --time=100:00:00
#SBATCH --output=out/retrieve_metadata%j.out
#SBATCH --error=err/retrieve_metadata%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
DATADIR="/home/lleal/programs/plasmidEvo/data"
SCRIPTSDIR="scripts/"

seqkit fx2tab -ni "${DATADIR}/genbank_plasmid_seqs.fna" | awk '{sub(/^>/,""); print $1}' | awk -F'.' '{print $1}' > "${DATADIR}/accession_list.txt"

echo -e "accession\tdescription\tcollection_date\tcountry\tkeywords\tsequence_accession\tdataclass\tsample_accession\tdev_stage\trun_accession\tpubmed_id\tidentified_by\tcell_line\thost\ttag\tserotype\tstrain\tbio_material\tlast_updated\tgermline\torganelle\ttopology\tagricola_id\tsequence_md5\tscientific_name\tcollection_date_end\tculture_collection\ttax_id\tstudy_accession\tcultivar\tdoi\tmol_type\tstatus\taltitude\tmetagenome_source\tplasmid\tcollected_by\tsecondary_sample_accession\thost_tax_id\tisolate\ttax_lineage\tvariety\tcell_type\tecotype\thaplotype\tmating_type\ttissue_lib\tcollection_date_start\tenvironmental_sample\tfirst_public\tsub_species\tsex\tsub_strain\tbase_count\tspecimen_voucher\tassembly_accession\tpatent_number\ttax_division\tserovar\tlocation\tlab_host\ttissue_type\tindexed_date\tisolation_source\tsequence_version" > "${DATADIR}/sequence_metadata.tsv"

for f in $(awk "NR=1 {print $1}" "${DATADIR}/accession_list.txt");
    do pixi run python "${SCRIPTSDIR}/retrieve_sequence_metadata.py" $f >> "${DATADIR}/sequence_metadata.tsv"; 
done
