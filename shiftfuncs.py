"""
Some helper functions to set the output of an old multimeter 4x7 segment display.
"""

from shift74HC595 import ShiftRegister
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# enable display pin
ENABLE_PIN = 6
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.output(ENABLE_PIN, GPIO.LOW)

# first shift register's pins
CLOCK_PIN = 21
DATA_PIN = 20
LATCH_PIN = 16

# second shift register's pins
CLOCK_PIN2 = 26
DATA_PIN2 = 19
LATCH_PIN2 = 13

reg1 = ShiftRegister(DATA_PIN, LATCH_PIN, CLOCK_PIN)
reg2 = ShiftRegister(DATA_PIN2, LATCH_PIN2, CLOCK_PIN2)
reg1.set_output(15, GPIO.HIGH)

# NOTE: each segment of the 7 digits display has its own pin connected to an shift register output
# List of pin numbers for 0-9 for least significant digit
numberslist1 = [[1, 3, 4, 5, 6, 7], [5, 6], [1, 2, 4, 5, 7], [2, 4, 5, 6, 7], [2, 3, 5, 6], [
    2, 3, 4, 6, 7], [1, 2, 3, 4, 6, 7], [4, 5, 6], [1, 2, 3, 4, 5, 6, 7], [2, 3, 4, 5, 6, 7]]
# List of pin numbers for 0-9 for msot significant digit
numberslist10 = [[0, 11, 12, 13, 14, 15], [14, 15], [0, 10, 11, 13, 14], [0, 10, 13, 14, 15], [10, 12, 14, 15], [
    0, 10, 12, 13, 15], [0, 10, 11, 12, 13, 15], [13, 14, 15], [0, 10, 11, 12, 13, 14, 15], [0, 10, 12, 13, 14, 15]]
# list of output pins to display "CH" in front of channel number
chlist = [0, 3, 4, 5, 10, 11, 12, 13, 14]


def cleardisp():
    # set all shift registers outputs low
    for pin in range(0, 16):
        reg1.set_output(pin, GPIO.LOW)
        reg2.set_output(pin, GPIO.LOW)


def shiftdec(x: int):
    # display channel number with leading zero
    for num in range(0, 8):
        if num in numberslist1[x % 10]:
            reg1.set_output(num, GPIO.HIGH)
        else:
            reg1.set_output(num, GPIO.LOW)
    for num in [0, 10, 11, 12, 13, 14, 15]:
        if num in numberslist10[x // 10 % 10]:
            reg1.set_output(num, GPIO.HIGH)
        else:
            reg1.set_output(num, GPIO.LOW)


def shiftch():
    # display "CH" in front of the channel number
    for num in range(15):
        if num in chlist:
            reg2.set_output(num, GPIO.HIGH)
        else:
            reg2.set_output(num, GPIO.LOW)


def shiftchoff():
    # clear "CH" in front of the channel number
    for num in range(15):
        if num in chlist:
            reg2.set_output(num, GPIO.LOW)
        else:
            reg2.set_output(num, GPIO.LOW)
