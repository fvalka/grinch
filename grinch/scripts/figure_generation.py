import geopandas
import csv
from collections import defaultdict
from collections import Counter
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from epiweeks import Week


from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import datetime as dt
import seaborn as sns
import numpy as np
import math
import os

# #for testing
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("--map")
# parser.add_argument("--figdir")
# parser.add_argument("--metadata")
# args = parser.parse_args()
# lineages_of_interest = ["B.1.1.7", "B.1.351"]
# ###

plt.rcParams.update({'font.size': 10})

def prep_map(world_map_file):

    world_map = geopandas.read_file(world_map_file)

    new_names = []
    for i in world_map["admin"]:
        new_name = i.replace(" ","_").upper()
        new_names.append(new_name)
    world_map["admin"] = new_names

    countries = []
    for i in world_map["admin"]:
        countries.append(i.replace(" ", "_"))

    return world_map, countries

def prep_inputs():

    omitted = ["ST_EUSTATIUS", "CRIMEA"] #too small, no shape files

    conversion_dict = {}

    conversion_dict["United_States"] = "United_States_of_America"
    conversion_dict["USA"] = "United_States_of_America"
    conversion_dict["Viet_Nam"] = "Vietnam"
    conversion_dict["North_Macedonia"] = "Macedonia"
    conversion_dict["Serbia"] = "Republic_of_Serbia"
    conversion_dict["Côte_d’Ivoire"] = "Ivory_Coast"
    conversion_dict["Cote_dIvoire"] = "Ivory_Coast"
    conversion_dict["Czech_Repubic"] = "Czech_Republic"
    conversion_dict["UK"] = "United_Kingdom"
    conversion_dict["Timor-Leste"] = "East_Timor"
    conversion_dict["DRC"] = "Democratic_Republic_of_the_Congo"
    conversion_dict["Saint_Barthélemy"] = "Saint-Barthélemy"
    conversion_dict["Saint_Martin"] = "Saint-Martin"
    conversion_dict["Curacao"] = "Curaçao"

    conversion_dict2 = {}

    for k,v in conversion_dict.items():
        conversion_dict2[k.upper().replace(" ","_")] = v.upper().replace(" ","_")

    return conversion_dict2, omitted

def make_dataframe(metadata, conversion_dict2, omitted, lineage_of_interest, countries, world_map):

    locations_to_dates = defaultdict(list)
    country_to_new_country = {}
    country_new_seqs = {}
    country_dates = defaultdict(list)

    with open(metadata) as f:
        data = csv.DictReader(f)
        for seq in data:
            if seq["lineage"] == lineage_of_interest:
                seq_country = seq["country"].upper().replace(" ","_")
                if seq_country in conversion_dict2:
                    new_country = conversion_dict2[seq_country]
                else:
                    if seq_country not in omitted:
                        new_country = seq_country
                    else:
                        new_country = ""
                if new_country not in countries and new_country != "":
                    pass
                elif new_country != "":
                    locations_to_dates[new_country].append(dt.datetime.strptime(seq["sample_date"], "%Y-%m-%d").date())
                country_to_new_country[seq_country] = new_country
    

    loc_to_earliest_date = {}
    loc_seq_counts = {}

    df_dict = defaultdict(list)

    for country, dates in locations_to_dates.items():
        loc_seq_counts[country] = len(dates)
        loc_to_earliest_date[country] = min(dates)
        
        df_dict["admin"].append(country.upper().replace(" ","_"))
        df_dict["earliest_date"].append(min(dates))
        df_dict["number_of_sequences"].append(np.log(len(dates)))
        
    info_df = pd.DataFrame(df_dict)

    with_info = world_map.merge(info_df, how="outer")


    with open(metadata) as f:
        data = csv.DictReader(f)    
        for seq in data:
            seq_country = seq["country"].upper().replace(" ","_")
            if seq_country in country_to_new_country:
                new_country = country_to_new_country[seq_country]
                date = dt.datetime.strptime(seq["sample_date"], "%Y-%m-%d").date()
                if date >= loc_to_earliest_date[new_country]:
                    if new_country not in country_new_seqs:
                        country_new_seqs[new_country] = 1
                    else:
                        country_new_seqs[new_country] += 1
                    country_dates[new_country].append(date)


    return with_info, locations_to_dates, country_new_seqs, loc_to_earliest_date, country_dates

def plot_date_map(figdir, with_info, lineage):

    muted_pal = sns.cubehelix_palette(as_cmap=True, reverse=True)

    fig, ax = plt.subplots(figsize=(10,10))


    with_info = with_info.to_crs("EPSG:4326")

    with_info.plot(ax=ax, cmap=muted_pal, legend=True, column="earliest_date", 
                    legend_kwds={'bbox_to_anchor':(-.03, 1.05),'fontsize':8,'frameon':False},
                    missing_kwds={"color": "lightgrey","label": "No variant recorded"})
    
    ax.axis("off")
    
    plt.savefig(os.path.join(figdir,f"Date_of_earliest_{lineage}_detected.svg"), format='svg', bbox_inches='tight')




