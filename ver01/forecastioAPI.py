#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import hashlib
import json
import time
import datetime

import datamodel as dm
from apiconfig import APIConfig
import forecastio

from logger import Logger


class ForecastIOAPI:
    def getDateStr(self, delta_days):
        #create time string of the following format: "yyyy-mm-dd"
        today = datetime.date.today()
        target = today + datetime.timedelta(days=delta_days)
        return target.strftime("%Y-%m-%d")
    
    def __init__(self, config):
        # set up API data
        self.project = config.project_name
        self.api_key = config.api_key
        self.longitude = config.city_longitude
        self.latitude = config.city_latitude
        self.logfile = "logFIO.txt"

        with Logger(self.logfile) as log:
            log.lprint("--- NEW ---")

        # create MD5 checksum to verfiy your identity at wetter.com API
##        self.checksum = self.project+self.apikey+self.city_code
##        self.md5_sum = hashlib.md5(self.checksum).hexdigest()
##        self.url = "https://api.forecast.io/forecast/{0}/{1},{2}".format(
##            self.api_key,
##            self.latitude,
##            self.longitude)

        # get date and hour to read API results
        nr_days_forecast = 3

        self.api_dates = []
        for i in range(0, nr_days_forecast):
            self.api_dates.append( self.getDateStr(i) )
        
        self.api_hours = ["06:00", "11:00", "17:00", "23:00"]
        self.api_hours_num = [6,11,17,23]

        self.sampled_days = []

    def get_forecast(self, wind_named=False):
        forecast_status = None

        # read data as JSON and transform it this way to a dict
        try:
            with Logger(self.logfile) as log:
                log.lprint("fetching data from API... ForecastIO")
            print "fetching data from API... ForecastIO"
##            time_target = datetime.datetime.now() + datetime.timedelta(days=3)
##            forecast = forecastio.load_forecast(self.api_key,
##                                                self.latitude,
##                                                self.longitude,
##                                                time=time_target,
##                                                units="si")
##            data = forecast.hourly()
##            print data
            forecast_status = True
        except:
            with Logger(self.logfile) as log:
                log.lprint("Could not connect to the ForecastIO server.")
            print "Could not connect to the ForecastIO server - sorry, please \
check your internet connection and possible server down times."
            forecast_status = False

        # read the forecast basis in the variable
        if forecast_status:
            #print data
            del self.sampled_days[:]
            #for d in self.api_dates:
            for i in range(len(self.api_dates)):
                d = self.api_dates[i]
                time_target = datetime.datetime.now() + datetime.timedelta(days=i)
                wds = dm.WeatherDaySample(d, self.api_hours)
                
                got_good_data = False
                counter = 0
                while not got_good_data:
                    counter = counter + 1
                    forecast = forecastio.load_forecast(self.api_key,
                                                        self.latitude,
                                                        self.longitude,
                                                        time=time_target,
                                                        units="si")
                    data = forecast.hourly()
                    for h in self.api_hours:
                        wsp = dm.WeatherSamplePoint(d, h)
                        for hdp in data.data:
                            #hdp = hourly data point
                            #print hdp.time
                            if str(hdp.time) == str(d + " " + h + ":00"):
                                if hdp.temperature is not None and hdp.precipIntensity is not None and hdp.windSpeed is not None:
                                    got_good_data = True
                                    with Logger(self.logfile) as log:
                                        log.lprint("Got good data for time: " + str(hdp.time))
                                else:
                                    with Logger(self.logfile) as log:
                                        log.lprint("Got BAD data for time: " + str(hdp.time))
                                # high temp, low temp, rain chance, wind speed
                                wsp.setValues(hdp.temperature,
                                              hdp.temperature,
                                              hdp.precipIntensity,
                                              hdp.windSpeed)
                                wds.setValuesDayTimeData(wsp)
                    if counter > 5:
                        with Logger(self.logfile) as log:
                            log.lprint("Got only bad data!")
                        print "FIO: Got only bad data!"
                        got_good_data = True
                self.sampled_days.append(wds)
                
            with Logger(self.logfile) as log:
                log.lprint("--- end ---\n") 
        else:
            with Logger(self.logfile) as log:
                log.lprint("WARNING: could not get forecast!")
            print "WARNING: could not get forecast!"

