"""
Filename:   GUI_Master_Demo.py
Author:     Jacob Kucinski and Kelsey Marquez
Date:       8/8/24
Description:
"""
from tkinter import Label, LabelFrame, Button, StringVar, OptionMenu, END
from tkinter import messagebox 
from tkinter import filedialog
import customtkinter as ctk
import serial.tools.list_ports
import tkinter as tk
import serial
import os
import struct
import time
import csv
import datetime
import threading
import math
import matplotlib.dates as mdates
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import python files
import globals
from IV_Window import IVWindow 
from IZ_Window import IZWindow  
from value_conversion import Convert
from ztmSerialCommLibrary import usbMsgFunctions, ztmCMD, ztmSTATUS
from SPI_Data_Ctrl import SerialCtrl
from GUI_Widgets import HomepageWidgets

###########################################
############# GLOBAL VARIABLES ############
curr_setpoint   = 0.0

# For MCU sent measurements
curr_data       = 0.0
vb_V            = 0.0
vp_V            = 0.0

vpiezo_dist     = 0

vbias_save      = None
vbias_done_flag = 0

# Used for the tip approach
vpiezo_tip      = 0.0
tunneling_steps = 0

# Used for the sample rate
sample_rate_save        = None
sample_rate_done_flag   = 0

# Used for the sample size
sample_size_save        = None
sample_size_done_flag   = 0

# Used for keeping track of the position of the stepper motor
total_steps    = None

# Used for the tunneling approach
tip_app_total_steps     = None

startup_flag    = 0

TUNN_APPR_FLAG      = 0
CAP_APPR_FLAG       = 0
PERIODICS_FLAG      = 0
FEEDBACK_CTRL_FLAG  = 0
TUNN_APPROACH_ESCAPE_FLG    = 0
POS_CURR_SETPOINT_FLAG      = 0
NEG_CURR_SETPOINT_FLAG      = 0
POS_SAMPLE_BIAS_FLAG        = 0
NEG_SAMPLE_BIAS_FLAG        = 0
STOP_BTN_FLAG               = 0
###########################################


###################################################################################################################
#                                                 RootGUI CLASS                                                   #
###################################################################################################################
class RootGUI:
    def __init__(self):
        """
        Initializes the main window and its components.
        """
        self.root = ctk.CTk()
        self.root.title("Homepage")
        self.root.config(bg="#eeeeee")
        self.root.geometry("1100x650")
        
        # Add a method to quit the application
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
        
        # Initialize serial control
        self.serial_ctrl = SerialCtrl(None, globals.BAUDRATE)
        self.ztm_serial = usbMsgFunctions(self)
					
        # Initialize other components
        self.meas_gui = MeasGUI(self.root, self)
        self.graph_gui = GraphGUI(self.root, self.meas_gui)
        self.com_gui = ComGUI(self.root, self)
        
        # Initialize MeasGUI components
        self.widget_initializer = HomepageWidgets(self.root, self)
        self.widget_initializer.initialize_widgets(self.meas_gui)
        
    def quit_application(self):
        """
        Quits the application and closes the serial read thread.
        """
        if self.serial_ctrl:
            self.serial_ctrl.stop()
        self.root.quit()
    
    def start_reading(self):
        """
        Opens the serial read thread and enables the start of periodic data reading.
        """
        if self.serial_ctrl:
            if(TUNN_APPR_FLAG):
                self.meas_gui.tunneling_approach()
            elif(CAP_APPR_FLAG):
                self.meas_gui.cap_approach()
            elif(PERIODICS_FLAG):
                self.meas_gui.enable_periodics()
            self.serial_ctrl.running = True
    
    def stop_reading(self):
        """
        Disables the reading of periodic data in a background thread.
        """
        def stop_reading_task():
            # Clear buffer
            self.clear_buffer()
            
            start_time = time.time()
            success = self.meas_gui.send_msg_retry(self.serial_ctrl.serial_port, globals.MSG_C, ztmCMD.CMD_PERIODIC_DATA_DISABLE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)

            while not success and (time.time() - start_time) < globals.TIMEOUT:
                success = self.meas_gui.send_msg_retry(self.serial_ctrl.serial_port, globals.MSG_C, ztmCMD.CMD_PERIODIC_DATA_DISABLE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)
            if success:
                self.widget_initializer.enable_widgets(self.meas_gui)
                self.meas_gui.stop_leds()
        # Run the stop reading task in a separate thread
        stop_thread = threading.Thread(target=stop_reading_task)
        stop_thread.start()
    
    def clear_buffer(self):
        """
        Clears the serial buffer to make room for other messages.
        """
        if self.serial_ctrl.serial_port.in_waiting > 0:
            self.serial_ctrl.serial_port.read(self.serial_ctrl.serial_port.in_waiting)

###################################################################################################################
#                                                 ComGUI CLASS                                                    #
###################################################################################################################
class ComGUI:
    def __init__(self, root, parent):
        """
        Initializes the communication manager interface.

        Args:
            root (tkinter.Tk): The root window of the application.
            parent (RootGUI): The parent class that manages the main application logic.
        """
        self.root = root
        self.parent = parent
        self.frame = LabelFrame(root, text="Com Manager", padx=5, pady=5, bg="white")
        self.label_com = Label(self.frame, text="Available Port(s): ", bg="white", width=15, anchor="w")
        
        # Setup the Drop option menu
        self.ComOptionMenu()

        # Add the control buttons for refreshing the COMs & Connect
        self.btn_refresh = Button(self.frame, text="Refresh", width=10, command=self.com_refresh)
        self.btn_connect = Button(self.frame, text="Connect", width=10, state="disabled", command=self.serial_connect)
        
        # Optional Graphic parameters
        self.padx = 7
        self.pady = 5

        # Put on the grid all the elements
        self.publish()

    def publish(self):
        """
        Publishes the widgets for the communication manager.
        """
        self.frame.grid(row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5, sticky="n")
        self.label_com.grid(column=1, row=0)
        self.drop_com.grid(column=2, row=0, padx=self.padx)
        self.btn_refresh.grid(column=3, row=0, padx=self.padx)
        self.btn_connect.grid(column=3, row=1, padx=self.padx)

    def ComOptionMenu(self):
        """
        Gets the list of available COM ports and displays them in the application.
        """
        ports = serial.tools.list_ports.comports()
        self.serial_ports = [port.device for port in ports]
        self.clicked_com = StringVar()
        self.clicked_com.set("-" if self.serial_ports else "No COM port found")
        self.drop_com = OptionMenu(self.frame, self.clicked_com, *self.serial_ports, command=self.connect_ctrl)
        self.drop_com.config(width=10)
    
    def connect_ctrl(self, widget):
        """
        Determines the state of the connect button.
        """
        if self.clicked_com.get() == "-":
            self.btn_connect["state"] = "disabled"
        else:
            self.btn_connect["state"] = "active"

    def com_refresh(self):
        """
        Refreshes the list of available COMs.
        """
        self.drop_com.destroy()
        self.ComOptionMenu()
        self.drop_com.grid(column=2, row=0, padx=self.padx)
        logic = []
        self.connect_ctrl(logic)

    def serial_connect(self):
        """
        Verifies the connection of a port.
        """
        global startup_flag
        if self.btn_connect["text"] == "Connect":
            port = self.clicked_com.get()
            try:
                # Attempt to open the serial port to check if it is already in use
                test_serial = serial.Serial(port)
                test_serial.close()

                # If the port is available, proceed with the connection
                self.parent.serial_ctrl.port = port
                
                # Attempt to start the threads
                serial_response = self.parent.serial_ctrl.start()

                if serial_response:
                    self.startup_routine()
                else:
                    self.btn_connect["text"] = "Connect"
                    self.btn_refresh["state"] = "active"
                    self.drop_com["state"] = "active"
                    InfoMsg = f"Failed to connect to {self.clicked_com.get()}."
                    messagebox.showerror("Connection Error", InfoMsg)
                    self.parent.serial_ctrl.running = False
            except serial.SerialException as e:
                self.btn_connect["text"] = "Connect"
                self.btn_refresh["state"] = "active"
                self.drop_com["state"] = "active"
                InfoMsg = f"Failed to connect to {self.clicked_com.get()}: {e}"
                messagebox.showerror("Connection Error", InfoMsg)
                self.parent.serial_ctrl.running = False
        else:
            if self.parent.serial_ctrl:
                self.parent.serial_ctrl.stop()
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] = "active"
            self.drop_com["state"] = "active"
            InfoMsg = f"UART connection using {self.clicked_com.get()} is now closed."
            messagebox.showwarning("Disconnected", InfoMsg)
            
            startup_flag = 0

    def startup_routine(self):
        """
        A message sent to the MCU upon valid connection of a port, starting the MCU program.
        """
        global startup_flag
        global total_steps
        global vb_V
        global vp_V
        
        port = self.parent.serial_ctrl.serial_port
        
        msg_response = self.parent.meas_gui.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_CLR.value, ztmSTATUS.STATUS_RDY.value, ztmSTATUS.STATUS_ACK.value)   
        
        if msg_response:
            self.parent.clear_buffer()
            time.sleep(0.1)
            print("=============== STARTUP ROUTINE ===============")
            # Obtain step count
            total_steps = self.parent.meas_gui.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_STEP_COUNT.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_STEP_COUNT.value)
            print(f"Step count upon startup: {total_steps}")
            
            # Set vbias to 0 upon startup
            self.parent.meas_gui.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_SET_VBIAS.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, 0)
            # Set vpzo to 0 upon startup
            self.parent.meas_gui.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_PIEZO_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, 0)
            # Check vbias and vpzo have been set to 0
            self.parent.meas_gui.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_DATA.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_MEASUREMENTS.value)
            print(f"Measured vbias: {vb_V} V")
            print(f"Measured vpzo: {vp_V} V")
            
            self.btn_connect["text"] = "Disconnect"
            self.btn_refresh["state"] = "disable"
            self.drop_com["state"] = "disable"
            InfoMsg = f"Successful UART connection using {self.clicked_com.get()}."
            messagebox.showinfo("Connected", InfoMsg)
            startup_flag = 1
            self.parent.clear_buffer()
        else:
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] = "active"
            self.drop_com["state"] = "active"
            InfoMsg = f"Failed to connect to {self.clicked_com.get()}."
            messagebox.showerror("Connection Error", InfoMsg)
            self.parent.serial_ctrl.running = False
            startup_flag = 0