def plot_count_map(figdir, with_info, lineage):

    muted_pal = sns.cubehelix_palette(as_cmap=True)
    dark = mpatches.Patch(color=muted_pal.colors[-1], label='Max sequences')
    light = mpatches.Patch(color=muted_pal.colors[0], label='1 sequence')
    none = mpatches.Patch(color="lightgrey", label='No variant record')
    fig, ax = plt.subplots(figsize=(10,10))

    with_info = with_info.to_crs("EPSG:4326")
    with_info.plot(ax=ax, cmap=muted_pal, legend=False, column="number_of_sequences", 
                    # legend_kwds={'bbox_to_anchor':(-.03, 1.05),'fontsize':7,'frameon':False},
                    missing_kwds={"color": "lightgrey","label": "No variant recorded"})

    ax.legend(handles=[dark,light,none],bbox_to_anchor=(-.03, 1.05),fontsize=8,frameon=False)
    ax.axis("off")

    # colourbar = ax.get_figure().get_axes()[1]
    # yticks = colourbar.get_yticks()
    # colourbar.set_yticklabels([round(math.exp(ytick)) for ytick in yticks])

    plt.savefig(os.path.join(figdir,f"Map_of_{lineage}_sequence_counts.svg"), format='svg', bbox_inches='tight')


def plot_bars(figdir, locations_to_dates, lineage):

    x = []
    y = []
    text_labels = []
    counts = []
    sortable_data = []

    for k in locations_to_dates:

        count = len(locations_to_dates[k])
        counts.append(count)
        sortable_data.append((count, k))
    
    for k in sorted(sortable_data, key = lambda x : x[0], reverse=True):
        count,location=k
        text_labels.append(count)
        y.append(np.log10(count))
        x.append(location.replace("_", " ").title())

    fig, ax = plt.subplots(1,1, figsize=(5,3), frameon=False)

    plt.bar(x,y,color="#86b0a6")

    [ax.spines[loc].set_visible(False) for loc in ['top','right']]

    yticks = ax.get_yticks()
    ax.set_yticklabels([(int(10**ytick)) for ytick in yticks])
    
    rects = ax.patches
    for rect, label in zip(rects, text_labels):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 0.1, label,
                ha='center', va='bottom')

    plt.ylabel("Sequence count\n(log10)")
    plt.xlabel("Country")
    plt.xticks(rotation=90)

    plt.savefig(os.path.join(figdir,f"Sequence_count_per_country_{lineage}.svg"), format='svg', bbox_inches='tight')


def plot_frequency_new_sequences(figdir, locations_to_dates, country_new_seqs, loc_to_earliest_date, lineage):

    voc_frequency = {}
    text_label_dict = {}

    for country, all_dates in locations_to_dates.items():
        total = country_new_seqs[country]
        freq = len(all_dates)/total
        voc_frequency[country.replace("_"," ").title()] = freq
        text_label_dict[country.replace("_"," ").title()] = f"{len(all_dates)}/{total}"


    fig, ax = plt.subplots(figsize=(8,5))

    sort = {k: v for k, v in sorted(voc_frequency.items(), key=lambda item: item[1], reverse=True)}

    x = []
    y = []
    text_labels = []
    for key, value in sort.items():
        x.append(key)
        y.append(value)
        text_labels.append(text_label_dict[key])

        
    [ax.spines[loc].set_visible(False) for loc in ['top','right']]

    plt.ylabel("Frequency")
    plt.xlabel("Country")
    plt.xticks(rotation=90)

    plt.bar(x,y, color="#86b0a6")

    rects = ax.patches
    for rect, label in zip(rects, text_labels):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 0.01, label,
                ha='center', va='bottom', size=12, rotation=90)

    plt.savefig(os.path.join(figdir,f"Frequency_{lineage}_in_sequences_produced_since_first_new_variant_reported_per_country.svg"), format='svg', bbox_inches='tight')

