#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import copy

import time
from datetime import datetime

import pickle

import datamodel as dm
from statmodel import *

from apiconfig import APIConfig
from openweathermap import OpenWeatherMap
from wettercom import WetterCom
from forecastioAPI import ForecastIOAPI

from plotter import Plotter

from consts import *

from logger import Logger

log = Logger('logChecker.txt')

log.lprint("WeatherDataChecker --- START")

if not os.path.exists(file_path+'wettercomDump.pkl'):
    log.lprint("dump files missing! - quit!")
    quit()

#--------------
# setup weather API for current weather data
#--------------
log.lprint("set up weather APIs")
conf = APIConfig()
conf.loadFromFile(file_path+'openweathermap.conf')
owm = OpenWeatherMap(conf)
fio = ForecastIOAPI(conf)
wcom = WetterCom(conf)

#--------------
# get weather data
#--------------
log.lprint("get current weather")
owm.getCurrentData()
current_data = dm.WeatherSamplePoint(owm.current_weather.date, owm.current_weather.time)
current_data.copyData(owm.current_weather)

#--------------
# load time series data from file
#--------------
log.lprint("load time series data")

log.lprint("WCOM")
pkl_file = open(file_path+'wettercomDump.pkl', 'rb')
tsd_wetterCom = pickle.load(pkl_file)
pkl_file.close()

log.lprint("OWM")
pkl_file = open(file_path+'owmDump.pkl', 'rb')
tsd_owm = pickle.load(pkl_file)
pkl_file.close()

log.lprint("FIO")
pkl_file = open(file_path+'fioDump.pkl', 'rb')
tsd_fio = pickle.load(pkl_file)
pkl_file.close()

log.lprint("Current")
tsd_current = None
if os.path.exists(file_path+'currentDump.pkl'):
    log.lprint("current data found.")
    pkl_file = open(file_path+'currentDump.pkl', 'rb')
    tsd_current = pickle.load(pkl_file)
    pkl_file.close()
else:
    log.lprint("no current data found")
    tsd_current = []

#--------------
# update time series data with current data
#--------------
log.lprint("update time series data")
tsd_current.append(current_data)

#--------------
# save time series data to file
#--------------
log.lprint("save time series data")
output = open(file_path+'currentDump.pkl', 'wb')
pickle.dump(tsd_current, output)
output.close()

#--------------
# do statistics!
#--------------
log.lprint("do statistics")
nr_days_forecast = 3

#---
# setup date and hour
#---
log.lprint("set up date and hour")
current_date = owm.getDateStr(0)
current_hour = datetime.now().time().hour
log.lprint("current hour: " + str(current_hour))

min_i = 0
min_diff = 24
for i in range(len(owm.api_hours_num)):
    if abs(current_hour - owm.api_hours_num[i]) < min_diff:
        min_i = i
        min_diff = abs(current_hour - owm.api_hours_num[i])
log.lprint("closest hour" + str(owm.api_hours_num[min_i]))

#---
# setup statistical error computation
#---
log.lprint("setup statistical error computation")
log.lprint("read files")
error_day = {'owm':[], 'fio':[], 'wcom':[]}
if os.path.exists(file_path+'owmError.pkl'):
    #owm
    log.lprint("OWM")
    pkl_file = open(file_path+'owmError.pkl', 'rb')
    error_day['owm'] = pickle.load(pkl_file)
    pkl_file.close()
    #fio
    log.lprint("FIO")
    pkl_file = open(file_path+'fioError.pkl', 'rb')
    error_day['fio'] = pickle.load(pkl_file)
    pkl_file.close()
    #wcom
    log.lprint("WCOM")
    pkl_file = open(file_path+'wcomError.pkl', 'rb')
    error_day['wcom'] = pickle.load(pkl_file)
    pkl_file.close()
else:
    log.lprint("files not found.")
    for i in range(nr_days_forecast):
        error_day['owm'].append(ForecastError())
        error_day['owm'][i].setName(str(i)+'day_OWM')
        error_day['fio'].append(ForecastError())
        error_day['fio'][i].setName(str(i)+'day_ForecastIO')
        error_day['wcom'].append(ForecastError())
        error_day['wcom'][i].setName(str(i)+'day_WetterCom')

##error_samplePoint = {'owm':{0:None, 1:None, 2:None, 3:None}
##                     'fio':{0:None, 1:None, 2:None, 3:None}
##                     'wcom':{0:None, 1:None, 2:None, 3:None}}

error_samplePoint = {'owm':[], 'fio':[], 'wcom':[]}

log.lprint("read errorsamplepoints")
if os.path.exists(file_path+'errorSamplePoints.pkl'):
    log.lprint("file found")
    pkl_file = open(file_path+'errorSamplePoints.pkl', 'rb')
    error_samplePoint.update(pickle.load(pkl_file))
    pkl_file.close()
else:
    log.lprint("file not found")
    for x in range(nr_days_forecast):
        error_samplePoint['owm'].append({0:None, 1:None, 2:None, 3:None})
        error_samplePoint['fio'].append({0:None, 1:None, 2:None, 3:None})
        error_samplePoint['wcom'].append({0:None, 1:None, 2:None, 3:None})
        for i in range(4):
            error_samplePoint['owm'][x][i] = ForecastError()
            error_samplePoint['owm'][x][i].setName(str(x+1)+'day_'+str(owm.api_hours_num[i])+'time_OWM')
            error_samplePoint['fio'][x][i] = ForecastError()
            error_samplePoint['fio'][x][i].setName(str(x+1)+'day_'+str(fio.api_hours_num[i])+'time_ForecastIO')
            error_samplePoint['wcom'][x][i] = ForecastError()
            error_samplePoint['wcom'][x][i].setName(str(x+1)+'day_'+str(wcom.api_hours_num[i])+'time_WetterCom')