###################################################################################################################
#                                                 MeasGUI CLASS                                                   #
###################################################################################################################
# class for measurements/text box widgets in homepage
class MeasGUI:
    def __init__(self, root, parent):
        """
        Initializes the widgets and logic for sending and receiving messages.

        Args:
            root (tkinter.Tk): The root window of the application
            parent (RootGUI): The parent class that manages the main application logic.
        """
        self.root = root
        self.parent = parent

        # Initialize MeasGUI widgets
        self.initializer = HomepageWidgets(root, parent)
        self.initializer.initialize_widgets(self)
        self.initializer.publish(self)
        
        self.DropDownMenu()
        
        # Local variables for distnace and adc current readings
        self.distance   = 0.0
        self.adc_curr   = 0.0
        
        # Local variables for vpzo adjusting
        self.vpzo_down  = 0
        self.vpzo_up    = 0
        vpiezo_tip = 0.0
        
        # Local variables for stepper motor adjusting
        self.step_up    = 0
        self.step_down  = 0
        
        # Initialize measurement widgets
        self.update_label()
        

    def open_iv_window(self):
        """
        Method to open the I-V Sweep window when the "Acquire I-V" button is clicked.
        """
        self.acquire_iz_btn["state"] = "disabled"
        new_window = ctk.CTkToplevel(self.root)
        IVWindow(new_window, self.parent.serial_ctrl)
        new_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(new_window))
        
        # Disable main window
        self.root.attributes("-disabled", True)

    def open_iz_window(self):
        """
        Method to open the I-Z Sweep window when the "Acquire I-Z" button is clicked.
        """
        self.acquire_iv_btn["state"] = "disabled"
        new_window = ctk.CTkToplevel(self.root)
        IZWindow(new_window, self.parent.serial_ctrl)
        new_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(new_window))
        
        # Disable main window
        self.root.attributes("-disabled", True)

    def on_closing(self, window):
        """
        Method to re-enable the main window when the IV or IZ window is closed.
        """
        window.destroy()
        self.root.attributes("-disabled", False)
        self.acquire_iv_btn["state"] = "normal"
        self.acquire_iz_btn["state"] = "normal"
        
    def startup_leds(self):
        """
        Method to change the LEDs upon the user pressing the start button.
        """
        self.stop_led_btn.grid_remove()
        self.start_led_btn.grid(row=0, column=1, sticky="")
    
    def stop_leds(self):
        """
        Method to change the LEDs upon the user pressing the stop button.
        """
        self.stop_led_btn.grid()
        self.start_led_btn.grid_remove()

    def start_tip_appr(self):
        """
        Enables the tunneling approach through its global flag.
        """
        global TUNN_APPR_FLAG
        global CAP_APPR_FLAG
        global PERIODICS_FLAG
        global FEEDBACK_CTRL_FLAG

        TUNN_APPR_FLAG = 1
        CAP_APPR_FLAG = 0
        PERIODICS_FLAG = 0
        FEEDBACK_CTRL_FLAG = 0

        self.start_reading()

    def start_cap_appr(self):
        """
        Enables the capacitance approach through its global flag.
        """
        global TUNN_APPR_FLAG
        global CAP_APPR_FLAG
        global PERIODICS_FLAG
        global FEEDBACK_CTRL_FLAG

        TUNN_APPR_FLAG = 0
        CAP_APPR_FLAG = 1
        PERIODICS_FLAG = 0
        FEEDBACK_CTRL_FLAG = 0

        self.start_reading()

    def start_periodics(self):
        """
        Enables the periodic data through its global flag.
        """
        global TUNN_APPR_FLAG
        global CAP_APPR_FLAG
        global PERIODICS_FLAG
        global FEEDBACK_CTRL_FLAG

        TUNN_APPR_FLAG = 0
        CAP_APPR_FLAG = 0
        PERIODICS_FLAG = 1
        FEEDBACK_CTRL_FLAG = 0
        
        self.start_reading()
        
    def start_reading(self):
        """
        Initializes the data reading process when the start button is pressed.
        
        This method performs the following steps:
        1. Checks the connection status and if not connected exits out of the method.
        2. If connected, it prints a message and updates the button states.
        3. Calls the `startup_leds` method to change the LED status.
        4. Calls the parent's `start_reading` method in the RootGUI class to begin data reading.
        """
        global STOP_BTN_FLAG
        if self.check_connection():
            return
        else:
            STOP_BTN_FLAG = 0
            self.parent.start_reading()			  
    
    def stop_reading(self):
        """
        Stops the data reading process when the stop button is pressed.
        
        This method performs the following steps:
        1. Checks the connection status and if not connected exits out of the method.
        2. If connected, it prints a message and updates the button states.
        3. Calls the `stop_leds` method to change the LED status.
        4. Calls the parent's `stop_reading` method in the RootGUI class to stop data reading.
        """
        global STOP_BTN_FLAG
        global CAP_APPR_FLAG
        
        if self.check_connection():
            return
        else:
            STOP_BTN_FLAG = 1
            self.parent.stop_reading()

    def send_msg_retry(self, port, msg_type, cmd, status, status_response, *params, max_attempts=globals.MAX_ATTEMPTS):
        """
        Function to send a message to the MCU and retry if we do
        not receive expected response.

        Args:
            port (Serial): Port the serial is communicating with.
            msg_type (byte): Send message type byte.
            cmd (byte): Sent command byte.
            status (byte): Sent status byte.
            status_response (byte): Expected status response byte.
            max_attempts (int, optional): Number of maximum attempts that the message will be sent. Defaults to 10.
        Returns:
            float: Depending on the status response, the function will return a specific value or values.
        """
        global curr_data
        global vb_V
        global vp_V
        global vpiezo_tip

        msg_type_map = {
            globals.MSG_A: self.parent.ztm_serial.sendMsgA,
            globals.MSG_B: self.parent.ztm_serial.sendMsgB,
            globals.MSG_C: self.parent.ztm_serial.sendMsgC,
            globals.MSG_D: self.parent.ztm_serial.sendMsgD,
            globals.MSG_E: self.parent.ztm_serial.sendMsgE,
        }
        
        send_msg = msg_type_map.get(msg_type)
        if send_msg is None:
            messagebox.showerror("ERROR", "Internal error. Please try again.")
            return False
        
        status_byte = globals.STAT_BYTE
        msg_bytes    = globals.MSG_BYTES
        status_msmt = ztmSTATUS.STATUS_MEASUREMENTS.value
        status_step_count = ztmSTATUS.STATUS_STEP_COUNT.value
        cmd_set_vbias = ztmCMD.CMD_SET_VBIAS.value
        cmd_adj_vpzo = ztmCMD.CMD_PIEZO_ADJ.value
        
        attempt = 0
        
        while attempt < max_attempts:
            msg_response = send_msg(port, cmd, status, *params) if msg_type != globals.MSG_E else send_msg(port, *params)
            if msg_response:
                testMsg = self.parent.serial_ctrl.receive_serial()
                # Unpack data and display on the GUI
                if testMsg:
                    testMsg_hex = list(testMsg)
                    # checks if status byte read is the same as status byte expected AND that the response is 11 bytes long
                    if testMsg_hex[status_byte] == status_response and len(testMsg) == msg_bytes:
                        unpackResponse = self.parent.ztm_serial.unpackRxMsg(testMsg)
                        
                        if isinstance(unpackResponse, tuple) and len(unpackResponse) == 3:
                            if testMsg_hex[status_byte] == status_msmt:
                                curr_data, vb_V, vp_V = unpackResponse
                                #print(f"Vbias: {vb_V} V")
                                #print(f"Vpzo: {vp_V} V")
                                
                                vpiezo_tip = vp_V
                                return True
                        elif testMsg_hex[status_byte] == status_step_count:
                                return unpackResponse  
                            
                        return True
                    elif testMsg_hex[status_byte] == status_msmt:
                        if cmd == cmd_set_vbias:
                            vb_V = round(Convert.get_Vbias_float(struct.unpack('H',bytes(testMsg[7:9]))[0]), 3)
                            #print(f"Vbias: {vb_V} V")
                            
                            return vb_V
                        elif cmd == cmd_adj_vpzo:
                            vp_V = round(Convert.get_Vpiezo_float(struct.unpack('H',bytes(testMsg[9:11]))[0]), 3) 
                            #print(f"Vpzo: {vp_V} V")
                            
                            return vp_V
                attempt += 1
            else:
                messagebox.showerror("ERROR", "Error. Please try again.")
                return False
    
    def send_msg_cap_approach(self, port, cmd, status, status_response, timeout=globals.TIMEOUT):
        """
        Function to send a message to the MCU and retry if we do
        not receive the expected response, using a timeout instead of a fixed sleep.

        Args:
            port (Serial): Port the serial is communicating with.
            cmd (byte): Sent command byte.
            status (byte): Sent status byte.
            status_response (byte): Expected status response byte.
            max_attempts (int): Number of maximum attempts to send the message.
            timeout (float): Timeout period for each attempt in seconds.

        Returns:
            fft_amp, fft_freq (float): FFT amplitude and FFT frequency.
        """
        global curr_data
        global vb_V
        global vp_V
        global vpiezo_tip
        
        msg_bytes = globals.MSG_BYTES
        status_byte = globals.STAT_BYTE
        fft_status = ztmSTATUS.STATUS_FFT_DATA.value
        
        attempt = 0
        
        msg_response = self.parent.ztm_serial.sendMsgC(port, cmd, status)
        if msg_response:
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                testMsg = self.parent.serial_ctrl.ztmGetMsg()
                if testMsg:
                    testMsg_hex = list(testMsg)
                    
                    if testMsg_hex[status_byte] == status_response and len(testMsg) == msg_bytes:
                        unpackResponse = self.parent.ztm_serial.unpackRxMsg(testMsg)

                        if isinstance(unpackResponse, tuple) and len(unpackResponse) == 2 and testMsg_hex[status_byte] == fft_status:
                            fft_amp, fft_freq = unpackResponse
                            curr_data = fft_amp
                            #print(f"Current measurement: {curr_data}")
                            return fft_amp, fft_freq
            attempt += 1
        else:
            messagebox.showerror("ERROR", "Error, no response received. Please try again.")
            return False
        messagebox.showerror("ERROR", "Error. Please try again.")
        return False
    
    def get_float_value(self, label, default_value, value_name):
        """
        Method to error check user inputs and update widget.

        Args:
            label (tkinter Label): Label widget.
            default_value (float): Default value the widget could be set to.
            value_name (string): Name of value.

        Returns:
            value (float): Value the widget will be set to.
        """
        user_input = label.get()
        
        if user_input == '':
            value = 0.0
            print(f"Empty input detected for {value_name}. Setting value to 0.0.")
            return value
        
        try:
            value = float(user_input)
        except ValueError:
            print(f"Invalid input for {value_name}. Using default value of {default_value}.")
            messagebox.showerror("INVALID VALUE", f"Invalid input for {value_name}. Using default value of {default_value}.")
            value = default_value
        
        return value
    
