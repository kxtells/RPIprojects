# Copyright (c) 2013 Jordi Castells j.castells.sala at gmail
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
# Python example for retreiving rain information from weather underground
# and light the leds accordingly.
#


import RPi.GPIO as GPIO
import urllib2
import json
import time
import sys
import logging
import datetime

#CONFIGURATION
#Your Weather Underground API KEY HERE
APIKEY  = ""
PLACE   = "UK/Cambridge"

MINPOP  = 30
LEDPIN  = 7
BUTPIN  = 11

def get_url(url):
    """Return the results from the given url in a python structure.
    It assumes that the url returns a JSON
    """
    f = urllib2.urlopen(url)
    json_string = f.read()
    parsed_json = json.loads(json_string)
    return parsed_json

def url_string(service):
    """Generate a string for a weather underground service"""
    return "http://api.wunderground.com/api/%s/%s/q/%s.json" % (APIKEY, service, PLACE)

def get_today_pop():
    """Get the Probability of Precipitation for the current day, given
    the result set. This is using the "forecast" service
    """
    dataset = get_url(url_string("forecast"))
    return int(dataset['forecast']['txt_forecast']['forecastday'][0]['pop'])

def get_pop_coming_12_hours():
    """Return a list of the pop for the coming 12 hours.
    using the "hourly" service
    """
    dataset = get_url(url_string("hourly"))
    dataset["hourly_forecast"][0]["pop"]
    pops = [int(d["pop"]) for d in dataset["hourly_forecast"]]
    return pops[0:11]

def board_clean_up():
    GPIO.cleanup()

def board_set_up():
    """Set up the Raspberry pins"""
    board_clean_up()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LEDPIN, GPIO.OUT)
    GPIO.setup(BUTPIN, GPIO.IN)
    GPIO.add_event_detect(BUTPIN, GPIO.RISING)

    led_blink() #blink a couple of times indicating the setup

def script_set_up():
    """Set up the script facilities """
    logformat = '%(asctime)s %(message)s'
    logging.basicConfig(format=logformat,level=logging.DEBUG)

def led_on():
    GPIO.output(LEDPIN, GPIO.HIGH)

def led_off():
    GPIO.output(LEDPIN, GPIO.LOW)

def led_blink(timing=0.1):
    """Blink the led 5 times"""
    led_off()
    for x in range(5):
        led_on()
        time.sleep(timing)
        led_off()
        time.sleep(timing)

def exit_handler():
    """When exiting:
        Log the exit.
        Leave the Raspberry PI in a good state
   """
    logging.info("Exiting. Clean up the board settings")
    board_clean_up()
    sys.exit(0)

def update_weather_and_led():
    """Gets the last pop value from weather underground. With that value
    light the led or not, according to the value MINPOP
    """
    logging.info("Retreiving weather information")
    pop = max(get_pop_coming_12_hours())

    if pop > MINPOP:
        led_on()
    else:
        led_off()

    logging.info("Pop: %s MinPop: %s",pop,MINPOP)

def main():
    script_set_up()
    board_set_up()
    update = True
    now = datetime.datetime.now()
    chour = now.hour

    while True:
        # Update handling
        if update:
            update_weather_and_led()
            update = False

        # Button Pressed handler
        if GPIO.event_detected(BUTPIN):
            led_blink()
            update = True

        now = datetime.datetime.now()
        if now.hour != chour:
            update = True
            chour  = now.hour

        # Wait for next loop
        time.sleep(0.5)

if __name__=="__main__":
    try:
        main()
    except:
        exit_handler()

