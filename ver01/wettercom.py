#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import hashlib
import json
import time
import datetime

import datamodel as dm
from apiconfig import APIConfig

class WetterCom:
    def getDateStr(self, delta_days):
        #create time string of the following format: "yyyy-mm-dd"
        today = datetime.date.today()
        target = today + datetime.timedelta(days=delta_days)
        return target.strftime("%Y-%m-%d")
    
    def __init__(self, config):
        # set up API data
        self.project = config.project_name
        self.apikey = config.api_key
        self.city_code = config.city_code

        # create MD5 checksum to verfiy your identity at wetter.com API
        self.checksum = self.project+self.apikey+self.city_code
        self.md5_sum = hashlib.md5(self.checksum).hexdigest()
        self.url = "http://api.wetter.com/forecast/weather/city/{0}/project/{1}\
/cs/{2}/output/json".format(self.city_code, self.project, self.md5_sum)

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
            print "fetching data from API... WetterCom"
            f = urllib2.urlopen(self.url)
            data = json.load(f)
            forecast_status = True
        except:
            print "Could not connect to the wetter.com server - sorry, please \
check your internet connection and possible server down times."
            forecast_status = False

        # read the forecast basis in the variable
        if forecast_status:
            #print data
            del self.sampled_days[:]
            for d in self.api_dates:
                wds = dm.WeatherDaySample(d, self.api_hours)
                for h in self.api_hours:
                    f = data["city"]["forecast"][d][h]
                    wsp = dm.WeatherSamplePoint(d, h)
                    wsp.setValues(f["tx"], f["tn"], f["pc"], f["ws"])
                    wds.setValuesDayTimeData(wsp)
                self.sampled_days.append(wds)
            
        else:
            print "WARNING: could not get forecast!"