############################################# TIP APPROACH #################################################
    '''
    def tunneling_approach(self):
        """
        Starts the tunneling approach algorithm ina  separate thread to avoid freezing
        the GUI.
        """
        self.tunn_approach_thread = threading.Thread(target=self._tunneling_approach_impl)
        self.tunn_approach_thread.start()
    '''
    
    def tunneling_approach(self):
        """
        This function looks for a desired tunneling current using the traditional algorithm.
        """
        global STOP_BTN_FLAG
        global PERIODICS_FLAG
        global CAP_APPR_FLAG
        global TUNN_APPR_FLAG
        global TUNN_APPROACH_ESCAPE_FLG
        global FEEDBACK_CTRL_FLAG
        
        global POS_CURR_SETPOINT_FLAG
        global NEG_CURR_SETPOINT_FLAG
        global POS_SAMPLE_BIAS_FLAG
        global NEG_SAMPLE_BIAS_FLAG
        
        global curr_setpoint
        global vpiezo_tip
        global tunneling_steps
        global curr_data
        global vb_V
        global vp_V
        
        if self.check_connection():
            return
        else:
        ##########    
            port = self.parent.serial_ctrl.serial_port
            
            if not self.saveCurrentSetpoint():
                messagebox.showerror("ERROR", "Error. Please enter a current setpoint.")
                return 
            if not self.saveSampleBias():
                messagebox.showerror("ERROR", "Error. Please enter a sample bias.")
                return
            if not POS_CURR_SETPOINT_FLAG == POS_SAMPLE_BIAS_FLAG or not NEG_CURR_SETPOINT_FLAG == NEG_SAMPLE_BIAS_FLAG:
                messagebox.showerror("ERROR", "Error. Please enter a current setpoint and sample bias with the same signage.")
                return
            
            TUNN_APPR_FLAG = 1
            CAP_APPR_FLAG = 0
            PERIODICS_FLAG = 0
            FEEDBACK_CTRL_FLAG = 0
            TUNN_APPROACH_ESCAPE_FLG = 0
            
            # Set sample size to TUNNELING_SAMPLE_SIZE
            self.send_msg_retry(port, globals.MSG_B, ztmCMD.CMD_SET_ADC_SAMPLE_SIZE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.TUNNELING_SAMPLE_SIZE)

            
            # Get a measurement from the MCU, send_msg_retry() will change the val of the global vars curr, vbias, vpzo
            success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_DATA.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_MEASUREMENTS.value)
                       
            if success:
                # Resets visual graph and data
                self.parent.graph_gui.reset_graph()
                
                # Turns interactive graph on
                ### TURNED OFF FOR DEBUGGING
                #plt.ion()
                
                self.startup_leds()
                self.initializer.disable_widgets(self)

                #stepDownDelayCounter = 0
                #stepDownThreshold = 3
                while True:
                    if STOP_BTN_FLAG == 1:
                        plt.ioff()
                        self.stop_leds()
                        self.initializer.enable_widgets(self)
                        return
                    
                    success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_DATA.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_MEASUREMENTS.value)
                    
                    if success:
                        # Immediately step back and return if current >= target
                        if(curr_data >= curr_setpoint):
                            adjust_success = self.send_msg_retry(port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.EIGHTH_STEP, globals.DIR_UP, globals.NUM_STEPS)
                            self.piezo_full_retract()
                            if adjust_success:
                                tunneling_steps -= globals.INC_EIGHT
                                TUNN_APPROACH_ESCAPE_FLG = 1
                                
                                break
                                #return 1, curr_data, vb_V, vp_V, tunneling_steps
                            else:
                                messagebox.showerror("ERROR", "Error. Unable to adjust the stepper motor.")
                        else:       
                            # delay stepping down by stepDownThreshold samples                   
                            #if(stepDownDelayCounter == stepDownThreshold-1):
                            vpiezo_tip, tunneling_steps = self.auto_move_tip(tunneling_steps, globals.APPROACH_STEP_SIZE_NM, globals.DIR_DOWN)
                            #stepDownDelayCounter = (stepDownDelayCounter + 1) % stepDownThreshold
                        
                        self.update_label()
                        self.parent.graph_gui.update_graph('tunneling_approach')
                STOP_BTN_FLAG = 0
                plt.ioff()
                messagebox.showinfo("TUNNELING APPROACH", f"Success. The tunneling approach has ended. Received {curr_data} nA at Piezo Voltage of {vpiezo_tip} V. You can now enter the feedback controller.")
                #self.feedback_ctrl_btn.configure(state="normal")
                self.stop_leds()
                self.initializer.enable_widgets(self)
            else:
                messagebox.showerror("ERROR", "Error. Did not receive correct response back.")
        # Turns interactive graph off
        #plt.ioff()
        #self.stop_leds()
        #self.initializer.enable_widgets(self)
############################################# END OF TIP APPROACH #################################################

