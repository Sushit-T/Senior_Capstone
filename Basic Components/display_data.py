import tkinter as tk
from tkinter import messagebox, Toplevel, Label
from PIL import Image, ImageTk, ImageSequence

class GifPopup:
    def __init__(self, parent, gif_path):
        self.top = Toplevel(parent)
        self.top.title("yippee")
        self.gif_label = Label(self.top)
        self.gif_label.pack()

        self.load_gif(gif_path)

    def load_gif(self, gif_path):
        self.gif = Image.open(gif_path)
        self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(self.gif)]
        self.current_frame = 0
        self.update_gif()

    def update_gif(self):
        self.gif_label.configure(image=self.frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.top.after(100, self.update_gif)  # Adjust the delay for animation speed

def show_message_with_gif():
    GifPopup(root, "Basic Components/yippee.gif")

root = tk.Tk()
root.title(":3")
root.geometry("200x75")

btn = tk.Button(root, text="click me!", command=show_message_with_gif)
btn.pack(pady=20)

root.mainloop()
