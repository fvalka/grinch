#!/usr/bin/env python3
import os
import argparse
import collections
from grinch import __version__
from datetime import date

from mako.template import Template
from mako.runtime import Context
from mako.exceptions import RichTraceback
from io import StringIO
import json
import csv

import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Report generator script")
    parser.add_argument("--metadata", required=True, help="metadata file", dest="metadata")
    parser.add_argument("--snps",help="snps")
    parser.add_argument("--figdir",help="figure directory")
    parser.add_argument("--command",help="command string", dest="command")
    parser.add_argument("--template-b117",help="template mako html",dest="template_b117")
    parser.add_argument("--template-b1351",help="template mako html",dest="template_b1351")
    parser.add_argument("--template-p1",help="template mako html",dest="template_p1")
    parser.add_argument("--report", help="output report file", dest="report")
    parser.add_argument("--time", help="timestamp", dest="time")
    parser.add_argument("--captions",help="caption info",dest="captions")
    parser.add_argument("--import-report-b117", help="import report", dest="import_report_b117")
    parser.add_argument("--import-report-b1351", help="import report", dest="import_report_b1351")
    parser.add_argument("--import-report-p1", help="import report", dest="import_report_p1")
    return parser.parse_args()


def get_svg_as_string(fig_dir,fig_name):
    fig_string = ""
    fig_file = os.path.join(fig_dir, fig_name)
    if not os.path.isfile(fig_file):
        print("not a real file", fig_file)
        sys.exit(-1)

    with open(fig_file,"r") as f:
        for l in f:
            fig_string += l.rstrip("\n")
    
    height = False
    width = False
    original_preamble = fig_string.split("<metadata>")[0]
    preamble = fig_string.split('<svg')[1].split("<metadata>")[0]
    
    replace_dict = {}
    for i in preamble.split(" "):
        if i.startswith("height="):
            new_i = ""
            if fig_name.startswith("Sequence"):
                new_i = "height=50%"
            elif fig_name.startswith("Air"):
                new_i = "height=80%"
            replace_dict[i] = new_i
            height = True
        if width== False:
            if i.startswith("width="):
                new_i = "width=50%"
                
                if fig_name.startswith("Map") or fig_name.startswith("Date"):
                    new_i="width=90%"
                if fig_name.startswith("Air"):
                    new_i="width=70%"
                replace_dict[i] = new_i
    
    for i in replace_dict:
        preamble= preamble.replace(i, replace_dict[i])
    
    fig_string = "<svg" + fig_string.replace(original_preamble, preamble)

    return fig_string

