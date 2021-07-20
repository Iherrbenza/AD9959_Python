# @Date:   2020-09-08T18:05:28+10:00
# @Last modified time: 2021-07-15T19:47:28+10:00



# Connection table for example of a labscript sequence for the Quantum Gas Microscope laboratory
# __author__ = "Ivan Herrera Benzaquen"


# DDS AD9959 ESP32 WiFi control

# Author: Ivan Herrera Benzaquen

# Date: 06/07/2020

# Swinburne University of Technology

# This document form part of a system to control a AD9959 (eval_board) with Python and/or Labscript using a ESP32 microcontroller via WiFi. 
# Example of  Labscript script sequence for the Quantum Gas Microscope laboratory

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

# Auxiliary functions
def print_time(t, desc): # time label
    print('t = %9.6f s : ' % t, desc)
t = 0

#definition funtion to store a command in the ESP32_DDS and trigger it
def DDS0memory_amplitude(time, channel, amplitude):
	DDS_command = DDS_0.set_amplitude(channel, amplitude)
	DDS_0.to_memory(DDS_command)
	Fast_Trig.go_high(time)
	Fast_Trig.go_low(time + 2E-6)
	return( 15E-6)

#definition funtion to store a command in the ESP32_DDS and trigger it
def DDS1memory_amplitude(time, channel, amplitude):
	DDS_command = DDS_1.set_amplitude(channel, amplitude)
	DDS_1.to_memory(DDS_command)
	Fast_Trig.go_high(time)
	Fast_Trig.go_low(time + 2E-6)

#-----DDS Aliexpress AD9959 set start commands--------------------------------------------------------------
DDS_command = DDS_0.set_amplitude(0, amplitude_0)
DDS_0.to_start(DDS_command)
DDS_command = DDS_0.set_frequency(0, frequency_0)
DDS_0.to_start(DDS_command)
DDS_command = DDS_0.set_phase(1, phase_0)
DDS_0.to_start(DDS_command)
DDS_command = DDS_0.set_amplitude(1, amplitude_1)
DDS_0.to_start(DDS_command)
DDS_command = DDS_0.set_frequency(1, frequency_1)
DDS_0.to_start(DDS_command)
DDS_command = DDS_0.set_phase(1, phase_1)
DDS_0.to_start(DDS_command)

#-----DDS AD eval AD9959 set start commands--------------------------------------------------------------
DDS_command = DDS_1.set_amplitude(0, 200)
DDS_1.to_start(DDS_command)
DDS_command = DDS_1.set_frequency(0, 25E6)
DDS_1.to_start(DDS_command)
DDS_command = DDS_1.set_phase(1, 0)
DDS_1.to_start(DDS_command)
DDS_command = DDS_1.set_amplitude(1, 500)
DDS_1.to_start(DDS_command)
DDS_command = DDS_1.set_frequency(1, 10E6)
DDS_1.to_start(DDS_command)
DDS_command = DDS_1.set_phase(1, 165)
DDS_1.to_start(DDS_command)



# -------- EXPERIMENTAL SEQUENCE STARTS HERE ----------------------------------------------------------------
print('\n\nCompiling labscript...')
start()
t = 0
Test_DO_0.go_high(t)
Test_DO_1.go_high(t)
Free7.go_high(t)
Fibre_Laser_100W.constant(t, 0)
RF_Switch_Trigger.go_low(t)
Free1.constant(t, 0)
t += 0.1

Test_DO_0.go_low(t)
Fibre_Laser_100W.constant(t, 0)
Analogue0.constant(t, 10)
MOT_AOM_Rep.constant(t, 1)
t += Free1.ramp(t, 0.1, 0, 1, 100e3 )

t += Test_AI_0.acquire(label='Test_AI_0', start_time= t, end_time=t+3)

# send to list memory of DDS_ESP32 1
for i, j in enumerate(np.arange(0,1023,10)):
	# add_time_marker(t, "Toggle DDS %d)"%i, verbose=True)
	DDS1memory_amplitude(t,channel= 0, amplitude= j)
	# Wait more than 20E-6 s between commands (max rate of SPI transmission)
	t += 0.1
t += 1E-3

DDS1memory_amplitude(t,channel= 0, amplitude= 0)
t += 1E-3

# composition of 2 level modulation on channel 0 with 1st freq the former one and set the 2nd
DDS_command = DDS_1.set_2mod_amplitude(ch=0, amp_2nd= 1023)
#its a composition of commands, we need to send one by one
for c in DDS_command:
	DDS_1.to_memory(c)
	Fast_Trig.go_high(t)
	Fast_Trig.go_low(t + 2E-6)
	t += 20E-6 # Wait more than 20E-6 s between commands (max rate of SPI transmission)

t += 100E-6

# toggle P0 to change to the 2nd value
RF_Switch_Trigger.go_high(t)
t += 0.5E-6
RF_Switch_Trigger.go_low(t)

t += 100E-6

DDS1memory_amplitude(t,channel= 0, amplitude= 1023)
t += 1E-3

# set a single memory command
DDS_command = DDS_1.set_frequency(ch=0, freq=10E6)
DDS_1.to_memory(DDS_command)
Fast_Trig.go_high(t)
t += 2E-6
Fast_Trig.go_low(t)
t += 100E-6

n = 5
for i in range(n):
	#Fibre_Laser_100W.constant(t, t)
	if (i % 2) == 0:
		Free7.go_high(t)
	else:
		Free7.go_low(t)
	t += 0.01

t+= 5


print_time(t, 'experiment ends')
stop(t)
