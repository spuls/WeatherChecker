#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import pickle
from datetime import datetime
import datamodel as dm
from wettercom import WetterCom
from apiconfig import APIConfig
from openweathermap import OpenWeatherMap
from forecastioAPI import ForecastIOAPI

from consts import *

from logger import Logger

log = Logger('logAgregator.txt')

log.lprint("WeatherDataAgregator --- START")


#--------------
# setup weather APIs
#--------------
log.lprint("setup weather APIs")
if not os.path.exists(file_path+'openweathermap.conf'):
    log.lprint("conf files missing!")
    quit()

conf = APIConfig()
conf.loadFromFile(file_path+'wettercom.conf')
wCom = WetterCom(conf)

conf2 = APIConfig()
conf2.loadFromFile(file_path+'openweathermap.conf')
owm = OpenWeatherMap(conf2)

conf3 = APIConfig()
conf3.loadFromFile(file_path+'forecastio.conf')
fio = ForecastIOAPI(conf3)

#--------------
# get forecasts
#--------------
log.lprint("get forecasts")
wCom.get_forecast()
owm.get_forecast()
fio.get_forecast()

#--------------
# get time series
#--------------
log.lprint("get time series")
log.lprint("WCOM")
tsd_wetterCom = {'date':[]}
time_series_day_wetterCom = {'date':[]}
time_series_day_wetterCom[wCom.getDateStr(0)] = wCom.sampled_days

log.lprint("OWM")
tsd_owm = {'date':[]}
time_series_day_owm = {'date':[]}
time_series_day_owm[owm.getDateStr(0)] = owm.sampled_days

log.lprint("FIO")
tsd_fio = {'date':[]}
time_series_day_fio = {'date':[]}
time_series_day_fio[fio.getDateStr(0)] = fio.sampled_days

#--------------
# load time series data from file
#--------------
log.lprint("load time series data from file")
if os.path.exists(file_path+'wettercomDump.pkl'):
    log.lprint("WCOM")
    pkl_file = open(file_path+'wettercomDump.pkl', 'rb')
    tsd_wetterCom = pickle.load(pkl_file)
    pkl_file.close()
else:
    log.lprint("Dump file missing: WCOM!")

if os.path.exists(file_path+'owmDump.pkl'):
    log.lprint("OWM")
    pkl_file = open(file_path+'owmDump.pkl', 'rb')
    tsd_owm = pickle.load(pkl_file)
    pkl_file.close()
else:
    log.lprint("Dump file missing: OWM!")

if os.path.exists(file_path+'fioDump.pkl'):
    log.lprint("FIO")
    pkl_file = open(file_path+'fioDump.pkl', 'rb')
    tsd_fio = pickle.load(pkl_file)
    pkl_file.close()
else:
    log.lprint("Dump file missing: FIO!")
    

#--------------
# update time series data with current forecast
#--------------
log.lprint("update time series with current forecast")
tsd_wetterCom.update(time_series_day_wetterCom)
tsd_owm.update(time_series_day_owm)
tsd_fio.update(time_series_day_fio)

#--------------
# save time series data to file
#--------------
log.lprint("save time series data to file")
log.lprint("WCOM")
output = open(file_path+'wettercomDump.pkl', 'wb')
pickle.dump(tsd_wetterCom, output)
output.close()

log.lprint("OWM")
output = open(file_path+'owmDump.pkl', 'wb')
pickle.dump(tsd_owm, output)
output.close()

log.lprint("FIO")
output = open(file_path+'fioDump.pkl', 'wb')
pickle.dump(tsd_fio, output)
output.close()

log.lprint("--- END ---\n")