############################################# FEEDBACK CONTROL #################################################
    #def feedback_controller(self):
    #    """
    #    Starts the feedback controller separate thread to avoid freezing
    #    the GUI.
    #    """
    #    self.feedback_ctrl_thread = threading.Thread(target=self._feedback_ctrl_impl)
    #    self.feedback_ctrl_thread.start()
    #
        
    def feedback_controller(self):# _feedback_ctrl_impl(self):
        """
        This function uses feedback to hold a desired tunneling current.

        Args:
            target_curr (float): This is the target tunneling current.
        """
        global STOP_BTN_FLAG
        global FEEDBACK_CTRL_FLAG
        global TUNN_APPR_FLAG
        
        global POS_CURR_SETPOINT_FLAG
        global NEG_CURR_SETPOINT_FLAG
        global POS_SAMPLE_BIAS_FLAG
        global NEG_SAMPLE_BIAS_FLAG
        
        global curr_setpoint
        global vpiezo_tip
        global tunneling_steps
        global curr_data
        global vb_V
        global vp_V
        
        if self.check_connection():
            return
        else:
        ##########    
            TUNN_APPR_FLAG = 0
            FEEDBACK_CTRL_FLAG = 1
            sum = 0
            errors = [0 for _ in range(3)]
            avg_error = 0
            error_index = 0
    
            #if FEEDBACK_CTRL_FLAG == 0:
            #    messagebox.showerror("ERROR", "Error. Tunneling current has not been found yet.")
            #    return 
            
            port = self.parent.serial_ctrl.serial_port
            
            if not self.saveCurrentSetpoint():
                messagebox.showerror("ERROR", "Error. Please enter a current setpoint.")
                return 
            #if not self.saveSampleBias():
            #    messagebox.showerror("ERROR", "Error. Please enter a sample bias.")
            #    return

            if not POS_CURR_SETPOINT_FLAG == POS_SAMPLE_BIAS_FLAG or not NEG_CURR_SETPOINT_FLAG == NEG_SAMPLE_BIAS_FLAG:
                messagebox.showerror("ERROR", "Error. Please enter a current setpoint and sample bias with the same signage.")
                return
            
            self.parent.clear_buffer()
            
            # Set sample size to 26
            self.send_msg_retry(port, globals.MSG_B, ztmCMD.CMD_SET_ADC_SAMPLE_SIZE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.CONTROLLER_DEFAULT_SMPL_SZ)

            # Get a measurement from the MCU, send_msg_retry() will change the val of the global vars curr, vbias, vpzo
            success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_DATA.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_MEASUREMENTS.value)
            
            if success:
                # Resets visual graph and data
                self.parent.graph_gui.reset_graph()
                plt.ion()
                self.startup_leds()
                self.initializer.disable_widgets(self)
                last_error = curr_setpoint - curr_data
                while True:
                    if STOP_BTN_FLAG == 1:
                        plt.ioff()
                        self.stop_leds()
                        self.initializer.enable_widgets(self)
                        STOP_BTN_FLAG = 0
                        return
                    
                    # Request Measurement
                    success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_DATA.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_MEASUREMENTS.value)
                    
                    if success:
                        error = curr_setpoint - curr_data
                        avg_error += ((error - errors[error_index]) / 3)
                        errors[error_index] = error
                        error_index = (error_index + 1) % 3
                        # If no tunneling current is detected, step down with a constant step size
                        if(curr_data < globals.CONTROLLER_MIN_CURR):
                            vpiezo_tip, tunneling_steps = self.auto_move_tip(tunneling_steps, globals.CONTROLLER_CONST_STEP_SZ_NM, globals.DIR_DOWN)
                            sum = 0
                            last_output = 0
                        # Use feedback control to maintain target current
                        else:
                            sum += avg_error * globals.Ts
                            dist = avg_error * globals.Kp + globals.Ki * sum + (globals.Kd * (avg_error - last_error) / globals.Ts)
                            last_error = avg_error
                            #print(f"Vpzo = {vpiezo_tip}, dist = {dist}, error = {error}, steps = {tunneling_steps}") ## DEBUG
                            if(dist < 0):
                                vpiezo_tip, tunneling_steps = self.auto_move_tip(tunneling_steps, -dist, globals.DIR_UP)               
                                #time.sleep(0.005)
                            else:
                                vpiezo_tip, tunneling_steps = self.auto_move_tip(tunneling_steps, dist, globals.DIR_DOWN)
                                #time.sleep(0.005)

                        self.update_label()
                        self.parent.graph_gui.update_graph('feedback_control')
            else:
                messagebox.showerror("ERROR", "Error. Did not receive correct response back.")
                # Turns interactive graph off
                plt.ioff()
                self.stop_leds()
                self.initializer.enable_widgets(self)
############################################# END OF FEEDBACK CONTROL #################################################

    def auto_move_tip(self, steps, dist, dir):
        """
        This function changes the tip height using either the piezo or stepper motor.
        Note: If the distance is out of range for the piezo then the stepper motor will step up
        or down, and the new distance will not be exactly what was desired. This function was 
        created for the tunneling_approach function.

        Args:
            steps (float): Tne number of steps the microscope moves during the approach.
            dist (float): The desired change in distance in nm.
            dir (int): Direction for tip to move. Send "DOWN" to move tip down and "UP" to move tip up.
        Returns:
            vpiezo_tip (float): Global variable that collects the vpiezo value during the tunneling approach process.
            steps (float): The number of steps the microscope moves during the approach.
        """
        global vpiezo_tip
        
        port = self.parent.serial_ctrl.serial_port
        stepSet = False
        piezoSet = False
        delta_V = dist / globals.PIEZO_EXTN_RATIO
        
        # MOVING DOWN
        if(dir == globals.DIR_DOWN):
            # Piezo is fully extended, so we retract the tip and step the motor down
            if(vpiezo_tip + delta_V > globals.VPIEZO_APPROACH_MAX):
                vpiezo_tip = self.piezo_full_retract()
                # Move stepper motor DOWN an eighth step
                while(stepSet == False):
                    stepSet = self.send_msg_retry(port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.EIGHTH_STEP, globals.DIR_DOWN, globals.NUM_STEPS)
                # Increment number of steps 
                steps += globals.INC_EIGHT
            # Increment the piezo voltage by delta_V to step it down
            else:
                vpiezo_tip += delta_V
                # Send message to update vpiezo
                while(piezoSet == False):
                    piezoSet = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_PIEZO_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, vpiezo_tip)
        ########################################################################
        # MOVING UP
        else:
            if(vpiezo_tip - delta_V < globals.VPIEZO_APPROACH_MIN):
            # Piezo is fully retracted, so we extend the tip and step the motor up
            # Place the tip in approximately the same position
                # Move stepper motor UP an eighth step    
                while(stepSet == False):
                    stepSet = self.send_msg_retry(port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.EIGHTH_STEP, globals.DIR_UP, globals.NUM_STEPS)
                # Decrement number of steps 
                steps -= globals.INC_EIGHT
                #vpiezo_tip = self.piezo_full_extend()
            else:
                vpiezo_tip -= delta_V
                # Send message to update vpiezo
                while(piezoSet == False):
                    piezoSet = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_PIEZO_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, vpiezo_tip)
        #print(f"\nNew vpiezo for tip approach: {vpiezo_tip} V\nStep Count: {steps}")   # Debug 
        return vpiezo_tip, steps
                
    def piezo_full_extend(self):
        """
        This function adjusts the tip down in increments instead of one total distance.

        Args:
            vpiezo_tip (float): Global variable that collects the vpiezo value during the tunneling approach process.
        """
        global vpiezo_tip

        port = self.parent.serial_ctrl.serial_port
        piezoSet = False
        
        # Extend piezo in small increments
        piezoStep = vpiezo_tip / 32
        while (vpiezo_tip != globals.VPIEZO_APPROACH_MAX):
            if vpiezo_tip < globals.VPIEZO_APPROACH_MAX:
                vpiezo_tip += piezoStep
            elif vpiezo_tip > globals.VPIEZO_APPROACH_MAX:
                vpiezo_tip = globals.VPIEZO_APPROACH_MAX
            while(piezoSet == False):
                piezoSet = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_PIEZO_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, vpiezo_tip)
            piezoSet = False
        return vpiezo_tip
    
    def piezo_full_retract(self):
        """
        This function adjusts the tip up in increments instead of one total distance.

        Returns:
            vpiezo_tip (float): Global variable that collects the vpiezo value during the tunneling approach process.
        """
        global vpiezo_tip

        port = self.parent.serial_ctrl.serial_port
        piezoSet = False

        # Retract piezo in small increments
                                   
        piezoStep = (vpiezo_tip - globals.VPIEZO_APPROACH_MIN)/ 32
        while (vpiezo_tip > globals.VPIEZO_APPROACH_MIN):
            vpiezo_tip -= piezoStep
            if vpiezo_tip < globals.VPIEZO_APPROACH_MIN:
                vpiezo_tip = globals.VPIEZO_APPROACH_MIN
            while(piezoSet == False):
                piezoSet = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_PIEZO_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, vpiezo_tip)
            piezoSet = False
        return vpiezo_tip


