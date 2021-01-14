import figure_generation as fig_gen
import grinchfunks as gfunk


output_prefix = config["output_prefix"]
config["lineages_of_interest"] = ["B.1.1.7","B.1.351","P.1"]

rule render_report:
    input:
        metadata = config["metadata"],
        template_b117 = config["template_b117"],
        template_b1351 = config["template_b1351"],
        template_p1 = config["template_p1"]
    params:
        report_stem = os.path.join(config["outdir"],"report", f"{output_prefix}")
    output:
        report_b117 = os.path.join(config["outdir"],"report", f"{output_prefix}_B.1.1.7.html"),
        report_b1351 = os.path.join(config["outdir"],"report", f"{output_prefix}_B.1.351.html"),
        report_p1 = os.path.join(config["outdir"],"report", f"{output_prefix}_P.1.html")
    run:
        fig_gen.plot_figures(config["world_map_file"], config["figdir"], input.metadata, config["lineages_of_interest"],config["flight_data_b117"],config["flight_data_b1351"],config["import_report_b117"],config["import_report_b1351"],config["import_report_p1"])

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
        print(gfunk.green("Grinch report written to:") + f"{output.report_b117}, {output.report_p1}and {output.report_b1351}")