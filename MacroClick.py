import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import time
import ctypes
import win32api
import keyboard
from pathlib import Path
import re
from sys import exit
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode
import pydirectinput
from ImageSnipper import ImageSnipper
# Why import libraries that do basically the same thing?
# From my testing this combination has worked best for the games I tested it on.

SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseMover:
    def move_mouse_right(self, pixel_amount):
        pydirectinput.move(pixel_amount, None)
    def move_mouse_up(self, pixel_amount):
        pydirectinput.move(None, pixel_amount)
    def move_mouse_to(self, x, y):
        pydirectinput.moveTo(x, y)

class Keyboard:
    def __init__(self):
        # Key Scan Codes
        # Even though they aren't really used too much in this code manually
        # I want to keep them here as a just in case the keyboard library isn't perfect
        self.ZERO = 0x0B
        self.ONE = 0x02
        self.TWO = 0x03
        self.THREE = 0x04
        self.FOUR = 0x05
        self.FIVE = 0x06
        self.SIX = 0x07
        self.SEVEN = 0x08
        self.EIGHT = 0x09
        self.NINE = 0x0A
        self.NUMP_ZERO = 0x52
        self.NUMP_ONE = 0x4F
        self.NUMP_TWO = 0x50
        self.NUMP_THREE = 0x51
        self.NUMP_FOUR = 0x4B
        self.NUMP_FIVE = 0x4C
        self.NUMP_SIX = 0x4D
        self.NUMP_SEVEN = 0x47
        self.NUMP_EIGHT = 0x48
        self.NUMP_NINE = 0x49
        self.A = 0x1E
        self.B = 0x30
        self.C = 0x2E
        self.D = 0x20
        self.E = 0x12
        self.F = 0x21
        self.G = 0x22
        self.H = 0x23
        self.I = 0x17
        self.J = 0x24
        self.K = 0x25
        self.L = 0x26
        self.M = 0x32
        self.N = 0x31
        self.O = 0x18
        self.P = 0x19
        self.Q = 0x10
        self.R = 0x13
        self.S = 0x1F
        self.T = 0x14
        self.U = 0x16
        self.V = 0x2F
        self.W = 0x11
        self.X = 0x2D
        self.Y = 0x15
        self.Z = 0x2C
        self.TAB = 0x0F
        self.LEFT_SHIFT = 0x2A
        self.RIGHT_SHIFT = 0x36
        self.LEFT_CONTROL = 0x1D
        self.RIGHT_CONTROL = 0x9D
        self.BACKSPACE = 0x0E
        self.ENTER = 0x1C
        self.LEFT_ALT = 0x38
        self.SPACE = 0x39
        self.SEMICOLON = 0x27
        self.APOSTROPHE = 0x28
        self.BACKSLASH = 0x2B
        self.COMMA = 0x33
        self.PERIOD = 0x34
        self.SLASH = 0x35
        self.STAR = 0x37
        self.MINUS = 0x4A
        self.PLUS = 0x4E
        self.EQUALS = 0x8D
        self.UP = 0xC8
        self.LEFT = 0xCB
        self.RIGHT = 0xCD
        self.DOWN = 0xD0
        self.ESC = 0x01


    def press_key(self, hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


    def release_key(self, hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0,
                            ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def click_key(self, hexKeyCode):
        self.press_key(hexKeyCode)
        time.sleep(0.01)
        self.release_key(hexKeyCode)
        time.sleep(0.01)

# I have had this code on my computer for so long I don't rmember the original author of these classes.
# So the classes below here up until MacroClickGUI class are not my original creations.
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

        

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


class MacroClickGUI:

    class MacroExecuter:
        def __init__(self, key, command_types, command_vals, master):
            self.master = master
            self.image_snipper = ImageSnipper(self.master)
            self.key = key
            self.command_types = command_types
            self.command_vals = command_vals
            self.running = False
            self.mouse = Controller()

            self.PROCESS_PER_MONITOR_DPI_AWARE = 2
            self.MDT_EFFECTIVE_DPI = 0
            self.x_scale, self.y_scale = self.get_dpi_scale()


        ## So depending on what you have your screen scaling set to, that can mess with
        ## moving the mouse to the correct cordinates.
        ## Here is a function that get's the scaling for windows I just found it easier to
        ## set my screen scaling to 100% so I haven't tried implementing the function anywhere
        def get_dpi_scale(self):
            shcore = ctypes.windll.shcore
            monitors = win32api.EnumDisplayMonitors()
            hresult = shcore.SetProcessDpiAwareness(self.PROCESS_PER_MONITOR_DPI_AWARE)
            assert hresult == 0
            dpiX = ctypes.c_uint()
            dpiY = ctypes.c_uint()
            for i, monitor in enumerate(monitors):
                shcore.GetDpiForMonitor(
                    monitor[0].handle,
                    self.MDT_EFFECTIVE_DPI,
                    ctypes.byref(dpiX),
                    ctypes.byref(dpiY)
                )
                x_scale = dpiX.value / 96
                y_scale = dpiY.value / 96

                return x_scale, y_scale

        def start_macro(self):
            self.running = True

        def stop_macro(self):
            self.running = False
            
        def run(self):
            try:
                if self.running:
                    keyb = Keyboard()
                    mouse_mover = MouseMover()
                    i = 0
                    for elem in self.command_types:
                        if elem == 'delay':
                            delay = float(self.command_vals[i])
                            time.sleep(delay)
                        elif elem == 'key_text':
                            key = str(self.command_vals[i][1])
                            if len(key) > 1:
                                if key == 'up':
                                    key_hexcode = keyb.UP
                                elif key == 'down':
                                    key_hexcode = keyb.DOWN
                                elif key == 'right':
                                    key_hexcode = keyb.RIGHT
                                elif key == 'left':
                                    key_hexcode = keyb.LEFT
                                elif key == 'esc':
                                    key_hexcode = keyb.ESC
                                elif key == 'tab':
                                    key_hexcode = keyb.TAB
                                elif key == 'l_shift':
                                    key_hexcode = keyb.LEFT_SHIFT
                                elif key == 'r_shift':
                                    key_hexcode = keyb.RIGHT_SHIFT
                                elif key == 'l_control':
                                    key_hexcode = keyb.LEFT_CONTROL
                                elif key == 'r_control':
                                    key_hexcode = keyb.RIGHT_CONTROL
                                elif key == 'backspace':
                                    key_hexcode = keyb.BACKSPACE
                                elif key == 'enter':
                                    key_hexcode = keyb.ENTER
                                elif key == 'l_alt':
                                    key_hexcode = keyb.LEFT_ALT
                                elif key == 'space':
                                    key_hexcode = keyb.SPACE
                                else:
                                    key_hexcode = keyb.Z
                            else:
                                key_hexcode = keyboard.key_to_scan_codes(key)[0]
                            if self.command_vals[i][0] == 'press': # Press
                                keyb.press_key(key_hexcode)
                                time.sleep(0.0001)
                            elif self.command_vals[i][0] == 'release': # Release
                                keyb.release_key(key_hexcode)
                                time.sleep(0.0001)
                            elif self.command_vals[i][0] == 'click': # Click
                                keyb.click_key(key_hexcode)
                            
                                
                        elif elem == 'mouse_press':
                            if self.command_vals[i][0] == 'press':
                                if self.command_vals[i][1] == 'right':
                                    self.mouse.press(Button.right)
                                else:
                                    self.mouse.press(Button.left)
                        elif elem == 'mouse_release':
                            if self.command_vals[i][0] == 'release':
                                if self.command_vals[i][1] == 'right':
                                    self.mouse.release(Button.right)
                                else:
                                    self.mouse.release(Button.left)
                        elif elem == 'mouse_click':
                            if self.command_vals[i][0] == 'click':
                                if self.command_vals[i][1] == 'right':
                                    self.mouse.click(Button.right)
                                else:
                                    self.mouse.click(Button.left)
                        elif elem == 'mouse_text':
                            move_mouse = self.command_vals[i]
                            if move_mouse[0] == 'up':
                                pixels = (- int(move_mouse[1]))
                                mouse_mover.move_mouse_up(pixels)
                            elif move_mouse[0] == 'down':
                                pixels = (int(move_mouse[1]))
                                mouse_mover.move_mouse_up(pixels)
                            elif move_mouse[0] == 'left':
                                pixels = (- int(move_mouse[1]))
                                mouse_mover.move_mouse_right(pixels)
                            elif move_mouse[0] == 'right':
                                pixels = (int(move_mouse[1]))
                                mouse_mover.move_mouse_right(pixels)
                            elif move_mouse[0] == 'to':
                                index = 0
                                for l in move_mouse:
                                    if l == ',':
                                        break
                                    index += 1
                                pixels_x = (int(move_mouse[1]))
                                pixels_y = (int(move_mouse[2]))
                                
                                mouse_mover.move_mouse_to(pixels_x, pixels_y)

                        elif elem == 'click_image':
                            folder = self.command_vals[i][0]
                            image = self.command_vals[i][1]
                            if self.command_vals[i][2] != None:
                                match_pct = float(self.command_vals[i][2])
                            else:
                                match_pct = 0.8

                            found, pos = self.image_snipper.find_template(folder, image, match_pct)
                            if found:
                                pixels_x = (int(pos[0]))
                                pixels_y = (int(pos[1]))
                                    
                                mouse_mover.move_mouse_to(pixels_x, pixels_y)
                                time.sleep(0.001)
                                self.mouse.click(Button.left)

                        elif elem == 'click_images':
                            folder = self.command_vals[i][0]
                    
                            if self.command_vals[i][1] != None:
                                match_pct = float(self.command_vals[i][1])
                            else:
                                match_pct = 0.8

                            images_pos = self.image_snipper.find_templates_in_folder(folder, match_pct)
                            for pos in images_pos:
                                pixels_x = (int(pos[0]))
                                pixels_y = (int(pos[1]))
                                    
                                mouse_mover.move_mouse_to(pixels_x, pixels_y)
                                time.sleep(0.001)
                                self.mouse.click(Button.left)

                        elif elem == 'click_color':
                            folder, image, smallest_size = self.command_vals[i]

                            found, centers = self.image_snipper.detect_color(folder, image, smallest_size)
                            
                            if found:
                                for center in centers:
                                    # Get center of first bounding rect
                                    x = center[0]
                                    y = center[1]
                                    mouse_mover.move_mouse_to(x, y)
                                    time.sleep(0.001)
                                    self.mouse.click(Button.left)

                            else:
                                pass

                        else:
                            pass
                    
                        i += 1
                        


                    self.master.after(1, self.run)
                    
                else:
                    self.master.after(1, self.run)
            except:
                self.master.after(1, self.run)

 
    # Initialize gui and variables
    def __init__(self, master):
        self.macro_thread = MacroClickGUI.MacroExecuter(KeyCode(char='x'), command_types=['delay'], command_vals=['0.001'], master=master)
        self.image_snipper = self.macro_thread.image_snipper
        self.master = master
        
        
        self.master.title("Macro Click")

        self.display_frame = tk.Frame(self.master)

        self.natural_lang_text_box = tk.Text(self.display_frame)
        self.natural_lang_text_box.insert("1.0", "[start_key x] [delay 1] [click mouse]")
        self.natural_lang_text_box.grid(row=0, column=0)
        nl_update_button = tk.Button(self.display_frame, text="Update Command", bg='steelblue1', command=lambda: self.update_nl(str(self.natural_lang_text_box.get("1.0", tk.END))))
        nl_update_button.grid(row=1, column=0, sticky='n')

        load_button = tk.Button(self.display_frame, text='Load Macro', bg='DarkGoldenrod1' ,command=lambda: self.load_macro())
        load_button.grid(row=4, column=0, sticky='ew')

        save_button = tk.Button(self.display_frame, text='Save Macro', bg='RosyBrown2', command=lambda: self.save_macro(str(self.natural_lang_text_box.get("1.0", tk.END))))
        save_button.grid(row=2, column=0, sticky='ew')

        snip_button = tk.Button(self.display_frame, text='Snip Image', bg='SpringGreen1', command=self.image_snipper.snip_image) 
        snip_button.grid(row=5, column=0, sticky='ew')

        instruct_button = tk.Button(self.display_frame, text='Help!!', bg='green', command=lambda: self.help())
        instruct_button.grid(row=6, column=0, sticky='ew')

        self.run_macro = False

        self.start_key = 'x'
  
        self.command_vals = []
        self.command_types = []

        self.display_frame.pack()
            

    def letter_finder(self, content):
        if 'up' in content:
            return 'up'
        elif 'down' in content:
            return 'down'
        elif 'right' in content:
            return 'right'
        elif 'left' in content:
            return 'left'
        elif 'esc' in content:
            return 'esc'
        elif 'tab' in content:
            return 'tab'
        elif 'l_shift' in content:
            return 'l_shift'
        elif 'r_shift' in content:
            return 'r_shift'
        elif 'l_control' in content:
            return 'l_control'
        elif 'r_control' in content:
            return 'r_control'
        elif 'backspace' in content:
            return 'backspace'
        elif 'enter' in content:
            return 'enter'
        elif 'l_alt' in content:
            return 'l_alt'
        elif 'space' in content:
            return 'space'
        else:
            # Define the pattern to match single letters within the content
            letters_pattern = re.compile(r'\b([a-zA-Z])\b')
            letters = letters_pattern.findall(content)
            return letters[0] 
        
    def get_bracket_content(self, text, key):
        pattern = r'(\w+)\((.+?)\)' 
        matches = re.finditer(pattern, text)

        for match in matches:
            tag = match.group(1)
            content = match.group(2)
            if tag == key:
                return content

    
    def update_nl(self, nl_commands):
        self.command_vals = []
        self.command_types = []
        brackets_pattern = re.compile(r'\[([^]]+)\]')
        # Define the pattern to match integers and floats within the content
        numbers_pattern = re.compile(r'\b(?:\d+\.\d+|\d+)\b')
        
        # Use finditer to get match objects with positions
        matches = brackets_pattern.finditer(nl_commands)

        for match in matches:
            content = (match.group(1)).lower()  # Content within the brackets

            if 'delay' in content:
                # Search for numbers within the content
                numbers = numbers_pattern.findall(content)

                # Additional checks on the numbers
                duration = float(numbers[0])

                if ('minutes' in content) or ('minute' in content) or ('min' in content) or ('mins' in content):
                    duration = duration * 60
                elif ('hours' in content) or ('hour' in content) or ('hr' in content) or ('hrs' in content):
                    duration = (duration * 60) * 60

                self.command_types.append('delay')
                self.command_vals.append(str(duration))

            elif 'press' in content:
                if 'mouse' in content:
                    if 'right' in content:
                        self.command_types.append('mouse_press')
                        self.command_vals.append(['press', 'right'])
                    else:
                        self.command_types.append('mouse_press')
                        self.command_vals.append(['press', 'left'])
                else:
                    letter = self.letter_finder(content)
                    self.command_types.append('key_text')
                    self.command_vals.append(['press', letter])
                    

            elif 'release' in content:
                if 'mouse' in content:
                    if 'right' in content:
                        self.command_types.append('mouse_release')
                        self.command_vals.append(['release', 'right'])
                        
                    else:
                        self.command_types.append('mouse_release')
                        self.command_vals.append(['release', 'left'])
                else:
                    letter = self.letter_finder(content)
                    self.command_types.append('key_text')
                    self.command_vals.append(['release', letter])


            elif 'click_images' in content:
                folder = self.get_bracket_content(content, 'folder')
                match_pct = float(self.get_bracket_content(content, 'percent')) / 100.0
                
                self.command_types.append('click_images')
                self.command_vals.append([folder, match_pct])

            elif 'click_image' in content:
                folder = self.get_bracket_content(content, 'folder') 
                if not folder:
                    folder = ""
                image = self.get_bracket_content(content, 'image')
                match_pct = self.get_bracket_content(content, 'percent')
                if match_pct:
                    match_pct = float(match_pct) / 100

                else:
                    match_pct = 0.8

                self.command_types.append('click_image')
                self.command_vals.append([folder, image, match_pct])

            elif 'click_color' in content:
                folder = self.get_bracket_content(content, 'folder') 
                image_file = self.get_bracket_content(content, 'image')
                smallest_size = self.get_bracket_content(content, 'size')
                if smallest_size:
                    numbers = numbers_pattern.findall(smallest_size)
                    numberx = int(numbers[0])
                    numbery = int(numbers[1])
                
                    self.command_types.append('click_color')
                    self.command_vals.append([folder, image_file, (numberx, numbery)])
                
                else:
                    self.command_types.append('click_color')
                    self.command_vals.append([folder, image_file, (0, 0)])

            elif ('autoclick' in content) or ('ac' in content):
                numbers = numbers_pattern.findall(content)
                duration = float(numbers[0])

                self.command_types.append('mouse_click')
                self.command_vals.append(['click', 'left'])
                self.command_types.append('delay')
                self.command_vals.append(str(duration))
                    

            elif 'click' in content:
                if 'mouse' in content:
                    if 'right' in content:
                        self.command_types.append('mouse_click')
                        self.command_vals.append(['click', 'right'])  
                    else:
                        self.command_types.append('mouse_click')
                        self.command_vals.append(['click', 'left'])
                else:
                    letter = self.letter_finder(content)
                    self.command_types.append('key_text')
                    self.command_vals.append(['click' ,letter])

            elif 'move' in content:
                if 'mouse' in content:
                    if 'left' in content:
                        numbers = numbers_pattern.findall(content)
                        number = numbers[0]
                        self.command_types.append('mouse_text')
                        self.command_vals.append(['left', number])
                    elif 'right' in content:
                        numbers = numbers_pattern.findall(content)
                        number = numbers[0]
                        self.command_types.append('mouse_text')
                        self.command_vals.append(['right', number])
                    elif 'up' in content:
                        numbers = numbers_pattern.findall(content)
                        number = numbers[0]
                        self.command_types.append('mouse_text')
                        self.command_vals.append(['up', number])

                    elif 'down' in content:
                        numbers = numbers_pattern.findall(content)
                        number = numbers[0]
                        self.command_types.append('mouse_text')
                        self.command_vals.append(['down', number])

                    elif 'to' in content:
                        numbers = numbers_pattern.findall(content)
                        numberx = numbers[0]
                        numbery = numbers[1]
                        self.command_types.append('mouse_text')
                        self.command_vals.append(['to', numberx, numbery])

            
                    
            elif 'start_key' in content:
                letter = self.letter_finder(content)
                self.start_key = letter

            

            



        self.apply_settings()
        
    # Function to apply settings and turn the run_macro boolean true so that the macro will run instead of the autoclicker
    def apply_settings(self):
        try:
            key = KeyCode(char=self.start_key)
            self.master.after(100, self.macro_thread.run)
            self.macro_thread.key = key
            self.macro_thread.command_types = self.command_types
            self.macro_thread.command_vals = self.command_vals
            self.run_macro = True
        except:
            pass
        

    # Function for when the key that is specified is pressed it will run the autoclicker or the macro
    def on_press(self, key):
        try:
            if self.run_macro:
                if key == self.macro_thread.key:
                    self.macro_thread.running = not self.macro_thread.running
            
        except:
            try:
                if key == self.macro_thread.key:
                    self.macro_thread.running = not self.macro_thread.running
            except:
                pass

    

    # Function to save the current values of the inputs for the current macro
    def save_macro(self, text_of_box):
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            initialfile="macro.txt",
            title="Save macro as", 
            filetypes=(("Text files", "*.txt"), ("all files", "*.*"))  
        )

        if filename:
            # Append .txt if needed
            filename = Path(filename)
            if filename.suffix != ".txt":
                filename = filename.with_suffix(".txt")

            try:
                with open(filename, 'w') as f:
                    f.write(text_of_box)   
                messagebox.showinfo("Saved", "Macro Saved!")

            except:
                messagebox.showwarning("Not Saved", "Error saving macro!")

    # Function to load previously saved macros
    def load_macro(self):
        filename = filedialog.askopenfilename(
        initialdir=".", 
        title="Select macro file",
        filetypes=(("Text files", "*.txt"), ("all files", "*.*"))
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                messagebox.showinfo("Loaded", "Macro Loaded!")
                self.natural_lang_text_box.delete("1.0", tk.END)
                self.natural_lang_text_box.insert("1.0", content)
                self.macro_thread.running = False
                self.update_nl(str(self.natural_lang_text_box.get("1.0", tk.END)))

            except:
                messagebox.showwarning("Not Loaded", "Error loading macro!")

    # Function to display a help message box
    def help(self):
        messagebox.showinfo("Help", """How to use: \n
        0. [start_key z] start key must come first if using
        1. [autoclick 1] autoclick every second
        2. [delay 1] [delay 1 second] [delay 1 minute] [delay 1 hour] delays are defaulted to seconds.
        3. [click a] [click mouse] [click mouse right] [click tab] etc.
        4. [press a] [press mouse] [press mouse right] [press l_ctrl] etc.
        5. [release a] [release mouse] [release mouse right] [release enter] etc.
        6. [move mouse left 100 pixels] [move mouse right 100] [move mouse to 500 , 500]
        7. [click_image folder(folder_name) image(image_name)] Do not need to add extension such as .jpg
        8. [click_images folder(folder_name) percent(85)] percent can be used for percent to match before clicking.
        9. [click_color folder(folder_name) image(to_get_avg_color_of)]
        10.[click_color folder(folder_name) image(to_get_avg_color_of) size(25,25)] Don't click on detected color below that size
        11. Enjoy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        https://github.com/PurifiedBananaWater/Macro-Click""")

# Function to make sure the entire program is exited on close
def quit_after_window_closed():
    exit()


window = tk.Tk()
window.protocol("WM_DELETE_WINDOW", quit_after_window_closed)
program = MacroClickGUI(window)
with Listener(on_press=program.on_press) as listener:
    window.mainloop()
    listener.join()