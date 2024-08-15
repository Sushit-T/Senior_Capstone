"""
Filename:       ztmSerialCommLibrary.py
Author:         Dustin Matthews
Date:           8/8/24
Description:    This file was created to communicate to the ZTM controller
                via custom-made messages. The format creates a message header
                with the message type byte, command byte, then status byte. The
                rest of the bytes contained in the message depend on what is
                being done.
"""
from enum import Enum
import struct
import serial

# Import python files
import globals
from value_conversion import Convert

###########################################
padByte = [0x00]
###########################################

class ztmCMD(Enum): 
    CMD_CLR	,                           \
    CMD_SET_VBIAS,                      \
    CMD_SET_ADC_SAMPLE_RATE	,           \
    CMD_SET_ADC_SAMPLE_SIZE,            \
    CMD_PERIODIC_DATA_ENABLE,           \
    CMD_PERIODIC_DATA_DISABLE,          \
    CMD_REQ_DATA,                       \
    CMD_REQ_STEP_COUNT,                 \
    CMD_STEPPER_ADJ,                    \
    CMD_PIEZO_ADJ,                      \
    CMD_VBIAS_SET_SINE,                 \
    CMD_VBIAS_STOP_SINE,                \
    CMD_REQ_FFT_DATA,                   \
    CMD_RETURN_TIP_HOME,                \
    CMD_STEPPER_RESET_HOME_POSITION,    \
    CMD_ABORT,                          \
    CMD_ADC_CAL_MODE,                   \
    CMD_ADC_CAL_LOAD_CURR,              \
    CMD_ADC_CAL_MEAS_GND,               \
    CMD_ADC_CAL_MEAS_TEST_CURR,         \
    CMD_ADC_CAL_STOP,                   \
    CMD_DAC_CAL_MODE_VBIAS,             \
    CMD_DAC_CAL_MODE_VPZO,              \
    CMD_DAC_CAL_SET_0V,                 \
    CMD_DAC_CAL_STORE_0V,               \
    CMD_DAC_CAL_SET_MID_SCALE,          \
    CMD_DAC_CAL_STORE_MID_SCALE,        \
    CMD_DAC_CAL_CHECK,                  \
    CMD_DAC_CAL_STOP = range(0 , 29)

class ztmSTATUS(Enum):
    STATUS_ACK,         \
    STATUS_NACK,        \
    STATUS_DONE,        \
    STATUS_FAIL,        \
    STATUS_RESEND,      \
    STATUS_OVERCURRENT, \
    STATUS_CLR,         \
    STATUS_RDY,         \
    STATUS_BUSY,        \
    STATUS_ERROR,       \
    STATUS_STEP_COUNT,  \
    STATUS_MEASUREMENTS,\
    STATUS_FFT_DATA,    \
    STATUS_TIP_CRASHED = range(0 , 14)

