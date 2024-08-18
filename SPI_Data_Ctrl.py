"""
Filename:       SPI_Data_Ctrl.py
Author:         Jacob Kucinski and Kelsey Marquez
Date:           8/13/24
Description:    This file establishes serial communication between the PC 
                and the ZTM controller through a COM port. It starts and 
                stops the threads used for communication, as well as reads 
                bytes from the ZTM controller. 
"""
import serial
import threading
import queue
from tkinter import messagebox 

# File import
import globals

class SerialCtrl:
    def __init__(self, port, baudrate):
        """
        Initializes the SerialCtrl class, setting up the serial communication 
        parameters, threads, and queues for handling data transmission and reception.

        Args:
            port (str): The COM port or device name to which the serial communication 
                        will be established (e.g., "COM3" or "/dev/ttyUSB0").
            baudrate (int): The baud rate for the serial communication, which 
                            determines the speed of data transmission (e.g., 9600, 115200).
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.send_thread = None
        self.receive_thread = None
        self.send_queue = queue.Queue()     # Queue for data to be sent
        self.receive_queue = queue.Queue()  # Queue for received data
        self.send_running = False
        self.receive_running = False

    def ztmGetMsg(self):
        """
        Attempts to read a message from the ZTM controller through the serial port. 
        The function will try at most 10 times to retrieve a message. If the maximum 
        number of attempts is reached without success, the function returns `False`.

        Returns:
            response (bytes or bool): 
                - The message read from the serial port as a bytes object if successful.
                - `False` if the maximum number of attempts is reached without successfully 
                reading a message.
        
        Raises:
            serial.SerialException: If an error occurs while reading from the serial port, 
                                    an error message is displayed, and the process is 
                                    terminated. 
        """
        attempts = 0

        while(attempts < globals.MAX_ATTEMPTS):
            try:
                response = self.serial_port.read(globals.MSG_BYTES)
                return response
            except serial.SerialException as e:  
                attempts += 1        
        if attempts == globals.MAX_ATTEMPTS:
            return False
        
    def receive_serial(self):
        """
        Continuously reads data from the serial port while `receive_running` is True. 
        The function checks if there is data available to read, and if so, reads the 
        data and processes it by placing it into the `receive_queue`.

        Returns:
            raw_data (bytes or None): The raw data read from the serial port if data 
                                    is available, or `None` if no data is read.

        Raises:
            serial.SerialException: If an error occurs while reading from the serial port, 
                                    an error message is displayed, and the process is 
                                    terminated.    
        """
        while self.receive_running:
            try:
                if self.serial_port.in_waiting > 0:
                    raw_data = self.serial_port.read(self.serial_port.in_waiting)
                    self.receive_queue.put(raw_data)        # Push received data to queue
                    return raw_data
            except serial.SerialException as e:
                messagebox.showerror("ERROR", f"Error reading serial port: {e}")
                self.receive_running = False

    def send_serial(self):
        """
        Continuously sends data from the send queue to the serial port while 
        `send_running` is True. The function attempts to retrieve data from the 
        send queue with a short timeout. If data is available, it is written to the 
        serial port. If the send queue is empty, the function continues looping 
        until data is available or until `send_running` is set to False.

        Raises:
            queue.Empty: If the send queue is empty and no data is retrieved within 
                        the specified timeout, the loop continues without raising an error.
            serial.SerialException: If an error occurs while writing to the serial port, 
                                    an error message is displayed, and the sending process 
                                    continues or stops depending on `send_running`.
        """
        while self.send_running:
            try:
                data = self.send_queue.get(timeout=0.01)    # Wait for data with a timeout
                if data:
                    self.serial_port.write(data)
            except queue.Empty:
                continue  # No data to send, loop back
            except serial.SerialException as e:
                messagebox.showerror("ERROR", f"Failed to write to serial port: {e}")

    def start(self):
        """
        Attempts to open the specified serial port with the configured settings and 
        starts the threads for sending and receiving data. The function also increases 
        the buffer sizes for both reading and writing to enhance performance.

        Returns:
            bool: True if the serial port is successfully opened and the threads are 
                started; False if the serial port could not be opened.

        Raises:
            serial.SerialException: If an error occurs while attempting to open the 
                                    serial port, an error message is printed, and 
                                    the function returns False.
        """
        try:
            print(f"Attempting to open serial port: {self.port}")
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.01,       # Set a timeout for read operations
                write_timeout=0.01, # Set a timeout for write operations
                xonxoff=False,
                rtscts=True,
            )
            # Increase the read and write buffer sizes
            self.serial_port.set_buffer_size(rx_size=65536, tx_size=65536)
            
            self.send_running = True
            self.receive_running = True
            self.send_thread = threading.Thread(target=self.send_serial)
            self.receive_thread = threading.Thread(target=self.receive_serial)
            self.send_thread.start()
            self.receive_thread.start()
            return True
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            self.serial_port = None
            return False

    def stop(self):
        """
        Stops the serial communication threads and closes the serial port. 
        """
        self.send_running = False
        self.receive_running = False
        if self.serial_port:
            self.send_thread.join()
            self.receive_thread.join()
            self.serial_port.close()
            