def make_summary_data(metadata,fig_dir,snp_dict,caption_dict):
    # add lineages and sub lineages into a dict with verity's summary information about each lineage

    summary_dict = collections.defaultdict(dict)

    for lineage in ["B.1.351","B.1.1.7","P.1"]:
        summary_dict[lineage] = {"Lineage":lineage,
                                "Country count":0,
                                "Countries":collections.Counter(),
                                "Earliest date": "",
                                "Count":0,
                                "Date":collections.Counter(),
                                "Travel history":collections.Counter(),
                                "SNPs":snp_dict[lineage],
                                "Likely origin":"",
                                "figures":[]}
    
    summary_dict["B.1.1.7"]["Likely origin"] = "United Kingdom"
    summary_dict["B.1.351"]["Likely origin"] = "South Africa"
    summary_dict["P.1"]["Likely origin"] = "Brazil"
    # compile data for json
    with open(metadata,"r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["sample_date"]:
                country = row["country"]
            
                d = date.fromisoformat(row["sample_date"])

                travel_history = row["travel_history"]
                lineage = row["lineage"]

                if lineage != "" and lineage in ["B.1.1.7","B.1.351","P.1"]:
                    
                    summary_dict[lineage]["Countries"][country]+=1
                    
                    if summary_dict[lineage]["Earliest date"]:
                    
                        if d < summary_dict[lineage]["Earliest date"]:
                            summary_dict[lineage]["Earliest date"] = d
                    else:
                        summary_dict[lineage]["Earliest date"] = d
                    
                    summary_dict[lineage]["Date"][str(d)] +=1

                    summary_dict[lineage]["Count"] +=1 

                    if travel_history:
                        summary_dict[lineage]["Travel history"][travel_history]+=1

    flight_figure_b117 = get_svg_as_string(fig_dir,"Air_traffic_by_destination_B.1.1.7.svg")
    flight_figure_b1351 = get_svg_as_string(fig_dir,"Air_traffic_by_destination_B.1.351.svg")
    flight_figure_p1 = get_svg_as_string(fig_dir,"Air_traffic_by_destination_P.1.svg")
    for lineage in summary_dict:
        fig_count = 0
        travel = summary_dict[lineage]["Travel history"]
        travel_info = ""
        for k in travel:
            travel_info += f"{travel[k]} {k}; "
        travel_info = travel_info.rstrip(";")
        summary_dict[lineage]["Travel history"] = travel_info

        countries = summary_dict[lineage]["Countries"]
        summary_dict[lineage]["Country count"] = len(countries)
        country_info = ""
        total = sum(countries.values())
        for k in countries.most_common(50):
            
            pcent = round((100*k[1])/total, 0)
            country_info += f"{k[0]} {k[1]}, "
        country_info = country_info.rstrip(", ")
        summary_dict[lineage]["Countries"] = country_info
        
        summary_dict[lineage]["Earliest date"] = str(summary_dict[lineage]["Earliest date"])

        date_objects = []
        for d in summary_dict[lineage]["Date"]:

            date_objects.append({"date":d,"count":summary_dict[lineage]["Date"][d]})
        summary_dict[lineage]["Date"] = date_objects

        figure_names = [f"Cumulative_sequence_count_over_time_{lineage}.svg",
                        f"Date_of_earliest_{lineage}_detected.svg",
                        f"Map_of_{lineage}_sequence_counts.svg",
                        f"Sequence_count_per_country_{lineage}.svg",
                        f"Frequency_{lineage}_in_sequences_produced_since_first_new_variant_reported_per_country.svg",
                        f"{lineage}_count_per_continent.svg",
                        f"Rolling_average_{lineage}_frequency_per_continent.svg",
                        f"Map_of_{lineage}_local_transmission.svg"
                        ]

        for fig_name in figure_names:
            fig_count+=1
            fig_string = get_svg_as_string(fig_dir,fig_name)

            fig_stem = ".".join(fig_name.split(".")[:-1])
            fig_stem = fig_stem.replace("_"," ")
            summary_dict[lineage]["figures"].append({
                "name": fig_stem,
                "data": fig_string,
                "number": fig_count
            })

    rows = []
    for lineage in summary_dict:
        rows.append(summary_dict[lineage])
    for row in rows:
        print(row["Lineage"]) 
    return rows,flight_figure_b117,flight_figure_b1351,flight_figure_p1

def parse_import_data(import_report):
    import_data = []
    with open(import_report, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_data = {"Country": row["Country"],
                        "Earliest report": row["earliest_report"],
                        "Date local transmission": row["date_local"],
                        "Local transmission": row["imported_local"],
                        "Method of surveillance": row["method_surveillance"],
                        "Source": row["Source"]
                        }
            import_data.append(row_data)
    return import_data

def lineage_report(template, command, time, today, data, report_stem, lineage, flight_figure,import_report):
    mytemplate = Template(filename=template)
    buf = StringIO()

    import_data = parse_import_data(import_report)

    ctx = Context(buf, command = command, timestamp = time, date = today, version = __version__, summary_data = data, lineage_data = [lineage],flight_figure=flight_figure,import_report=import_data)

    try:
        mytemplate.render_context(ctx)
    except:
        traceback = RichTraceback()
        for (filename, lineno, function, line) in traceback.traceback:
            print("File %s, line %s, in %s" % (filename, lineno, function))
            print(line, "\n")
        print("%s: %s" % (str(traceback.error.__class__.__name__), traceback.error))

    with open(f"{report_stem}_{lineage}.html","w") as fw:
        fw.write(buf.getvalue())




def make_report():

    args = parse_args()

    snp_list = args.snps.split(",")
    snp_dict = {}
    for i in snp_list:
        lineage,snps = i.split("=")
        snp_dict[lineage]= snps.replace(";","<br> ")

    caption_dict = make_caption_dict(args.captions)

    summary_data, flight_figure_b117,flight_figure_b1351,flight_figure_p1 = make_summary_data(args.metadata,args.figdir,snp_dict)

    today = date.today()

    lineage_report(args.template_b1351, args.command, args.time, today, [summary_data[0]], args.report, 'B.1.351', flight_figure_b1351,args.import_report_b1351)

    lineage_report(args.template_b117, args.command, args.time, today, [summary_data[1]], args.report, 'B.1.1.7', flight_figure_b117,args.import_report_b117)

    lineage_report(args.template_p1, args.command, args.time, today, [summary_data[2]], args.report, 'P.1',flight_figure_p1,args.import_report_p1)

if __name__ == "__main__":
    make_report()

