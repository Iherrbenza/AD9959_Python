# AD9959_Python
System to control a [AD9959](https://www.analog.com/en/products/ad9959.html#) (eval_board) with Python and/or [Labscript](https://github.com/labscript-suite) using a ESP32 microcontroller via WiFi.

## Description
The AD9959 is controlled by writing into the registers via SPI protocol.  A [ESP32-DevKitC](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/hw-reference/esp32s2/user-guide-devkitm-1-v1.html) development board programmed in arduino enviroment will do the SPI transfers. The board with WiFi interactivity could be controlled 
with python commands.
As well is integrated into a [Labscript](https://github.com/labscript-suite) enviroment for precise time sequence of commands.

## AD9959
[AD9959](https://www.analog.com/en/products/ad9959.html#) DDS from Analog Devices. 4 channels with modulation and sweep capabilities. 


Bear in mind that this is a project on development, bugs may appear.
