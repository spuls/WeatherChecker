#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import datamodel

from logger import Logger

class MeanError:
    def __init__(self):
        self.error_sum = 0.0 #sum of error
        self.nr = 0 #nr of data points
        self.current_mean_error = 0.0 #mean error achieved by error_sum and nr
        self.error_vals_signed = []
        self.current_mean_signed_error = 0.0
        self.current_sdev = 0.0 #standard deviation
        self.name = ''

    def setName(self, n):
        self.name = n

    def addNewError(self, signed_error):
        self.error_sum += math.fabs(signed_error)
        self.nr += 1
        self.current_mean_error = self.error_sum / float(self.nr)
        self.error_vals_signed.append(signed_error)
        for i in range(len(self.error_vals_signed)):
            self.current_mean_signed_error += self.error_vals_signed[i]
        self.current_mean_signed_error = self.current_mean_signed_error / float(self.nr)
        self.computeSDev()

    def computeSDev(self):
        if len(self.error_vals_signed) == 1:
            return
        summe = 0.0
        for i in range(len(self.error_vals_signed)):
            summe = summe + (self.error_vals_signed[i] - self.current_mean_signed_error)**2
        summe = summe * (1.0 / (len(self.error_vals_signed) - 1.0))
        self.current_sdev = math.sqrt(summe)

class ForecastError:
    def __init__(self):
        self.temp_error = MeanError()
        self.rain_error = MeanError()
        self.wind_error = MeanError()

    def compareForecastToCurrent(self, forecast, current):
        if forecast.high_temp is None or forecast.low_temp is None:
            with Logger('logStatmodel.txt') as log:
                log.lprint('### temperature is None! for: ' + self.temp_error.name)
            return
        temp = (forecast.high_temp + forecast.low_temp) / 2.0
        self.temp_error.addNewError(temp - current.high_temp)
        self.rain_error.addNewError(forecast.rain_chance - current.rain_chance)
        self.wind_error.addNewError(forecast.wind_speed - current.wind_speed)

    def setName(self, name):
        self.temp_error.setName(name + '_Temperature')
        self.rain_error.setName(name + '_Rain')
        self.wind_error.setName(name + '_Wind')