def plot_rolling_frequency_and_counts(figdir, locations_to_dates, loc_to_earliest_date, country_dates, lineage):

    frequency_over_time = defaultdict(dict)
    counts_over_time = defaultdict(dict)

    for country, all_dates in locations_to_dates.items():

        day_one = loc_to_earliest_date[country]
        date_dict = {}
        count_date_dict = {}

        overall_counts = Counter(country_dates[country])
        voc_counts = Counter(all_dates)
        
        # if country == "NETHERLANDS":
        #     print("overall")
        #     for k,v in sorted(overall_counts.items()):
        #         print(k,v)
        #     print("voc counts")
        #     for k,v in sorted(voc_counts.items()):
        #         print(k,v)

        for i in all_dates:
            day_frequency = voc_counts[i]/overall_counts[i]
            date_dict[i] = day_frequency

            count_date_dict[i] = voc_counts[i]

            
        date_range = (max(date_dict.keys())-day_one).days
        for day in (day_one + dt.timedelta(n) for n in range(1,date_range)):
            if day not in date_dict.keys():
                date_dict[day] = date_dict[day-dt.timedelta(1)]

        count_date_range = (max(count_date_dict.keys())-day_one).days
        for day in (day_one + dt.timedelta(n) for n in range(1,count_date_range)):
            if day not in count_date_dict.keys():
                count_date_dict[day] = count_date_dict[day-dt.timedelta(1)]
                    
        frequency_over_time[country.replace("_"," ").title()] = OrderedDict(sorted(date_dict.items())) 
        counts_over_time[country.replace("_"," ").title()] = OrderedDict(sorted(count_date_dict.items()))

    frequency_df_dict = defaultdict(list)
    for k,v in frequency_over_time.items():
        for k2, v2 in v.items():
            frequency_df_dict['country'].append(k)
            frequency_df_dict["date"].append(k2)
            frequency_df_dict["frequency"].append(v2)
            

    frequency_df = pd.DataFrame(frequency_df_dict)

    fig, ax = plt.subplots(figsize=(15,7))

    for i,v in frequency_over_time.items():
        if len(v) > 10:
            relevant = frequency_df.loc[frequency_df["country"] == i]
            y = relevant['frequency'].rolling(7).mean()    
            x = list(frequency_df.loc[frequency_df["country"] == i]["date"])

            plt.plot(x,y, label = i)

    plt.legend()
    plt.ylabel("Frequency (7 day rolling average)")
    plt.xlabel("Date")

    plt.savefig(os.path.join(figdir,f"frequency_rolling_{lineage}.svg"), format='svg', bbox_inches='tight')

    count_df_dict = defaultdict(list)
    for k,v in counts_over_time.items():
        for k2, v2 in v.items():
            count_df_dict['country'].append(k)
            count_df_dict["date"].append(k2)
            count_df_dict["count"].append(np.log10(v2))
            


    count_df = pd.DataFrame(count_df_dict)
    fig, ax = plt.subplots(figsize=(15,7))

    for i,v in counts_over_time.items():
        if len(v) > 10:
            relevant = count_df.loc[count_df["country"] == i]
            y = relevant['count'].rolling(7).mean()    
            x = list(count_df.loc[count_df["country"] == i]["date"])

            plt.plot(x,y, label = i)

    plt.legend()
    plt.ylabel("Count (7 day rolling average)")
    plt.xlabel("Date")
    yticks = ax.get_yticks()
    ax.set_yticklabels([(int(10**ytick)) for ytick in yticks])

    plt.savefig(os.path.join(figdir,f"count_rolling_{lineage}.svg"), format='svg', bbox_inches='tight')


def cumulative_seqs_over_time(figdir, locations_to_dates,lineage):

    dates = []
    epiweek_lst = []

    for k,v in locations_to_dates.items():
        dates.extend(v)
        
    date_counts = Counter(dates)

    seq_number = 0
    cum_counts = {}
    for date, value in sorted(date_counts.items()):
        seq_number = seq_number + value
        cum_counts[date] = seq_number

    for i in dates:
        epiweek_lst.append(Week.fromdate(i).startdate())
    
    epiweek_counts = Counter(epiweek_lst)
    sorted_epiweeks = OrderedDict(sorted(epiweek_counts.items()))

    fig, ax1 = plt.subplots(1,1,figsize=(6,4))

    ax1.plot(list(cum_counts.keys()), list(cum_counts.values()))

    ax2 = ax1.twinx()
    ax2.bar(list(sorted_epiweeks.keys()), list(sorted_epiweeks.values()), color="#86b0a6", width=5)

    ylims = (0,4000) 
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    ax1.xaxis.set_tick_params(rotation=90)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Sequence count")
    ax2.set_ylabel("New sequences")
    ax2.set_ylim(ylims)
    
    plt.savefig(os.path.join(figdir,f"Cumulative_sequence_count_over_time_{lineage}.svg"), format='svg', bbox_inches='tight')


def plot_figures(world_map_file, figdir, metadata, lineages_of_interest):

    world_map, countries = prep_map(world_map_file)
    conversion_dict2, omitted = prep_inputs()

    for lineage in lineages_of_interest:
        with_info, locations_to_dates, country_new_seqs, loc_to_earliest_date, country_dates = make_dataframe(metadata, conversion_dict2, omitted, lineage, countries, world_map)

        plot_date_map(figdir, with_info, lineage)
        plot_count_map(figdir, with_info, lineage)
        plot_bars(figdir, locations_to_dates, lineage)
        cumulative_seqs_over_time(figdir,locations_to_dates,lineage)
        plot_frequency_new_sequences(figdir, locations_to_dates, country_new_seqs, loc_to_earliest_date, lineage)
        plot_rolling_frequency_and_counts(figdir, locations_to_dates, loc_to_earliest_date, country_dates, lineage)


# plot_figures(args.map, args.figdir, args.metadata, lineages_of_interest)