############################################# CAPACITANCE APPROACH #################################################
    def cap_approach(self):
        """
        Starts the capacitance approach algorithm in a separate thread to avoid
        freezing the GUI.
        """
        self.cap_approach_thread = threading.Thread(target=self._cap_approach_impl)
        self.cap_approach_thread.start()

    
    def _cap_approach_impl(self):
        """
        This function gets the tip close to the sample by using the displacement current
        between the tip and the sample. It looks at the difference between the present displacement
        current and a previous displacement current. It uses a circular buffer to store the delayed
        displacement currents.
        """
        global STOP_BTN_FLAG
        global vbias_save
        
        if self.check_connection():
            return
        else:
            port = self.parent.serial_ctrl.serial_port
            
            # Start Sinusoidal Vbias
            success = self.send_msg_retry(port, globals.MSG_E, ztmCMD.CMD_VBIAS_SET_SINE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.CAP_APPROACH_AMPL, globals.CAP_APPROACH_FREQ)
            
            if success:
                #########
                # init gui stuff
                self.parent.graph_gui.reset_graph()
                plt.ion()
                self.startup_leds()
                self.initializer.disable_widgets(self)
                
                #######
                # start cap approach
                fft_meas = self.get_fft_peak()
                if fft_meas is None:
                    return

                # Using deque for efficient circular buffer management
                    # load fft_buffer with zeros
                fft_buffer = deque([0] * globals.FFT_AVG_LENGTH, maxlen=globals.FFT_AVG_LENGTH)
                    # load delay_line with first fft msmt
                delay_line = deque([fft_meas] * (globals.DELAY_LINE_LEN), maxlen=globals.DELAY_LINE_LEN)
                    # load difference buffer with zeros
                diff_buffer = deque([0] * (globals.DIFF_AVG_BUF_LEN), maxlen=globals.DIFF_AVG_BUF_LEN)
                
                
                not_done = True
                # index counters
                fft_count = 0
                delay_index = 0
                diff_index = 0
                # variables
                avg_diff = 0
                diff = 0
                fft_peak = 0
                
                # cap approach process
                while not_done:
                    if STOP_BTN_FLAG == 1:
                        break
                        '''
                        plt.ioff()
                        self.stop_leds()
                        self.initializer.enable_widgets(self)
                        self.parent.clear_buffer()
                        self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_VBIAS_STOP_SINE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)
                        STOP_BTN_FLAG = 0
                        return
                        '''
                    
                    # Measure fft peak and update the peaks buffer
                    # gather 5 FFT's
                    while(fft_count < globals.FFT_AVG_LENGTH):
                        fft_sample = self.get_fft_peak()
                        if fft_sample is None:
                            continue  # Skip this iteration if FFT measurement failed

                        fft_buffer[fft_count] = fft_sample
                        fft_count += 1
                    # reset counter    
                    fft_count = 0    
                    # Calculate the average of the peak measurements
                    # call this 'fft_peak' for now
                    fft_peak = self.get_avg_meas(fft_buffer)    
                      
                    # calculate new difference
                    diff = fft_peak - delay_line[delay_index]
                    # update average difference
                    avg_diff = avg_diff + (diff - diff_buffer[diff_index])/globals.DIFF_AVG_BUF_LEN 
                    # load the avg FFT into delay line
                    delay_line[delay_index] = fft_peak
                    # load difference buffer
                    diff_buffer[diff_index] = diff
                    
                    # update indices
                    diff_index = (diff_index + 1) %  globals.DIFF_AVG_BUF_LEN       
                    delay_index = (delay_index + 1) %  globals.DELAY_LINE_LEN 

                    # Check if difference exceeds the threshold
                    if diff > globals.CRIT_CAP_SLOPE:
                        not_done = False
                        vbias_save = 0.0
                    else:
                        self.send_msg_retry(port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.EIGHTH_STEP, globals.DIR_DOWN, globals.CAP_APPROACH_NUM_STEPS)

                    self.update_label()
                    self.parent.graph_gui.update_graph('cap_approach')

                # Process when the capacitance approach is complete
                STOP_BTN_FLAG = 0   
                plt.ioff()
                self.stop_leds()
                self.initializer.enable_widgets(self)
                self.parent.clear_buffer()
                self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_VBIAS_STOP_SINE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)
                
                self.root.focus()
                self.label6.delete(0, END)
                self.label6.insert(0, str(vbias_save)) 
    
    def get_fft_peak(self):
        """
        Retrieve the FFT peak data from the device.

        Returns:
            peak (float): FFT peak data measurement.
        """
        global STOP_BTN_FLAG
        
        port = self.parent.serial_ctrl.serial_port
        
        if STOP_BTN_FLAG == 1:
            return None
        
        result = self.send_msg_cap_approach(port, ztmCMD.CMD_REQ_FFT_DATA.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_FFT_DATA.value)
        if result is None or STOP_BTN_FLAG == 1:
            return None
        else:
            #self.update_label()
            #self.parent.graph_gui.update_graph()
            peak, _ = result
            return peak
    
    def get_avg_meas(self, measurements):
        """
        Calculate the average of the valid FFT measurements.

        Args:
            measurements (list): List of valid FFT measurements.
        Returns:
            sum(valid_measurements) / len(valid_measurements) (float): Average of the FFT measurements.
        """
        global STOP_BTN_FLAG
        
        if STOP_BTN_FLAG == 1:
            return None
        
        valid_measurements = [m for m in measurements if m is not None]
        if not valid_measurements or STOP_BTN_FLAG == 1:
            return None
        return sum(valid_measurements) / len(valid_measurements)
