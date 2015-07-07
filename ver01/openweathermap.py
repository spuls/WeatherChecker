#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import hashlib
import json
import time
import datetime

import datamodel as dm
from apiconfig import APIConfig

from logger import Logger

class OpenWeatherMap:
    def getDateStr(self, delta_days):
        #create time string of the following format: "yyyy-mm-dd"
        today = datetime.date.today()
        target = today + datetime.timedelta(days=delta_days)
        return target.strftime("%Y-%m-%d")
    
    def __init__(self, config):
        # set up API data
        self.api_key = config.api_key
        self.city_code = config.city_code

        self.url = "http://api.openweathermap.org/data/2.5/forecast/city?id={0}&APPID={1}&units=metric".format(self.city_code, self.api_key)
        self.current_url = "http://api.openweathermap.org/data/2.5/weather?id={0}&APPID={1}&units=metric".format(self.city_code, self.api_key)
##        print "OWM url: " + self.url

        # get date and hour to read API results
        nr_days_forecast = 3

        self.api_dates = []
        for i in range(0, nr_days_forecast):
            self.api_dates.append( self.getDateStr(i) )
        
        self.api_hours = ["06:00", "12:00", "18:00", "21:00"]
        self.api_hours_num = [6,12,18,21]

        self.sampled_days = []

        self.current_weather = None

        self.logfile = "logOWM.txt"
        with Logger(self.logfile) as log:
            log.lprint("--- NEW ---")
        

    def getCurrentData(self):
        #get current weather data
        data_status = None
        # read data as JSON and transform it this way to a dict
        try:
            with Logger(self.logfile) as log:
                log.lprint("fetching data from API... OWM")
            print "fetching data from API... OWM"
##            print "URL - Request",
            req = urllib2.Request(self.current_url)
##            print " - Open",
            response = urllib2.urlopen(req)
##            print " - Read Response"
            output = response.read()
            data = json.loads(output)
            #req = urllib2.urlopen(self.url)
            #data = json.load(req)
            data_status = True
        except urllib2.URLError, e:
            with Logger(self.logfile) as log:
                log.lprint("URLError: " + str(e.reason))
            print "Could not connect to the openweathermap server - sorry, please \
check your internet connection and possible server down times: URLError:" + str(e.reason)
            data_status = False

        if data_status:
            date = self.getDateStr(0)
            time = datetime.datetime.now().strftime('%H:00')
            self.current_weather = dm.WeatherSamplePoint(date, time)
            rain_mm = 0.0
            if 'rain' not in data:
                rain_mm = 0.0
            else:
                if '3h' not in data['rain']:
                    rain_mm = 0.0
                else:
                    rain_mm = float(data['rain']['3h'])/3.0
            self.current_weather.setValues(data['main']['temp'],
                                           data['main']['temp'],
                                           rain_mm,
                                           data['wind']['speed'])
            

    def get_forecast(self, wind_named=False):
        forecast_status = None

        # read data as JSON and transform it this way to a dict
        try:
            with Logger(self.logfile) as log:
                log.lprint("fetching data")
            print "fetching data from API... OWM"
##            print "URL - Request",
            req = urllib2.Request(self.url)
##            print " - Open",
            response = urllib2.urlopen(req)
##            print " - Read Response"
            output = response.read()
            data = json.loads(output)
            #req = urllib2.urlopen(self.url)
            #data = json.load(req)
            forecast_status = True
        except urllib2.URLError, e:
            with Logger(self.logfile) as log:
                log.lprint("URLError: " + str(e.reason))
            print "Could not connect to the openweathermap server - sorry, please \
check your internet connection and possible server down times: URLError:" + str(e.reason)
            forecast_status = False

        # read the forecast basis in the variable
        if forecast_status:
            #print data
            count = data['cnt']
            del self.sampled_days[:]
            for d in self.api_dates:
                wds = dm.WeatherDaySample(d, self.api_hours)
                for h in self.api_hours:
                    wsp = dm.WeatherSamplePoint(d, h)
                    for x in range(count):
                        f = data['list'][x]
                        fstamp = f['dt_txt']
                        fdate = fstamp[0:10]
                        ftime = fstamp[11:16]
                        if fdate == d and ftime == h:
                            # high temp, low temp, rain chance, wind speed
                            rain_mm = 0.0
                            if 'rain' not in f:
                                rain_mm = 0.0
                            else:
                                if '3h' not in f['rain']:
                                    rain_mm = 0.0
                                else:
                                    rain_mm = float(f['rain']['3h']) / 3.0
                            rain = 0
                            if(rain_mm > 0):
                                rain = 1
                            wsp.setValues(f['main']['temp_max'],
                                          f['main']['temp_min'],
                                          rain_mm,
                                          f['wind']['speed'])
                            wds.setValuesDayTimeData(wsp)
                self.sampled_days.append(wds)
            with Logger(self.logfile) as log:
                log.lprint("--- end ---\n")    
        else:
            print "WARNING: could not get forecast!"

