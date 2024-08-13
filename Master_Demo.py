"""
Filename:       Master_Demo.py
Author:         Jacob Kucinski and Kelsey Marquez
Date:           8/8/24
Description:    This is the main file where the user runs the Python GUI ZTM application 
                on.
"""
from GUI_Master_Demo import RootGUI, MeasGUI, GraphGUI, ComGUI

# Initialize the root GUI
RootMaster = RootGUI()

# Initialize other GUI components
GUIMeas = MeasGUI(RootMaster.root, RootMaster)
GUIGraph = GraphGUI(RootMaster.root, GUIMeas)
GUICom = ComGUI(RootMaster.root, RootMaster)

# Link the initialized components to RootMaster
RootMaster.meas_gui = GUIMeas
RootMaster.graph_gui = GUIGraph
RootMaster.com_gui = GUICom

# Ensure MeasGUI has a reference to RootMaster's graph_gui
GUIMeas.parent.graph_gui = GUIGraph

# Start the Tkinter event loop
RootMaster.root.mainloop()

