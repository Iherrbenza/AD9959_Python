# DDS AD9959 ESP32 WiFi control

# Author: Ivan Herrera Benzaquen

# Date: 06/07/2020

# Swinburne University of Technology

# This document form part of a system to control a AD9959 (eval_board) with Python and/or Labscript using a ESP32 microcontroller via WiFi. 
# In particula this gives funcionality to the Labscript part

# Bear in mind that this is a project on development, bugs may appear.

from blacs.tab_base_classes import Worker
import socket
import labscript_utils.h5_lock
import h5py
import time


class DDS_ESP32Worker(Worker):

  
    def init(self):
        """
        Initialise the worker
        Checks if the ESP32 is responding correctly
        """
        from .DDS_ESP32 import DDS_ESP32
        self.DDS_AD9959 = DDS_ESP32(self.IP, port=self.port, clock=self.clock, pll=self.pll)
        
        self.ESP32timeout = 3
        self.shot_file = None

        global old_panel_values
        old_panel_values = []
        

    def transition_to_buffered(self, device_name, h5_file, panel_values, refresh):
        """Reading DDS commands in the shot file and send to the ESP32"""
        
        self.DDS_AD9959.initialise_viaSPI(PLL_div=self.pll, send=True) # re-initialise the DDS (cautional)
        time.sleep(0.05)
        
        self.DDS_AD9959.list_reset() # Clear the list and set the variable number or list elements to zero
        time.sleep(0.05)

        self.shot_file  = h5_file
        with h5py.File(self.shot_file, "r") as f:
            group = f[f"devices/{self.device_name}"]

            if "start_commands" in group:
                # print("start")
                dds_commands_list = group["start_commands"][:]
                for command in dds_commands_list:
                    command = command.decode("UTF-8")
                    self.DDS_AD9959.direct_spi(command) 
                    time.sleep(0.01) # cautional                   
            else: dds_commands_list = None
            
            if "memory_commands" in group:
                # print("memory")
                dds_memory_list = group["memory_commands"][:]
                # print(dds_memory_list[-1])
                # set the maximun time allow the ESP32 be in list mode,
                # the stop time from the hdf file is use for this 
                stop_time = int(1E3*f["devices/pulseblaster_0"].attrs["stop_time"])
                self.DDS_AD9959.list_time(stop_time)
                # print(stop_time)
                # set the dimension of the array to going through
                self.DDS_AD9959.list_length(len(dds_memory_list)) 
                
                # storing in the ESP32 memory
                self.DDS_AD9959.memory_storage(list(dds_memory_list))
                time.sleep(0.01) # cautional
                
                self.DDS_AD9959.list_mode()                   
            else: dds_memory_list = None

        return {}

    def transition_to_manual(self):
        time.sleep(0.01) # cautional                   
        self.DDS_AD9959.initialise_viaSPI(PLL_div=self.pll, send=True) # re-initialise the DDS (cautional)

        for i in range(4):

            self.DDS_AD9959.set_amplitude(i, old_panel_values['channel %d'%i]['amp'],send=True)
            print("Ch{} amp updated to {}".format(i, int(old_panel_values['channel %d'%i]['amp'])))

            self.DDS_AD9959.set_frequency(i, 1E6*old_panel_values['channel %d'%i]['freq'],send=True) # hard code to MHz units
            print("Ch{} freq updated to {} MHz".format(i, old_panel_values['channel %d'%i]['freq']))

            self.DDS_AD9959.set_phase(i, old_panel_values['channel %d'%i]['phase'],send=True)
            print("Ch{} phase updated to {} degree".format(i, old_panel_values['channel %d'%i]['phase']))

        return True

    def program_manual(self, panel_values):
        # change values in the front panel
        global old_panel_values
        self.DDS_AD9959.initialise_viaSPI(PLL_div=self.pll, send=True) # re-initialise the DDS (cautional)
        time.sleep(0.05) # cautional

        if not len(old_panel_values) == 0:
            for i in range(4):

                if panel_values['channel %d'%i]['amp'] != old_panel_values['channel %d'%i]['amp']:
                    self.DDS_AD9959.set_amplitude(i, panel_values['channel %d'%i]['amp'],send=True)
                    print("Ch{} amp updated to {}".format(i, int(panel_values['channel %d'%i]['amp'])))

                if panel_values['channel %d'%i]['freq'] != old_panel_values['channel %d'%i]['freq']:
                    self.DDS_AD9959.set_frequency(i, 1E6*panel_values['channel %d'%i]['freq'],send=True) # hard code to MHz units
                    print("Ch{} freq updated to {} MHz".format(i, panel_values['channel %d'%i]['freq']))

                if panel_values['channel %d'%i]['phase'] != old_panel_values['channel %d'%i]['phase']:
                    self.DDS_AD9959.set_phase(i, panel_values['channel %d'%i]['phase'],send=True)
                    print("Ch{} phase updated to {} degree".format(i, panel_values['channel %d'%i]['phase']))
            
        old_panel_values = panel_values # storage the front panel values for an after shot
        return panel_values

    def abort(self):
        print('aborting!')
        # self.scope.write('*RST')
        return True

    def abort_buffered(self):
        print('abort_buffered: ...')
        return self.abort()

    def abort_transition_to_buffered(self):
        print('abort_transition_to_buffered: ...')
        self.shot_file = None
        return self.abort()

    def shutdown(self):
        return True
