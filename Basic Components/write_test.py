import tkinter as tk
from tkinter import ttk

class ResizableGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resizable GUI")
        
        # Configure the root window's grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create a Frame inside the root window
        self.frame = ttk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure the frame's grid
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Add a widget that will resize
        self.button = ttk.Button(self.frame, text="Resizable Button")
        self.button.grid(row=0, column=0, sticky="nsew")
        
        # Bind the <Configure> event to dynamically resize widgets
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        # Get the new window size
        width = event.width
        height = event.height
        
        # Dynamically adjust widget sizes
        self.button.config(width=width//10, height=height//30)

if __name__ == "__main__":
    app = ResizableGUI()
    app.mainloop()
