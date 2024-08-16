"""
Filename:       GUI_Widgets.py
Author:         Jacob Kucinski and Kelsey Marquez
Date:           8/13/24
Description:    This file creates and publishes the measurement widgets for the
                homepage window and also disables and enables the state of 
                specific widgets while a process is running.
"""
from tkinter import Label, LabelFrame, Entry, StringVar, OptionMenu, Text, Image
import customtkinter as ctk
from PIL import Image

class HomepageWidgets:
    def __init__(self, root, parent):
        """
        Initializes the HomepageWidgets class, setting up the root and parent 
        attributes that are essential for managing the widget layout and interactions.

        Args:
            root (Tk or Toplevel): The root window or main container for the widgets.
            parent (object): The parent object or controller that manages the 
                             overall application or GUI framework. This is typically 
                             used for accessing shared resources or methods.
        """
        self.root = root
        self.parent = parent

    def initialize_widgets(self, meas_gui):
        """
        Initializes the widgets needed for data collection in the GUI. This includes 
        setting up labels, drop-down menus, and other UI elements.

        Args:
            meas_gui (object): The GUI object that contains the root window and other 
                            necessary attributes for managing the user interface 
                            components.
        """
        small_font = ("Helvetica", 12)
        
        # Sample rate drop-down list   ### ADJUST LATER
        meas_gui.sample_rate = LabelFrame(meas_gui.root, text="", padx=5, pady=5, bg="#ADD8E6")
        meas_gui.label_sample_rate = Label(meas_gui.sample_rate, text="Sample Rate: ", bg="#ADD8E6", width=11, anchor="w")
        meas_gui.sample_rate_var = StringVar()
        meas_gui.sample_rate_var.set("-")
        meas_gui.sample_rate_menu = OptionMenu(meas_gui.sample_rate, meas_gui.sample_rate_var, "62.5 kHz", "40 kHz", "20 kHz", "10 kHz", "1 kHz", command=meas_gui.saveSampleRate)  
        meas_gui.sample_rate_menu.config(width=7)
        
        # Sample size user entry
        meas_gui.sample_size = LabelFrame(meas_gui.root, text="Sample Size", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.sample_size_entry = Entry(meas_gui.sample_size, bg="white", width=26)
        meas_gui.sample_size_entry.bind("<Return>", meas_gui.saveSampleSize)

        # Current
        meas_gui.frame2 = LabelFrame(meas_gui.root, text="Current (nA)", padx=10, pady=2, bg="gray")
        meas_gui.label2 = Label(meas_gui.frame2, bg="white", width=20)
        
        # Current setpoint
        meas_gui.frame3 = LabelFrame(meas_gui.root, text="Current Setpoint (nA)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.label3 = Entry(meas_gui.frame3, bg="white", width=24)
        meas_gui.label3.bind("<Return>", meas_gui.saveCurrentSetpoint)
        
        # Current offset
        meas_gui.frame4 = LabelFrame(meas_gui.root, text="Current Offset (nA)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.label4 = Entry(meas_gui.frame4, bg="white", width=24)
        meas_gui.label4.bind("<Return>", meas_gui.saveCurrentOffset)
                
        # Sample bias
        meas_gui.frame6 = LabelFrame(meas_gui.root, text="Sample Bias (V)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.label6 = Entry(meas_gui.frame6, bg="white", width=24)
        meas_gui.label6.bind("<Return>", meas_gui.saveSampleBias)

        # User notes text box
        meas_gui.frame7 = LabelFrame(meas_gui.root, text="NOTES", padx=10, pady=5, bg="#ADD8E6")
        meas_gui.label7 = Text(meas_gui.frame7, height=7, width=30)
        meas_gui.label7.bind("<Return>", meas_gui.save_notes)
        
        meas_gui.label8 = Entry(meas_gui.frame7, width=10)
        meas_gui.label9 = Label(meas_gui.frame7, padx=10, text="Date:", height=1, width=5)
        meas_gui.label8.bind("<Return>", meas_gui.save_date)
    
        # Define images
        meas_gui.add_btn_image0 = ctk.CTkImage(Image.open("Images/Vpzo_Up_Btn.png"), size=(40,40))
        meas_gui.add_btn_image1 = ctk.CTkImage(Image.open("Images/Vpzo_Down_Btn.png"), size=(40,40))
        meas_gui.add_btn_image2 = ctk.CTkImage(Image.open("Images/Fine_Adjust_Btn_Up.png"), size=(50,45))
        meas_gui.add_btn_image3 = ctk.CTkImage(Image.open("Images/Fine_Adjust_Btn_Down.png"), size=(50,45))
        meas_gui.add_btn_image4 = ctk.CTkImage(Image.open("Images/Start_Tip_Approach.png"), size=(100,35))
        meas_gui.add_btn_image5 = ctk.CTkImage(Image.open("Images/Stop_Btn.png"), size=(90,35))
        meas_gui.add_btn_image6 = ctk.CTkImage(Image.open("Images/Acquire_IV.png"), size=(100,35))
        meas_gui.add_btn_image7 = ctk.CTkImage(Image.open("Images/Acquire_IZ.png"), size=(100,35))
        meas_gui.add_btn_image12 = ctk.CTkImage(Image.open("Images/Start_Cap_Approach.png"), size=(100,45))
        meas_gui.add_btn_image13 = ctk.CTkImage(Image.open("Images/Start_Periodic_Data.png"), size=(100,45))
        meas_gui.add_btn_image14 = ctk.CTkImage(Image.open("Images/Start_Feedback_Ctrl.png"), size=(100,45))
        meas_gui.add_btn_image8 = ctk.CTkImage(Image.open("Images/Stop_LED.png"), size=(35,35))
        meas_gui.add_btn_image9 = ctk.CTkImage(Image.open("Images/Start_LED.png"), size=(35,35))
        meas_gui.add_btn_image10 = ctk.CTkImage(Image.open("Images/Save_Home_Btn.png"), size=(100,35))
        meas_gui.add_btn_image11 = ctk.CTkImage(Image.open("Images/Return_Home_Btn.png"), size=(35,35))
        
        # Start/stop widgets													   
        meas_gui.start_stop_frame = LabelFrame(meas_gui.root, text="Start/Stop Processes", labelanchor="n", padx=10, pady=10, bg="#eeeeee")
        meas_gui.tip_approach_btn = ctk.CTkButton(meas_gui.start_stop_frame, image=meas_gui.add_btn_image4, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.start_tip_appr)
        meas_gui.cap_approach_btn = ctk.CTkButton(meas_gui.start_stop_frame, image=meas_gui.add_btn_image12, text="", width=100, height=45, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.start_cap_appr)
        meas_gui.enable_periodics_btn = ctk.CTkButton(meas_gui.start_stop_frame, image = meas_gui.add_btn_image13, text="", width=100, height=45, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.start_periodics)
        meas_gui.feedback_ctrl_btn = ctk.CTkButton(meas_gui.start_stop_frame, image = meas_gui.add_btn_image14, text="", width=100, height=45, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.feedback_controller)
        meas_gui.stop_btn = ctk.CTkButton(meas_gui.start_stop_frame, image=meas_gui.add_btn_image5, text="", width=90, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.stop_reading)
        meas_gui.stop_led_btn = ctk.CTkLabel(meas_gui.start_stop_frame, image=meas_gui.add_btn_image8, text="", width=35, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0)
        meas_gui.start_led_btn = ctk.CTkLabel(meas_gui.start_stop_frame, image=meas_gui.add_btn_image9, text="", width=30, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0)
        
        # Sweep windows frame and buttons
        meas_gui.sweep_windows_frame = LabelFrame(meas_gui.root, text="Sweep Windows", labelanchor="n", padx=10, pady=10, bg="#eeeeee")
        meas_gui.acquire_iv_btn = ctk.CTkButton(meas_gui.sweep_windows_frame, image=meas_gui.add_btn_image6, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.open_iv_window)
        meas_gui.acquire_iz_btn = ctk.CTkButton(meas_gui.sweep_windows_frame, image=meas_gui.add_btn_image7, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.open_iz_window)
        meas_gui.save_home_pos = ctk.CTkButton(meas_gui.root, image=meas_gui.add_btn_image10, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.save_home)
        
        # Return/save home position buttons
        meas_gui.return_to_home_frame = LabelFrame(meas_gui.root, text="Return Home", labelanchor= "s", padx=10, pady=5, bg="#eeeeee")
        meas_gui.return_to_home_pos = ctk.CTkButton(meas_gui.return_to_home_frame, image=meas_gui.add_btn_image11, text="", width=30, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.return_home)

       # Total distance (nm)
        meas_gui.total_distance_frame = LabelFrame(meas_gui.start_stop_frame, text="Total Distance (nm)", padx=10, pady=2, bg="gray")
        meas_gui.total_distance_label = Label(meas_gui.total_distance_frame, bg="white", width=15)
        
        # Vpiezo adjust frame and buttons
        meas_gui.vpiezo_btn_frame = LabelFrame(meas_gui.root, text="Piezo Tip Adjust", padx=10, pady=5, bg="#eeeeee")
        meas_gui.vpiezo_adjust_btn_up = ctk.CTkButton(master=meas_gui.vpiezo_btn_frame, image=meas_gui.add_btn_image0, text = "EXTEND TIP", text_color="black", font=small_font, width=40, height=40, compound="bottom", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.piezo_inc)
        meas_gui.vpiezo_adjust_btn_down = ctk.CTkButton(master=meas_gui.vpiezo_btn_frame, image=meas_gui.add_btn_image1, text="RETRACT TIP", text_color="black", font=small_font, width=40, height=40, compound="top", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.piezo_dec)

        # Vpiezo adjust step size
        meas_gui.frame10 = LabelFrame(meas_gui.vpiezo_btn_frame, text="", padx=5, pady=5, bg="#d0cee2")
        meas_gui.label_vpeizo_delta = Label(meas_gui.frame10, text="Vpiezo ΔV (V):", bg="#d0cee2", width=11, anchor="w")

        # Total distance (nm)
        meas_gui.total_distance_frame = LabelFrame(meas_gui.start_stop_frame, text="Total Distance (nm)", padx=10, pady=2, bg="gray")
        meas_gui.total_distance_label = Label(meas_gui.total_distance_frame, bg="white", width=20)
        
        ### ADJUST LATER
        meas_gui.label_vpeizo_delta_distance = Label(meas_gui.frame10, text="Approx. Dist", bg="#d0cee2", width=9, anchor="w")
        meas_gui.label10 = Entry(meas_gui.frame10, bg="white", width=10)
        meas_gui.label10.bind("<Return>", meas_gui.savePiezoValue)
        meas_gui.label11 = Label(meas_gui.frame10, bg="white", width=10)
        meas_gui.label_vpeizo_total = Label(meas_gui.frame10, text="Total Voltage", bg="#d0cee2", width=10, anchor="w")
        meas_gui.label12 = Label(meas_gui.frame10, bg="white", width=10)
        
        # Stepper motor adjust frame and buttons
        meas_gui.fine_adjust_frame = LabelFrame(meas_gui.root, text="Stepper Motor", padx=10, pady=5, bg="#eeeeee")
        meas_gui.fine_adjust_btn_up = ctk.CTkButton(master=meas_gui.fine_adjust_frame, image=meas_gui.add_btn_image2, text = "RETRACT MOTOR", text_color="black", font=small_font, width=50, height=45, compound="bottom", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.stepper_motor_up)
        meas_gui.fine_adjust_btn_down = ctk.CTkButton(master=meas_gui.fine_adjust_frame, image=meas_gui.add_btn_image3, text="EXTEND MOTOR", text_color="black", font=small_font, width=50, height=45, compound="top", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.stepper_motor_down)

        # Stepper motor adjust step size
        meas_gui.frame9 = LabelFrame(meas_gui.fine_adjust_frame, text="", padx=5, pady=5, bg="#ADD8E6")
        meas_gui.label_coarse_adjust = Label(meas_gui.frame9, text="Step Size: ", bg="#ADD8E6", width=10, anchor="w")
        meas_gui.coarse_adjust_var = StringVar()
        meas_gui.coarse_adjust_var.set("-")
        meas_gui.coarse_adjust_menu = OptionMenu(meas_gui.frame9, meas_gui.coarse_adjust_var, "Full", "Half", "Quarter", "Eighth", command=meas_gui.saveStepperMotorAdjust) 
        meas_gui.coarse_adjust_menu.config(width=6)
        meas_gui.label_coarse_adjust_inc = Label(meas_gui.frame9, text="Approx. Dist", bg="#ADD8E6", width=10, anchor="w")
        meas_gui.label5 = Label(meas_gui.frame9, bg="white", width=10)
        
        # Cache data logging
        meas_gui.cache_data_var = ctk.BooleanVar()
        meas_gui.cache_data_checkbtn = ctk.CTkCheckBox(meas_gui.start_stop_frame, text="Cache Data", text_color="black", variable=meas_gui.cache_data_var, onvalue=True, offvalue=False, command=meas_gui.cache_data)

        # Warning image
        meas_gui.warning_image = ctk.CTkImage(Image.open("Images/warning.png"), size=(200, 175))
        meas_gui.warning_label = ctk.CTkLabel(meas_gui.root, image=meas_gui.warning_image,  text="")

        # Tip controller parameters
        meas_gui.ctrl_frame = LabelFrame(meas_gui.root, text="Feedback Control Parameters", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.kp_frame = LabelFrame(meas_gui.ctrl_frame, text="Kp (nm/nA)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.kp_label = Entry(meas_gui.kp_frame, bg="white", width=24)
        meas_gui.kp_label.bind("<Return>", meas_gui.saveKp)

        meas_gui.kd_frame = LabelFrame(meas_gui.ctrl_frame, text="Kd (nm/nA*s)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.kd_label = Entry(meas_gui.kd_frame, bg="white", width=24)
        meas_gui.kd_label.bind("<Return>", meas_gui.saveKd)

        meas_gui.ki_frame = LabelFrame(meas_gui.ctrl_frame, text="Ki (nm*s/nA)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.ki_label = Entry(meas_gui.ki_frame, bg="white", width=24)
        meas_gui.ki_label.bind("<Return>", meas_gui.saveKi)

    def publish(self, meas_gui):
        """
        Publishes the widgets needed for data collection in the GUI. This includes 
        setting up labels, drop-down menus, and other UI elements.

        Args:
            meas_gui (object): The GUI object that contains the root window and other 
                            necessary attributes for managing the user interface 
                            components.
        """
        # Positioning sample rate menu
        meas_gui.label_sample_rate.grid(row=1, column=1, pady=10, sticky="nw")
        meas_gui.sample_rate_menu.grid(row=1, column=2) 
        meas_gui.sample_rate.grid(row=12, column=4, padx=5, pady=5)

        # Positioning sample size
        meas_gui.sample_size.grid(row=12, column=5, pady=5, sticky="n")
        meas_gui.sample_size_entry.grid(row=0, column=0, pady=5)
        
        # Positioning current text box
        meas_gui.frame2.grid(row=10, column=4, padx=5, pady=5, sticky="nw")
        meas_gui.label2.grid(row=0, column=0, padx=5, pady=5)   
        
        # Positioning current setpoint text box
        meas_gui.frame3.grid(row=11, column=4, padx=5, pady=5, sticky="nw")
        meas_gui.label3.grid(row=0, column=0, padx=5, pady=5) 
        
        # Positioning current offset text box
        meas_gui.frame4.grid(row=10, column=5, padx=5, pady=5, sticky="nw")
        meas_gui.label4.grid(row=0, column=0, padx=5, pady=5) 

        # Positioning sample bias text box
        meas_gui.frame6.grid(row=11, column=5, padx=5, pady=5, sticky="nw")
        meas_gui.label6.grid(row=2, column=0, padx=5, pady=5) 

        # Positioning the notes text box
        meas_gui.frame7.grid(row=10, column=7, rowspan=3, pady=5, sticky="n")
        meas_gui.label7.grid(row=1, column=0, pady=5, columnspan=3, rowspan=3) 
        meas_gui.label8.grid(row=0, column=2, pady=5, sticky="e")
        meas_gui.label9.grid(row=0, column=2, pady=5, sticky="w")

        # Vpiezo tip fine adjust buttons
        meas_gui.vpiezo_btn_frame.grid(row=2, column=1, rowspan=4, columnspan=2, padx=5, sticky="ne")
        meas_gui.vpiezo_adjust_btn_up.grid(row=0, column=0, padx=5, sticky="e")
        meas_gui.vpiezo_adjust_btn_down.grid(row=1, column=0, padx=5, sticky="e")

        # Vpiezo frame
        meas_gui.frame10.grid(row=0, column=1, rowspan=4, columnspan=2, padx=5, pady=5, sticky="")
        # Vpiezo delta user entry
        meas_gui.label10.grid(row=1, column=0, padx=5) 
        # Vpiezo approx. distance
        meas_gui.label11.grid(row=1, column=1, padx=5) 
        # Vpiezo total voltage
        meas_gui.label12.grid(row=3, column=0, columnspan=2) 
        # Vpiezo delta label
        meas_gui.label_vpeizo_delta.grid(row=0, column=0)
        # Vpiezo approx. distance label
        meas_gui.label_vpeizo_delta_distance.grid(row=0, column=1) 
        # Vpiezo total voltage label
        meas_gui.label_vpeizo_total.grid(row=2, column=0, columnspan=2) 

        # Stepper motor adjust frame
        meas_gui.fine_adjust_frame.grid(row=6, column=1, rowspan=4, columnspan=2, padx=5, pady=10, sticky="s")
        # Stepper motor up button
        meas_gui.fine_adjust_btn_up.grid(row=0, column=0)
        # Stepper motor down button
        meas_gui.fine_adjust_btn_down.grid(row=1, column=0)

        # Stepper motor user input frame
        meas_gui.frame9.grid(row=0, column=1, rowspan=2, columnspan=2, padx=5, pady=5, sticky="")
        # Stepper motor label
        meas_gui.label_coarse_adjust.grid(row=1, column=1)
        # Stepper motor drop down menu
        meas_gui.coarse_adjust_menu.grid(row=2, column=1) 
        # Stepper motor approx. distance label
        meas_gui.label_coarse_adjust_inc.grid(row=1, column=2)
        # Stepper motor approx. distsance value box
        meas_gui.label5.grid(row=2, column=2, padx=5, pady=5)
        
        # Start/stop buttons
        meas_gui.start_stop_frame.grid(row=0, column=9, columnspan=4, rowspan=4)
        meas_gui.tip_approach_btn.grid(row=0, column=0, sticky="e")
        meas_gui.cap_approach_btn.grid(row=2, column=0, sticky="e")
        meas_gui.feedback_ctrl_btn.grid(row=1, column=0, sticky="e")
        meas_gui.enable_periodics_btn.grid(row=3, column=0, sticky="e")
        meas_gui.stop_btn.grid(row=1, column=1, sticky="ne", padx=20, pady=10)
        meas_gui.cache_data_checkbtn.grid(row=3, column=1, padx=10, pady=5, sticky="e")
        
        # Stop LED (red)
        meas_gui.stop_led_btn.grid(row=0, column=1, sticky="")

        # Total distance position
        meas_gui.total_distance_frame.grid(row=2, column=1, sticky="e")
        meas_gui.total_distance_label.grid(row=0, column=0)

        # Sweep windows buttons
        meas_gui.sweep_windows_frame.grid(row=7, column=9, columnspan=4)
        meas_gui.acquire_iv_btn.grid(row=0, column=0, sticky="e")
        meas_gui.acquire_iz_btn.grid(row=0, column=1, padx=15, sticky="e")

        # Save home position
        meas_gui.save_home_pos.grid(row=11, column=9, padx=10, sticky="sw")
        
        # Reset home position
        meas_gui.return_to_home_frame.grid(row=10, column=9, rowspan=2, padx=20, pady=5, sticky="nw")
        meas_gui.return_to_home_pos.grid(row=0, column=0, padx=18)
        
        # Total distance position
        meas_gui.total_distance_frame.grid(row=2, column=1, sticky="e")
        meas_gui.total_distance_label.grid(row=0, column=0)
        
        # Warning image
        meas_gui.warning_label.grid(row=10, column=1, columnspan=2, rowspan=3, sticky="n")
        
        # Tip controller parameters
        meas_gui.ctrl_frame.grid(row=10, column=10, columnspan=2, rowspan=3, sticky="n")
        meas_gui.kp_frame.grid(row=0, column=0)
        meas_gui.kp_label.grid(row=1, column=0)
        
        meas_gui.kd_frame.grid(row=2, column=0)
        meas_gui.kd_label.grid(row=3, column=0)
        
        meas_gui.ki_frame.grid(row=4, column=0)
        meas_gui.ki_label.grid(row=5, column=0)
        
    def disable_widgets(self, meas_gui):
        """
        Function to disable entry widgets when a process is running.
        Disables:
            - current setpoint
            - sample rate
            - sample size
            - reset home
            - save home
            - start tip approach 
            - start cap approach 
            - start feedback control 
            - start enabling periodics
            - stop process btn

        Args:
        meas_gui (object): The GUI object that contains the root window and other 
                           necessary attributes for managing the user interface 
                           components.
        """
        meas_gui.label3.configure(state="disabled")
        meas_gui.sample_rate_menu.configure(state="disabled")
        meas_gui.sample_size_entry.configure(state="disabled")
        meas_gui.save_home_pos.configure(state="disabled")
        meas_gui.return_to_home_pos.configure(state="disabled")
        meas_gui.tip_approach_btn.configure(state="disabled")
        meas_gui.cap_approach_btn.configure(state="disabled")
        meas_gui.feedback_ctrl_btn.configure(state="disabled")
        meas_gui.enable_periodics_btn.configure(state="disabled")
        meas_gui.stop_btn.configure(state="normal")
    
    def enable_widgets(self, meas_gui):
        """
        Function to disable entry widgets when a process is running.
        Disables:
            - current setpoint
            - sample rate
            - sample size
            - reset home
            - save home
            - start tip approach 
            - start cap approach 
            - start feedback control 
            - start enabling periodics
            - stop process btn

        Args:
        meas_gui (object): The GUI object that contains the root window and other 
                           necessary attributes for managing the user interface 
                           components.
        """
        meas_gui.label3.configure(state="normal")
        meas_gui.sample_rate_menu.configure(state="normal")
        meas_gui.sample_size_entry.configure(state="normal")
        meas_gui.save_home_pos.configure(state="normal")
        meas_gui.return_to_home_pos.configure(state="normal")
        meas_gui.tip_approach_btn.configure(state="normal")
        meas_gui.cap_approach_btn.configure(state="normal")
        meas_gui.feedback_ctrl_btn.configure(state="normal")
        meas_gui.enable_periodics_btn.configure(state="normal")
        meas_gui.stop_btn.configure(state="disable")
