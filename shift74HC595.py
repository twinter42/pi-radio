import RPi.GPIO as GPIO


class ShiftRegister:
    """
    Simple class for setting outputs of a 74HC595 shift register.
    """

    def __init__(self, data_pin, latch_pin, clock_pin):
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        self.outputs = [0] * 16
        # set as outputs
        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.setup(self.latch_pin, GPIO.OUT)
        GPIO.setup(self.clock_pin, GPIO.OUT)

    def set_output(self, output_number, value):
        try:
            self.outputs[output_number] = value
        except IndexError:
            raise ValueError(
                "Invalid output number. Can be only an int from 0 to 15")
        GPIO.output(self.latch_pin, GPIO.LOW)
        for output in range(15, -1, -1):
            GPIO.output(self.clock_pin, GPIO.LOW)
            value = self.outputs[output]
            GPIO.output(self.data_pin, value)
            GPIO.output(self.clock_pin, GPIO.HIGH)
        GPIO.output(self.latch_pin, GPIO.HIGH)
