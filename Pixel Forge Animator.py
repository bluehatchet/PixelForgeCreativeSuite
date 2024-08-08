import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageSequence, GifImagePlugin
import os

#############################################################################
##                                                                         ##
## PixelForge Animator 16bit                                               ##
## Copyright (C) 2024  Justin Garcia                                       ##
##                                                                         ##
## This program is free software: you can redistribute it and/or modify    ##
## it under the terms of the GNU General Public License as published by    ##
## the Free Software Foundation, either version 3 of the License, or       ##
## (at your option) any later version.                                     ##
##                                                                         ##
## This program is distributed in the hope that it will be useful,         ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of          ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           ##
## GNU General Public License for more details.                            ##
##                                                                         ##
## You should have received a copy of the GNU General Public License       ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>.   ##
##                                                                         ##
#############################################################################

class PNGToGIFConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pixel Forge Animator")
        self.configure(bg='light gray')
        self.png_files = []
        self.frame_duration = 100  # Default frame duration in milliseconds
        self.preview_images = []
        self.current_preview_index = 0
        self.preview_animation_running = False
        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self, text="Load PNGs", command=self.load_pngs, bg='light blue', fg='black')
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        self.clear_button = tk.Button(self, text="Clear PNGs", command=self.clear_pngs, bg='red', fg='white')
        self.clear_button.grid(row=0, column=1, padx=10, pady=10)

        self.save_button = tk.Button(self, text="Save as GIF", command=self.save_as_gif, bg='light green', fg='black')
        self.save_button.grid(row=0, column=2, padx=10, pady=10)

        self.duration_button = tk.Button(self, text="Set Frame Duration", command=self.set_frame_duration, bg='orange', fg='black')
        self.duration_button.grid(row=0, column=3, padx=10, pady=10)

        self.preview_label = tk.Label(self, text="GIF Preview", bg='light gray', fg='black')
        self.preview_label.grid(row=1, column=0, columnspan=4)

        self.preview_canvas = tk.Canvas(self, bg='white')
        self.preview_canvas.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

        self.sequence_label = tk.Label(self, text="Sequence Control", bg='light gray', fg='black')
        self.sequence_label.grid(row=3, column=0, columnspan=4)

        self.up_button = tk.Button(self, text="Move Up", command=self.move_up, bg='light blue', fg='black')
        self.up_button.grid(row=4, column=0, padx=10, pady=10)

        self.down_button = tk.Button(self, text="Move Down", command=self.move_down, bg='light blue', fg='black')
        self.down_button.grid(row=4, column=1, padx=10, pady=10)

        self.remove_button = tk.Button(self, text="Remove", command=self.remove_selected, bg='light blue', fg='black')
        self.remove_button.grid(row=4, column=2, padx=10, pady=10)

        self.preview_listbox = tk.Listbox(self)
        self.preview_listbox.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        self.preview_listbox.bind("<<ListboxSelect>>", self.show_preview)

        self.preview_button = tk.Button(self, text="Preview Animation", command=self.toggle_preview_animation, bg='light blue', fg='black')
        self.preview_button.grid(row=6, column=0, columnspan=4, padx=10, pady=10)

    def load_pngs(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
        if file_paths:
            self.png_files.extend(file_paths)
            self.update_preview_list()
            self.show_preview()
            self.update_preview_canvas_size()

    def clear_pngs(self):
        self.png_files.clear()
        self.preview_listbox.delete(0, tk.END)
        self.preview_canvas.delete("all")
        self.preview_images.clear()

    def save_as_gif(self):
        if not self.png_files:
            messagebox.showwarning("No PNGs", "No PNG files loaded to convert.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
        if file_path:
            images = [Image.open(png) for png in self.png_files]
            images[0].save(file_path, save_all=True, append_images=images[1:], duration=self.frame_duration, loop=0, disposal=2)
            messagebox.showinfo("GIF Saved", f"GIF saved as {file_path}")

    def set_frame_duration(self):
        duration = simpledialog.askinteger("Frame Duration", "Enter frame duration in milliseconds:", initialvalue=self.frame_duration)
        if duration is not None:
            self.frame_duration = duration

    def update_preview_list(self):
        self.preview_listbox.delete(0, tk.END)
        for png in self.png_files:
            self.preview_listbox.insert(tk.END, os.path.basename(png))
        self.load_preview_images()

    def load_preview_images(self):
        self.preview_images.clear()
        for png in self.png_files:
            img = Image.open(png)
            self.preview_images.append(ImageTk.PhotoImage(img))

    def show_preview(self, event=None):
        selected_index = self.preview_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_images[index])

    def move_up(self):
        selected_index = self.preview_listbox.curselection()
        if selected_index and selected_index[0] > 0:
            index = selected_index[0]
            self.png_files.insert(index - 1, self.png_files.pop(index))
            self.update_preview_list()
            self.preview_listbox.selection_set(index - 1)

    def move_down(self):
        selected_index = self.preview_listbox.curselection()
        if selected_index and selected_index[0] < len(self.png_files) - 1:
            index = selected_index[0]
            self.png_files.insert(index + 1, self.png_files.pop(index))
            self.update_preview_list()
            self.preview_listbox.selection_set(index + 1)

    def remove_selected(self):
        selected_index = self.preview_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.png_files.pop(index)
            self.update_preview_list()
            self.show_preview()

    def toggle_preview_animation(self):
        if self.preview_animation_running:
            self.preview_animation_running = False
            self.preview_button.config(text="Preview Animation")
        else:
            self.preview_animation_running = True
            self.preview_button.config(text="Stop Animation")
            self.animate_preview()

    def animate_preview(self):
        if not self.preview_animation_running:
            return

        if self.preview_images:
            self.preview_canvas.delete("all")  # Clear the canvas for disposal=2 effect
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_images[self.current_preview_index])
            self.current_preview_index = (self.current_preview_index + 1) % len(self.preview_images)
            self.after(self.frame_duration, self.animate_preview)

    def update_preview_canvas_size(self):
        if self.png_files:
            first_image = Image.open(self.png_files[0])
            self.preview_canvas.config(width=first_image.width, height=first_image.height)

if __name__ == "__main__":
    app = PNGToGIFConverter()
    app.mainloop()
