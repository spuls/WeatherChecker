#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import string
from datetime import datetime

from consts import *


class Logger:
    def __init__(self, filename):
        self.name = filename
        self.log = open(file_path + self.name, 'a')

    def getTimeStr(self):
        return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def lprint(self, line):
        print >> self.log, ">" + self.getTimeStr() + ": " + line

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.log.close()
