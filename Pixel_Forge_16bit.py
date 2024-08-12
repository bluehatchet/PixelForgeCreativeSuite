import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog
from PIL import Image, ImageColor
import json
import os
import math

#############################################################################
##                                                                         ##
## Pixel Forge 16px                                                        ##
## Copyright (C) 2024  Bluehatchet                                         ##
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

class SpriteEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PixelForge 16x16px Editor")
        self.configure(bg='black')
        self.icon_image = tk.PhotoImage(file='frame_9.png')  # Set the icon
        self.iconphoto(False, self.icon_image)
        self.grid_size = 16
        self.cell_size = 20
        self.canvas_size = self.grid_size * self.cell_size
        self.last_colors = []
        self.current_color = None
        self.history = []
        self.redo_stack = []
        self.painting = False
        self.layers = []
        self.current_layer = 0
        self.max_layers = 25

        self.circle_mode = False
        self.line_mode = False
        self.start_x = None
        self.start_y = None

        # Default key bindings
        self.key_bindings = {
            "add_layer": "Ctrl+A",
            "duplicate_layer": "Ctrl+Shift+D",
            "delete_layer": "Ctrl+D",
            "merge_above": "Ctrl+Q",
            "merge_below": "Ctrl+Shift+Z",
            "toggle_layer": "T",
            "rotate_cw": "Ctrl+Up",
            "rotate_ccw": "Ctrl+Down",
            "flip_horizontal": "Left",
            "flip_vertical": "Right",
            "paint": "Ctrl+P",
            "undo": "<Control-z>",
            "redo": "<Control-Z>",
            "rename_layer": "Ctrl+R"
        }

        self.create_menu()
        self.create_widgets()
        self.create_grid()  # Create the grid before adding the first layer
        self.add_layer()
        self.bind_shortcuts()

    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        # File Menu
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export as 16x16 PNG", command=lambda: self.save_image(16))
        file_menu.add_command(label="Export as 32x32 PNG", command=lambda: self.save_image(32))
        file_menu.add_command(label="Export as 64x64 PNG", command=lambda: self.save_image(64))
        file_menu.add_command(label="Export as ICO", command=self.save_as_ico)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator=self.key_bindings["add_layer"])
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator=self.key_bindings["duplicate_layer"])

        # Edit Menu
        edit_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit_menu)

        # Layer Functions
        edit_menu.add_command(label=f"Add Layer ({self.key_bindings['add_layer']})", command=self.add_layer)
        edit_menu.add_command(label=f"Duplicate Layer ({self.key_bindings['duplicate_layer']})", command=self.duplicate_layer)
        edit_menu.add_command(label=f"Delete Layer ({self.key_bindings['delete_layer']})", command=self.delete_layer)
        edit_menu.add_command(label=f"Merge Above ({self.key_bindings['merge_above']})", command=self.merge_above)
        edit_menu.add_command(label=f"Merge Below ({self.key_bindings['merge_below']})", command=self.merge_below)
        edit_menu.add_command(label=f"Toggle Layer ({self.key_bindings['toggle_layer']})", command=self.toggle_layer)
        edit_menu.add_command(label=f"Rename Layer ({self.key_bindings['rename_layer']})", command=self.rename_layer)

        edit_menu.add_separator()  # Separator between Layers and Grid functions

        # Grid Functions
        edit_menu.add_command(label=f"Rotate 90° CW ({self.key_bindings['rotate_cw']})", command=self.rotate_clockwise)
        edit_menu.add_command(label=f"Rotate 90° CCW ({self.key_bindings['rotate_ccw']})", command=self.rotate_counterclockwise)
        edit_menu.add_command(label=f"Flip Horizontal ({self.key_bindings['flip_horizontal']})", command=self.flip_horizontal)
        edit_menu.add_command(label=f"Flip Vertical ({self.key_bindings['flip_vertical']})", command=self.flip_vertical)
        edit_menu.add_command(label=f"Paint ({self.key_bindings['paint']})", command=self.enable_paint_bucket)

        # Undo/Redo Functions
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo (Ctrl+Z)", command=self.undo)
        edit_menu.add_command(label="Redo (Ctrl+Shift+Z)", command=self.redo)

        # Help Menu
        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        about_text = "Pixel Forge\nVersion 1.0\n\nCreated by [Your Name]\n\nThis application allows you to create and edit pixel art sprites with multiple layers and export them in various formats."
        messagebox.showinfo("About", about_text)

    def create_widgets(self):
        self.layer_listbox = tk.Listbox(self, bg='dark gray', fg='white')
        self.layer_listbox.grid(row=0, column=0, padx=10, pady=10, rowspan=12, sticky="nsew")
        self.layer_listbox.bind("<<ListboxSelect>>", self.select_layer)

        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg='white')
        self.canvas.grid(row=0, column=1, rowspan=12, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.start_paint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.stop_paint)
        self.canvas.bind("<Button-3>", self.erase)
        self.canvas.bind("<B3-Motion>", self.erase)

        self.color_button = tk.Button(self, text="Choose Color", command=self.choose_color, bg='light blue', fg='black')
        self.color_button.grid(row=0, column=2, padx=10, pady=10)

        self.rotate_clockwise_button = tk.Button(self, text="Rotate 90° CW", command=self.rotate_clockwise, bg='orange', fg='black')
        self.rotate_clockwise_button.grid(row=1, column=2, padx=10, pady=10)

        self.rotate_counterclockwise_button = tk.Button(self, text="Rotate 90° CCW", command=self.rotate_counterclockwise, bg='orange', fg='black')
        self.rotate_counterclockwise_button.grid(row=2, column=2, padx=10, pady=10)

        self.flip_horizontal_button = tk.Button(self, text="Flip Horizontal", command=self.flip_horizontal, bg='purple', fg='white')
        self.flip_horizontal_button.grid(row=3, column=2, padx=10, pady=10)

        self.flip_vertical_button = tk.Button(self, text="Flip Vertical", command=self.flip_vertical, bg='purple', fg='white')
        self.flip_vertical_button.grid(row=4, column=2, padx=10, pady=10)

        self.paint_bucket_button = tk.Button(self, text="Paint", command=self.enable_paint_bucket, bg='light green', fg='black')
        self.paint_bucket_button.grid(row=5, column=2, padx=10, pady=10)

        self.draw_circle_button = tk.Button(self, text="Draw Circle", command=self.enable_circle_mode, bg='cyan', fg='black')
        self.draw_circle_button.grid(row=6, column=2, padx=10, pady=10)

        self.draw_line_button = tk.Button(self, text="Draw Line", command=self.enable_line_mode, bg='cyan', fg='black')
        self.draw_line_button.grid(row=7, column=2, padx=10, pady=10)

        self.add_layer_button = tk.Button(self, text="Add Layer", command=self.add_layer, bg='blue', fg='white')
        self.add_layer_button.grid(row=8, column=2, padx=10, pady=5)

        self.duplicate_layer_button = tk.Button(self, text="Duplicate Layer", command=self.duplicate_layer, bg='blue', fg='white')
        self.duplicate_layer_button.grid(row=9, column=2, padx=10, pady=5)

        self.rename_layer_button = tk.Button(self, text="Rename Layer", command=self.rename_layer, bg='blue', fg='white')
        self.rename_layer_button.grid(row=10, column=2, padx=10, pady=5)

        self.merge_above_button = tk.Button(self, text="Merge Above", command=self.merge_above, bg='green', fg='white')
        self.merge_above_button.grid(row=11, column=2, padx=10, pady=5)

        self.merge_below_button = tk.Button(self, text="Merge Below", command=self.merge_below, bg='green', fg='white')
        self.merge_below_button.grid(row=12, column=2, padx=10, pady=5)

        self.delete_layer_button = tk.Button(self, text="Delete Layer", command=self.delete_layer, bg='red', fg='white')
        self.delete_layer_button.grid(row=13, column=2, padx=10, pady=5)

        self.toggle_layer_button = tk.Button(self, text="Toggle Layer", command=self.toggle_layer, bg='yellow', fg='black')
        self.toggle_layer_button.grid(row=14, column=2, padx=10, pady=5)

        self.opacity_slider = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, label="Opacity", command=self.adjust_opacity, bg='black', fg='white')
        self.opacity_slider.set(100)
        self.opacity_slider.grid(row=15, column=2, padx=10, pady=10)

        self.color_history = tk.Frame(self, bg='black')
        self.color_history.grid(row=0, column=3, padx=10, pady=10, rowspan=12)

        self.paint_bucket_mode = False

    def bind_shortcuts(self):
        self.bind_all(self.key_bindings["add_layer"], self.add_layer)
        self.bind_all(self.key_bindings["duplicate_layer"], self.duplicate_layer)
        self.bind_all(self.key_bindings["delete_layer"], self.delete_layer)
        self.bind_all(self.key_bindings["merge_above"], self.merge_above)
        self.bind_all(self.key_bindings["merge_below"], self.merge_below)
        self.bind_all(self.key_bindings["rotate_cw"], self.rotate_clockwise)
        self.bind_all(self.key_bindings["rotate_ccw"], self.rotate_counterclockwise)
        self.bind_all(self.key_bindings["flip_horizontal"], self.flip_horizontal)
        self.bind_all(self.key_bindings["flip_vertical"], self.flip_vertical)
        self.bind_all(self.key_bindings["paint"], self.enable_paint_bucket)
        self.bind_all(self.key_bindings["toggle_layer"], self.toggle_layer)
        self.bind_all(self.key_bindings["rename_layer"], self.rename_layer)
        self.bind_all(self.key_bindings["undo"], self.undo)
        self.bind_all(self.key_bindings["redo"], self.redo)

    def create_grid(self):
        self.rectangles = {}
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rect_id = self.canvas.create_rectangle(i * self.cell_size, j * self.cell_size,
                                                       (i + 1) * self.cell_size, (j + 1) * self.cell_size,
                                                       fill="", outline="gray")
                self.rectangles[(i, j)] = rect_id
        self.load_grid_data()

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color
            if color not in self.last_colors:
                self.last_colors.append(color)
                self.update_color_history()

    def update_color_history(self):
        for widget in self.color_history.winfo_children():
            widget.destroy()

        for color in self.last_colors:
            color_button = tk.Button(self.color_history, bg=color, width=2, height=1,
                                     command=lambda c=color: self.set_color(c))
            color_button.pack(pady=2)

    def set_color(self, color):
        self.current_color = color

    def start_paint(self, event):
        self.record_state()
        self.painting = True
        self.start_x = event.x // self.cell_size
        self.start_y = event.y // self.cell_size

        if self.circle_mode or self.line_mode:
            return
        self.paint(event)

    def paint(self, event):
        if self.painting and self.current_color:
            x = event.x // self.cell_size
            y = event.y // self.cell_size

            if self.paint_bucket_mode:
                self.paint_bucket_fill(x, y)
            elif self.circle_mode:
                self.update_temp_circle(x, y)
            elif self.line_mode:
                self.update_temp_line(x, y)
            else:
                self.canvas.itemconfig(self.rectangles[(x, y)], fill=self.current_color)
                self.layers[self.current_layer]["data"][y][x] = self.current_color

    def stop_paint(self, event):
        if self.painting:
            if self.circle_mode:
                self.commit_temp_circle(event)
            elif self.line_mode:
                self.commit_temp_line(event)

        self.painting = False
        self.circle_mode = False
        self.line_mode = False
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def erase(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        self.record_state()
        self.canvas.itemconfig(self.rectangles[(x, y)], fill="")
        self.layers[self.current_layer]["data"][y][x] = None
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def rotate_clockwise(self, event=None):
        self.record_state()
        self.layers[self.current_layer]["data"] = [list(reversed(col)) for col in zip(*self.layers[self.current_layer]["data"])]
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def rotate_counterclockwise(self, event=None):
        self.record_state()
        self.layers[self.current_layer]["data"] = [list(row) for row in zip(*self.layers[self.current_layer]["data"])][::-1]
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def flip_horizontal(self, event=None):
        self.record_state()
        self.layers[self.current_layer]["data"] = [row[::-1] for row in self.layers[self.current_layer]["data"]]
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def flip_vertical(self, event=None):
        self.record_state()
        self.layers[self.current_layer]["data"].reverse()
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def enable_paint_bucket(self, event=None):
        self.paint_bucket_mode = True
        self.circle_mode = False
        self.line_mode = False
        self.canvas.bind("<Button-1>", self.paint_bucket_start)

    def enable_circle_mode(self):
        self.circle_mode = True
        self.paint_bucket_mode = False
        self.line_mode = False

    def enable_line_mode(self):
        self.line_mode = True
        self.paint_bucket_mode = False
        self.circle_mode = False

    def update_temp_circle(self, x, y):
        self.load_grid_data()  # Clear previous temporary shapes
        r = int(math.sqrt((x - self.start_x) ** 2 + (y - self.start_y) ** 2))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cx = i - self.start_x
                cy = j - self.start_y
                if cx * cx + cy * cy <= r * r:
                    self.canvas.itemconfig(self.rectangles[(i, j)], fill=self.current_color)

    def update_temp_line(self, x, y):
        self.load_grid_data()  # Clear previous temporary shapes
        x0, y0 = self.start_x, self.start_y
        dx = abs(x - x0)
        dy = abs(y - y0)
        sx = 1 if x0 < x else -1
        sy = 1 if y0 < y else -1
        err = dx - dy

        while True:
            self.canvas.itemconfig(self.rectangles[(x0, y0)], fill=self.current_color)
            if x0 == x and y0 == y:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def commit_temp_circle(self, event):
        end_x = event.x // self.cell_size
        end_y = event.y // self.cell_size
        r = int(math.sqrt((end_x - self.start_x) ** 2 + (end_y - self.start_y) ** 2))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cx = i - self.start_x
                cy = j - self.start_y
                if cx * cx + cy * cy <= r * r:
                    self.canvas.itemconfig(self.rectangles[(i, j)], fill=self.current_color)
                    self.layers[self.current_layer]["data"][j][i] = self.current_color

    def commit_temp_line(self, event):
        end_x = event.x // self.cell_size
        end_y = event.y // self.cell_size
        x0, y0 = self.start_x, self.start_y
        dx = abs(end_x - x0)
        dy = abs(end_y - y0)
        sx = 1 if x0 < end_x else -1
        sy = 1 if y0 < end_y else -1
        err = dx - dy

        while True:
            self.canvas.itemconfig(self.rectangles[(x0, y0)], fill=self.current_color)
            self.layers[self.current_layer]["data"][y0][x0] = self.current_color
            if x0 == end_x and y0 == end_y:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def paint_bucket_start(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        self.paint_bucket_fill(x, y)
        self.paint_bucket_mode = False
        self.canvas.bind("<Button-1>", self.start_paint)

    def paint_bucket_fill(self, x, y):
        target_color = self.layers[self.current_layer]["data"][y][x]
        if target_color == self.current_color:
            return
        self.record_state()
        self.flood_fill(x, y, target_color, self.current_color)
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def flood_fill(self, x, y, target_color, replacement_color):
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return
        if self.layers[self.current_layer]["data"][y][x] != target_color:
            return
        self.layers[self.current_layer]["data"][y][x] = replacement_color
        self.flood_fill(x + 1, y, target_color, replacement_color)
        self.flood_fill(x - 1, y, target_color, replacement_color)
        self.flood_fill(x, y + 1, target_color, replacement_color)
        self.flood_fill(x, y - 1, target_color, replacement_color)

    def add_layer(self, event=None):
        if len(self.layers) >= self.max_layers:
            messagebox.showwarning("Layer Limit", "Cannot add more than 25 layers.")
            return
        self.layers.append({"data": [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)], "visible": True, "opacity": 1.0})
        self.layer_listbox.insert(tk.END, f"Layer {len(self.layers)}")
        self.layer_listbox.selection_clear(0, tk.END)
        self.layer_listbox.selection_set(tk.END)
        self.current_layer = len(self.layers) - 1
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def duplicate_layer(self, event=None):
        if len(self.layers) >= self.max_layers:
            messagebox.showwarning("Layer Limit", "Cannot duplicate layer; maximum layers reached.")
            return
        self.record_state()
        duplicate_data = [row[:] for row in self.layers[self.current_layer]["data"]]
        self.layers.append({"data": duplicate_data, "visible": True, "opacity": 1.0})
        self.layer_listbox.insert(tk.END, f"Layer {len(self.layers)} (Duplicate)")
        self.layer_listbox.selection_clear(0, tk.END)
        self.layer_listbox.selection_set(tk.END)
        self.current_layer = len(self.layers) - 1
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def rename_layer(self, event=None):
        current_name = self.layer_listbox.get(self.current_layer)
        new_name = simpledialog.askstring("Rename Layer", "Enter new layer name:", initialvalue=current_name)
        if new_name:
            self.layer_listbox.delete(self.current_layer)
            self.layer_listbox.insert(self.current_layer, new_name)
            self.layer_listbox.selection_set(self.current_layer)

    def select_layer(self, event):
        selected = self.layer_listbox.curselection()
        if selected:
            self.current_layer = selected[0]
            self.load_grid_data()

    def toggle_layer(self, event=None):
        self.layers[self.current_layer]["visible"] = not self.layers[self.current_layer]["visible"]
        self.load_grid_data()

    def merge_above(self, event=None):
        if self.current_layer == 0:
            messagebox.showwarning("Merge Error", "Cannot merge the top layer with a layer above.")
            return
        self.record_state()
        for j in range(self.grid_size):
            for i in range(self.grid_size):
                if self.layers[self.current_layer]["data"][j][i] is not None:
                    self.layers[self.current_layer - 1]["data"][j][i] = self.layers[self.current_layer]["data"][j][i]
        self.delete_layer()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def merge_below(self, event=None):
        if self.current_layer == len(self.layers) - 1:
            messagebox.showwarning("Merge Error", "Cannot merge the bottom layer with a layer below.")
            return
        self.record_state()
        for j in range(self.grid_size):
            for i in range(self.grid_size):
                if self.layers[self.current_layer]["data"][j][i] is not None:
                    self.layers[self.current_layer + 1]["data"][j][i] = self.layers[self.current_layer]["data"][j][i]
        self.delete_layer()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def delete_layer(self, event=None):
        if len(self.layers) == 1:
            messagebox.showwarning("Delete Error", "Cannot delete the only layer.")
            return
        self.record_state()
        del self.layers[self.current_layer]
        self.layer_listbox.delete(self.current_layer)
        self.current_layer = max(0, self.current_layer - 1)
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def adjust_opacity(self, value):
        opacity = int(value) / 100
        self.layers[self.current_layer]["opacity"] = opacity
        self.load_grid_data()
        self.clear_redo_stack()  # Clear redo stack when a new action is taken

    def save_image(self, size):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")],
                                                 title="Save as")
        if file_path:
            image = Image.new("RGBA", (self.grid_size, self.grid_size), (0, 0, 0, 0))
            pixels = image.load()

            for layer in self.layers:
                if layer["visible"]:
                    layer_opacity = layer.get("opacity", 1.0)
                    for i in range(self.grid_size):
                        for j in range(self.grid_size):
                            color = layer["data"][j][i]
                            if color:
                                rgb_color = ImageColor.getrgb(color)
                                r, g, b = [int(c * layer_opacity) for c in rgb_color]
                                pixel_color = (r, g, b, int(255 * layer_opacity))
                                pixels[i, j] = pixel_color

            image = image.resize((size, size), Image.NEAREST)
            image.save(file_path)

    def save_as_ico(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".ico",
                                                 filetypes=[("ICO files", "*.ico")],
                                                 title="Save as ICO")
        if file_path:
            image = Image.new("RGBA", (self.grid_size, self.grid_size), (0, 0, 0, 0))
            pixels = image.load()

            for layer in self.layers:
                if layer["visible"]:
                    layer_opacity = layer.get("opacity", 1.0)
                    for i in range(self.grid_size):
                        for j in range(self.grid_size):
                            color = layer["data"][j][i]
                            if color:
                                rgb_color = ImageColor.getrgb(color)
                                r, g, b = [int(c * layer_opacity) for c in rgb_color]
                                pixel_color = (r, g, b, int(255 * layer_opacity))
                                pixels[i, j] = pixel_color

            # Create different sizes for ICO file
            icon_sizes = [image.resize((16, 16), Image.NEAREST),
                          image.resize((32, 32), Image.NEAREST),
                          image.resize((64, 64), Image.NEAREST)]
            icon_sizes[0].save(file_path, format='ICO', sizes=[(16, 16), (32, 32), (64, 64)])

    def save_project(self, event=None):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")],
                                                 title="Save Project")
        if file_path:
            project_data = {
                "layers": self.layers,
                "last_colors": self.last_colors
            }
            with open(file_path, 'w') as f:
                json.dump(project_data, f)
            messagebox.showinfo("Save Project", "Project saved successfully!")

    def open_project(self, event=None):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json")],
                                               title="Open Project")
        if file_path:
            with open(file_path, 'r') as f:
                project_data = json.load(f)
            self.layers = project_data["layers"]
            self.last_colors = project_data["last_colors"]
            self.update_color_history()
            self.load_grid_data()
            messagebox.showinfo("Open Project", "Project loaded successfully!")

    def load_grid_data(self):
        for j in range(self.grid_size):
            for i in range(self.grid_size):
                color = None
                for layer in self.layers:
                    if layer["visible"] and layer["data"][j][i]:
                        layer_opacity = layer.get("opacity", 1.0)
                        color = layer["data"][j][i]
                        if color:
                            rgb_color = ImageColor.getrgb(color)
                            r, g, b = [int(c * layer_opacity) for c in rgb_color]
                            color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.itemconfig(self.rectangles[(i, j)], fill=color if color else "")

    def record_state(self):
        # Push current state to the undo stack
        self.history.append([row[:] for row in self.layers[self.current_layer]["data"]])
        # Clear redo stack since a new action is taken
        self.redo_stack.clear()

    def undo(self, event=None):
        if self.history:
            # Push current state to the redo stack before undoing
            self.redo_stack.append([row[:] for row in self.layers[self.current_layer]["data"]])
            # Pop the last state from the undo stack
            self.layers[self.current_layer]["data"] = self.history.pop()
            self.load_grid_data()

    def redo(self, event=None):
        if self.redo_stack:
            # Push current state to the undo stack before redoing
            self.history.append([row[:] for row in self.layers[self.current_layer]["data"]])
            # Pop the last state from the redo stack
            self.layers[self.current_layer]["data"] = self.redo_stack.pop()
            self.load_grid_data()

    def clear_redo_stack(self):
        self.redo_stack.clear()

if __name__ == "__main__":
    app = SpriteEditor()
    app.mainloop()
