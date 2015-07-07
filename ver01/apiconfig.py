#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle

class APIConfig:
    def __init__(self):
        self.project_name = None
        self.api_key = None
        self.city_code = None
        self.city_latitude = None
        self.city_longitude = None

    def setParameter(self, _project_name, _api_key, _city_code):
        self.project_name = _project_name
        self.api_key = _api_key
        self.city_code = _city_code

    def setGPS(self, latitude, longitude):
        self.city_latitude = latitude
        self.city_longitude = longitude

    def loadFromFile(self, file_name):
        f = open(file_name, 'rb')
        c = pickle.load(f)
        f.close()
        self.__dict__.update(c)

    def saveToFile(self, file_name):
        f = open(file_name, 'wb')
        pickle.dump(self.__dict__, f)
        f.close()