class usbMsgFunctions:
    def __init__(self, val):
        """
        Initialization of the class.
        """
        self.val=val
        
    ################################################
    # STANDARD COMMAND MESSAGES FOR ZTM CONTROLLER #
    ################################################

    # MSG A 
    def sendMsgA(self, port, msgCmd, msgStatus, current_nA, vbias, vpzo):
        """
        Sends a message of type 'A' to the microcontroller, which includes a command, 
        status, and data values for current, bias voltage, and piezo voltage. The 
        function constructs the message with the specified parameters and attempts 
        to send it multiple times if necessary.

        Args:
            port (serial.Serial): The COM port object used for communication, 
                                initialized using pySerial functions.
            msgCmd (int): The command to be sent, represented as a `ztmCMD` value. 
                        Refer to the documentation for valid commands.
            msgStatus (int): The status to be sent, typically `ztmSTATUS.STATUS_CLR`.
            current_nA (float): The current value to be sent, in nanoamperes (nA).
            vbias (float): The bias voltage to be sent, in volts.
            vpzo (float): The piezo voltage to be sent, in volts.

        Returns:
            bool: True if the message is successfully sent; False if the message 
                could not be sent after the maximum number of retries.    
        """
        messageA = struct.pack('<BBBfHH', globals.MSG_A, msgCmd, msgStatus, current_nA, Convert.get_Vbias_int(vbias), Convert.get_Vpiezo_int(vpzo))
        retry = 0
        maxRetries = 10
        while retry < maxRetries:  
            try:   
                port.write(serial.to_bytes(messageA)) 
                # Clear buffer
                port.flush() 
                return True
            except serial.SerialException as e:
                retry += 1  
        return False 

    # MSG B
    # Note: account for parsing different commands and rateHz vs. sample size
    def sendMsgB(self, port, msgCmd, msgStatus, uint16_rateHz):
        """
        Used to set the sample rate in Hertz or the sample size. The function 
        constructs the message with the specified parameters and attempts to 
        send it multiple times if necessary.

        Args:
            port (serial.Serial): The COM port object used for communication, 
                                initialized using pySerial functions.
            msgCmd (int): The command to be sent, represented as a `ztmCMD` value. 
                        Refer to the documentation for valid commands.
            msgStatus (int): The status to be sent, typically `ztmSTATUS.STATUS_CLR`.
            uint16_rateHz (int): The data rate to be assigned, in Hertz. The maximum 
                                valid rate is 65535 Hz.

        Returns:
            bool: True if the message is successfully sent; False if the message 
                could not be sent after the maximum number of retries.    
        """
        payload = bytes(globals.PAYLOAD_BYTES - 2) 
        messageB = struct.pack('<BBBHBBBBBB', globals.MSG_B, msgCmd, msgStatus, uint16_rateHz, *payload)
        retry = 0
        maxRetries = 10
        while retry < maxRetries:  
            try:      
                port.write(serial.to_bytes(messageB)) 
                # Clear buffer    
                port.flush()       
                return True
            except serial.SerialException as e:
                retry += 1 
        return False        

    # MSG C
    def sendMsgC(self, port, msgCmd, msgStatus):
        """
        Used solely for transmitting commands and statuses (e.g., ACK or DONE). The function 
        constructs the message with the appropriate command and status.

        Args:
            port (serial.Serial): The COM port object used for communication, 
                                initialized using pySerial functions.
            msgCmd (int): The command to be sent, represented as a `ztmCMD` value. 
                        Refer to the documentation for valid commands.
            msgStatus (int): The status to be sent, typically `ztmSTATUS.STATUS_CLR`.

        Returns:
            bool: True if the message is successfully sent; False if the message 
                could not be sent after the maximum number of retries or if a 
                write timeout occurs when sending a `STATUS_RDY` message.
        """
        payload = padByte * 8
        messageC = struct.pack('BBBBBBBBBBB', globals.MSG_C, msgCmd, msgStatus, *payload)
        retry = 0
        maxRetries = 10
        while retry < maxRetries:
            try:   
                port.write(serial.to_bytes(messageC))
                # Clear buffer    
                port.flush()  
                return True
            except serial.SerialException as e:
                if "Write timeout" in str(e) and msgStatus == ztmSTATUS.STATUS_RDY.value:
                    return False
                retry += 1 
        return False  

    # MSG D
    def sendMsgD(self, port, msgCmd, msgStatus, size, dir, count):
        """
        Controls the stepper motor's movement on the microcontroller. The 
        message includes the command, status, step size, direction, and 
        the number of steps. 

        Args:
            port (serial.Serial): The COM port object used for communication, 
                                initialized using pySerial functions.
            msgCmd (int): The command to be sent, represented as a `ztmCMD` value. 
                        Refer to documentation for valid commands.
            msgStatus (int): The status to be sent, typically `ztmSTATUS.STATUS_CLR`.
            size (int): The step size, typically defined in global constants, such as `FULL_STEP`.
            dir (int): The direction for the stepper motor movement, where `1` represents 
                    one direction (e.g., up) and `0` represents the opposite direction (e.g., down).
            count (int): The number of steps to move the stepper motor at the specified step size.

        Returns:
            bool: True if the message is successfully sent; False if the message 
                could not be sent after the maximum number of retries.    
        """     
        payload = bytes(2)
        messageD = struct.pack('<BBBBBiBB', globals.MSG_D, msgCmd, msgStatus, size, dir, count, *payload)

        retry = 0
        maxRetries = 10
        while retry < maxRetries:
            try:     
                port.write(serial.to_bytes(messageD))
                # Clear buffer    
                port.flush()   
                return True  
            except serial.SerialException as e:
                retry += 1   
        return False   

    # MSG E
    def sendMsgE(self, port, sineVbiasAmp, uint16_rateHz):
        """
        Sets the sine wave bias voltage parameters on the microcontroller. 

        Args:
            port (serial.Serial): The COM port object used for communication, initialized 
                                using pySerial functions.
            sineVbiasAmp (float): The amplitude of the sine wave bias voltage to be set, 
                                in volts.
            uint16_rateHz (int): The frequency of the sine wave, in Hz. The maximum 
                                valid frequency is 5000 Hz.

        Returns:
            bool: True if the message is successfully sent; False if the message 
                could not be sent after the maximum number of retries.        
        """           
        # ONLY VALID CMD IN MSG E IS CMD_VBIAS_SET_SINE
        payload = bytes(4)
        messageE = struct.pack('<BBBHHBBBB', globals.MSG_E, ztmCMD.CMD_VBIAS_SET_SINE.value, ztmSTATUS.STATUS_CLR.value, 
                                                Convert.get_Vbias_int(sineVbiasAmp), uint16_rateHz, *payload)
        retry = 0
        maxRetries = 10
        while retry < maxRetries:
            try:    
                port.write(serial.to_bytes(messageE))
                # clear buffer    
                port.flush()
                return True
            except serial.SerialException as e:
                retry += 1  
        return False    
        
    ###############################################
    # UNPACK MSG DATA - Reading MCU
    def unpackRxMsg(self, rxMsg):
        """
        The function handles different message types and extracts relevant data, such as 
        current, bias voltage, piezo voltage, and FFT data.

        Args:
            rxMsg (bytes): The raw message received from the microcontroller, 
                        containing command and status bytes, as well as data.

        Returns:
            - Tuple (adcRx_nA, vBiasRx_V, vPiezoRx_V) for MSG_A if successful.
            - Integer representing the status byte for MSG_C if successful.
            - Float representing the number of full steps for MSG_D if successful.
            - Tuple (adcRxFFT_nA, freqRxFFT_Hz) for MSG_F if successful.
            - False if the message is invalid, does not match the expected format, 
            or if the microcontroller sends an unexpected command.

        Raises:
            None explicitly, but returns `False` if an exception occurs during unpacking.        
        """
        ################################
        # DEBUG - PRINT CMD AND STATUS #
        try:
            cmdRx = ztmCMD(rxMsg[globals.CMD_BYTE])
            #print("Received : " + cmdRx.name)
            statRx = ztmSTATUS(rxMsg[globals.STAT_BYTE])
            #print("Received : " + statRx.name + "\n")
        ################################
        
        # EXTRACT THE DATA FROM RX MSG #
            if(rxMsg[0] == globals.MSG_A):
                if(rxMsg[globals.CMD_BYTE] != ztmCMD.CMD_CLR.value):
                    # Microcontroller should not send commands
                    return False
                elif(rxMsg[2] == ztmSTATUS.STATUS_MEASUREMENTS.value):              
                    adcRx_nA    = round(struct.unpack('f', bytes(rxMsg[3:7]))[0], 4)                            # Unpack bytes & convert  
                    vBiasRx_V   = round(Convert.get_Vbias_float(struct.unpack('H',bytes(rxMsg[7:9]))[0]), 3)    # Unpack bytes & convert
                    vPiezoRx_V  = round(Convert.get_Vpiezo_float(struct.unpack('H',bytes(rxMsg[9:11]))[0]), 5)  # Unpack bytes & convert
                    return adcRx_nA, vBiasRx_V, vPiezoRx_V
                else:
                    return False

            elif (rxMsg[0] == globals.MSG_B):
                # Microcontroller should not send msg B       
                return False

            elif (rxMsg[0] == globals.MSG_C):
                if(rxMsg[globals.CMD_BYTE] != ztmCMD.CMD_CLR.value):
                    # Microcontroller should not send commands
                    return False
                else:
                    statRx = ztmSTATUS(rxMsg[globals.STAT_BYTE])
                    return rxMsg[globals.STAT_BYTE]

            elif (rxMsg[0] == globals.MSG_D):
                if(rxMsg[globals.CMD_BYTE] != ztmCMD.CMD_CLR.value):
                    # Microcontroller should not send commands
                    return False
                else:
                    stepsRx = struct.unpack('i', bytes(rxMsg[5:9]))[0]               
                    stepsRx = stepsRx / 8   # Return the number of full steps as a float for conversion
                    return stepsRx 

            elif (rxMsg[0] == globals.MSG_E):
                # Microcontroller should not send msg B       
                return False 

            elif (rxMsg[0] == globals.MSG_F):
                if(rxMsg[globals.CMD_BYTE] != ztmCMD.CMD_CLR.value):
                    # Microcontroller should not send commands     
                    return False
                else:
                    adcRxFFT_nA = round(struct.unpack('f', bytes(rxMsg[3:7]))[0], 3) # Unpack bytes & convert                                     
                    freqRxFFT_Hz = round(struct.unpack('f', bytes(rxMsg[7:11]))[0], 3) # Unpack bytes & convert 
                    return adcRxFFT_nA, freqRxFFT_Hz
        except:
            return False  
            
