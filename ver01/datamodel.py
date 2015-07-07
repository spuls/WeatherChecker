#!/usr/bin/python
# -*- coding: utf-8 -*-

from logger import Logger

class WeatherSamplePoint:
    def __init__(self, d, t):
        self.date = d
        self.time = t
        self.high_temp = None
        self.low_temp = None
        self.rain_chance = None
        self.wind_speed = None

    def setValues(self, _high_temp, _low_temp, _rain_chance, _wind_speed):
        with Logger('logWeatherSamplePoint.txt') as log:
            log.lprint("setValues: " + str(_high_temp) + "," + str(_low_temp) + "," + str(int(_rain_chance)) + "," + str(_wind_speed))
        self.high_temp = int(_high_temp)
        self.low_temp = int(_low_temp)
        self.rain_chance = int(_rain_chance)
        self.wind_speed = int(_wind_speed)

    def setDateTime(self, _date, _time):
        self.date = _date
        self.time = _time

    def copyData(self, other):
        with Logger('logWeatherSamplePoint.txt') as log:
            log.lprint("copyData: " + str(other.high_temp) + "," + str(other.low_temp) + "," + str(other.rain_chance) + "," + str(other.wind_speed))
        self.high_temp = other.high_temp
        self.low_temp = other.low_temp
        self.rain_chance = other.rain_chance
        self.wind_speed = other.wind_speed

    def copyAll(self, other):
        self.copyData(other)
        self.date = other.date
        self.time = other.time

class WeatherDaySample:
    def __init__(self, _date, _times):
        self.date = _date
        self.times = _times
        self.sample_points = []

        for t in self.times:
            wsp = WeatherSamplePoint(self.date, t)
            self.sample_points.append(wsp)

    def setValuesDayData(self, samples):
        if len(samples) != len(self.sample_points):
            print "ERROR: Sample Size doesnt match!"
        for i in range(len(samples)):
            self.sample_points[i].copyData(samples[i])

    def setValuesDayAll(self, samples):
        if len(samples) != len(self.sample_points):
            print "ERROR: Sample Size doesnt match!"
        for i in range(len(samples)):
            self.sample_points[i].copyAll(samples[i])

    def setValuesDayTimeData(self, sample):
        for i in range(len(self.sample_points)):
            if sample.time == self.sample_points[i].time:
                self.sample_points[i].copyData(sample)
                return
