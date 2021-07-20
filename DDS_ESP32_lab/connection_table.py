# DDS AD9959 ESP32 WiFi control

# Author: Ivan Herrera Benzaquen

# Date: 06/07/2020

# Swinburne University of Technology

# This document form part of a system to control a AD9959 (eval_board) with Python and/or Labscript using a ESP32 microcontroller via WiFi. 
# Example of  Connection table for labscript sequence for the Quantum Gas Microscope laboratory

# Bear in mind that this is a project on development, bugs may appear.

#---Import of necessary packages---------------------------------------------------------------------------------------------------------
from __future__ import division
from labscript import *
from labscript_devices.PulseBlasterESRPro200 import PulseBlasterESRPro200 as PulseBlaster
from labscript_devices.NI_DAQmx.models import NI_PXIe_6535
from labscript_devices.NI_DAQmx.models import NI_PXIe_6738
from labscript_devices.NI_DAQmx.models import NI_PXIe_6361
from user_devices.DDS_ESP32.labscript_devices import DDS_ESP32

#--Wiring channels names with devices output/input---------------------------------------------------------------------------------------------------------------------------------
# Device definitions
PulseBlaster(name='pulseblaster_0',            board_number=0)
ClockLine(name='ni6738_0_clock',               pseudoclock=pulseblaster_0.pseudoclock, connection='flag 0') # clock for the analog card PXIe-6738
ClockLine(name='ni6535_0_clock',               pseudoclock=pulseblaster_0.pseudoclock, connection='flag 1') # clock for the analog card PXIe-6535
ClockLine(name='ni6361_0_clock',               pseudoclock=pulseblaster_0.pseudoclock, connection='flag 2') # clock for the analog card PXIe-6361
DigitalOut(name='Fast_Trig',                   parent_device=pulseblaster_0.direct_outputs, connection='flag 3')
# PXI Cards definitions
NI_PXIe_6361(name='ni_pxi_6361_0',             parent_device=ni6361_0_clock, MAX_name='PXI1Slot2', clock_terminal='/PXI1Slot2/PFI8', acquisition_rate=1e4)
NI_PXIe_6738(name='ni_pxi_6738_0',             parent_device=ni6738_0_clock, MAX_name='PXI1Slot3', clock_terminal='/PXI1Slot3/PFI0', max_AO_sample_rate=400e3)
NI_PXIe_6535(name='ni_pxi_6535_0',             parent_device=ni6535_0_clock, MAX_name='PXI1Slot4', clock_terminal='/PXI1Slot4/PFI4')
#Channel definitions for NI PXI 6738
AnalogOut(name='Analogue0',                    parent_device=ni_pxi_6738_0, connection='ao0')
AnalogOut(name='MOT_AOM_Rep',                  parent_device=ni_pxi_6738_0, connection='ao1')
AnalogOut(name='Secondary_Coil_Pwave',         parent_device=ni_pxi_6738_0, connection='ao2')
AnalogOut(name='Free1',                        parent_device=ni_pxi_6738_0, connection='ao3')
AnalogOut(name='FB_MOSFET',                    parent_device=ni_pxi_6738_0, connection='ao4')
AnalogOut(name='Feshbach_Coils',               parent_device=ni_pxi_6738_0, connection='ao5')
AnalogOut(name='PID_Set_100W',                 parent_device=ni_pxi_6738_0, connection='ao6')
AnalogOut(name='Fibre_Laser_100W',             parent_device=ni_pxi_6738_0, connection='ao7')
AnalogOut(name='Free2',                        parent_device=ni_pxi_6738_0, connection='ao8')
AnalogOut(name='MOT_FET',                      parent_device=ni_pxi_6738_0, connection='ao9')
AnalogOut(name='MOT_Gradient',                 parent_device=ni_pxi_6738_0, connection='ao10')
AnalogOut(name='MOT_Detuning',                 parent_device=ni_pxi_6738_0, connection='ao11')
AnalogOut(name='Zeeman_Switch',                parent_device=ni_pxi_6738_0, connection='ao12')
AnalogOut(name='PID_Set_10W',                  parent_device=ni_pxi_6738_0, connection='ao13')
AnalogOut(name='PID_Set_2D',                   parent_device=ni_pxi_6738_0, connection='ao14')
AnalogOut(name='Imaging_Beat',                 parent_device=ni_pxi_6738_0, connection='ao15')
AnalogOut(name='Bragg_Pulse_Anlg',             parent_device=ni_pxi_6738_0, connection='ao16')
AnalogOut(name='RF_Modulation',                parent_device=ni_pxi_6738_0, connection='ao17')
AnalogOut(name='RF_List_Trig',                 parent_device=ni_pxi_6738_0, connection='ao18')
AnalogOut(name='Free3',                        parent_device=ni_pxi_6738_0, connection='ao19')
AnalogOut(name='Free4',                        parent_device=ni_pxi_6738_0, connection='ao20')
AnalogOut(name='Free5',                        parent_device=ni_pxi_6738_0, connection='ao21')
AnalogOut(name='Free6',                        parent_device=ni_pxi_6738_0, connection='ao22')
AnalogOut(name='Imaging_Comp_Trig',            parent_device=ni_pxi_6738_0, connection='ao23')
#Channel definitions for NI PXI 6535
DigitalOut(name='Side_Cam_Trig',               parent_device=ni_pxi_6535_0, connection='port0/line0')
DigitalOut(name='Imaging_Shutter',             parent_device=ni_pxi_6535_0, connection='port0/line1')
DigitalOut(name='Flip_Mirror',                 parent_device=ni_pxi_6535_0, connection='port0/line2')
DigitalOut(name='TopCam_Trigger',              parent_device=ni_pxi_6535_0, connection='port0/line3')
DigitalOut(name='RF_Switch_Trigger',           parent_device=ni_pxi_6535_0, connection='port0/line4')
DigitalOut(name='RF_Spin_Mixture',             parent_device=ni_pxi_6535_0, connection='port0/line5')
DigitalOut(name='Bragg_Shutter',               parent_device=ni_pxi_6535_0, connection='port0/line6')
DigitalOut(name='Bragg_Phase_TTL',             parent_device=ni_pxi_6535_0, connection='port0/line7')
DigitalOut(name='PID_Reset_10W',               parent_device=ni_pxi_6535_0, connection='port1/line0')
DigitalOut(name='PID_Reset_2D',                parent_device=ni_pxi_6535_0, connection='port1/line1')
DigitalOut(name='Bragg_PID_Reset',             parent_device=ni_pxi_6535_0, connection='port1/line2')
DigitalOut(name='Imaging_AOM',                 parent_device=ni_pxi_6535_0, connection='port1/line3')
DigitalOut(name='MOT_Cool_Switch',             parent_device=ni_pxi_6535_0, connection='port1/line4')
DigitalOut(name='MOT_Rep_Switch',              parent_device=ni_pxi_6535_0, connection='port1/line5')
DigitalOut(name='MOT_Shutter',                 parent_device=ni_pxi_6535_0, connection='port1/line6')
DigitalOut(name='Zeeman_Shutter',              parent_device=ni_pxi_6535_0, connection='port1/line7')
DigitalOut(name='Free7',                       parent_device=ni_pxi_6535_0, connection='port2/line0')
DigitalOut(name='Free8',                       parent_device=ni_pxi_6535_0, connection='port2/line1')
DigitalOut(name='Free9',                       parent_device=ni_pxi_6535_0, connection='port2/line2')
DigitalOut(name='Free10',                      parent_device=ni_pxi_6535_0, connection='port2/line3')
DigitalOut(name='Free11',                      parent_device=ni_pxi_6535_0, connection='port2/line4')
DigitalOut(name='Free12',                      parent_device=ni_pxi_6535_0, connection='port2/line5')
DigitalOut(name='Free13',                      parent_device=ni_pxi_6535_0, connection='port2/line6')
DigitalOut(name='Imaging_Monitor',             parent_device=ni_pxi_6535_0, connection='port2/line7')
#PXIe-6361 channel definitions:
DigitalOut(name='Test_DO_0',                   parent_device=ni_pxi_6361_0, connection='port0/line0')
DigitalOut(name='Test_DO_1',                   parent_device=ni_pxi_6361_0, connection='port0/line1')
AnalogOut(name='Test_AO_0',                    parent_device=ni_pxi_6361_0, connection='ao0')
AnalogOut(name='Test_AO_1',                    parent_device=ni_pxi_6361_0, connection='ao1')
AnalogIn(name='Test_AI_0',                 parent_device=ni_pxi_6361_0, connection='ai0')
AnalogIn(name='Test_AI_1',                 parent_device=ni_pxi_6361_0, connection='ai1')
# DDS_ESP32
DDS_ESP32(name='DDS_0', IP="192.168.20.103", port=80, clock=25E6, pll=20)#Aliexpress
DDS_ESP32(name='DDS_1', IP="192.168.20.105", port=80, clock=50E6, pll=10)#AD eval board

start()

stop(1)