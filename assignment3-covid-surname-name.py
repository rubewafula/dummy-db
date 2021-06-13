#!/bin/python
"""
Simple graph to plot new cases per million, total deaths per million 
and total vaccinations per hundred for Czech Republic and United Kingdom 
in the last 12 months (i.e. July 2020 to June 2021)

Using Matplotlib python plotting library, numpy and scipy.interpolate

"""
import os
import requests
import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
import json
from collections import defaultdict
import configparser
import getopt, sys

class CovidGraph:

    """
    Config file
    """
    config_file = "./config.ini"

    """
    Store online data path for fail over o missing downloaded file
    """
    data_store_url="https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json"

    """
    Name of data file to read
    """
    json_data_file="owid-covid-data.json"
    
    """
    Store data for plotting out graph
    """
    graph_data=None
   
    """
    Default selection of countries to plot
    """
    countries = ['CZE','GBR']
    country_names = []

    """
    stats to be collected
    """

    stats_meta = {
        "new_cases_per_million": {"color":"blue", "y-plot":"left"},
        "total_deaths_per_million":{"color":"red", "y-plot":"left"},
        "total_vaccinations_per_hundred":{"color":"green", "y-plot":"right"}
    }

    """
    Start and stop date for our graph data July 2020 - June 2021
    """
    stats_start_date = dt.datetime.strptime('2020-07-01', "%Y-%m-%d")
    stats_end_date = dt.datetime.strptime('2021-06-30', "%Y-%m-%d")

    """
    Default Plot and axis labels
    """
    subtitle="“COVID-19” statistics"
    xlabel="Month"
    yleftlabel="Total deaths per million,\nNew cases per million"
    yrightlabel="Total vaccinations per hundred"
    line_styles = ["solid","dotted"]
    legend_location="lower left"
    
    """
    Command line args extras
    """
    short_options = "hc:v"
    long_options = ["help", "config-file="]
    verbose=False


    """
    Help get params from external passing and initialize

    """
    def __init__(self):
        cmd_arguments = sys.argv[1:]

        help_text="\n---\nCOVID 19: stats. A small lib to draw graph based"\
            "on json data for covid 19.\nDraws multiple line graph"\
            "on both axis using matplotlib library\n---\nTo run this"\
            "your please execute the command below.\n"\
            ":~ python3 script-name.py --config-file=config.ini\n"\
            ":~ python3 script-name.py -c config.ini\n"\
            "use -h or --help to get this message"\
            "\n---\n"

        try:
            arguments, values = getopt.getopt(cmd_arguments, self.short_options, self.long_options)
        except:
            print("\n--\nError in supplid arguments\nPlease use -h option "\
                "to get details on how to call\n")
            exit(0)
            
        for current_argument, current_value in arguments:
            if current_argument in ("-h", "--help"):
                print(help_text)
                exit(0)
            elif current_argument in ("-c", "--config-file"):
                self.config_file = current_value
            elif current_argument in ("-v", "--verbose"):
                self.verbose = True
            else:
                print("Missing args will default to local config "\
                    "./config.ini  use -h option to get help on possible option")
 
        if not arguments:
            print(help_text)
        self._print("Reading config file %s " % self.config_file)
        self.read_config()


    def _print(self, message):
        if self.verbose:
            print(message)

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file) 
        if config.has_option('data', 'data_store_url'):
            self.data_store_url = config.get('data', 'data_store_url')
            self._print("Read config data url %s" % self.data_store_url)
        
        if config.has_option('data', 'json_data_file'):
            self.json_data_file = config.get('data', 'json_data_file')
            self._print("Read config data file %s" % self.json_data_file)

        if config.has_option('countries', 'countries'):
            self.countries = config.get('countries', 'countries').split(",")
            self._print("Read config countries %s" % self.countries)

        if config.has_section('stats'):
            _stats = config.items('stats')
            self.stats_meta = {}
            for _stat, _meta in _stats:
                _options = {_metad.split(":")[0]:_metad.split(":")[1] for _metad in _meta.split(",")}
                self.stats_meta[_stat] = _options
            self._print("Read config stats: %r" % self.stats_meta)

        if  config.has_option('statsdates', 'stats_start_date'):
            _start_date = config.get('statsdates', 'stats_start_date')
            self.stats_start_date = dt.datetime.strptime(_start_date, "%Y-%m-%d")
            self._print("Read config stats start date: %r" % self.stats_start_date)

        if  config.has_option('statsdates', 'stats_end_date'):
            _end_date = config.get('statsdates', 'stats_end_date')
            self.stats_end_date = dt.datetime.strptime(_end_date, "%Y-%m-%d")
            self._print("Read config end date: %r" % self.stats_end_date)
        
        # graph labels
        if config.has_section('labels'):
            self.subtitle=config.get('labels', 'subtitle')
            self.xlabel=config.get('labels', 'xlabel')
            self.yleftlabel="\n".join(config.get('labels', 'yleftlabel').split(","))
            self.yrightlabel="\n".join(config.get('labels', 'yrightlabel').split(","))
            self.line_styles = config.get('labels', 'line_styles').split(",")
            self.legend_location=config.get('labels', 'legend_location')
            self._print("Read config labels ..")


    """
    Read data from downloaded file -- could read from online
    Will attempt to read file "owid-covid-data.json" from current folder
    if not found will download from "online_data_store_path
    """
    def get_data(self):
        # if we have it locally read
        if os.path.isfile(self.json_data_file):
            self._print("Starting to fetch data from %s" % self.json_data_file)
            with open(self.json_data_file, "r") as read_file:
                raw_data = json.loads(read_file.read())
        elif self.data_store_url:
            self._print("Starting to fetch data from  %s" % self.data_store_url)
            response = requests.get(self.data_store_url)
            raw_data = response.json()
        else:
            raise Exception("Cannot read graph data from both local and online sources")
        self._print("Data found ... OK")
        return raw_data

    """
    Extract graph data from raw data -- Just what we need to get out graph
    Czech
       July 2020
           --cases_per_million
           --total_deaths_per_million
           -- total_vaccinations_per_hundred
       Feb
           ---
       ...
       June -- 2021

    """
    def get_graph_data(self, raw_data):
        graph_data = {}
        self._print("Populating graph data ...")
        for country in self.countries:
            country_data =  raw_data[country]
            country_name = country_data['location']
            self.country_names.append(country_name)
            graph_data[country_name] = defaultdict(dict)

            data = country_data['data']
            for stats in data:
                _stats_date = dt.datetime.strptime(stats['date'], "%Y-%m-%d")
                stats_date = stats['date']
                if _stats_date < self.stats_start_date:
                    continue
                
                if _stats_date > self.stats_end_date:
                    break
                for stat_key in self.stats_meta.keys():
                    graph_data[country_name][stat_key][stats_date] = stats.get(stat_key, 0)

        return graph_data

    def add_line_to_plot(self, country_name, statistic_name, 
            x_values, y_values, axis, line_style, color):
        self._print("Adding plot line %s, %s" % (statistic_name, country_name))
        x = np.array(x_values)
        y = np.array(y_values)
        axis.plot(x, y, 
            color = color, 
            label = '%s - %s' % (statistic_name, country_name),
            linestyle=line_style,
            alpha=0.7
        )


    """
    Draw the graph
    """
    def draw(self):

        data_to_plot = self.get_graph_data(
            self.get_data()
        )
        
        _months = []
        cases_per_million = []

        _m_date =  self.stats_start_date

        while _m_date < self.stats_end_date:
            _stats_month = dt.datetime.strftime(_m_date, "%Y-%m")
            _months.append(_stats_month)
            _m_date = _m_date + relativedelta(months=1)

        fig, ax = plt.subplots(1, 1, figsize=(20, 12), sharey=True)
        fig.suptitle(self.subtitle, fontsize = 16)
        # left y axis
        ax.set(title = ",".join(self.country_names),
           xlabel = self.xlabel,
           ylabel = self.yleftlabel
        )

        #right y axis
        ax2 = ax.twinx()
        ax2.set(ylabel = self.yrightlabel)

        for stat_key, meta in self.stats_meta.items():
            color = meta.get("color")
            y_plot = meta.get("y-plot")

            for index,country_name in enumerate(self.country_names):
                y_values = list(data_to_plot.get(country_name).get(stat_key).values())
                x_values = list(data_to_plot.get(country_name).get(stat_key).keys())
                #alternate the line style set in config -- i.e solid to dotted
                line_style = self.line_styles[index % 2]

                # we plot on right or left based meta in stats_meta
                if y_plot == "left":
                    self.add_line_to_plot( country_name, stat_key.title().replace("_", " "), 
                        x_values, y_values, ax, line_style, color)
                else:
                    self.add_line_to_plot( country_name, stat_key.title().replace("_", " "), 
                        x_values, y_values, ax2, line_style, color)

        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(start, end, (end-start)/len(_months)))
        ax.set_xticklabels(_months)
        
        #add all labels for both axis
        lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
        handles, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        plt.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=self.legend_location)
        plt.margins(0.2)
        #tight
        fig.tight_layout()
        self._print("Plotting graph .. (:.:'`.|') yey!")
        plt.show()



#call the class to draw out plot
covid_g = CovidGraph()
covid_g.draw()

