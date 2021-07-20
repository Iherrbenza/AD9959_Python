# DDS AD9959 ESP32 WiFi control

# Author: Ivan Herrera Benzaquen

# Date: 06/07/2020

# Swinburne University of Technology

# This document form part of a system to control a AD9959 (eval_board) with Python and/or Labscript using a ESP32 microcontroller via WiFi. 
# In particula this gives funcionality to the Labscript part

# Bear in mind that this is a project on development, bugs may appear.

from labscript_devices import register_classes

register_classes(
    'DDS_ESP32',
    BLACS_tab='user_devices.DDS_ESP32.blacs_tabs.DDS_ESP32Tab',
    runviewer_parser=None
)
