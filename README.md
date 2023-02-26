# pi-radio
Rasperry Pi internet radio using Music Player Daemon (mpd). It was built inside an old multimeter and controls its 4x7 segment display by four shift registers (74HC595), while reading input from two rotary encoders for channel and volume control. Since rotary encoders tend to suffer from contact a noise, a circuit consisting of two NAND gates and a Schmitt trigger was applied ([see here](https://www.bristolwatch.com/ele2/rotary.htm)).

![radio](https://user-images.githubusercontent.com/108329282/221422657-99dcb99a-44f0-45c3-987e-9b2ca93163d4.jpg)
