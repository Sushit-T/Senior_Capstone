"""
Filename:   SPI_Data_Ctrl.py
Author:     Jacob Kucinski and Kelsey Marquez
Date:       8/8/24
Description:
"""
import serial
import threading
import queue
from tkinter import messagebox 

# File import
import globals

class SerialCtrl:
    def __init__(self, port, baudrate):
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
        Attempt to read a message from the ZTM controller.

        Returns:
            response (bytes): _description_
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
        Continuously reads data from the serial port and processes it.
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
        Continuously sends data from the send queue to the serial port.
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
        Stops the serial threads.
        """
        self.send_running = False
        self.receive_running = False
        if self.serial_port:
            self.send_thread.join()
            self.receive_thread.join()
            self.serial_port.close()
            