############################################# END OF CAPACITANCE APPROACH #################################################

    def enable_periodics(self):
        """
        Function to enable and read periodic data from the MCU.
        """
        global STOP_BTN_FLAG
        global curr_data
        global vp_V
        
        status_byte = globals.STAT_BYTE
        status_msmt = ztmSTATUS.STATUS_MEASUREMENTS.value
        status_ack  = ztmSTATUS.STATUS_ACK.value
        status_done = ztmSTATUS.STATUS_DONE.value
        status_clr  = ztmSTATUS.STATUS_CLR.value
        msg_c       = globals.MSG_C
        cmd_periodic_data = ztmCMD.CMD_PERIODIC_DATA_ENABLE.value
        
        if self.check_connection():
            return
        else:
        ########## 
            port = self.parent.serial_ctrl.serial_port
            
            enable_data_success = self.send_msg_retry(port, msg_c, cmd_periodic_data, status_clr, status_done)
            
            if enable_data_success:
                # Resets visual graph and data
                self.parent.graph_gui.reset_graph() 
                # Turns interactive graph on
                plt.ion()
                
                self.startup_leds()
                self.initializer.disable_widgets(self)
                
                while STOP_BTN_FLAG == 0:
                    response = self.parent.serial_ctrl.ztmGetMsg()
                    if response:
                        if response[status_byte] == status_msmt or response[status_byte] == status_ack:
                            curr_data = round(struct.unpack('f', bytes(response[3:7]))[0], 3) 
                            vp_V = round(Convert.get_Vpiezo_float(struct.unpack('H',bytes(response[9:11]))[0]), 3) 
                            #print(f"Vpiezo: {vp_V}") 
                    self.update_label()
                    self.parent.graph_gui.update_graph('enable_periodics') 
            else:
                messagebox.showerror("ERROR.", "Failed to enable periodic data. Try again.")
            # Turns interactive graph off
            plt.ioff()    
            self.stop_leds()
            self.initializer.enable_widgets(self)
            STOP_BTN_FLAG = 0

    ############################################################################################################
    ###################################### DELETE LATER, DON'T FORGET ##########################################
    def saveKp(self, _=None):
            self.root.focus()
            globals.Kp = float(self.kp_label.get())
            print(f"Saved Kp: {globals.Kp}")

    def saveKd(self, _=None):
            self.root.focus()
            globals.Kd = float(self.kd_label.get())
            print(f"Saved Kd: {globals.Kd}")

    def saveKi(self, _=None):
            self.root.focus()
            globals.Ki = float(self.ki_label.get())
            print(f"Saved Ki: {globals.Ki}")

    ###################################### DELETE LATER, DON'T FORGET ##########################################   
    ############################################################################################################
     
    def savePiezoValue(self, _=None):         
        """
        Method to save the piezo voltage delta value; the
        value cannot be less than 3 mV.

        Args:
            event (_type_): [ADD DESCRIPTION HERE.]
        """
        if self.check_connection():
            self.root.focus()
            return
        else:
            self.root.focus()
            
            vpzo_value = self.get_float_value(self.label10, 1.0, "Piezo Voltage")
            if vpzo_value < globals.VPIEZO_DELTA_MIN:
                vpzo_value = globals.VPIEZO_DELTA_MIN
                messagebox.showerror("Invalid Value", f"Invalid input. Voltage is too small, defaulted to {globals.VPIEZO_DELTA_MIN*1000} mV.")

            self.label12.configure(text=f"{0:.3f} ")
            self.label10.delete(0, END)
            self.label10.insert(0, str(vpzo_value))
        
        self.updateVpzoDistance(vpzo_value)
    
    def updateVpzoDistance(self, delta):
        """
        Method to update the vpiezo approximate distance.

        Args:
            delta (float): User inputted vpiezo delta value.
        """
        vpzo_dist = delta * globals.PIEZO_EXTN_RATIO
        self.label11.configure(text=f"{vpzo_dist:.3f}")
        
    def piezo_inc(self):
        """
        Method to identify that the up arrow was pressed for Vpzo.
        """
        if self.check_connection():
            return
        else: 
            self.vpzo_up = 1
            self.vpzo_down = 0
            self.sendPiezoAdjust()
    
    def piezo_dec(self):
        """
        Method to identify that the down arrow was pressed for Vpzo.
        """
        if self.check_connection():
            return
        else:
            self.vpzo_down = 1
            self.vpzo_up = 0
            self.sendPiezoAdjust()
        
    def sendPiezoAdjust(self):
        """
        Method to send total piezo voltage to MCU, with a valid range
        of 0 to 10 V.
        """
        global vpiezo_tip
        
        if self.check_connection():
            return
        else:
            port = self.parent.serial_ctrl.serial_port
            
            delta_v_float = self.get_float_value(self.label10, 1.0, "Piezo Voltage")
            if globals.VPIEZO_MIN <= vpiezo_tip <= globals.VPIEZO_MAX:
                if self.vpzo_up:
                    if vpiezo_tip + delta_v_float <= globals.VPIEZO_MAX:
                        vpiezo_tip += delta_v_float
                    else:
                        vpiezo_tip = globals.VPIEZO_MAX
                        messagebox.showerror("INVALID", "Total voltage exceeds 10 V. Maximum allowed is 10 V.")
                        return
                    self.vpzo_up = 0
                elif self.vpzo_down:
                    if vpiezo_tip - delta_v_float >= globals.VPIEZO_MIN:
                        vpiezo_tip -= delta_v_float
                    else:
                        vpiezo_tip = globals.VPIEZO_MIN
                        messagebox.showerror("INVALID", "Total voltage is below 0 V. Minimum allowed is 0 V.")
                        return
                    self.vpzo_down = 0
            else:
                messagebox.showerror("INVALID", "Invalid range. Stay within 0 - 10 V.")
                return

            # Clear buffer
            self.parent.clear_buffer()
                
            start_time = time.time()
            success = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_PIEZO_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, vpiezo_tip)

            while not success and (time.time() - start_time) < globals.TIMEOUT:
                success = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_PIEZO_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, 0, vpiezo_tip)
            if isinstance(success, bool):       # If we received a DONE msg
                if success:
                    self.label12.configure(text=f"{vpiezo_tip:.3f} ")
                    return
                else:
                    messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
            elif isinstance(success, float):    # If we received a MEASUREMENT msg
                # Clear buffer
                self.parent.clear_buffer()
                
                # Get msg
                testMsg = self.parent.serial_ctrl.ztmGetMsg()

                # Unpack new vpzo value
                _, _, vpzo_new = self.parent.ztm_serial.unpackRxMsg(testMsg)
                
                if abs(vpzo_new - vpiezo_tip) <= 0.05 * vpiezo_tip:
                    self.label12.configure(text=f"{vpiezo_tip:.3f} ")
                    return
                else:
                    messagebox.showinfo("Information", f"Did not process change in value within {globals.TIMEOUT} period. Please try again.")
                
    def saveCurrentSetpoint(self, _=None): 
        """
        Function to save the user inputted value of current setpoint to use for 
        the tip approach algorithm. The valid range is 0.1 nA to 10 nA.
        
        Args:
            _ (_type_): [ADD DESCRIPTION HERE.]
        """
        global curr_setpoint 
        global POS_CURR_SETPOINT_FLAG
        global NEG_CURR_SETPOINT_FLAG
        
        self.root.focus()
        if self.check_connection():
            return
        else:
            curr_setpoint = self.get_float_value(self.label3, 0.0, "current setpoint")
            if globals.POS_CURR_SETPOINT_MIN <= curr_setpoint <= globals.POS_CURR_SETPOINT_MAX:
                POS_CURR_SETPOINT_FLAG = 1
                NEG_CURR_SETPOINT_FLAG = 0
                return True
            elif globals.NEG_CURR_SETPOINT_MIN <= curr_setpoint <= globals.NEG_CURR_SETPOINT_MAX:
                NEG_CURR_SETPOINT_FLAG = 1
                POS_CURR_SETPOINT_FLAG = 0
                return True
            else:
                NEG_CURR_SETPOINT_FLAG = 0
                POS_CURR_SETPOINT_FLAG = 0
                self.label3.delete(0,END)
                self.label3.insert(0,0.000)
                return False


    def saveCurrentOffset(self, _=None): 
        """
        Save current offset and uses to offset the graph.
        QUESTION: Range for current offset?

        Args:
            event (_type_): [ADD DESCRIPTION HERE.]
        """
        if self.check_connection():
            self.root.focus()
            return
        else:
            user_input = self.label4.get()
            if user_input == '':
                self.root.focus()
                self.label4.delete(0,END)
                self.label4.insert(0,0.000)
                
            try:
                self.curr_offset = float(self.label4.get())
                self.root.focus()
            except ValueError:
                self.root.focus()
                self.label4.delete(0,END)
                self.label4.insert(0,0.000)
                messagebox.showerror("Invalid Value", "Error. Please enter a valid input.")

    def saveSampleBias(self, _=None): 
        """
        Function to send vbias msg to the MCU and waits for a DONE response, 
        witha  valid range of -10 V to 10 V.

        Args:
            event (_type_): [ADD DESCRIPTION HERE.]
        """
        global vbias_save
        global vbias_done_flag
        global TUNN_APPR_FLAG
        global POS_SAMPLE_BIAS_FLAG
        global NEG_SAMPLE_BIAS_FLAG
        
        if self.check_connection():
            self.root.focus()
            return
        else:
            self.root.focus()
            port = self.parent.serial_ctrl.serial_port
            try:
                # Checks if it is a non-numeric value
                vbias_save = self.get_float_value(self.label6, 0.0, "sample bias")
                
                if TUNN_APPR_FLAG:
                    if vbias_save == None:
                        vbias_save = 0.0
                        messagebox.showerror("Invalid Value", f"Invalid voltage bias. Please enter a nonzero value.")
                        self.label6.delete(0, END)
                        self.label6.insert(0, vbias_save)
                        return
                    elif vbias_save == 0.0:
                        self.label6.delete(0, END)
                        self.label6.insert(0, vbias_save)
                        return
                
                # Checks if it is within range
                if vbias_save < globals.VBIAS_MIN:
                    vbias_save = globals.VBIAS_MIN + 1
                    messagebox.showerror("Invalid Value", f"Invalid input. Sample bias cannot subceed -10 V.")
                elif vbias_save > globals.VBIAS_MAX:
                    vbias_save = globals.VBIAS_MAX - 1
                    messagebox.showerror("Invalid Value", f"Invalid input. Sample bias cannot exceed 10 V.")
                    
                if globals.VBIAS_MIN <= vbias_save < 0:
                    NEG_SAMPLE_BIAS_FLAG = 1
                    POS_SAMPLE_BIAS_FLAG = 0
                elif 0 < vbias_save < globals.VBIAS_MAX:
                    POS_SAMPLE_BIAS_FLAG = 1
                    NEG_SAMPLE_BIAS_FLAG = 0
                else:
                    POS_SAMPLE_BIAS_FLAG = 0
                    NEG_SAMPLE_BIAS_FLAG = 0
                    
                self.label6.delete(0, END)
                self.label6.insert(0, vbias_save)
                    
                # Clear buffer
                self.parent.clear_buffer()
                         
                start_time = time.time()
                success = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_SET_VBIAS.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, vbias_save, 0)

                while not success and (time.time() - start_time) < globals.TIMEOUT:
                    success = self.send_msg_retry(port, globals.MSG_A, ztmCMD.CMD_SET_VBIAS.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, 0, vbias_save, 0)
                
                if isinstance(success, bool):       # if we received a DONE msg
                    if success:
                        return True
                    else:
                        messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
                elif isinstance(success, float):    # if we received a MEASUREMENT msg
                    # Clear buffer
                    self.parent.clear_buffer()
                    
                    # Get newest vbias value
                    testMsg = self.parent.serial_ctrl.ztmGetMsg()

                    _, vbias_new, _ = self.parent.ztm_serial.unpackRxMsg(testMsg)
                    
                    if abs(vbias_new - vbias_save) <= 0.05 * vbias_save:
                        return
                    else:
                        messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
                else:
                    messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
            except ValueError:
                self.root.focus()
                self.label6.delete(0, END)
                messagebox.showerror("Invalid Value", "Please enter a number from -10 V to 10 V.")
            
            
    def saveSampleRate(self, _=None):
        """
        Saves sample rate as an integer and sends that to the MCU.

        Args:
            _ (_type_): [ADD DESCRIPTION HERE.]
        """
        global sample_rate_done_flag
        global sample_rate_save
        
        if self.check_connection():
            return
        else:
            port = self.parent.serial_ctrl.serial_port
            
            if self.sample_rate_var.get() == "25 kHz":
                sample_rate_save = 25000
            elif self.sample_rate_var.get() == "12.5 kHz":
                sample_rate_save = 12500
            elif self.sample_rate_var.get() == "37.5 kHz":
                sample_rate_save = 37500
            elif self.sample_rate_var.get() == "10 kHz":
                sample_rate_save = 10000
            elif self.sample_rate_var.get() == "5 kHz":
                sample_rate_save = 5000

            # Clear buffer
            self.parent.clear_buffer()
                        
            start_time = time.time()
            success = self.send_msg_retry(port, globals.MSG_B, ztmCMD.CMD_SET_ADC_SAMPLE_RATE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, sample_rate_save)

            while not success and (time.time() - start_time) < globals.TIMEOUT:
                success = self.send_msg_retry(port, globals.MSG_B, ztmCMD.CMD_SET_ADC_SAMPLE_RATE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, sample_rate_save)
            
            if success:
                sample_rate_done_flag = 1
                return
            else:
                sample_rate_done_flag = 0
                messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
                
    def saveSampleSize(self, _=None):
        """
        Send sample size as an integer and sends that to the MCU with a
        valid range of 1 to 1024.

        Args:
            _ (_type_): [ADD DESCRIPTION HERE.]
        """
        global sample_size_save
        global sample_size_done_flag
        if self.check_connection():
            self.root.focus()
            return
        else:
            self.root.focus()
            port = self.parent.serial_ctrl.serial_port
            
            try:
                sample_size_save = int(self.sample_size_entry.get())
                if sample_size_save not in range(1, 1025):
                    if sample_size_save < 1:
                        sample_size_save = 1
                        messagebox.showerror("Invalid Value", "Invalid input. Sample size cannot subceed 1.")
                    elif sample_size_save > 1024:
                        sample_size_save = 1024
                        messagebox.showerror("Invalid Value", "Invalid input. Sample size cannot exceed 1024.")

                    sample_size_str = str(sample_size_save)
                    self.root.focus()
                    self.sample_size_entry.delete(0, END)
                    self.sample_size_entry.insert(0, sample_size_str)

                # Clear buffer
                self.parent.clear_buffer()
                         
                start_time = time.time()
                success = self.send_msg_retry(port, globals.MSG_B, ztmCMD.CMD_SET_ADC_SAMPLE_SIZE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, sample_size_save)

                while not success and (time.time() - start_time) < globals.TIMEOUT:
                    success = self.send_msg_retry(port, globals.MSG_B, ztmCMD.CMD_SET_ADC_SAMPLE_SIZE.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, sample_size_save)
                
                if success:
                    sample_size_done_flag = 1
                    return
                else:
                    sample_size_done_flag = 0
                    messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
            except ValueError:
                self.root.focus()
                self.sample_size_entry.delete(0, END)
                messagebox.showerror("Invalid Value", "Invalid input. Please enter a whole number from 1 to 1024.")
                        
    def saveStepperMotorAdjust(self, _=None):
        """
        Saves adjust stepper motor step size as an integer 'fine_adjust_step_size' .

        Args:
            _ (_type_): [ADD DESCRIPTION HERE.]
        """
        if self.check_connection():
            return
        else:
            if self.coarse_adjust_var.get() == "Full":
                self.fine_adjust_step_size = globals.FULL_STEP
                approx_step_distance = globals.FULL_STEP_DISTANCE   
            elif self.coarse_adjust_var.get() == "Half":
                self.fine_adjust_step_size = globals.HALF_STEP
                approx_step_distance = globals.HALF_STEP_DISTANCE   
            elif self.coarse_adjust_var.get() == "Quarter":
                self.fine_adjust_step_size = globals.QUARTER_STEP
                approx_step_distance = globals.QUARTER_STEP_DISTANCE   
            elif self.coarse_adjust_var.get() == "Eighth":
                self.fine_adjust_step_size = globals.EIGHTH_STEP
                approx_step_distance = globals.EIGHTH_STEP_DISTANCE  
        # Display approx distance per step size to user
        self.label5.configure(text=f"{approx_step_distance:.3f} nm")

    def stepper_motor_up(self):
        """
        Handles the button click for the stepper motor up arrow.
        """
        if self.check_connection():
            return
        else:
            self.step_up = 1
            self.step_down = 0
            self.sendStepperMotorAdjust()
    
    def stepper_motor_down(self):
        """
        Handles the button click for the stepper motor down arrow.
        """
        if self.check_connection():
            return
        else:
            self.step_down = 1
            self.step_up = 0
            self.sendStepperMotorAdjust()

    def sendStepperMotorAdjust(self):
        """
        Send stepper motor adjust msg to the MCU.
        """
        if self.check_connection():
            return
        else:
            port = self.parent.serial_ctrl.serial_port
            
            # Fine adjust direction : direction = 0 for up, 1 for down
            if self.step_up:
                fine_adjust_dir = globals.DIR_UP
                self.step_up    = 0 
            elif self.step_down:
                fine_adjust_dir = globals.DIR_DOWN
                self.step_down  = 0

            # Clear buffer
            self.parent.clear_buffer()
                        
            start_time = time.time()
            success = self.send_msg_retry(port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, self.fine_adjust_step_size, fine_adjust_dir, globals.NUM_STEPS)

            while not success and (time.time() - start_time) < globals.TIMEOUT:
                success = self.send_msg_retry(port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, self.fine_adjust_step_size, fine_adjust_dir, globals.NUM_STEPS)
            if success:
                return
            else:
                messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
              
    def save_home(self):
        """
        Function to save the new home position, where the tip is at when the function is called.
        """
        global total_steps
        
        if self.check_connection():
            return
        else:
            port = self.parent.serial_ctrl.serial_port
            
            # Clear buffer
            self.parent.clear_buffer()
            
            start_time = time.time()
            success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_STEPPER_RESET_HOME_POSITION.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)

            while not success and (time.time() - start_time) < globals.TIMEOUT:
                success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_STEPPER_RESET_HOME_POSITION.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)
            if success:
                total_steps = 0
                return
            else:
                messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")

    def return_home(self):
        """
        Method to return to the home position.

        Returns:
            _type_: _description_
        """
        timeout = globals.TIMEOUT
        
        if self.check_connection():
            return
        else:
            # Request total step for stepper motor from MCU
            port = self.parent.serial_ctrl.serial_port
            
            # Clear buffer
            self.parent.clear_buffer()

            start_time = time.time()
            
            success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_RETURN_TIP_HOME.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)
            while not success and (time.time() - start_time) < timeout:
                success = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_RETURN_TIP_HOME.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value)

            # If a home position has not been set, error message and return from function
            if total_steps == None:
                messagebox.showerror("INVALID", f"No home position has been set.")
                return
            '''
            elif home_pos_total_steps == curr_pos_total_steps:
                messagebox.showerror("INVALID", f"Stepper motor is already at home position.")
                return
            '''
            
    '''
    def return_home(self):
        """
        Function to return to the home position and send it to the MCU.
        """
        global home_pos_total_steps
        global curr_pos_total_steps
        
        if self.check_connection():
            return
        else:
            # Request total step for stepper motor from MCU
            port = self.parent.serial_ctrl.serial_port
            
            # Clear buffer
            self.parent.clear_buffer()
            
            start_time = time.time()
            curr_pos_total_steps = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_STEP_COUNT.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_STEP_COUNT.value)

            while not curr_pos_total_steps and (time.time() - start_time) < globals.TIMEOUT:
                curr_pos_total_steps = self.send_msg_retry(port, globals.MSG_C, ztmCMD.CMD_REQ_STEP_COUNT.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_STEP_COUNT.value)
                
            # If a home position has not been set, error message and return from function
            if home_pos_total_steps == None:
                messagebox.showerror("INVALID", f"No home position has been set.")
                return
            elif home_pos_total_steps == curr_pos_total_steps:
                messagebox.showerror("INVALID", f"Stepper motor is already at home position.")
                return
            
            if curr_pos_total_steps:
                # If home position is lower than the tip's current position
                if home_pos_total_steps > curr_pos_total_steps:
                    return_dir = 1 # down
                    num_of_steps = (home_pos_total_steps - curr_pos_total_steps) * 8
                    
                    # Send command to stepper motor for number of steps between current position and home position
                    num_of_steps_int = int(num_of_steps)
                    self.send_msg_retry(self.parent.serial_ctrl.serial_port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.EIGHTH_STEP, return_dir, num_of_steps_int)

                # If home position is higher than the tip's current position
                elif home_pos_total_steps < curr_pos_total_steps:
                    return_dir = 0 # up
                    num_of_steps = (curr_pos_total_steps - home_pos_total_steps) * 8
                    num_of_steps_int = int(num_of_steps)
                    # Send command to stepper motor for number of steps between current position and home position
                    self.send_msg_retry(self.parent.serial_ctrl.serial_port, globals.MSG_D, ztmCMD.CMD_STEPPER_ADJ.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_DONE.value, globals.EIGHTH_STEP, return_dir, num_of_steps_int)
                curr_pos_total_steps = self.send_msg_retry(self.parent.serial_ctrl.serial_port, globals.MSG_C, ztmCMD.CMD_REQ_STEP_COUNT.value, ztmSTATUS.STATUS_CLR.value, ztmSTATUS.STATUS_STEP_COUNT.value)
            else:
                messagebox.showinfo("Information", "Did not process change in value within timeout period. Please try again.")
        '''
        
    def check_connection(self):
        """
        Function to check that there is a valid port connection.

        Returns:
            boolean: [ADD DESCRIPTION HERE.]
        """
        global startup_flag
        
        port = self.parent.serial_ctrl.serial_port
        if port is None or startup_flag == 0:
            InfoMsg = f"ERROR. Connect to COM PORT."
            messagebox.showerror("Connection Error", InfoMsg)
            return True
        else:
            return False

    def update_label(self):
        """
        Method to update the value of ADC current in label 2.
        """
        global curr_data
        global vp_V
        
        # Get current offset from label 4
        try:
            self.curr_offset = float(self.label4.get())
        except ValueError:
            self.curr_offset = 0.0  # Default to 0 if the value is not a valid float
        curr_data += self.curr_offset
        self.label2.configure(text=f"{curr_data:.4f} nA")
        self.label12.configure(text=f"{vp_V:.5f} ")
        self.kp_label.insert(0, str(globals.Kp))
        self.kd_label.insert(0, str(globals.Kd))
        self.ki_label.insert(0, str(globals.Ki))

    def save_notes(self, _=None):
        """
        Method to save the notes inputted by the user in the notes widget.

        Args:
            _ (_type_, optional): [ADD DESCRIPTION HERE.] Defaults to None.

        Returns:
            note (string): _description_
        """
        if self.check_connection():
            self.root.focus()
            return
        else:
            self.root.focus()
            note = self.label7.get(1.0, ctk.END)
            note = note.strip()
            return note
    
    def save_date(self, _=None):
        """
        Method to save the date inputted by the user in the notes widget.

        Args:
            _ (_type_, optional): [ADD DESCRIPTION HERE.] Defaults to None.

        Returns:
            date (string): _description_
        """
        if self.check_connection():
            self.root.focus()
            return
        else:
            self.root.focus()
            date = self.label8.get()
            return date
    
    def DropDownMenu(self):
        """
        Method to list all the file menu options in a drop menu.
        """
        # Create menu bar
        self.menubar = tk.Menu(self.root)
        
        # Create drop-down menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Save", command=self.save_graph)
        self.filemenu.add_command(label="Save As", command=self.save_graph_as)
        self.filemenu.add_command(label="Export (.csv)", command=self.export_data)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        self.root.config(menu=self.menubar)
    
    def save_graph(self):
        """
        Saves the current graph image with a default file name.
        """
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        default_filename = os.path.join(downloads_folder, "current_graph.png")
        self.parent.graph_gui.fig.savefig(default_filename)
        messagebox.showinfo("Save Graph", f"Graph saved in Downloads as {default_filename}")

    def save_graph_as(self):
        """
        Saves the current graph image with a user-specified file name.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.parent.graph_gui.fig.savefig(file_path)
            messagebox.showinfo("Save Graph As", f"Graph saved as {file_path}")
    
    def export_data(self):
        """
        Menu option to export graph data into a CSV file.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w', newline='') as file:
                # Collects the user input text from the notes widget
                header_text = self.save_notes()
                header_date = self.save_date()

                # Get the last 1000 data points from deque buffers
                #num_points_to_export = 1000
                recent_times = list(self.parent.graph_gui.time_data) #[-num_points_to_export:]
                recent_currents = list(self.parent.graph_gui.y_data) #[-num_points_to_export:]

                # Conjoining and formatting data
                headers = ["Time", "Current (nA)"]
                data_to_export = [headers]
                data_to_export.extend(zip(recent_times, recent_currents))

                # Writing to file being created
                writer = csv.writer(file)
                # If the header notes widget has been used, include information in .csv
                if header_date:
                    writer.writerow(['Date:', header_date])
                if header_text:
                    writer.writerow(['Notes:',header_text])
                writer.writerows(data_to_export)
            messagebox.showinfo("Export Data", f"Data exported as {file_path}")
    
    def cache_data(self):
        global curr_data
        
        if self.cache_data_var.get():
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if file_path:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    # Headers
                    writer.writerow(["Time (s)", "Current (nA)"])
                    
                    # Write all data points
                    for time, current in zip(self.parent.graph_gui.time_data, self.parent.graph_gui.y_data):
                        writer.writerow([time, current])

                    # Optionally add the current data point
                    writer.writerow([self.parent.graph_gui.formatted_time, curr_data])
                    
                    # Ensure data is written immediately
                    #file.flush()
        
    
