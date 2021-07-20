# DDS AD9959 ESP32 WiFi control

# Author: Ivan Herrera Benzaquen

# Date: 06/07/2020

# Swinburne University of Technology

# This document form part of a system to control a AD9959 (eval_board) with Python and/or Labscript using a ESP32 microcontroller via WiFi. 
# In particula this gives funcionality to the Labscript part

# Bear in mind that this is a project on development, bugs may appear.

from blacs.device_base_class import DeviceTab

class DDS_ESP32Tab(DeviceTab):
    
    def initialise_GUI(self):

        self.base_units     = {'freq':'MHz', 'amp':'',   'phase':'Degrees'}
        self.base_min       = {'freq':0,     'amp':0.0,  'phase':0}
        self.base_max       = {'freq':500,   'amp':1023, 'phase':360}
        self.base_step      = {'freq':1,     'amp':1,    'phase':1}
        self.base_decimals  = {'freq':6,     'amp':0,    'phase':3}
        self.num_DDS = 4
        
        dds_chn= {}
        for i in range(self.num_DDS): 
            dds_chn['channel %d'%i] = {}
            for chnl in ['amp','freq', 'phase']:
                dds_chn['channel %d'%i][chnl] = {'base_unit':self.base_units[chnl],
                                                 'min':self.base_min[chnl],
                                                 'max':self.base_max[chnl],
                                                 'step':self.base_step[chnl],
                                                 'decimals':self.base_decimals[chnl]
                                                }          
        self.create_dds_outputs(dds_chn)

        # Create widgets for output/input objects
        dds_widgets,ao_widgets,do_widgets_ = self.auto_create_widgets()

        # auto place the widgets in the UI
        self.auto_place_widgets(("DDS channels", dds_widgets))


    def initialise_workers(self):

        worker_initialisation_kwargs = self.connection_table.find_by_name(self.device_name).properties
        worker_initialisation_kwargs['IP'] = self.BLACS_connection


        self.create_worker(
            'main_worker',
            'user_devices.DDS_ESP32.blacs_workers.DDS_ESP32Worker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'

        self.supports_remote_value_check(False)
        self.supports_smart_programming(False) 
