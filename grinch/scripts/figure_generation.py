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

def flight_data_plot(figdir, flight_data,locations_to_dates):

    data = []
    with open(flight_data,"r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["flights"]) > 5000:
                if row["gisaidNumber"] =="":
                    data.append((row["country"], int(row["flights"]), 0))
                else:
                    data.append((row["country"], int(row["flights"]), int(row["gisaidNumber"])))

    sorted_data = sorted(data, key=lambda x : x[1], reverse=True)
    

    gisaid_counts = {}
    for i in locations_to_dates:
        if len(locations_to_dates[i]) != 0:
            loc = i.replace("_", " ").title()
            if loc != "United Kingdom":
                gisaid_counts[loc] = len(locations_to_dates[i])
    
    counts = sorted(list(set(gisaid_counts.values())))
    muted_pal = sns.cubehelix_palette(gamma=1.2,n_colors=len(counts)+2)
    muted_dict = {0: "white",9999:"lightgrey"}
    legend_patches = [mpatches.Patch(color="white", label='0')]

    for i in range(0,len(counts)):

        legend_patches.append(mpatches.Patch(color=muted_pal[i], label=counts[i]))
        muted_dict[counts[i]] = muted_pal[i]

    legend_patches.append(mpatches.Patch(color="lightgrey", label='Reported'))

    print("muted dict",muted_dict)
    x,y,z=[],[],[]
    no_seq_dict = {}
    for i in sorted_data:
        x.append(i[0])
        y.append(i[1])
        z.append(i[2])

        if i[2] == 9999:
            no_seq_dict[i[0]] = "lightgrey"
        elif i[2] == 0:
            no_seq_dict[i[0]] = "white"
        
    d = {'country': x, 'flights': y,"gisaid_count":z}
    df = pd.DataFrame(data=d)

    muted_mapping = {}
    for i in x:
        if i in gisaid_counts:
            muted_mapping[i] = muted_dict[gisaid_counts[i]]
        else:
            if i in no_seq_dict:
                muted_mapping[i] = no_seq_dict[i]

    
    fig,ax = plt.subplots(figsize=(9,8))
    
    colours = [muted_mapping[i] for i in x ]
    print("mapping",muted_mapping)
    print(x)
    print("Colours",colours)
    customPalette = sns.set_palette(sns.color_palette(colours))
    # colours = [[0.9157923182358403, 0.7887382324108813, 0.762379547318096], [0.35236581054056426, 0.19374450047758163, 0.36385783424464163], 'white', 'white', 'lightgrey', [0.22670646986529738, 0.13274650666137483, 0.2712570360553994], 'white', 'white', 'white', [0.6000254545207635, 0.34357712853426287, 0.49642279322522603], 'white', [0.9157923182358403, 0.7887382324108813, 0.762379547318096], [0.9157923182358403, 0.7887382324108813, 0.762379547318096], 'white', 'white', 'white', 'white', [0.7912783609518846, 0.5423668589478735, 0.6004332530547714], 'white', [0.47646765006069514, 0.2608912893189593, 0.4358483640521266], 'white', 'lightgrey', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', [0.7045593173634487, 0.43636067561566483, 0.5471495749492405], 'white', 'white', 'white', 'white', 'white', [0.8624113337043101, 0.664860941446331, 0.6706114180923453], 'white']
    sns.barplot(x="flights", y="country", palette=customPalette, edgecolor=".8", dodge=False,data=df)
    plt.xlabel("Total Number of Passengers from London\nOctober")
    plt.ylabel("Country")
    ax.legend(handles=legend_patches,fontsize=8,frameon=False)
    [ax.spines[loc].set_visible(False) for loc in ['top','right']]

    plt.savefig(os.path.join(figdir,f"Air_traffic_from_UK_by_destination.svg"), format='svg', bbox_inches='tight')


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

    muted_pal = sns.cubehelix_palette(n_colors=10)
    muted_pal = sns.color_palette("muted")
    for country, all_dates in locations_to_dates.items():#a dictionary with locations:[dates of variant sequences]

        day_one = loc_to_earliest_date[country]
        date_dict = {}
        count_date_dict = {}

        overall_counts = Counter(country_dates[country]) #counter of all sequences since the variant was first sampled in country
        voc_counts = Counter(all_dates) #so get a counter of variant sequences

        for i in all_dates: #looping through all of the dates with a variant on
            day_frequency = voc_counts[i]/overall_counts[i]
            date_dict[i] = day_frequency #key=date, value=frequency on that day

            count_date_dict[i] = voc_counts[i] #key=date, value=count on that day

        #fill in days from first date of variant to most recent date of variant
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
    for k,v in frequency_over_time.items(): #key=country, value=dict of dates to frequencies
        for k2, v2 in v.items():
            frequency_df_dict['country'].append(k)
            frequency_df_dict["date"].append(k2)
            frequency_df_dict["frequency"].append(v2)
            

    frequency_df = pd.DataFrame(frequency_df_dict)

    fig, ax = plt.subplots(figsize=(7,4))
    c = 0
    for i,v in frequency_over_time.items():
        if len(v) > 10:#so we do this for countries with more than ten days between the first variant sequence and last variant sequence
            c +=1
            relevant = frequency_df.loc[frequency_df["country"] == i]
            y = relevant['frequency'].rolling(7).mean()    
            x = list(frequency_df.loc[frequency_df["country"] == i]["date"])

            plt.plot(x,y, label = i, color=muted_pal[c],linewidth=3)
            [ax.spines[loc].set_visible(False) for loc in ['top','right']]
            plt.xticks(rotation=90)

    plt.legend(frameon=False)
    plt.ylabel("Frequency (7 day rolling average)")
    plt.xlabel("Date")

    plt.savefig(os.path.join(figdir,f"Rolling_average_{lineage}_frequency_per_country.svg"), format='svg', bbox_inches='tight')

    count_df_dict = defaultdict(list)
    for k,v in counts_over_time.items():#key=country, value=dict of dates to counts
        for k2, v2 in v.items():
            count_df_dict['country'].append(k)
            count_df_dict["date"].append(k2)
            count_df_dict["count"].append(np.log10(v2))
            

    count_df = pd.DataFrame(count_df_dict)
    fig, ax = plt.subplots(figsize=(7,4))
    c = 0
    for i,v in counts_over_time.items():
        if len(v) > 10:
            c+=1
            relevant = count_df.loc[count_df["country"] == i]
            y = relevant['count'].rolling(7).mean()    
            x = list(count_df.loc[count_df["country"] == i]["date"])

            plt.plot(x,y, label = i, color=muted_pal[c],linewidth=3)
            [ax.spines[loc].set_visible(False) for loc in ['top','right']]
            plt.xticks(rotation=90)

    plt.legend(frameon=False)
    plt.ylabel("Count (7 day rolling average)")
    plt.xlabel("Date")
    yticks = ax.get_yticks()
    ax.set_yticklabels([(int(10**ytick)) for ytick in yticks])

    plt.savefig(os.path.join(figdir,f"{lineage}_count_per_country.svg"), format='svg', bbox_inches='tight')


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

    

    
    ax1.bar(list(sorted_epiweeks.keys()), list(sorted_epiweeks.values()), color="#86b0a6", width=5)
    ax2 = ax1.twinx()
    ax2.plot(list(cum_counts.keys()), list(cum_counts.values()),linewidth=3,color="dimgrey")
    # ylims = (0,4000) 
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    ax1.xaxis.set_tick_params(rotation=90)
    ax1.set_xlabel("Date")
    ax2.set_ylabel("Total")
    ax1.set_ylabel("Sequence count")
    # ax2.set_ylim(ylims)
    
    plt.savefig(os.path.join(figdir,f"Cumulative_sequence_count_over_time_{lineage}.svg"), format='svg', bbox_inches='tight')


def plot_figures(world_map_file, figdir, metadata, lineages_of_interest,flight_data):

    world_map, countries = prep_map(world_map_file)
    conversion_dict2, omitted = prep_inputs()

    

    for lineage in lineages_of_interest:
        with_info, locations_to_dates, country_new_seqs, loc_to_earliest_date, country_dates = make_dataframe(metadata, conversion_dict2, omitted, lineage, countries, world_map)

        if lineage == "B.1.1.7":
            flight_data_plot(figdir, flight_data,locations_to_dates)

        plot_date_map(figdir, with_info, lineage)
        plot_count_map(figdir, with_info, lineage)
        plot_bars(figdir, locations_to_dates, lineage)
        cumulative_seqs_over_time(figdir,locations_to_dates,lineage)
        plot_frequency_new_sequences(figdir, locations_to_dates, country_new_seqs, loc_to_earliest_date, lineage)
        plot_rolling_frequency_and_counts(figdir, locations_to_dates, loc_to_earliest_date, country_dates, lineage)


# plot_figures(args.map, args.figdir, args.metadata, lineages_of_interest)







