import figure_generation as fig_gen
import grinchfunks as gfunk


output_prefix = config["output_prefix"]
config["lineages_of_interest"] = ["B.1.1.7","B.1.351"]
rule render_report:
    input:
        metadata = config["metadata"],
        template = config["template"]
    output:
        report = os.path.join(config["outdir"],"report", f"{output_prefix}.html")
    run:
        fig_gen.plot_figures(config["world_map_file"], config["figdir"], input.metadata, config["lineages_of_interest"],config["flight_data"])
        print(f"Generated the figure files  in {config['figdir']}")
        shell(
        """
        render_report.py \
        --metadata {input.metadata:q} \
        --template {input.template:q} \
        --figdir {config[outdir]}/figures \
        --report {output.report:q} \
        --command {config[command]:q} \
        --snps {config[snps]:q} \
        --time {config[timestamp]:q}
        """)
        print(gfunk.green("Grinch report written to:") + f"{output.report}")
        