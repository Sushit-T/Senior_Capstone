"""
Filename:       value_conversion.py
Author:         Sean Follo
Date:           8/8/24
Description:    This file is used to convert current, bias voltage, or piezo
                voltage to a readable format for the ZTM application, or formats 
                it into a writable format to the ZTM controller.
"""

class Convert:
    def get_curr_float(curr_int):
        '''
        Converts tunneling current in 18-bit fixed point integer format to
        floating point format with units of nA
        
        :param curr_int: Tunneling Current in 18-bit format used by ADC
        
        :return val: Tunneling Current as a float with a unit of nA
        '''
        # Converts unsigned int to signed int
        curr_float = curr_int - (2 * (curr_int & (2 ** 17))) 
        # Converts fixed point int to float
        curr_float = (curr_float * 5 * 1000000000) / (200000000 * (2 ** 18))
        return curr_float
    
    def get_curr_int(curr_float):
        """
        Converts tunneling current in floating point format with units of nA to 
        18-bit fixed point integer format
        
        :param curr_float: Tunneling Current as a float with a unit of nA
        
        :return val: Tunneling Current in 18-bit format used by ADC
        """
        # Convert to int
        curr_int = round((curr_float * 200000000 * (2 ** 18)) / (5 * 1000000000)) 
        
        # Convert to 2's complement if negative
        if curr_int < 0:
            curr_int = curr_int * -1
            curr_int = curr_int | (2 ** 17)
            curr_int = (curr_int ^ ((2 ** 17) - 1)) + 1
        return curr_int
            
    def get_Vbias_float(Vbias_int):
        """
        Converts Vbias voltage in 16-bit fixed point integer format to floating
        point format with a unit of Volts
        
        :param Vbias_int: Vbias in 16-bit format used by DAC
        
        :return val: Vbias as a float with a unit of Volts
        """
        Vbias_float = ((4 * 5 * Vbias_int) / (2 ** 16)) - 10
        return Vbias_float
        
    def get_Vbias_int(Vbias_float):
        """
        Converts Vbias voltage in floating point format with units of Volts to 
        16-bit fixed point integer format
        
        :param Vbias_float: Vbias voltage as a float with a unit of Volts
        
        :return val: Vbias Voltage in 16-bit format used by DAC
        """
        Vbias_int = round(((Vbias_float + 10) * (2 ** 16)) / (4 * 5))
        if(Vbias_int > 65535):
            Vbias_int = 65535
        if(Vbias_int < 0):
            Vbias_int = 0    
        return Vbias_int

    def get_Vpiezo_float(Vpiezo_int):
        """
        Converts Vpiezo voltage in 16-bit fixed point integer format to floating
        point format with a unit of Volts
        
        :param Vbias_int: Vpiezo in 16-bit format used by DAC
        
        :return val: Vpiezo as a float with a unit of Volts
        """
        Vpiezo_float = (2 * 5 * Vpiezo_int) / (2 ** 16)
        return Vpiezo_float
        
    def get_Vpiezo_int(Vpiezo_float):
        """
        Converts Vpiezo voltage in floating point format with units of Volts to 
        16-bit fixed point integer format
        
        :param Vpiezo_float: Vpiezo voltage as a float with a unit of Volts
        
        :return val: Vpiezo Voltage in 16-bit format used by DAC
        """
        Vpiezo_int = round(Vpiezo_float * (2 ** 16) / (2 * 5))
        if(Vpiezo_int > 65535):
            Vpiezo_int = 65535
        return Vpiezo_int
