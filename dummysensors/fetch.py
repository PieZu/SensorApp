from math import sin, cos, tan
from time import time

def ph(x):
    # some random complicated function to give a very rough model of real world data
    return ((abs(cos(x))+1)*(sin(3*x)/2 + sin(5*x - 8*cos(x/20)) + cos(x/5 -3) + 2*sin(x/7))+min(abs(tan(x/17)),10) * (2*cos(x/38))+ sin(x/77) * cos(x/3)- (x %(100 * (min(abs(1/cos(x/2000)), 3)/2+2))))/24+14

def temp(x):
    # some other random function to give a very rough model of real world data
    cos(x/2) + 2*cos(x/5) + sin(x/7) + 3*cos(x/19) + sin(x/37) + cos((x-1)/61) + 4*sin(x/71) + 8*sin(x//331)*cos((x-2)/29) + cos(cos(x))*sin(x/577) + 30 -(x %(100 * (min(abs(1/cos(x/2000)), 3)/2+2)))/20

def getSensorValue(sensorId):
    if sensorId == 1:
        return temp(time())
    if sensorId == 2:
        return ph(time())