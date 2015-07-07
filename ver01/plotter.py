#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import string

import os.path

import pickle

import plotly.plotly as py
from plotly.graph_objs import *

import datamodel

from consts import *

from logger import Logger

class Plotter:
    def __init__(self, name):
        #--------------
        # setup plotting
        #--------------
        signin = None
        if os.path.exists(file_path+'plotly.conf'):
            conffile = open(file_path+'plotly.conf', 'rb')
            signin = pickle.load(conffile)
            conffile.close()
        else:
            with Logger('logPlotly.txt') as log:
                log.lprint('conf file missing!')
            quit()
        py.sign_in(signin[0], signin[1])
        self.trace_list = []
        self.name = name

    def plot(self, y_in):
        trace0 = Scatter(
            x = range(1,len(y_in)+1),
            y = y_in
            )
        data = Data([trace0])
        plot_url = py.plot(data, filename='test-line', auto_open=False, world_readable=True)
        print plot_url

    def plotError(self, mean_error_in):
##        trace0 = Scatter(
##            x = range(1, len(mean_error_in.error_vals_signed)+1),
##            y = mean_error_in.error_vals_signed
##            )
        trace1 = Box(
            y = mean_error_in.error_vals_signed,
            name = 'Temperature',
            jitter=0.3,
            pointpos=-1.8,
            boxpoints='all'
            )
        # Make layout object (plot title, x-axis title and y-axis title)
        layout = Layout(
            title='Error Data', 
            xaxis=XAxis(title='Days'), 
            yaxis=YAxis(title='Error Values'),
            showlegend=True  # remove legend
            )
        data = Data([trace1])
        fig = Figure(data = data, layout=layout)
        plot_url = py.plot(fig, filename='test-line', auto_open=False, world_readable=True)

    def addForecastError(self, error_in):
        n = error_in.temp_error.name
        n = n + '_Mean:' + '{:.2f}'.format(error_in.temp_error.current_mean_signed_error)
        n = n + '_STD:' + '{:.2f}'.format(error_in.temp_error.current_sdev)
        n = string.replace(n, '_', '<br>')
        trace0 = Box(
            y = error_in.temp_error.error_vals_signed,
            name = n,
            jitter=0.3,
            pointpos=-1.8,
            boxpoints='all',
            boxmean='sd'
            )
        self.trace_list.append(trace0)
        n = error_in.rain_error.name
        n = n + '_Mean:' + '{:.2f}'.format(error_in.rain_error.current_mean_signed_error)
        n = n + '_STD:' + '{:.2f}'.format(error_in.rain_error.current_sdev)
        n = string.replace(n, '_', '<br>')
        trace1 = Box(
            y = error_in.rain_error.error_vals_signed,
            name = n,
            jitter=0.3,
            pointpos=-1.8,
            boxpoints='all',
            boxmean='sd'
            )
        self.trace_list.append(trace1)
        n = error_in.wind_error.name
        n = n + '_Mean:' + '{:.2f}'.format(error_in.wind_error.current_mean_signed_error)
        n = n + '_STD:' + '{:.2f}'.format(error_in.wind_error.current_sdev)
        n = string.replace(n, '_', '<br>')
        trace2 = Box(
            y = error_in.wind_error.error_vals_signed,
            name = n,
            jitter=0.3,
            pointpos=-1.8,
            boxpoints='all',
            boxmean='sd'
            )
        self.trace_list.append(trace2)

    def plotForecastError(self):
        layout = Layout(
            title='Error Data ' + self.name, 
            xaxis=XAxis(title='Forecasts'), 
            yaxis=YAxis(title='Error Values'),
            showlegend=False
            )
        data = Data(self.trace_list)
        fig = Figure(data = data, layout=layout)
        plot_url = py.plot(fig, filename=self.name,
                           auto_open=False,
                           world_readable=True)