###################################################################################################################
#                                                 GraphGUI CLASS                                                  #
###################################################################################################################
class GraphGUI:
    """
    Function to initialize the data arrays and the graphical display.
    """
    def __init__(self, root, meas_gui, max_data_points=4095):
        """
        This initializes the graph widget for the three different processes.
        
        Args:
            root (_type_): _description_
            meas_gui (_type_): _description_
        """
        self.root = root
        self.meas_gui = meas_gui

        # Initialize cache file paths for different processes
        self.cache_files = {
            'tunneling_approach': "tunneling_approach_cache.csv",
            'cap_approach': "cap_approach_cache.csv",
            'enable_periodics': "enable_periodics_cache.csv",
            'feedback_control': "feedback_control_cache.csv"
        }
        
        # INITIALIZE CACHE FILE
        #self.init_cache_file()
        
        # Configures plot
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Current (nA)')
       
        # Initializes graphical data
        self.max_data_points = max_data_points
        self.y_data = deque(maxlen=max_data_points)
        self.x_data = deque(maxlen=max_data_points)
        self.time_data = deque(maxlen=max_data_points)
        self.line, = self.ax.plot([], [], 'r-')

        # Initialize an update interval counter
        self.graphUpdateCounter = 0

        # Create a canvas to embed the figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=3, columnspan=6, rowspan=10, padx=10, pady=5, sticky="n")
        
    def init_cache_file(self):
        """
        Initializes the cache file for storing discarded graph data.
        """
        headers = ["Time (s)", "Current (nA)"]
        for _, path in self.cache_files.items():
            with open(path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                
    def write_to_cache(self, process, x_values, y_values):
        """
        Writes a single data point to the cache file.

        Args:
            x_values (_type_): _description_
            y_values (_type_): _description_
        """
        cache_file = self.cache_files.get(process)
        if cache_file:
            with open(cache_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([x_values, y_values])
            
    def update_graph(self, process):
        """
        This will update the visual graph with the data points obtained during
        the Piezo Voltage Sweep. The data points are appended to the data arrays.
        *Updates every 36ms
        """
        global curr_data
        global sample_size_save
        global PERIODICS_FLAG
        global CAP_APPR_FLAG
        global TUNN_APPR_FLAG
        global TUNN_APPROACH_ESCAPE_FLG
        global FEEDBACK_CTRL_FLAG
        
        rollover_time = globals.ROLLOVER_GRAPH_TIME

        # Update data with next data points
        self.y_data.append(curr_data)
        time_now = datetime.datetime.now()
        # Append current time to x axis on graph
        self.x_data.append(time_now)
        
        # Append time to include milliseconds for exported data
        formatted_time = time_now.strftime('%H:%M:%S.%f')[:-3]
        self.time_data.append(formatted_time)
        
        # Write every data point to the cache file for the specified process
        #self.write_to_cache(process, formatted_time, curr_data)

        # Set x-axis parameters
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.xaxis.set_major_locator(mdates.SecondLocator(interval=2))
        # Controls how much time is shown within the graph, currently displays the most recent 10 seconds
        self.ax.set_xlim(datetime.datetime.now() - datetime.timedelta(seconds=rollover_time), datetime.datetime.now())
        
        # Local variables - calculate update interval based on sample size
        A = 400    # Scaling factor    # mess with this a bit more
        k = 0.005   # Decay rate
        B = update_interval = 10     # Minimum interval and default value
        
        if PERIODICS_FLAG:
            if sample_size_save == None:
                update_interval = B
            else:
                A = 900     # Scaling factor    
                k = 0.005   # Decay rate
                update_interval = max(int(A* math.exp(-k * sample_size_save) + B), B)     # Minimum interval

            self.graphUpdateCounter = (self.graphUpdateCounter + 1) % update_interval


        elif TUNN_APPR_FLAG:
            update_interval = 511
            self.graphUpdateCounter = (self.graphUpdateCounter + 1) % update_interval
            if TUNN_APPROACH_ESCAPE_FLG:
                update_interval = 1
                self.line.set_data(self.x_data, self.y_data)
                #TUNN_APPROACH_ESCAPE_FLG = 0
            if (self.graphUpdateCounter == (update_interval-1)) and not TUNN_APPROACH_ESCAPE_FLG: # Calculate the average of y_data
                # self.avg_y = sum(self.y_data) / len(self.y_data) if len(self.y_data) > 0 else 0
                # Create a constant y-value list with the average value
                # self.avg_y_data = [self.avg_y] * len(self.x_data)
                #self.line.set_data(self.x_data, self.avg_y_data)
                # UPDATED HERE
                self.line.set_data(self.x_data, self.y_data)
        
        elif CAP_APPR_FLAG:
            update_interval = 10                    
            self.graphUpdateCounter = (self.graphUpdateCounter + 1) % update_interval
        elif FEEDBACK_CTRL_FLAG:
            update_interval = 3   
            self.graphUpdateCounter = (self.graphUpdateCounter + 1) % update_interval  
        # Define the time interval for scaling (e.g., last 30 seconds)
        time_interval = datetime.timedelta(seconds=30)
        min_time = datetime.datetime.now() - time_interval
            
        if (self.graphUpdateCounter == (update_interval-1)):
            if not TUNN_APPR_FLAG:
                self.line.set_data(self.x_data, self.y_data)
            filtered_y_data = [y for x, y in zip(self.x_data, self.y_data) if x >= min_time]
            #else:
            #    filtered_y_data = [y for x, y in zip(self.x_data, self.y_data) if x >= min_time]

            # Calculate the min and max y-values in the filtered data
            if filtered_y_data:
                min_y = min(filtered_y_data)
                max_y = max(filtered_y_data)
            else:
                min_y = min(self.y_data)
                max_y = max(self.y_data)
            
            # Avoid singular transformation
            if min_y == max_y:
                min_y -= 1.0  # or a small value like 0.1
                max_y += 1.0  # or a small value like 0.1
            
            # Apply a buffer to prevent the graph from being too tightly zoomed
            y_buffer = (max_y - min_y) * 0.1
            self.ax.set_ylim(min_y - y_buffer, max_y + y_buffer)
            
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            self.canvas.flush_events()
        
    def reset_graph(self):
        """
        Resets the visual graph and clears the data points.
        """
        self.ax.clear()
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Current (nA)')
        self.y_data = deque(maxlen=self.max_data_points)
        self.x_data = deque(maxlen=self.max_data_points)
        self.time_data = deque(maxlen=self.max_data_points)
        self.graphUpdateCounter = 0
        self.line, = self.ax.plot([], [], 'r-')
        self.canvas.draw()
        self.canvas.flush_events()


if __name__ == "__main__":
    root_gui = RootGUI()
    root_gui.root.mainloop()