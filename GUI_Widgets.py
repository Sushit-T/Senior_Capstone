"""
Filename:   GUI_Widgets.py
Author:     Jacob Kucinski and Kelsey Marquez
Date:       8/8/24
Description:
"""
from tkinter import Label, LabelFrame, Entry, StringVar, OptionMenu, Text, Image
import customtkinter as ctk
from PIL import Image

class HomepageWidgets:
    def __init__(self, root, parent):
        self.root = root
        self.parent = parent

    def initialize_widgets(self, meas_gui):
        """
        Initializes widgets needed for data.
        """
        # Optional graphic parameters
        meas_gui.padx = 20
        meas_gui.pady = 10
        
        # Sample rate drop-down list   ### ADJUST LATER
        meas_gui.frame8 = LabelFrame(meas_gui.root, text="", padx=5, pady=5, bg="#ADD8E6")
        meas_gui.label_sample_rate = Label(meas_gui.frame8, text="Sample Rate: ", bg="#ADD8E6", width=11, anchor="w")
        meas_gui.sample_rate_var = StringVar()
        meas_gui.sample_rate_var.set("-")
        meas_gui.sample_rate_menu = OptionMenu(meas_gui.frame8, meas_gui.sample_rate_var, "25 kHz", "12.5 kHz", "37.5 kHz", "10 kHz", "5 kHz", command=meas_gui.saveSampleRate)  
        meas_gui.sample_rate_menu.config(width=7)
        
        meas_gui.label_sample_rate.grid(column=1, row=1)
        meas_gui.sample_rate_menu.grid(column=2, row=1) 
        meas_gui.frame8.grid(row=12, column=4, padx=5, pady=5, sticky="")
        
        # Sample size user entry
        meas_gui.sample_size = Entry(meas_gui.frame8, width=13)
        meas_gui.sample_size_label = Label(meas_gui.frame8, text="Sample Size: ", bg="#ADD8E6", width=11, anchor="w")
        meas_gui.sample_size.bind("<Return>", meas_gui.saveSampleSize)
        
        meas_gui.sample_size.grid(column=2, row=2, pady=5)
        meas_gui.sample_size_label.grid(column=1, row=2)

        # Stepper motor adjust step size
        meas_gui.frame9 = LabelFrame(meas_gui.root, text="", padx=5, pady=5, bg="#ADD8E6")
        meas_gui.label_coarse_adjust = Label(meas_gui.frame9, text="Step Size: ", bg="#ADD8E6", width=8, anchor="w")
        meas_gui.coarse_adjust_var = StringVar()
        meas_gui.coarse_adjust_var.set("-")
        meas_gui.coarse_adjust_menu = OptionMenu(meas_gui.frame9, meas_gui.coarse_adjust_var, "Full", "Half", "Quarter", "Eighth", command=meas_gui.saveStepperMotorAdjust) 
        meas_gui.coarse_adjust_menu.config(width=6)

        meas_gui.label_coarse_adjust.grid(column=1, row=1)
        meas_gui.coarse_adjust_menu.grid(column=1, row=2) 
        meas_gui.frame9.grid(row=12, column=2, rowspan=2, columnspan=2, padx=5, pady=5, sticky="")
        meas_gui.label_coarse_adjust_inc = Label(meas_gui.frame9, text="Approx. Dist", bg="#ADD8E6", width=9, anchor="w")

        meas_gui.label5 = Label(meas_gui.frame9, bg="white", width=10)
        meas_gui.label_coarse_adjust_inc.grid(column=2, row=1)
        meas_gui.label5.grid(column=2, row=2, padx=5, pady=5)

        # Vpiezo adjust step size
        meas_gui.frame10 = LabelFrame(meas_gui.root, text="", padx=5, pady=5, bg="#d0cee2")
        meas_gui.label_vpeizo_delta = Label(meas_gui.frame10, text="Vpiezo ΔV (V):", bg="#d0cee2", width=11, anchor="w")
        meas_gui.label_vpeizo_delta.grid(column=1, row=1)
        meas_gui.frame10.grid(row=7, column=2, rowspan=4, columnspan=2, padx=5, pady=5, sticky="")
        
        ### ADJUST LATER
        meas_gui.label_vpeizo_delta_distance = Label(meas_gui.frame10, text="Approx. Dist", bg="#d0cee2", width=9, anchor="w")
        meas_gui.label_vpeizo_delta_distance.grid(column=2, row=1)
        meas_gui.label10 = Entry(meas_gui.frame10, bg="white", width=10)
        meas_gui.label10.bind("<Return>", meas_gui.savePiezoValue)
        meas_gui.label11 = Label(meas_gui.frame10, bg="white", width=10)
        meas_gui.label10.grid(column=1, row=2, padx=5)
        meas_gui.label11.grid(column=2, row=2, padx=5)
        meas_gui.label_vpeizo_total = Label(meas_gui.frame10, text="Total Voltage", bg="#d0cee2", width=10, anchor="w")
        meas_gui.label_vpeizo_total.grid(column=1, row=3, columnspan=2)
        meas_gui.label12 = Label(meas_gui.frame10, bg="white", width=10)
        meas_gui.label12.grid(column=1, row=4, columnspan=2)

        # distance  ### ADJUST LATER
        meas_gui.frame1 = LabelFrame(meas_gui.root, text="Distance (nm)", padx=10, pady=2, bg="gray", width=20)
        meas_gui.label1 = Label(meas_gui.frame1, bg="white", width=20)
        
        # current
        meas_gui.frame2 = LabelFrame(meas_gui.root, text="Current (nA)", padx=10, pady=2, bg="gray")
        meas_gui.label2 = Label(meas_gui.frame2, bg="white", width=20)
        
        # current setpoint
        meas_gui.frame3 = LabelFrame(meas_gui.root, text="Current Setpoint (nA)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.label3 = Entry(meas_gui.frame3, bg="white", width=24)
        meas_gui.label3.bind("<Return>", meas_gui.saveCurrentSetpoint)
        
        # current offset
        meas_gui.frame4 = LabelFrame(meas_gui.root, text="Current Offset (nA)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.label4 = Entry(meas_gui.frame4, bg="white", width=24)
        meas_gui.label4.bind("<Return>", meas_gui.saveCurrentOffset)
                
        # sample bias
        meas_gui.frame6 = LabelFrame(meas_gui.root, text="Sample Bias (V)", padx=10, pady=2, bg="#ADD8E6")
        meas_gui.label6 = Entry(meas_gui.frame6, bg="white", width=24)
        meas_gui.label6.bind("<Return>", meas_gui.saveSampleBias)

        # user notes text box
        meas_gui.frame7 = LabelFrame(meas_gui.root, text="NOTES", padx=10, pady=5, bg="#ADD8E6")
        meas_gui.label7 = Text(meas_gui.frame7, height=7, width=30)
        meas_gui.label7.bind("<Return>", meas_gui.save_notes)
        
        meas_gui.label8 = Entry(meas_gui.frame7, width=10)
        meas_gui.label9 = Label(meas_gui.frame7, padx=10, text="Date:", height=1, width=5)
        meas_gui.label8.bind("<Return>", meas_gui.save_date)
    
        # define images
        meas_gui.add_btn_image0 = ctk.CTkImage(Image.open("Images/Vpzo_Up_Btn.png"), size=(40,40))
        meas_gui.add_btn_image1 = ctk.CTkImage(Image.open("Images/Vpzo_Down_Btn.png"), size=(40,40))
        meas_gui.add_btn_image2 = ctk.CTkImage(Image.open("Images/Fine_Adjust_Btn_Up.png"), size=(40,40))
        meas_gui.add_btn_image3 = ctk.CTkImage(Image.open("Images/Fine_Adjust_Btn_Down.png"), size=(40,40))
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
        
        # start/stop widgets													   
        meas_gui.start_stop_frame = LabelFrame(meas_gui.root, text="Start/Stop Processes", labelanchor="n", padx=10, pady=10, bg="#eeeeee")
        meas_gui.tip_approach_btn = ctk.CTkButton(meas_gui.start_stop_frame, image=meas_gui.add_btn_image4, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.start_tip_appr)
        meas_gui.cap_approach_btn = ctk.CTkButton(meas_gui.start_stop_frame, image=meas_gui.add_btn_image12, text="", width=100, height=45, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.start_cap_appr)
        meas_gui.enable_periodics_btn = ctk.CTkButton(meas_gui.start_stop_frame, image = meas_gui.add_btn_image13, text="", width=100, height=45, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.start_periodics)
        meas_gui.feedback_ctrl_btn = ctk.CTkButton(meas_gui.start_stop_frame, image = meas_gui.add_btn_image14, text="", width=100, height=45, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.feedback_controller)
        meas_gui.stop_btn = ctk.CTkButton(meas_gui.start_stop_frame, image=meas_gui.add_btn_image5, text="", width=90, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.stop_reading)
        meas_gui.stop_led_btn = ctk.CTkLabel(meas_gui.start_stop_frame, image=meas_gui.add_btn_image8, text="", width=35, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0)
        meas_gui.start_led_btn = ctk.CTkLabel(meas_gui.start_stop_frame, image=meas_gui.add_btn_image9, text="", width=30, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0)
        
        # sweep windows frame and buttons
        meas_gui.sweep_windows_frame = LabelFrame(meas_gui.root, text="Sweep Windows", labelanchor="n", padx=10, pady=10, bg="#eeeeee")
        meas_gui.acquire_iv_btn = ctk.CTkButton(meas_gui.sweep_windows_frame, image=meas_gui.add_btn_image6, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.open_iv_window)
        meas_gui.acquire_iz_btn = ctk.CTkButton(meas_gui.sweep_windows_frame, image=meas_gui.add_btn_image7, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.open_iz_window)
        meas_gui.save_home_pos = ctk.CTkButton(meas_gui.root, image=meas_gui.add_btn_image10, text="", width=100, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.save_home)
        
        # Return/save home position buttons
        meas_gui.return_to_home_frame = LabelFrame(meas_gui.root, text="Return Home", labelanchor= "s", padx=10, pady=5, bg="#eeeeee")
        meas_gui.return_to_home_pos = ctk.CTkButton(meas_gui.return_to_home_frame, image=meas_gui.add_btn_image11, text="", width=30, height=35, fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.return_home)
        
        # Piezo adjust frame and buttons
        meas_gui.vpiezo_btn_frame = LabelFrame(meas_gui.root, text="Piezo Tip Adjust", padx=10, pady=5, bg="#eeeeee")
        meas_gui.vpiezo_adjust_btn_up = ctk.CTkButton(master=meas_gui.vpiezo_btn_frame, image=meas_gui.add_btn_image0, text = "", width=40, height=40, compound="bottom", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.piezo_inc)
        meas_gui.vpiezo_adjust_btn_down = ctk.CTkButton(master=meas_gui.vpiezo_btn_frame, image=meas_gui.add_btn_image1, text="", width=40, height=40, compound="bottom", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.piezo_dec)
        
        # Stepper motor adjust frame and buttons
        meas_gui.fine_adjust_frame = LabelFrame(meas_gui.root, text="Stepper Motor", padx=10, pady=5, bg="#eeeeee")
        meas_gui.fine_adjust_btn_up = ctk.CTkButton(master=meas_gui.fine_adjust_frame, image=meas_gui.add_btn_image2, text = "", width=40, height=40, compound="bottom", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.stepper_motor_up)
        meas_gui.fine_adjust_btn_down = ctk.CTkButton(master=meas_gui.fine_adjust_frame, image=meas_gui.add_btn_image3, text="", width=40, height=40, compound="bottom", fg_color="#eeeeee", bg_color="#eeeeee", corner_radius=0, command=meas_gui.stepper_motor_down)

        # setup the drop option menu
        #meas_gui.DropDownMenu()
        
        # put on the grid all the elements
        #meas_gui.publish()

    def publish(self, meas_gui):
        """
        Method to publish widgets in the MeasGUI class.
        """
        # positioning distance text box
        meas_gui.frame1.grid(row=10, column=4, padx=5, pady=5, sticky="nw")
        meas_gui.label1.grid(row=0, column=0, padx=5, pady=5)

        # positioning current text box
        meas_gui.frame2.grid(row=10, column=5, padx=5, pady=5, sticky="nw")
        meas_gui.label2.grid(row=0, column=1, padx=5, pady=5)   
        
        # positioning current setpoint text box
        meas_gui.frame3.grid(row=11, column=4, padx=5, pady=5, sticky="w")
        meas_gui.label3.grid(row=1, column=0, padx=5, pady=5) 
        
        # positioning current offset text box
        meas_gui.frame4.grid(row=11, column=5, padx=5, pady=5, sticky="w")
        meas_gui.label4.grid(row=1, column=1, padx=5, pady=5) 

        # positioning sample bias text box
        meas_gui.frame6.grid(row=12, column=5, padx=5, pady=5, sticky="nw")
        meas_gui.label6.grid(row=2, column=0, padx=5, pady=5) 

        # positioning the notes text box
        meas_gui.frame7.grid(row=10, column=7, rowspan=3, pady=5, sticky="n")
        meas_gui.label7.grid(row=1, column=0, pady=5, columnspan=3, rowspan=3) 
        meas_gui.label8.grid(row=0, column=2, pady=5, sticky="e")
        meas_gui.label9.grid(row=0, column=2, pady=5, sticky="w")

        # vpiezo tip fine adjust
        meas_gui.vpiezo_btn_frame.grid(row=7, column=0, rowspan=3, columnspan=2, padx=5, sticky="e")
        meas_gui.vpiezo_adjust_btn_up.grid(row=0, column=0, sticky="e")
        meas_gui.vpiezo_adjust_btn_down.grid(row=1, column=0, sticky="e")
        
        # stepper motor adjust
        meas_gui.fine_adjust_frame.grid(row=11, column=0, rowspan=4, columnspan=2, padx=5, sticky="e")
        meas_gui.fine_adjust_btn_up.grid(row=0, column=0)
        meas_gui.fine_adjust_btn_down.grid(row=1, column=0)
        
        # start/stop buttons
        meas_gui.start_stop_frame.grid(row=0, column=9, columnspan=4, rowspan=4)
        meas_gui.tip_approach_btn.grid(row=0, column=0, sticky="e")
        meas_gui.cap_approach_btn.grid(row=2, column=0, sticky="e")
        meas_gui.feedback_ctrl_btn.grid(row=1, column=0, sticky="e")
        meas_gui.enable_periodics_btn.grid(row=3, column=0, sticky="e")
        meas_gui.stop_btn.grid(row=1, column=1, sticky="ne", padx=20, pady=10)
        # led
        meas_gui.stop_led_btn.grid(row=0, column=1, sticky="")

        # sweep windows buttons
        meas_gui.sweep_windows_frame.grid(row=7, column=9, columnspan=4)
        meas_gui.acquire_iv_btn.grid(row=0, column=0, sticky="e")
        meas_gui.acquire_iz_btn.grid(row=0, column=1, padx=15, sticky="e")

        # save home position
        meas_gui.save_home_pos.grid(row=8, column=9, padx=10, sticky="w")
        
        # reset home position
        meas_gui.return_to_home_frame.grid(row=10, column=9, sticky="w", padx=20)
        meas_gui.return_to_home_pos.grid(row=0, column=0, padx=18)
        
    def disable_widgets(self, meas_gui):
        '''
        Function to disable entry widgets when we start seeking
        Disabling:
            - current setpoint
            - sample rate
            - stepper motor step size
            - stepper motor up
            - stepper motor down
            - iv window
            - iz window
            - reset home
            - save home
            - start btn
            - stop btn
        '''
        meas_gui.label3.configure(state="disabled")
        meas_gui.sample_rate_menu.configure(state="disabled")
        #meas_gui.coarse_adjust_menu.configure(state="disabled")
        meas_gui.sample_size.configure(state="disabled")
        meas_gui.acquire_iv_btn.configure(state="disabled")
        meas_gui.acquire_iz_btn.configure(state="disabled")
        meas_gui.save_home_pos.configure(state="disabled")
        meas_gui.return_to_home_pos.configure(state="disabled")
        meas_gui.tip_approach_btn.configure(state="disabled")
        meas_gui.cap_approach_btn.configure(state="disabled")
        meas_gui.enable_periodics_btn.configure(state="disabled")
        meas_gui.feedback_ctrl_btn.configure(state="disabled")
        meas_gui.stop_btn.configure(state="normal")
    
    def enable_widgets(self, meas_gui):
        meas_gui.label3.configure(state="normal")
        meas_gui.sample_rate_menu.configure(state="normal")
        #meas_gui.coarse_adjust_menu.configure(state="normal")
        meas_gui.sample_size.configure(state="normal")
        meas_gui.acquire_iv_btn.configure(state="normal")
        meas_gui.acquire_iz_btn.configure(state="normal")
        meas_gui.save_home_pos.configure(state="normal")
        meas_gui.return_to_home_pos.configure(state="normal")
        meas_gui.tip_approach_btn.configure(state="normal")
        meas_gui.cap_approach_btn.configure(state="normal")
        meas_gui.enable_periodics_btn.configure(state="normal")
        meas_gui.feedback_ctrl_btn.configure(state="normal")
        meas_gui.stop_btn.configure(state="disable")