#---
# do actual statistics and parse forecast data
#---
log.lprint("do statistics and parse forecast data")
for i in range(nr_days_forecast):
    backwards_forecast_date = owm.getDateStr(-i)
    log.lprint("check date: " + backwards_forecast_date)

    # openweathermap
    if backwards_forecast_date not in tsd_owm:
        log.lprint("date not found!")
        continue

    log.lprint("OWM")
    samples = tsd_owm[backwards_forecast_date]
    nr_day_samples = len(samples)
    for x in range(nr_day_samples):
        for t in range(4):
            if samples[x].date == current_date and samples[x].sample_points[t].time == owm.api_hours[min_i]:
                #get errors for each forecast value
                error_day['owm'][i].compareForecastToCurrent(samples[x].sample_points[t], current_data)
                error_samplePoint['owm'][i][min_i].compareForecastToCurrent(samples[x].sample_points[t], current_data)

    # forecastIO
    log.lprint("FIO")
    samples = tsd_fio[backwards_forecast_date]
    nr_day_samples = len(samples)
    for x in range(nr_day_samples):
        for t in range(4):
            if samples[x].date == current_date and samples[x].sample_points[t].time == fio.api_hours[min_i]:
                #get errors for each forecast value
                error_day['fio'][i].compareForecastToCurrent(samples[x].sample_points[t], current_data)
                error_samplePoint['fio'][i][min_i].compareForecastToCurrent(samples[x].sample_points[t], current_data)

    # do wetterCom last, as it uses probability for rain
    log.lprint("WCOM")
    # thus, if rain occured the current probability has to be set to 1
    if current_data.rain_chance > 0:
        current_data.rain_chance = 1.0
    else:
        current_data.rain_chance = 0.0
    # wetterCom
    samples = tsd_wetterCom[backwards_forecast_date]
    nr_day_samples = len(samples)
    for x in range(nr_day_samples):
        for t in range(4):
            if samples[x].date == current_date and samples[x].sample_points[t].time == wcom.api_hours[min_i]:
                #get errors for each forecast value
                error_day['wcom'][i].compareForecastToCurrent(samples[x].sample_points[t], current_data)
                error_samplePoint['wcom'][i][min_i].compareForecastToCurrent(samples[x].sample_points[t], current_data)

#---
# save statistical data
#---
log.lprint("save statistics")
#owm
pkl_file = open(file_path+'owmError.pkl', 'wb')
pickle.dump(error_day['owm'], pkl_file)
pkl_file.close()
#fio
pkl_file = open(file_path+'fioError.pkl', 'wb')
pickle.dump(error_day['fio'], pkl_file)
pkl_file.close()
#wcom
pkl_file = open(file_path+'wcomError.pkl', 'wb')
pickle.dump(error_day['wcom'], pkl_file)
pkl_file.close()
#samplePoint error data
pkl_file = open(file_path+'errorSamplePoints.pkl', 'wb')
pickle.dump(error_samplePoint, pkl_file)
pkl_file.close()


#--------------
# setup plotter
#--------------
log.lprint("plot data.")
plt_day1_owm = Plotter('1DayForecastOWM')
plt_day2_owm = Plotter('2DayForecastOWM')
plt_day3_owm = Plotter('3DayForecastOWM')

plt_day1_fio = Plotter('1DayForecastFIO')
plt_day2_fio = Plotter('2DayForecastFIO')
plt_day3_fio = Plotter('3DayForecastFIO')

plt_day1_wcom = Plotter('1DayForecastWCOM')
plt_day2_wcom = Plotter('2DayForecastWCOM')
plt_day3_wcom = Plotter('3DayForecastWCOM')

plt_all_days_owm = Plotter('EachDayForecastOWM')
plt_all_days_fio = Plotter('EachDayForecastFIO')
plt_all_days_wcom = Plotter('EachDayForecastWCOM')

#---
# plot statistical data
#---
for i in range(nr_days_forecast):
    plt_all_days_owm.addForecastError(error_day['owm'][i])
    plt_all_days_fio.addForecastError(error_day['fio'][i])
    plt_all_days_wcom.addForecastError(error_day['wcom'][i])

for x in range(nr_days_forecast):
    for i in range(4):
        if x == 0:
            plt_day1_owm.addForecastError(error_samplePoint['owm'][x][i])
            plt_day1_fio.addForecastError(error_samplePoint['fio'][x][i])
            plt_day1_wcom.addForecastError(error_samplePoint['wcom'][x][i])
        if x == 1:
            plt_day2_owm.addForecastError(error_samplePoint['owm'][x][i])
            plt_day2_fio.addForecastError(error_samplePoint['fio'][x][i])
            plt_day2_wcom.addForecastError(error_samplePoint['wcom'][x][i])
        if x == 2:
            plt_day3_owm.addForecastError(error_samplePoint['owm'][x][i])
            plt_day3_fio.addForecastError(error_samplePoint['fio'][x][i])
            plt_day3_wcom.addForecastError(error_samplePoint['wcom'][x][i])

plt_day1_owm.plotForecastError()
plt_day2_owm.plotForecastError()
plt_day3_owm.plotForecastError()

plt_day1_fio.plotForecastError()
plt_day2_fio.plotForecastError()
plt_day3_fio.plotForecastError()

plt_day1_wcom.plotForecastError()
plt_day2_wcom.plotForecastError()
plt_day3_wcom.plotForecastError()

plt_all_days_owm.plotForecastError()
plt_all_days_fio.plotForecastError()
plt_all_days_wcom.plotForecastError()

log.lprint("--- END ---\n")
