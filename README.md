# AD9959_Python
System to control a [AD9959](https://www.analog.com/en/products/ad9959.html#) (eval_board) with Python and/or [Labscript](https://github.com/labscript-suite) using a ESP32 microcontroller via WiFi.

## Description
The AD9959 is controlled by writing into the registers via SPI protocol. A [ESP32-DevKitC](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/hw-reference/esp32s2/user-guide-devkitm-1-v1.html) development board programmed in arduino enviroment will do the SPI transfers. The board with WiFi interactivity could be controlled 
with python commands.
As well is integrated into a [Labscript](https://github.com/labscript-suite) enviroment for precise time sequence of commands.

## AD9959
[AD9959](https://www.analog.com/en/products/ad9959.html#) DDS from Analog Devices. 4 channels with modulation and sweep capabilities. Can be found in a evaluation board format from Analog Devices or Aliexpress. In case of the Analog devices be sure of set the jumpers on manual mode.

## ESP32-DevKitC 
The system is uses a 38 pin, ESP32-DevKitC Core Board ESP32 to interface the AD9959. The ESP32 can write into the register of the AD9959 directly or memorise a list of commands
and then write when a trigger arrives to an interrup pin. The ESP32 will comunicate with the computer via WiFi in alocal network.

## DDS_ESP32_Arduino
This folder contains the program of the microcontroller written in an Arduino enviroment. Version 1.0.4 from espressif in borad manager was used to develop the program. A the begining of the program the ESP32 will print out via serial MacAddress, and IP/password in case of being connected to the local network, setup a fixed IP for the board to avoid IP hopping.

## DDS_ESP32_Jupyter
Jupyter notebook file with a DDS class and examples to ccontrol the DDS with the ESP32.

## DDS_ESP32_PCB
Gerber files for a PCB that interconnect the ESP32 and and a AD9959 evaluation board. 
Isolators, interrupt_1, filters and pull-down pull-up resistors footprints are placed but can be not used. Isolators can be bypassed (with resistors) and not populated. You will need to use a jumper on R1 to connect the grounds in case no using isolators. And all the 5V power section can be unpopulated as well if you don't use the isolators.
Jumper R16 is necessary if you don't want to control the powerdown (floating is a problem). 

The schematic and the BOOM file with a list of components are included.  

## DDS_ESP32_lab
Files to interface with the Labscript enviroment.

## DDS_ESP32_Test
Images of some test performed with the system.

Bear in mind that this is a project on development, bugs may appear.
