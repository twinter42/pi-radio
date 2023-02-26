import time
from radio import InternetRadio

CONFIG_DIR = "/home/pi/pi-radio/radio_config.ini"
radio = InternetRadio(config=CONFIG_DIR)

try:
    radio.setup()
    while (True):
        # pull the radio's state and act on input events
        current_time = time.time()
        radio.check_power_state(current_time)
        radio.check_sender_change()
        radio.check_volume_change()

except KeyboardInterrupt:
    # for debugging purposes
    radio.final_cleanup()

except Exception as e:
    print(f"Unexpected error: {e}. Shutting down radio.")
    radio.final_cleanup()
