# pi-radio
Rasperry Pi internet radio using Music Player Daemon (mpd). It was built inside an old multimeter and controls its 4x7 segment display by four shift registers (74HC595), while reading input from two rotary encoders for channel and volume control. Since rotary encoders tend to suffer from contact noise, a circuit consisting of two NAND gates and a Schmitt trigger was applied (found [here](https://www.bristolwatch.com/ele2/rotary.htm)).

![radio](https://user-images.githubusercontent.com/108329282/221422657-99dcb99a-44f0-45c3-987e-9b2ca93163d4.jpg)

## Requirements
```bash
$ sudo apt-get install python-rpi.gpio mpd mpc
```
The script is looking for a playlist at `/var/lib/mpd/playlists/sender.m3u`.

## Auto-start radio after reboot
Start the script `launcher.sh` by making a new cronjob
```bash
$ sudo crontab -e
```
and adding the line
```
@reboot sh /home/pi/pi-radio/launcher.sh >/home/pi/logs/cronlog 2>&1
```
If running the script fails for some reason, look at the log file at `/home/pi/logs/cronlog`.
