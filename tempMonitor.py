#!/usr/bin/python
#
# tempMonitor.py
#
# Copyright (C) 2018,  Hernan Monserrat hemonserrat<at>gmail<dot>com
# Reference material extracted from:
# https://docs.onion.io/omega2-starter-kit/starter-kit-temp-sensor.html
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #########################################################
# import modules and classes
import time
from temperatureSensor import TemperatureSensor
import oneWire
import datetime
import smtplib

# #########################################################
# setup onewire and polling interval
oneWireGpio = 11 # set the sensor GPIO
pollingInterval = 60 # seconds
infoInterval = 8  # hours
# setup Temp
setPoint = 22  # Celsius

# #########################################################
# e-mail settings - change these values with your provider
sender = 'sender@email'
toaddrs = 'recpient@email'
# Credentials
password = 'xxxxxxxx'
# #########################################################

def sendMail(mesg, severity):
    message = ("From: %s\r\nTo: %s\r\nSubject: Server Room Temp [%s]\r\n\r\n" % (sender, toaddrs, severity) )
    message = message + mesg
    # The actual mail send
    # change here the email smtp server of your provider
    server = smtplib.SMTP_SSL('smtp.gmail.com:465') # smtp server
    server.login(sender,password)
    server.sendmail(sender, toaddrs, message)
    server.quit()


def __main__():
    # check if 1-Wire is setup in the kernel
    if not oneWire.setupOneWire(str(oneWireGpio)):
        print "Kernel module could not be inserted. Please reboot and try again."
        return -1

    # get the address of the temperature sensor
    #   it should be the only device connected in this experiment    
    sensorAddress = oneWire.scanOneAddress()

    # instantiate the temperature sensor object
    sensor = TemperatureSensor("oneWire", { "address": sensorAddress, "gpio": oneWireGpio })
    if not sensor.ready:
        print "Sensor was not set up correctly. Please make sure that your sensor is firmly connected to the GPIO specified above and try again."
        return -1

    # infinite loop - runs main program code continuously
    noalarm = True
    start = datetime.datetime.now()
    while 1:
        # check and print the temperature
        value = sensor.readValue()
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        m = st + " T = " + str(value) + "[C] " +  str(9.0/5.0 * value + 32) + "[F]"
        # Remove the next comment to see the actual value in the console:
        #print m
        # if the temp is greater than 'setpoint' celsius trigger an ALERT email
        if value > setPoint:
              if noalarm:
                sendMail(m, "ALERT")
                noalarm = False
        else:
                noalarm = True
        # send an Info email each 8hs
        elapsed = datetime.datetime.now()
        if (elapsed-start) > datetime.timedelta(0,0,0,0,0,infoInterval,0):
                        sendMail(m, "INFO")
                        start = datetime.datetime.now()        
        time.sleep(pollingInterval)


if __name__ == '__main__':
    __main__()
