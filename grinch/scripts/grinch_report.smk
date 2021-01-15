import pandas as pd
from Bio import SeqIO
import figure_generation as fig_gen
import grinchfunks as gfunk

output_prefix = config["output_prefix"]

rule all:
    input:
        config["outdir"] + "/2/lineages.metadata.csv",
        os.path.join(config["outdir"],"report", f"{output_prefix}_B.1.1.7.html")

rule gisaid_process_json:
    input:
        json = config["json"],
        omit = config["omitted"]
    output:
        fasta = config["outdir"] + "/0/gisaid.fasta",
        metadata = config["outdir"] + "/0/gisaid.csv"
    log:
        config["outdir"] + "/logs/0_gisaid_process_json.log"
    shell:
        """
        datafunk process_gisaid_data \
          --input-json {input.json} \
          --input-metadata False \
          --exclude-file {input.omit} \
          --output-fasta {output.fasta} \
          --output-metadata {output.metadata} \
          --exclude-undated &> {log}
        """

rule gisaid_unify_headers:
    input:
        fasta = rules.gisaid_process_json.output.fasta,
        metadata = rules.gisaid_process_json.output.metadata,
    output:
        fasta = config["outdir"] + "/0/gisaid.UH.fasta",
        metadata = config["outdir"] + "/0/gisaid.UH.csv",
    log:
        config["outdir"] + "/logs/0_gisaid_unify_headers.log"
    run:

        fasta_in = SeqIO.index(str(input.fasta), "fasta")
        df = pd.read_csv(input.metadata, sep=',')

        sequence_name = []

        with open(str(output.fasta), 'w') as fasta_out:
            for i,row in df.iterrows():
                edin_header = row["edin_header"]
                new_header = edin_header.split("|")[0]
                sequence_name.append(new_header)

                try:
                    record = fasta_in[edin_header]
                    fasta_out.write(">" + new_header + "\n")
                    fasta_out.write(str(record.seq) + "\n")
                except:
                    continue

        df['sequence_name'] = sequence_name
        df.to_csv(output.metadata, index=False, sep = ",")

rule gisaid_remove_duplicates:
    input:
        fasta = rules.gisaid_unify_headers.output.fasta,
        metadata = rules.gisaid_unify_headers.output.metadata
    output:
        fasta = config["outdir"] + "/0/gisaid.UH.RD.fasta",
        metadata = config["outdir"] + "/0/gisaid.UH.RD.csv"
    log:
        config["outdir"] + "/logs/0_gisaid_remove_duplicates.log"
    shell:
        """
        fastafunk subsample \
          --in-fasta {input.fasta} \
          --in-metadata {input.metadata} \
          --group-column sequence_name \
          --index-column sequence_name \
          --out-fasta {output.fasta} \
          --sample-size 1 \
          --out-metadata {output.metadata} \
          --select-by-min-column edin_epi_day &> {log}
        """

rule make_chunks:
    input:
        fasta = rules.gisaid_unify_headers.output.fasta
    output:
        txt = config["outdir"] + "/1/placeholder.txt"
    shell:
        "make_chunks.py {input.fasta} {config[outdir]}/1/ && touch {output.txt}"

rule parallel_pangolin:
    input:
        snakefile = os.path.join(workflow.current_basedir,"parallel_pangolin.smk"),
        fasta = rules.make_chunks.output.txt
    params:
        chunk_dir = os.path.join(config["outdir"], "1")
    output:
        lineages = config["outdir"] + "/2/lineage_report.csv"
    threads: workflow.cores
    run:
        file_stems = []
        for r,d,f in os.walk(params.chunk_dir):
            for fn in f:
                if fn.endswith(".fasta"):
                    stem = fn.split(".")[0]
                    file_stems.append(stem)
        file_stems = ",".join(file_stems)
        shell("snakemake --nolock --snakefile {input.snakefile:q} "
                            "--config "
                            "outdir={config[outdir]} "
                            f"file_stems={file_stems} "
                            "--cores {workflow.cores}")

rule grab_metadata:
    input:
        metadata = rules.gisaid_remove_duplicates.output.metadata,
        lineages = rules.parallel_pangolin.output.lineages
    output:
        metadata = config["outdir"] + "/2/lineages.metadata.csv"
    log:
        config["outdir"] + "/logs/2_grab_metadata.log"
    shell:
        """
        fastafunk add_columns \
          --in-metadata {input.lineages} \
          --in-data {input.metadata} \
          --index-column sequence_name \
          --join-on sequence_name \
          --new-columns covv_accession_id country sample_date epi_week travel_history \
          --where-column epi_week=edin_epi_week country=edin_admin_0 travel_history=edin_travel sample_date=covv_collection_date \
          --out-metadata {output.metadata} &> {log}
        """

rule render_report:
    input:
        metadata = rules.grab_metadata.output.metadata,
        template_b117 = config["template_b117"],
        template_b1351 = config["template_b1351"],
        template_p1 = config["template_p1"],
        continent_file = config["continent_file"]
    params:
        report_stem = os.path.join(config["outdir"],"report", f"{output_prefix}")
    output:
        report_b117 = os.path.join(config["outdir"],"report", f"{output_prefix}_B.1.1.7.html"),
        report_b1351 = os.path.join(config["outdir"],"report", f"{output_prefix}_B.1.351.html"),
        report_p1 = os.path.join(config["outdir"],"report", f"{output_prefix}_P.1.html")
    run:
        fig_gen.plot_figures(config["world_map_file"], config["figdir"], input.metadata, input.continent_file, config["lineages_of_interest"],config["flight_data_b117"],config["flight_data_b1351"],config["import_report_b117"],config["import_report_b1351"],config["import_report_p1"])

        shell(
        """
        render_report.py \
        --metadata {input.metadata:q} \
        --template-b117 {input.template_b117:q} \
        --template-b1351 {input.template_b1351:q} \
        --template-p1 {input.template_p1:q} \
        --figdir {config[outdir]}/figures \
        --report {params.report_stem:q} \
        --command {config[command]:q} \
        --snps {config[snps]:q} \
        --time {config[timestamp]:q} \
        --import-report-b117 {config[import_report_b117]:q} \
        --import-report-b1351 {config[import_report_b1351]:q} \
        --import-report-p1 {config[import_report_p1]:q}
        """)
        print(gfunk.green("Grinch report written to:") + f"{output.report_b117} and {output.report_b1351}")
        