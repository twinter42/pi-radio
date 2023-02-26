"""
Class to initialize and control internet radio playback via mpd.
"""

import os
import time
import RPi.GPIO as GPIO
from urllib.request import urlopen
from shiftfuncs import *
from configparser import ConfigParser

# pin constants
ROT_EVENT_SENDER = 3
ROT_EVENT_VOLUME = 27
ROT_DIRECTION_SENDER = 2
ROT_DIRECTION_VOLUME = 17
STATUS_LED = 23
POWER_SWITCH = 22
MAXSENDER = 13


class InternetRadio:
    def __init__(self, config):
        # read last volume and sender settings (e.g. after shutdown)
        self.config = config
        self.parser = ConfigParser()
        self.parser.read(self.config)
        self.sender_idx = int(self.parser.get("safes", "channel"))
        self.volume = int(self.parser.get("safes", "volume"))
        self.__set_pins()
        self.__set_events()
        self.vol_changed = False
        self.sender_changed = False

    def __set_pins(self):
        GPIO.setmode(GPIO.BCM)
        # pin setup for rotary encoders
        for pin in [ROT_DIRECTION_SENDER,
                    ROT_EVENT_SENDER,
                    ROT_DIRECTION_VOLUME,
                    ROT_EVENT_VOLUME]:
            GPIO.setup(pin, GPIO.IN)
        # power switch and status LED
        GPIO.setup(POWER_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(STATUS_LED, GPIO.OUT)

    def __check_internet_connection(self):
        internet_connection = False
        while not internet_connection:
            try:
                response = urlopen('https://www.google.com/', timeout=1)
                internet_connection = True
                print("Internet connection established.")
            except:
                internet_connection = False
                print("No internet connection. Keep searching...")
            time.sleep(0.5)

    def __set_events(self):
        # add events detectors for rotary encoder circuits
        GPIO.add_event_detect(ROT_EVENT_SENDER,
                              GPIO.RISING,
                              callback=self.__sender_callback)
        GPIO.add_event_detect(ROT_EVENT_VOLUME,
                              GPIO.RISING,
                              callback=self.__volume_callback)

    def __standbymode(self):
        GPIO.output(ENABLE_PIN, GPIO.HIGH)

    def __offmode(self):
        # no longer detect rotary encoders
        GPIO.output(ENABLE_PIN, GPIO.HIGH)
        GPIO.remove_event_detect(ROT_EVENT_SENDER)
        GPIO.remove_event_detect(ROT_EVENT_VOLUME)
        # save channel and volume to config file
        self.__save_config()
        # stop radio, wait for wake-up
        os.system("mpc stop")
        time.sleep(0.3)
        while (GPIO.input(POWER_SWITCH) == 1):
            # pulling power switch state
            # NOTE: this is not power efficient at all, should be replaced by wake-up interrupt in the future
            time.sleep(0.05)
        # setup radio again after wake-up
        GPIO.output(STATUS_LED, GPIO.HIGH)
        GPIO.add_event_detect(ROT_EVENT_SENDER, GPIO.RISING,
                              callback=self.__sender_callback)
        GPIO.add_event_detect(ROT_EVENT_VOLUME, GPIO.RISING,
                              callback=self.__volume_callback)
        self.setup()
        GPIO.output(ENABLE_PIN, GPIO.LOW)

    def __sender_callback(self, arg):
        if (GPIO.input(ROT_DIRECTION_SENDER) == 1 and self.sender_idx < MAXSENDER):
            self.sender_idx += 1
        elif (GPIO.input(ROT_DIRECTION_SENDER) == 0 and self.sender_idx > 1):
            self.sender_idx -= 1
        self.sender_changed = True
        shiftch()
        shiftdec(self.sender_idx)

    def __volume_callback(self, arg):
        if (GPIO.input(ROT_DIRECTION_VOLUME) == 1 and self.volume < 91):
            self.volume += 5
        elif (GPIO.input(ROT_DIRECTION_VOLUME) == 0 and self.volume > 0):
            self.volume -= 5
        self.vol_changed = True
        shiftchoff()
        shiftdec(self.volume)

    def __save_config(self):
        self.parser['safes']['volume'] = str(self.volume)
        self.parser['safes']['channel'] = str(self.sender_idx)
        with open(self.config, "w") as configfile:
            self.parser.write(configfile)

    def setup(self):
        # check internet connection, startup radio
        self.__check_internet_connection()
        os.system("mpc clear")
        os.system("mpc load sender")
        os.system(f"mpc volume {self.volume}")
        os.system(f"mpc play {self.sender_idx}")
        # reset timers
        self.standby_timer = time.time()
        self.volmode_timer = time.time()
        # display channel in format "CH XX"
        cleardisp()
        shiftch()
        shiftdec(self.sender_idx)

    def check_power_state(self, current_time):
        if (GPIO.input(POWER_SWITCH) == 0):
            GPIO.output(STATUS_LED, GPIO.HIGH)
        else:
            GPIO.output(STATUS_LED, GPIO.LOW)
            self.__offmode()
        if (current_time - self.standby_timer > 90):
            # go to standby mode after 90 seconds
            self.__standbymode()
        if (current_time - self.volmode_timer > 3):
            # go back to show channel 3 seconds after volume control change
            shiftch()
            shiftdec(self.sender_idx)
            self.volmode_timer = time.time()

    def check_sender_change(self):
        # turn on display, change and show channel, reset standby timer
        if self.sender_changed:
            GPIO.output(ENABLE_PIN, GPIO.LOW)
            os.system(f"mpc play {self.sender_idx}")
            self.sender_changed = False
            self.standby_timer = time.time()

    def check_volume_change(self):
        # turn on display, change and show volume, reset timers
        if self.vol_changed:
            GPIO.output(ENABLE_PIN, GPIO.LOW)
            os.system(f"mpc volume {self.volume}")
            self.vol_changed = False
            self.volmode_timer = time.time()
            self.standby_timer = time.time()

    def final_cleanup(self):
        self.__save_config()
        os.system("mpc stop")
        GPIO.cleanup()
