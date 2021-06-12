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
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
import matplotlib.ticker as ticker
matplotlib.use('Qt5Agg')
import json
from collections import defaultdict

class CovidGraph:

    """
    Store online data path for fail over o missing downloaded file
    """
    data_store_path="https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-data.json"

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
    Help get params from external passing and initialize

    """
    def __init__(self):
        pass

    """
    Read data from downloaded file -- could read from online
    Will attempt to read file "owid-covid-data.json" from current folder
    if not found will download from "online_data_store_path
    """
    def get_data(self):
        # if we have it locally read
        if os.path.isfile(self.json_data_file):
            with open(self.json_data_file, "r") as read_file:
                raw_data = json.loads(read_file.read())
        elif self.data_store_path:
            raw_data = requests.get(self.data_store_url).json()
        else:
            raise Exception("Cannot read graph data from both local and online sources")

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
        fig.suptitle("“COVID-19” statistics", fontsize = 16)
        # left y axis
        ax.set(title = ",".join(self.country_names),
           xlabel = "Month",
           ylabel = "Total deaths per million,\nNew cases per million")
        #right y axis
        ax2 = ax.twinx()
        ax2.set(
           ylabel = "Total vaccinations per hundred")

        for stat_key, meta in self.stats_meta.items():
            color = meta.get("color")
            y_plot = meta.get("y-plot")

            for index,country_name in enumerate(self.country_names):
                y_values = list(data_to_plot.get(country_name).get(stat_key).values())
                x_values = list(data_to_plot.get(country_name).get(stat_key).keys())
                line_style = 'solid' if index % 2 == 0 else 'dotted'

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
        plt.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left')
        plt.margins(0.2)
        #tight
        fig.tight_layout()
        plt.show()




covid_g = CovidGraph()
covid_g.draw()

