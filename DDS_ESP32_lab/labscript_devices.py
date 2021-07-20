# DDS AD9959 ESP32 WiFi control

# Author: Ivan Herrera Benzaquen

# Date: 06/07/2020

# Swinburne University of Technology

# This document form part of a system to control a AD9959 (eval_board) with Python and/or Labscript using a ESP32 microcontroller via WiFi. 
# In particula this gives funcionality to the Labscript part

# Bear in mind that this is a project on development, bugs may appear.


import h5py
import numpy as np
from labscript import Device, LabscriptError, set_passed_properties
import socket

class DDS_ESP32(Device):
    """A labscript_device for controlling a DDS using a WiFi ESP32 uC intermediate device.
            
        Connection_table_properties:
            com_port: tupple (HOST, PORT), IP and port of the ESP32
            clock:  (clock input frequency)
            pll:  multiplier of the clock input frequency
    """
    description = 'AD9959_DDS via ESP32 WiFi communication'

    @set_passed_properties(
        property_names = {
            'connection_table_properties': ['IP', 'port', 'clock', 'pll']})

    def __init__(self, name, IP="192.168.20.103", port=80, clock=50E6, pll=10, **kwargs):

        Device.__init__(self, name, None, IP, **kwargs)
        self.name = name
        self.BLACS_connection = IP
        self.port = port
        self.clock = clock
        self.pll = pll
        self.start_commands = []
        self.memory_commands = []
        self.ESP32timeout = 5000

    global AFP_select
    AFP_select = 0b00
           
    # Communications functions with the ESP32: 
    
    def transfer_ESP32(self, out):
        """Transfer the data to the ESP32 via socket"""
        if len(out) > 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1000)
                s.connect((str(self.IP),int(self.port)))
                s.send(bytes(out,"utf-8"))
        else:
            print("empty data input")
        #print(out)
            
    def initialise(self):
        """initilise the DDS with the default values stored in the ESP32 non-volatile memory"""
        self.transfer_ESP32("i")
        
    def check(self):
        """check if the DDS its online """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.ESP32timeout)
                s.connect((str(self.IP),int(self.port)))
                s.send(bytes("?","utf-8"))
                msg = s.recv(1024)
                msg = msg.decode("utf-8")
                if (msg != "O"):
                    raise socket.error("Device not responding correctly")
                if (msg == "O"):
                    print("Device responding correctly")
        except (TimeoutError, socket.timeout, socket.error):
            print("Device not responding, check WiFi connections")
            time.sleep(0.5)
        
    def reset(self):
        """pulse the reset pin of the DDS, this completly reset DDS to default values"""
        self.transfer_ESP32("r") 
        
    def syncronise(self):
        """re-syncronise communications by pulsing the sync pin"""
        self.transfer_ESP32("c")  

    def update(self):
        """update the register by pulsing the IO_update pin"""
        self.transfer_ESP32(self, "u")  
        
    def direct_spi(self, spi_data):
        """ send data to the ESP32 that will be imediatly transmited to the DDS via SPi
            64bit MAX length.
        """
        if type(spi_data) is str and spi_data[1]=="x" : # command must be a hexadecimal string
            out = "d{}\n".format(spi_data)
        else:
            out = ""
        self.transfer_ESP32(out)
    
    def list_length(self, list_length):
        """sets the length of the list to go through"""
        if list_length <+ 10000:
            out = "n{}\n".format(int(list_length))
            self.transfer_ESP32(out)
        else:
            print("list lenght has to be less or equal to 1000")
            
    def list_maxtime(self, list_maxtime):
        """sets the maximun time the ucontroller will be in list mode, in milisenconds"""
        if (type(list_length) == type(120000)) and (list_length > 0) :
            out = "t{}\n".format(int(list_maxtime))
            self.transfer_ESP32(out)
        else:
            print("max time must be an integer larger than zero")
            
    def memory_storage(self, list_spic):     
        """ storing a list of spi commands in to the memory of the ESP332 """
        if all([type(i) is str for i in list_spic]) and all([i[1]=="x" for i in list_spic]) : # all command must be a hexadecimal string
            list = [str(i)+"n"+j +"w" for i,j in enumerate(list_spic)]
            list = "".join(list)
            out = "m" + list + "\n"
        else:
            print("input list in the wrong format, each command must be a hexadeciaml string")
            out = ""
        self.transfer_ESP32(out)
        time.sleep(0.05)
                    
    def list_reset(self):
        """ clear the list and set the variable number or list elements to zero
        """
        self.transfer_ESP32("k")
            
    def list_mode(self):
        """ sets the ESP32 in list mode, listen to the io_update pin to iterate througth the list.
        """
        self.transfer_ESP32("l")
    
    # AD9959 register functions
    
    def CSR_register(self, ch_0=0b0, ch_1=0b0, ch_2=0b0, ch_3=0b0):
        """Return a number to write into the Channel Select Register (CSR) register.
        The CSR determines if channels are enabled or disabled by the status of the four channel enable bits. 
        All four channels are enabled by their default state. The CSR also determines 
        which serial mode of operation is selected. In addition, the CSR offers a choice of MSB first
        or LSB first format."""
        
        CSR = 0x20<< 8 # Channel Select Register (CSR)—Address 0x00. 
                       # The ESP32 will be transfer as 0x00, 0x20 its to flag it. 

        """Bits are active immediately after being written. They do not require an I/O update to take effect.
        There are four sets of channel registers and profile (channel word) registers, one per channel. This
        is not shown in the channel register map or the profile register map. The addresses of all channel
        registers and profile registers are the same for each channel. Therefore, the channel enable bits
        distinguish the channel registers and profile registers values of each channel. For example,
        1001 = only Channel 3 and Channel 0 receive commands from the channel registers and profile
        registers.
        0010 = only Channel 1 receives commands from the channel registers and profile registers.
        """
        ch_3 = ( ch_3 & 0b1 ) << 7
        ch_2 = ( ch_2 & 0b1 ) << 6
        ch_1 = ( ch_1 & 0b1 ) << 5 
        ch_0 = ( ch_0 & 0b1 ) << 4
        Open = 0b0 << 3 # must be 0
        # Modes of communications with the DDS, for the momment only the 1st one is possible at the moment.
        singlebit_2wire = 0b00 << 1
        singlebit_3wire = 0b01 << 1
        Serial_2bit = 0b10 << 1
        Serial_3bit = 0b11 << 1
        # Order of communications with the DDS, the ESP32 is transmiting in default.
        MSB = 0b0 # default, most significant bit protocol
        LSB = 0b1
        
        # composition of the command.
        out_CSR = CSR | ch_3 | ch_2 | ch_1 | ch_0 | Open |singlebit_2wire | MSB   
        return(out_CSR)

    def FR1_register(self, PLL_div, Mod_level=0b00):
        """Return a number to write into the Function Register 1 (FR1) register.
        Three bytes are assigned to this register. FR1 is used to control the mode of operation of the chip.
        
        """
        
        FR1 = 0x01 << 24                     # Function Register 1 (FR1)—Address 0x01
        VCO_gain = 0b1 << 23                 # 0 = the low range (system clock below 160 MHz) (default).
                                             # 1 = the high range (system clock above 255 MHz).
        PLL_div = PLL_div << 18              # If the value is 4 or 20 (decimal) or between 4 and 20, the PLL is enabled and the value sets the
                                             # multiplication factor. If the value is outside of 4 and 20 (decimal), the PLL is disabled.
        Pump_75uA  = 0b00 << 16              # 00 (default) = the charge pump current is 75 μA
        Pump_100uA = 0b01 << 16              # 01 (default) = the charge pump current is 100 μA
        Pump_125uA = 0b10 << 16              # 10 (default) = the charge pump current is 125 μA
        Pump_150uA = 0b11 << 16              # 11 (default) = the charge pump current is 150 μA
        Open1 = 0b0 << 15                    # open
        PPC_conf = 0b000  << 12              # The profile pin configuration bits control the configuration of the data and SDIO_x pins for the
                                             # different modulation modes. 
        RU_RD = 0b00 << 10                   # The RU/RD bits control the amplitude ramp-up/ramp-down time of a channel.
        Mod_level = (Mod_level & 0b00) << 8  # 00 = 2-level modulation
                                             # 01 = 4-level modulation
                                             # 10 = 8-level modulation
                                             # 11 = 16-level modulation
        Ref_clock = 0b0 << 7                 # 0 = the clock input circuitry is enabled for operation (default).
                                             # 1 = the clock input circuitry is disabled and is in a low power dissipation state. 
        Pow_mode = 0b0 << 6                  # 0 = the external power-down mode is in fast recovery power-down mode (default). In this mode,
                                             # when the PWR_DWN_CTL input pin is high, the digital logic and the DAC digital logic are 
                                             # powered down. The DAC bias circuitry, PLL, oscillator, and clock input circuitry are not powered down.
                                             # 1 = the external power-down mode is in full power-down mode. In this mode, when the
                                             # PWR_DWN_CTL input pin is high, all functions are powered down. This includes the DAC and PLL,
                                             # which take a significant amount of time to power up
        Sync_clock = 0b0 << 5                # 0 = the SYNC_CLK pin is active (default).
                                             # 1 = the SYNC_CLK pin assumes a static Logic 0 state (disabled). In this state, the pin drive logic is
                                             # shut down. However, the synchronization circuitry remains active internally to maintain normal
                                             # device operation.
        DAC_ref = 0b0 << 4                   # 0 = DAC reference is enabled (default).
                                             # 1 = DAC reference is powered down  
        Open2 = 0b00 << 2                    # open   
        Man_hard_sync =  0b0 << 1            # 0 = the manual hardware synchronization feature of multiple devices is inactive (default).
                                             # 1 = the manual hardware synchronization feature of multiple devices is active
        Man_soft_sync = 0b0                  # 0 = the manual software synchronization feature of multiple devices is inactive (default).
                                             # 1 = the manual software synchronization feature of multiple devices is active
            
        # composition of the command.
        out_FR1 = (FR1 | VCO_gain | PLL_div | Pump_150uA | Open1 | PPC_conf | Mod_level | Ref_clock | Pow_mode | Sync_clock 
                   | DAC_ref | Open2 | Man_hard_sync | Man_soft_sync )
        return(out_FR1)

    def FR2_register(self):
        """Return a number to write into the Function Register 2 (FR2) register.
        Two bytes are assigned to this register. The FR2 is used to control the various functions, features, and modes of the AD9959"""
        
        FR2 = 0x02 << 16                 # Function Register 2 (FR2)—Address 0x02
        Autoclear_sweep = 0b0 << 15      # 0 = a new delta word is applied to the input, as in normal operation, but not loaded into the accumulator (default).
                                         # 1 = this bit automatically and synchronously clears (loads 0s into) the sweep accumulator for one-
                                         # -cycle upon reception of the I/O_UPDATE sequence indicator on all four channels.
        Clear_sweep = 0b0 << 14          # 0 = the sweep accumulator functions as normal (default)
                                         # 1 = the sweep accumulator memory elements for all four channels are asynchronously cleared
        Autoclear_phase = 0b0 << 13      # 0 = a new frequency tuning word is applied to the inputs of the phase accumulator, but not loaded into the accumulator (default).
                                         # 1 = this bit automatically and synchronously clears (loads 0s into) the phase accumulator for one
                                         # cycle upon receipt of the I/O update sequence indicator on all four channels
        Clear_phase = 0b0 << 12          # 0 = the phase accumulator functions as normal (default).
                                         # 1 = the phase accumulator memory elements for all four channels are asynchronously cleared.
        Open = 0b00 << 8
        Auto_sync_enable = 0b0 << 7
        Sync_master_enable = 0b0 << 6    
        Sync_status = 0b0 << 5
        Sync_mask = 0b0 << 4
        Open = 0b00 << 2
        Clock_off = 0b0

        # composition of the command.
        out_FR2 = (FR2 | Autoclear_sweep | Clear_sweep | Autoclear_phase | Clear_phase | Open | Auto_sync_enable 
                   | Sync_master_enable | Sync_status | Sync_mask | Open | Clock_off)
        return(out_FR2)

    def CFR_register(self, AFP_select=0b00, Sweep_nodwell=0b0, Sweep_enable=0b0, SRR_IOupdate=0b0):
        """Return a number to write into the Channel Function Register (CFR) register.
        Three bytes are assigned to this register, 
        AFP_select:  Afects mod type of EACH channel.
        # 00 modulation disable
        # 01 Amplitude modulation
        # 10 Frequency modulation
        # 11 Phase modulation
        Sweep_nodwell:  Afects different setting of EACH channel. 
        # 0 = the linear sweep no-dwell function is inactive (default)
        # 1 = the linear sweep no-dwell function is active. If CFR[15] is active, the linear sweep no-dwell function is activated. 
            See the Linear Sweep Mode section for details. If CFR[14] is clear, this bit is don’t care.
        Sweep_enable:  Afects different setting of EACH channel. 
        # 0 = the linear sweep capability is inactive (default).
        # 1 = the linear sweep capability is enabled. When enabled, the delta frequency tuning word is applied to 
            the frequency accumulator at the programmed ramp rate.
        SRR_IOupdate:  Afects different setting of EACH channel. 
        # 0 = the linear sweep ramp rate timer is loaded only upon timeout (timer = 1)
        # 1= the linear sweep ramp rate timer is loaded upon timeout (timer = 1) or at the time of an I/O_UPDATE.
        Setting the Slope of the Linear Sweep
        The slope of the linear sweep is set by the intermediate step size
        (delta-tuning word) between S0 (memory 0 or actual value) and E0 (memory 1 see CW_register) and the time spent
        (sweep ramp rate word) at each step. The resolution of the
        delta-tuning word is 32 bits for frequency, 14 bits for phase, and
        10 bits for amplitude. The resolution for the delta ramp rate
        word is eight bits

        """
        
        CFR = 0x03 << 24                          # Channel Function Register (CFR)—Address 0x03
        AFP_select = (AFP_select & 0b11) << 22    # Controls what type of modulation is to be performed for that channel. See the Modulation Mode section for details
                                                  # 00 modulation disable
                                                  # 01 Amplitude modulation
                                                  # 10 Frequency modulation
                                                  # 11 Phase modulation
        Open1 = 0b000000 << 16                    # open
        Sweep_nodwell  = Sweep_nodwell << 15      # 0 = the linear sweep no-dwell function is inactive (default)
                                                  # 1 = the linear sweep no-dwell function is active. If CFR[15] is active, the linear sweep no-dwell function is-
                                                  # -activated. See the Linear Sweep Mode section for details. If CFR[14] is clear, this bit is don’t care.
        Sweep_enable = (Sweep_enable & 0b1) << 14 # 0 = the linear sweep capability is inactive (default).
                                                  # 1 = the linear sweep capability is enabled. When enabled, the delta frequency tuning word is applied to-
                                                  # -the frequency accumulator at the programmed ramp rate.
        SRR_IOupdate = SRR_IOupdate << 13         # 0 = the linear sweep ramp rate timer is loaded only upon timeout (timer = 1)
                                                  # 1 = the linear sweep ramp rate timer is loaded upon timeout (timer = 1) or at the time of an I/O_UPDATE-
                                                  # -input signal.
        Open2 = 0b00 << 11                        # open
        Open3 = 0b00 << 10                        # must be zero
        DACfull_scale = 0b11 << 8                 # 11 = the DAC is at the largest LSB value (default).
        Power_Down = 0b0 << 7                     # 0 = the digital core is enabled for operation (default).
                                                  # 1 = the digital core is disabled and is in its lowest power dissipation state.
        DACPower_Down = 0b0 << 6                  # 0 = the DAC is enabled for operation (default).
                                                  # 1 = the DAC is disabled and is in its lowest power dissipation state.
        Pipe_delay = 0b0 << 5                     # 0 = matched pipe delay mode is inactive (default).
                                                  # 1 = matched pipe delay mode is active.
        Autoclear_sweep = 0b0 << 4                # 0 = the current state of the sweep accumulator is not impacted by receipt of an I/O_UPDATE signal default).
                                                  # 1 = the sweep accumulator is cleared for one cycle upon receipt of an I/O_UPDATE signal.
        Clear_sweep = 0b0 << 3                    # 0 = the sweep accumulator functions as normal (default).
                                                  # 1 = the sweep accumulator memory elements are asynchronously cleared.
        Autoclear_phase = 0b0 << 2                # 0 = the current state of the phase accumulator is not impacted by receipt of an I/O_UPDATE signal (default).
                                                  # 1 = the phase accumulator is cleared for one cycle upon receipt of an I/O_UPDATE signal.
        Clear_phase = 0b0 << 1                    # 0 = the phase accumulator functions as normal (default).
                                                  # 1 = the phase accumulator memory elements are asynchronously cleared.
        Sin_wave = 0b0                            # 0 = the angle-to-amplitude conversion logic employs a cosine function (default).
                                                  # 1 = the angle-to-amplitude conversion logic employs a sine function.

        # composition of the command.
        out_CFR = ( CFR | AFP_select | Open1 | Sweep_nodwell | Sweep_enable | SRR_IOupdate | Open2 | Open3 | DACfull_scale | Power_Down | DACPower_Down 
                   | Pipe_delay | Autoclear_sweep | Clear_sweep | Autoclear_phase | Clear_phase | Sin_wave )
        return(out_CFR)


    def CFTW_register(self, frequency):
        """Return a number to write into the Channel Frequency Tuning Word (CFTW0) register.
        Four bytes are assigned to this register, the frequency word its calculated in function of
        the core clock frequency, reciprocal, PLL multiplier times input clock frequency.
        frequency: frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        """

        CFTW = 0x04 << 32                                   # Channel Frequency Tuning Word 0 (CFTW0)—Address 0x04
        core_clock = self.pll*self.clock
        CFTW_value = (0xFFFFFFFF+1)*frequency/(core_clock)  # calculation of the reciprocal frequency
        CFTW_value = int(CFTW_value) & 0xFFFFFFFF           # the input frequency must be a 32 bit word

        # composition of the command.
        out_CFRW = CFTW | CFTW_value
        return(out_CFRW)
    
    def CPOW_register(self, phase):
        """Return a number to write into the Channel Phase Offset Word (CFTW0) register.
        Two bytes are assigned to this register.
        phase: phase in degree, max=360, min = (360)/ (2^14)
        """

        CPOW = 0x05 << 16                        # Channel Phase Tuning Word 0 (CPOW0)—Address 0x05
        Open = 0b00 << 14                        # open
        CPOW_value = (0x3FFF+1)*phase/(360)      # calculation of the reciprocal phase
        CPOW_value = int(CPOW_value) & 0x3FFF    # phase offset word for each channel

        # composition of the command.
        out_CPOW = CPOW | Open | CPOW_value
        return(out_CPOW)

    def ACR_register(self, Mul_enable=0b1, amplitude=0):
        """Return a number to write into the Amplitude Control Register (ACR) register.
        Three bytes are assigned to this register.
        amplitude: amplitude of the output wave, max 1023, 10bit word
        """

        ACR = 0x06 << 24                          # Amplitude Control Register (ACR)—Address0x06
        ARR = 0x00 << 15                          # Amplitude ramp rate value.
        Rstep_size = 0b00 << 14                   # Amplitude increment/decrement step size.
        Open = 0b0 << 13                          # Open
        Mul_enable = int(Mul_enable) << 12        # 0 = amplitude multiplier is disabled. The clocks to this scaling function (auto RU/RD) are stoppe
                                                  # for power saving, and the data from the DDS core is routed around the multipliers (default)
        Ramp_enable = 0b0 << 11                   # This bit is valid only when ACR[12] is active high.
                                                  # 0 = when ACR[12] is active, Logic 0 on ACR[11] enables the manual RU/RD operation. See the
                                                  # Output Amplitude Control Mode section for details (default).
                                                  # 1 = if ACR[12] is active, a Logic 1 on ACR[11] enables the auto RU/RD operation. 
        ARR_atIOupdate = 0b0 << 10                # 0 = the amplitude ramp rate timer is loaded only upon timeout (timer = 1) and is not loaded due
                                                  # to an I/O_UPDATE input signal (default).
                                                  # 1 = the amplitude ramp rate timer is loaded upon timeout (timer = 1) or at the time of an
                                                  # I/O_UPDATE input signal.
        amplitude = int(amplitude) & 0x3FF 

        # composition of the command.
        out_ACR = ACR | ARR | Rstep_size | Open | Mul_enable | Ramp_enable | ARR_atIOupdate | amplitude  
        return(out_ACR)

    
    def LSRR_register(self, FallingRR, RisingRR):
        """Return a number to write into the Linear Sweep Ramp Rate (LSRR) register.
        Sets the rate of the slope, falling or rising side.
        FallingRR: the step size in time of the falling linear sweep in seconds. (max:2.048E-6 s min:8.0E-9 s)
        RisingRR: the step size in time of the rising linear sweep in seconds. (max:2.048E-6 s min:8.0E-9 s)
        Two bytes are assigned to this register.
        """

        LSRR = 0x07 << 16                                  # LinearSweep Ramp rate (LSRR)—Address 0x07
        SYNC_CLK = self.pll*self.clock/4                   # calculation of the Sync clock
        if(FallingRR > 0xFF/SYNC_CLK): 
            print("max time interval 2.048 microseconds")
            FallingRR = 0xFF/SYNC_CLK
        if(FallingRR < 1/SYNC_CLK): 
            print("min time interval 8.0 nanoseconds")
            FallingRR = 1/SYNC_CLK
        FRR = FallingRR*SYNC_CLK                           # calculation of the delta time of the falling linear sweep
        FRR = (int(FRR) << 8)                              # delta time of the falling linear sweep for each channel
        if(RisingRR > 0xFF/SYNC_CLK): 
            print("max time interval 2.048 microseconds")
            RisingRR = 0xFF/SYNC_CLK
        if(RisingRR < 1/SYNC_CLK): 
            print("min time interval 8.0 nanoseconds")
            RisingRR = SYNC_CLK
        RRR = RisingRR*SYNC_CLK                            # calculation of the delta time of the rising linear sweepe
        RRR = int(RRR)                                     # delta time of the rising linear sweep for each channel

        # composition of the command.
        out_LSRR = LSRR | FRR | RRR
        return(out_LSRR)
    
    def RDW_register(self, RisingDelta):
        """Return a number to write into the LSR Rising Delta Word (RDW) register.
        Sets the step of the raising slope
        RaisingDelta: the step size during the raising linear sweep. Units depends of modulation type selected (AFP_select)
        Four bytes are assigned to this register.
        RisindDelta:
        AFP_select = 0b01: frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        AFP_select = 0b10: amplitude:  max 1023, 10bit word
        AFP_select = 0b11: phase: phase in degree, max=360, min = (360)/ (2^14)
        """
        global AFP_select

        RDW = 0x08 << 32                                 # Rising Delta Word (RDW)—Address 0x08
        core_clock = self.pll*self.clock                 # calculation of the core clock
        if(AFP_select == 0b00):                          # no modulation selected
            print("no modulation selected ")
            RDW_value = 0
        if(AFP_select == 0b01):                          # amplitude modulation selected
            if(RisingDelta > 0x3FF): 
                print("amplitud modulation selected, max 1024")
                RisingDelta = 0x3FF
            RDW_value= (int(RisingDelta) & 0x3FF ) << 22
        if(AFP_select == 0b10):                          # frequency modulation selected
            if(RisingDelta > core_clock): 
                print("frequency modulation selected, max %s MHz"%(core_clock)*1E-6)
                RisingDelta = core_clock
            RDW_value = (0xFFFFFFFF+1)*RisingDelta/(core_clock) # calculation of the delta frequency word for the rising linear sweep
            RDW_value = int(RDW_value) & 0xFFFFFFFF
        if(AFP_select == 0b11):                          # phase modulation selected
            RDW_value = (0x3FFF+1)*RisingDelta/(360)     # calculation of the reciprocal phase
            RDW_value = (int(RDW_value) & 0x3FFF) << 18  # phase offset word for each channel
        # composition of the command.
        out_RDW = RDW | RDW_value

        return(out_RDW)
    
    def FDW_register(self, FallingDelta):
        """Return a number to write into the LSR Rising Delta Word (FDW) register.
        Sets the step of the falling slope
        FallingDelta: the step size during the falling linear sweep. Units depends of modulation type selected (AFP_select)
        Four bytes are assigned to this register.
        FallingDelta:
        AFP_select = 0b01: frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        AFP_select = 0b10: amplitude:  max 1023, 10bit word
        AFP_select = 0b11: phase: phase in degree, max=360, min = (360)/ (2^14)
        """
        global AFP_select

        FDW = 0x09 << 32                                 # Rising Delta Word (RDW)—Address 0x08
        core_clock = self.pll*self.clock                 # calculation of the core clock
        if(AFP_select == 0b00):                          # no modulation selected
            print("no modulation selected ")
            FDW_value = 0
        if(AFP_select == 0b01):                          # amplitude modulation selected
            if(FallingDelta > 0x3FF): 
                print("amplitud modulation selected, max 1024")
                FallingDelta = 0x3FF 
            FDW_value= (int(FallingDelta) & 0x3FF ) << 22
        if(AFP_select == 0b10):                          # frequency modulation selected
            if(FallingDelta > core_clock): 
                print("frequency modulation selected, max %s MHz"%(core_clock)*1E-6)
                FallingDelta = core_clock
            FDW_value =  (0xFFFFFFFF+1)*FallingDelta/(core_clock) # calculation of the delta frequency word for the rising linear sweep
            FDW_value = int(FDW_value) & 0xFFFFFFFF          
        if(AFP_select == 0b11):                           # phase modulation selected
            FDW_value = (0x3FFF+1)*FallingDelta/(360)     # calculation of the reciprocal phase
            FDW_value = (int(FDW_value) & 0x3FFF)  << 18  # phase offset word for each channel
   
        # composition of the command.
        out_FDW = FDW | FDW_value
        return(out_FDW)
    
    def CW_register(self, N_mem, word):
        """Return a number to write into the Channel word (CW) register. This sets a word in the memory of a selected channel
        for diferent types of modulations or linear sweeps. 15 memory slots for each channel.
        Four bytes are assigned to this register.
        N_mem: memory slot between 1 and 15
        word:
        AFP_select = 0b01: frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        AFP_select = 0b10: amplitude,  max 1023, 10bit word
        AFP_select = 0b11: phase phase in degree, max=360, min = (360)/ (2^14)
        """
        global AFP_select
        
        if N_mem > 15 or N_mem < 1:                      # memory slot between 1 and 15
            print("select a memory slot between 1 and 15")
            N_mem = 0
        CW_N = (N_mem + 0x09)                        
        CW_N = CW_N << 32                                # memory slot selection
        core_clock = self.pll*self.clock                 # calculation of the core clock
        if(AFP_select == 0b00):                          # no modulation selected
            print("no modulation selected ")
            CW_value = 0
        if(AFP_select == 0b01):                          # amplitude modulation selected
            if(word > 0x3FF): 
                print("amplitud modulation selected, max 1024")
                word = 0x3FF
            CW_value= int(word) & 0x3FF
            CW_value = CW_value << 22
        if(AFP_select == 0b10):                          # frequency modulation selected
            if(word > core_clock): 
                print("frequency modulation selected, max %s MHz"%(core_clock)*1E-6)
                word = core_clock
            CW_value =  (0xFFFFFFFF+1)*word/(core_clock) # calculation of the delta frequency word for the rising linear sweep
            CW_value = int(CW_value) & 0xFFFFFFFF
        if(AFP_select == 0b11):                          # phase modulation selected
            CW_value = (0x3FFF+1)*word/(360)             # calculation of the reciprocal phase
            CW_value = int(CW_value) & 0x3FFF            # phase offset word for each channel
            CW_value = CW_value << 18
        # composition of the command.
        out_CW = CW_N | CW_value
        return(out_CW)
    
    # Initialisation function

    def initialise_viaSPI(self,PLL_div=20, AFP_select=0b00, Mod_level=0b00, send=False):
        """Generate the spi code for write the registers to initialise the DDS with decided propierties
        PLL_div: sets the multiplier of the clock.
        AFP_select: 2bits selects the type of modulation # 00 modulation disable
                                                         # 01 Amplitude modulation
                                                         # 10 Frequency modulation
                                                         # 11 Phase modulation
        Mod_level: 2bits selects the level of modulation # 00 = 2-level modulation
                                                         # 01 = 4-level modulation
                                                         # 10 = 8-level modulation
                                                         # 11 = 16-level modulation
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending .
        """
        # composition of the command.
        CSR_spi = self.CSR_register(1, 1, 1, 1) 
        FR1_spi = self.FR1_register(PLL_div) 
        FR2_spi = self.FR2_register() 
        CFR_spi = self.CFR_register(AFP_select)
        out = [CSR_spi ,FR1_spi ,FR2_spi ,CFR_spi ]
        if send: 
            for i in out: self.direct_spi(hex(i))
        return(out)
    
    # Waveform channel setting functions 

    def set_frequency(self, ch, freq, send=False):
        """Generate the spi code for write into the register and change the frequency of a channel
        ch: channel to be changed
        freq:  frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending. 
        """
        
        CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1) << 40
        CFTW_spi = self.CFTW_register(freq)
        
        # composition of the command.
        set_freq = CSR_spi | CFTW_spi 
        if send: self.direct_spi(hex(set_freq))
        return(set_freq)

    def set_amplitude(self, ch, amp, send=False):
        """Generate the spi code for write into the register and change the amplitude of a channel
        ch: channel to be changed
        amp: amplitude,  max 1023, 10bit word
        send: if true send directly the command to the ESP32 nd will be executed directly
              if not true is not sending. 
        """
        
        CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1) << 32
        if amp > 1023: print("max amplitude 1023, clamped")
        ACR_spi = self.ACR_register(Mul_enable=0b1, amplitude=amp)
        
        # composition of the command.
        set_amp = CSR_spi | ACR_spi
        if send: self.direct_spi(hex(set_amp))
        return(set_amp)
    
    def set_phase(self, ch, phase, send=False):
        """Generate the spi code for write into the register and change the phase of a channel
        ch: channel to be changed
        phase: phase in degree, max=360, min = (360)/ (2^14)
        send: if true send directly the command to the ESP32 nd will be executed directly
              if not true is not sending. 
        """
        
        CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1) << 24
        if phase > 360: print("max phase 360, clamped")
        CPOW_spi = self.CPOW_register(phase)
        
        # composition of the command.
        set_phase = CSR_spi | CPOW_spi
        if send: self.direct_spi(hex(set_phase))
        return(set_phase)
    
    # Modulation and ramps functions
    
    def set_2mod_frequency(self, ch, freq_2nd, send=False):
        """Generate the spi code for write into the registers to set a channel into a 2-level frequency modulation
        and set the 2nd frequency level, the 1st one is the starting frequency.
        Change between levels is made via profile pins. (ch0->P0, ch1->P1, ch2->P2, ch3->P3)
        The 2-level modulation is default mode.
        ch: channel to be changed
        freq_2nd: 2nd  frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending. 
        """
        global AFP_select
        # channel selectio.n
        CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1)
        # select frequency modulation.
        AFP_select = 0b10
        CFR_spi = self.CFR_register(AFP_select=AFP_select, Sweep_nodwell=0b0, Sweep_enable=0b0, SRR_IOupdate=0b0)
        # save the 2nd value of frequency into the memory register number 1
        CW_spi = self.CW_register(1, freq_2nd)
       
        # composition of the command.
        out = [CSR_spi, CFR_spi, CW_spi]
       
        if send: 
            for i in out: self.direct_spi(hex(i))     
        return(out)
    
    def set_2mod_amplitude(self, ch, amp_2nd, send=False):
        """Generate the spi code for write into the registers to set a channel into a 2-level amplitude modulation
        and set the 2nd amplitude level, the 1st one is the starting amplitude.
        Change between levels is made via profile pins. (ch0->P0, ch1->P1, ch2->P2, ch3->P3)
        The 2-level modulation is default mode.
        ch: channel to be changed
        amp_2nd: 2nd amplitude,  max 1023, 10bit word
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending. 
        """
        global AFP_select
        # channel selection
        CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1)
        # select frequency modulation.
        AFP_select = 0b01
        CFR_spi = self.CFR_register(AFP_select=AFP_select, Sweep_nodwell=0b0, Sweep_enable=0b0, SRR_IOupdate=0b0)
        # save the 2nd value of frequency into the memory register number 1
        CW_spi = self.CW_register(1, amp_2nd)

        # composition of the command.
        out = [CSR_spi, CFR_spi, CW_spi]
       
        if send: 
            for i in out: self.direct_spi(hex(i))     
        return(out)
    
    def set_2mod_phase(self, ch, phase_2nd, send=False):
        """Generate the spi code for write into the registers to set a channel into a 2-level phase modulation
        and set the 2nd phase level, the 1st one is the starting phase.
        Change between levels is made via profile pins. (ch0->P0, ch1->P1, ch2->P2, ch3->P3)
        The 2-level modulation is default mode.
        ch: channel to be changed
        phase_2nd: 2nd phase in degree, max=360, min = (360)/ (2^14)
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending. 
        """
        global AFP_select
        # channel selectio.n
        CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1)
        # select frequency modulation.
        AFP_select = 0b11
        CFR_spi = self.CFR_register(AFP_select=AFP_select, Sweep_nodwell=0b0, Sweep_enable=0b0, SRR_IOupdate=0b0)
        # save the 2nd value of frequency into the memory register number 1
        CW_spi = self.CW_register(1, phase_2nd)

        # composition of the command.
        out = [CSR_spi, CFR_spi, CW_spi]
       
        if send: 
            for i in out: self.direct_spi(hex(i))     
        return(out)

    def ramp_frequency(self, ch, r_time, f_init, f_final, send=False):
        """"
        Setting the Slope of the Linear Sweep
        The slope of the linear sweep is set by the intermediate step size
        (delta-tuning word) between S0 (memory 0 or actual value) and E0 (memory 1 see CW_register) and the time spent
        (sweep ramp rate word) at each step.
        ch: channel to be changed
        r_time: ramp time in sec (max time step: 2.048 \u03BCs,  min time step: 8 ns )
        f_init: start of the ramp, frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        f_final: end of the ramp, frequency in Hz, max=clock x PLL, min = (clock x PLL)/ (2^32)
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending. 
        """
        
        global AFP_select    
        t_RR_max = 2.048E-6
        t_RR_min = 8E-9
        core_clock = self.pll*self.clock
        delta_f_min = core_clock/(2**32)
        n_points_tmin = int(r_time/t_RR_min)
        n_points_fmin = int(abs(f_final-f_init)/delta_f_min)
        
        try:
            if  f_init > f_final:
                print("initial value has to be larger than the second")
                raise ValueError
            if  f_init > core_clock or f_final > core_clock:
                print("Max freq value %s"%core_clock)
                raise ValueError
            if  abs(f_final-f_init) < delta_f_min:
                print("Ramp too short, min step: ",delta_f_min, " Hz" )
                raise ValueError
            if (r_time)/n_points_fmin > t_RR_max:
                print("Ramp time too long, max time step: 2.048 \u03BCs and the max n of steps is: ", int(n_points_fmin) )
                raise ValueError
            if  r_time < t_RR_min:
                print("Ramp time too short, min time step: 8 ns" )
                raise ValueError     

            else:    
                if abs(f_final-f_init)/n_points_tmin < delta_f_min and (r_time)/n_points_fmin > t_RR_min:
                    delta_f = delta_f_min
                    t_RR = r_time/n_points_fmin
                    n_points = n_points_fmin
                if (r_time)/n_points_fmin < t_RR_min and abs(f_final-f_init)/n_points_tmin > delta_f_min:
                    delta_f = abs(f_final-f_init)/n_points_tmin
                    t_RR= t_RR_min
                    n_points = n_points_tmin

                print("ramp time rate: ",t_RR, "  ramp value rate: ", delta_f)
                print("number of points: ",n_points, "  total time: ",n_points*t_RR, "  total change: ",n_points*delta_f )
                
                # select frequency modulation.
                AFP_select = 0b10
                #channel selection
                CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1)
                # set the delta time and delta freq for the ramp
                LSRR_spi = self.LSRR_register(t_RR, t_RR)
                FDW_spi = self.FDW_register(delta_f)
                RDW_spi = self.RDW_register(delta_f)
                # set frequency modulation.
                CFR_spi = self.CFR_register(AFP_select=AFP_select, Sweep_nodwell=0b0, Sweep_enable=0b1, SRR_IOupdate=0b0)
                #set 1st value of frequency into the memory register number 0
                CFTW_spi = self.CFTW_register(frequency=f_init)
                # save the 2nd value of frequency into the memory register number 1
                CW_spi = self.CW_register(1, f_final)


            # composition of the command.
            out = [CSR_spi, LSRR_spi, FDW_spi, RDW_spi, CFR_spi, CFTW_spi,  CW_spi]

        except ValueError:
            out = []
            raise
            
        if send: 
            for i in out: self.direct_spi(hex(i))     
        return(out)
    
    def ramp_amplitude(self, ch, r_time, a_init, a_final, send=False):
        """"
        Setting the Slope of the Linear Sweep
        The slope of the linear sweep is set by the intermediate step size
        (delta-tuning word) between S0 (memory 0 or actual value) and E0 (memory 1 see CW_register) and the time spent
        (sweep ramp rate word) at each step.
        ch: channel to be changed
        r_time: ramp time in sec (max time step: 2.048 \u03BCs,  min time step: 8 ns )
        a_init: start of the ramp, amplitude,  max 1023, 10bit word
        a_final: end of the ramp, amplitude,  max 1023, 10bit word
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending. 
        """
        
        global AFP_select    
        t_RR_max = 2.048E-6
        t_RR_min = 8E-9
        core_clock = self.pll*self.clock
        delta_a_min = 1
        n_points_tmin = int(r_time/t_RR_min)
        n_points_amin = int(abs(a_final-a_init)/delta_a_min)
        
        try:
            if  a_init > a_final:
                print("initial value has to be larger than the second")
                raise ValueError
            if  a_init > core_clock or a_final > core_clock:
                print("Max amplitude value 1023" )
                raise ValueError
            if  abs(a_final-a_init) < delta_a_min:
                print("Ramp too short, min step: ",delta_a_min, "" )
                raise ValueError
            if (r_time)/n_points_amin > t_RR_max:
                print("Ramp time too long, max time step: 2.048 \u03BCs and the max n of steps is: ", int(n_points_amin) )
                raise ValueError
            if  r_time < t_RR_min:
                print("Ramp time too short, min time step: 8 ns" )
                raise ValueError     

            else:    
                if abs(a_final-a_init)/n_points_tmin < delta_a_min and (r_time)/n_points_amin > t_RR_min:
                    delta_a = delta_a_min
                    t_RR = r_time/n_points_amin
                    n_points = n_points_amin
                if (r_time)/n_points_amin < t_RR_min and abs(a_final-a_init)/n_points_tmin > delta_a_min:
                    delta_a = abs(a_final-a_init)/n_points_tmin
                    t_RR= t_RR_min
                    n_points = n_points_tmin

                print("ramp time rate: ",t_RR, "  ramp value rate: ", delta_a)
                print("number of points: ",n_points, "  total time: ",n_points*t_RR, "  total change: ",n_points*delta_a)
                
                # select amplitude modulation.
                AFP_select = 0b01
                #channel selection
                CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1)
                # set the delta time and delta amplitude for the ramp
                LSRR_spi = self.LSRR_register(t_RR, t_RR)
                FDW_spi = self.FDW_register(delta_a)
                RDW_spi = self.RDW_register(delta_a)
                # set amplitude modulation.
                CFR_spi = self.CFR_register(AFP_select=AFP_select, Sweep_nodwell=0b0, Sweep_enable=0b1, SRR_IOupdate=0b0)
                #set 1st value of amplitude into the memory register number 0
                ACR_spi = self.ACR_register(Mul_enable=0b0, amplitude=a_init)
                # save the 2nd value of amplitude into the memory register number 1
                CW_spi = self.CW_register(1, a_final)

            # composition of the command.
            out = [CSR_spi, LSRR_spi, RDW_spi, FDW_spi, CFR_spi, ACR_spi, CW_spi]

        except ValueError:
            out = []
            raise
            
        if send: 
            for i in out: self.direct_spi(hex(i))     
        return(out)
    
    def ramp_phase(self, ch, r_time, p_init, p_final, send=False):
        """"
        Setting the Slope of the Linear Sweep
        The slope of the linear sweep is set by the intermediate step size
        (delta-tuning word) between S0 (memory 0 or actual value) and E0 (memory 1 see CW_register) and the time spent
        (sweep ramp rate word) at each step.
       
        ch: channel to be changed
        r_time: ramp time in sec (max time step: 2.048 \u03BCs,  min time step: 8 ns )
        p_init: start of the ramp, phase in degree, max=360, min = (360)/ (2^14)
        p_final: end of the ramp,  phase in degree, max=360, min = (360)/ (2^14)
        send: if true send directly the command to the ESP32 and will be executed directly
              if not true is not sending. 
        """
        
        global AFP_select    
        t_RR_max = 2.048E-6
        t_RR_min = 8E-9
        core_clock = self.pll*self.clock
        delta_p_min = (360)/ (2**14)
        n_points_tmin = int(r_time/t_RR_min)
        n_points_pmin = int(abs(p_final-p_init)/delta_p_min)
        
        try:
            if  p_init > p_final:
                print("initial value has to be larger than the second")
                raise ValueError
            if  p_init > 360 or p_final > 360:
                print("Max phase value 360 degree" )
                raise ValueError
            if  abs(p_final-p_init) < delta_p_min:
                print("Ramp too short, min step: ",delta_p_min, " degree" )
                raise ValueError
            if (r_time)/n_points_pmin > t_RR_max:
                print("Ramp time too long, max time step: 2.048 \u03BCs and the max n of steps is: ", int(n_points_pmin) )
                raise ValueError
            if  r_time < t_RR_min:
                print("Ramp time too short, min time step: 8 ns" )
                raise ValueError     

            else:    
                if abs(p_final-p_init)/n_points_tmin < delta_p_min and (r_time)/n_points_pmin > t_RR_min:
                    delta_p = delta_p_min
                    t_RR = r_time/n_points_pmin
                    n_points = n_points_pmin
                if (r_time)/n_points_pmin < t_RR_min and abs(p_final-p_init)/n_points_tmin > delta_p_min:
                    delta_p = abs(p_final-p_init)/n_points_tmin
                    t_RR= t_RR_min
                    n_points = n_points_tmin

                print("ramp time rate: ",t_RR, "  ramp value rate: ", delta_p)
                print("number of points: ",n_points, "  total time: ",n_points*t_RR, "  total change: ",n_points*delta_p)
                
                # select phase modulation.
                AFP_select = 0b11
                #channel selection
                CSR_spi = self.CSR_register((ch==0b00) & 1, (ch==0b01) & 1, (ch==0b10) & 1,(ch==0b11) & 1)
                # set the delta time and delta phase for the ramp
                LSRR_spi = self.LSRR_register(t_RR, t_RR)
                FDW_spi = self.FDW_register(delta_p)
                RDW_spi = self.RDW_register(delta_p)
                # set phase modulation.
                CFR_spi = self.CFR_register(AFP_select=AFP_select, Sweep_nodwell=0b0, Sweep_enable=0b1, SRR_IOupdate=0b0)
                #set 1st value of phase into the memory register number 0
                CPOW_spi = self.CPOW_register(phase=p_init)
                # save the 2nd value of phase into the memory register number 1
                CW_spi = self.CW_register(1, p_final)


            # composition of the command.
            out = [CSR_spi, LSRR_spi, FDW_spi, RDW_spi, CFR_spi, CPOW_spi, CW_spi]

        except ValueError:
            out = []
            raise
            
        if send: 
            for i in out: self.direct_spi(hex(i))     
        return(out)

    def to_start(self, command):
        self.start_commands.append(hex(command))

    def to_memory(self, command):
        self.memory_commands.append(hex(command))

    def generate_code(self, hdf5_file):
        #dt = np.dtype((str, 16))
        # start_commands_list = np.array(self.start_commands_list, dtype= "S32")
        vlenbytes = h5py.special_dtype(vlen=bytes)
        start_commands = np.array(self.start_commands, dtype= vlenbytes)
        memory_commands = np.array(self.memory_commands, dtype= vlenbytes)
        group = self.init_device_group(hdf5_file)
        if self.start_commands:
            group.create_dataset("start_commands", data = start_commands)
        if self.memory_commands:
            group.create_dataset("memory_commands", data = memory_commands)