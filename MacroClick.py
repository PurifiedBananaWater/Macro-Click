import tkinter as tk
from tkinter import messagebox
import time
import ctypes
import keyboard
import csv
import os
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode
import pydirectinput
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

    class AutoClicker:
        def __init__(self, delay, button, key, master):
            self.master = master
            self.delay = delay
            self.button = button
            self.key = key
            self.running = False
            self.mouse = Controller()

        def start_clicking(self):
            self.running = True

        def stop_clicking(self):
            self.running = False
            
        def run(self):
            try:
                if self.running:
                    self.mouse.click(self.button)
                    time.sleep(self.delay)
                    self.master.after(1, self.run)

                else:
                    self.master.after(1, self.run)
            except:
                self.master.after(1, self.run)

    class MacroExecuter:
        def __init__(self, key, command_types, command_vals, master):
            self.master = master
            self.key = key
            self.command_types = command_types
            self.command_vals = command_vals
            self.running = False
            self.mouse = Controller()

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
                            key = str(self.command_vals[i])
                            if len(key) > 1:
                                if key == 'up' or key == 'Up' or key == 'UP':
                                    key_hexcode = keyb.UP
                                elif key == 'down' or key == 'Down' or key == 'DOWN':
                                    key_hexcode = keyb.DOWN
                                elif key == 'right' or key == 'Right' or key == 'RIGHT':
                                    key_hexcode = keyb.RIGHT
                                elif key == 'left' or key == 'Left' or key == 'LEFT':
                                    key_hexcode = keyb.LEFT
                                elif key == 'esc' or key == 'Esc' or key == 'ESC':
                                    key_hexcode = keyb.ESC
                                elif key == 'tab' or key == 'Tab' or key == 'TAB':
                                    key_hexcode = keyb.TAB
                                elif key == 'l shift' or key == 'left shift' or key == 'L shift' or key == 'L Shift' or key == 'L SHIFT' or key == 'LEFT SHIFT' or key == 'Left Shift':
                                    key_hexcode = keyb.LEFT_SHIFT
                                elif key == 'r shift' or key == 'right shift' or key == 'R shift' or key == 'R Shift' or key == 'R SHIFT' or key == 'RIGHT SHIFT' or key == 'Right Shift':
                                    key_hexcode = keyb.RIGHT_SHIFT
                                elif key == 'l control' or key == 'left control' or key == 'L control' or key == 'L Control' or key == 'L CONTROL' or key == 'LEFT CONTROL' or key == 'Left Control' or key == 'ctrl' or key == 'l ctrl' or key == 'L CTRL':
                                    key_hexcode = keyb.LEFT_CONTROL
                                elif key == 'r control' or key == 'right control' or key == 'R control' or key == 'R Control' or key == 'R CONTROL' or key == 'RIGHT CONTROL' or key == 'Right Control' or key == 'r ctrl' or key == 'R CTRL':
                                    key_hexcode = keyb.RIGHT_CONTROL
                                elif key == 'backspace' or key == 'BACKSPACE' or key == 'bckspc' or key == 'back' or key == 'BACK':
                                    key_hexcode = keyb.BACKSPACE
                                elif key == 'enter' or key == 'return' or key == 'entr' or key == 'ENTER' or key == 'RETURN' or key == 'ENTR' or key == 'Enter' or key == 'Return':
                                    key_hexcode = keyb.ENTER
                                elif key == 'l alt' or key == 'left alt' or key == 'alt' or key == 'L Alt' or key == 'L ALT' or key == 'ALT':
                                    key_hexcode = keyb.LEFT_ALT
                                elif key == 'space' or key == 'Space' or key == 'SPACE' or key == 'spc':
                                    key_hexcode = keyb.SPACE
                                else:
                                    key_hexcode = keyb.Z
                            else:
                                key_hexcode = keyboard.key_to_scan_codes(key)[0]
                            if self.command_vals[i + 1] == '1': # Press
                                keyb.press_key(key_hexcode)
                                time.sleep(0.0001)
                            elif self.command_vals[i + 2] == '1': # Release
                                keyb.release_key(key_hexcode)
                                time.sleep(0.0001)
                            elif self.command_vals[i + 3] == '1': # Click
                                keyb.click_key(key_hexcode)
                            
                                
                        elif elem == 'mouse_press':
                            if self.command_vals[i] == '1':
                                if self.command_vals[i - 1] == '1':
                                    self.mouse.press(Button.right)
                                else:
                                    self.mouse.press(Button.left)
                        elif elem == 'mouse_release':
                            if self.command_vals[i] == '1':
                                if self.command_vals[i - 3] == '1':
                                    self.mouse.release(Button.right)
                                else:
                                    self.mouse.release(Button.left)
                        elif elem == 'mouse_click':
                            if self.command_vals[i] == '1':
                                if self.command_vals[i - 4] == '1':
                                    self.mouse.click(Button.right)
                                else:
                                    self.mouse.click(Button.left)
                        elif elem == 'mouse_text':
                            move_mouse = self.command_vals[i]
                            if move_mouse[0:2] == 'Up' or move_mouse[0:2] == 'up' or move_mouse[0:2] == 'UP':
                                pixels = - int(move_mouse[3:-1])
                                mouse_mover.move_mouse_up(pixels)
                            elif move_mouse[0:4] == 'Down' or move_mouse[0:4] == 'down' or move_mouse[0:4] == 'DOWN':
                                pixels = int(move_mouse[5:-1])
                                mouse_mover.move_mouse_up(pixels)
                            elif move_mouse[0:4] == 'Left' or move_mouse[0:4] == 'left' or move_mouse[0:4] == 'LEFT':
                                pixels = - int(move_mouse[5:-1])
                                mouse_mover.move_mouse_right(pixels)
                            elif move_mouse[0:5] == 'Right' or move_mouse[0:5] == 'right' or move_mouse[0:5] == 'RIGHT':
                                pixels = int(move_mouse[6:-1])
                                mouse_mover.move_mouse_right(pixels)
                            elif move_mouse[0:2] == 'To' or move_mouse[0:2] == 'to' or move_mouse[0:2] == 'TO':
                                index = 0
                                for l in move_mouse:
                                    if l == ',':
                                        break
                                    index += 1
                                pixels_x = int(move_mouse[3:index])
                                pixels_y = int(move_mouse[(index + 1):-1])
                                mouse_mover.move_mouse_to(pixels_x, pixels_y)

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
        self.click_thread = MacroClickGUI.AutoClicker(0, Button.left, KeyCode(char='z'), master)
        self.macro_thread = MacroClickGUI.MacroExecuter(KeyCode(char='z'), command_types=['delay'], command_vals=['0.001'], master=master)
        self.master = master
        
        self.master.title("Macro Click")

        self.display_frame = tk.Frame(self.master)

        delay_text_box = tk.Entry(self.display_frame)
        delay_text_box.insert(0, "Delay Between Clicks")

        strt_stp_text_box = tk.Entry(self.display_frame)
        strt_stp_text_box.insert(0, "Which key you press to start the auto click (default is z)")

        delay_text_box.grid(row=0, column=0)
        strt_stp_text_box.grid(row=1, column=0)

        rightclick_bool = tk.IntVar()
        r_click_button = tk.Checkbutton(self.display_frame, text="Right Click", variable=rightclick_bool)
        r_click_button.grid(row=0, column=1)

        auto_button = tk.Button(self.display_frame, text="Autoclick", command=lambda: self.autoclick(delay_text_box, rightclick_bool, strt_stp_text_box))
        auto_button.grid(row=0, column=2, sticky='ew')

        apply_button = tk.Button(self.display_frame, text="Apply Macro Settings", command=lambda: self.apply_settings(strt_stp_text_box))
        apply_button.grid(row=1, column=2, sticky='ew')

        add_button = tk.Button(self.display_frame, text="Add Command", command=self.add_command)
        add_button.grid(row=2, column=2, sticky='ew')

        load_text_box = tk.Entry(self.display_frame)
        load_text_box.grid(row=1, column=4, sticky='ew')
        load_text_box.insert(0, 'Name of Previously Saved Macro')
        load_button = tk.Button(self.display_frame, text='Load Macro', command=lambda: self.load_macro(str(load_text_box.get())))
        load_button.grid(row=1, column=3, sticky='ew')

        save_text_box = tk.Entry(self.display_frame)
        save_text_box.grid(row=0, column=4, sticky='ew')
        save_text_box.insert(0, 'Name of Macro to Save')
        save_button = tk.Button(self.display_frame, text='Save Macro', command=lambda: self.save_macro(str(save_text_box.get())))
        save_button.grid(row=0, column=3, sticky='ew')

        instruct_button = tk.Button(self.display_frame, text='Help!!', bg='green', command=lambda: self.help())
        instruct_button.grid(row=2, column=3, sticky='ew')

        self.remove_command_button = tk.Button()

        self.run_macro = False

        self.text_boxes = [delay_text_box, strt_stp_text_box]
        self.display_buttons = [auto_button, apply_button]
        self.key_buttons = []
        self.mouse_buttons = []
        self.command_boxes = []
        self.command_vars = []
        self.command_vals = []
        self.command_types = []
        self.command_count = 0
        self.command_row = 0
        self.row_count = 2
        self.column_count = 0

        self.display_frame.pack()
        
    # Function to run the autoclicker instead of the macro
    def autoclick(self, delay_text_box, click_bool, key_text_box):
        
        try:
            delay = float(delay_text_box.get())
            if click_bool.get() == 0:
                button = Button.left
            else:
                button = Button.right

            if key_text_box.get() == '':
                key = KeyCode(char='z')
            else:
                if len(key_text_box.get()) == 1:
                    key = KeyCode(char=key_text_box.get())
                else:
                    key = KeyCode(char='z')


            self.master.after(100, self.click_thread.run)
            self.click_thread.delay = delay
            self.click_thread.button = button
            self.click_thread.key = key
            self.run_macro = False

        except:
            pass
        
    # Function to apply settings and turn the run_macro boolean true so that the macro will run instead of the autoclicker
    def apply_settings(self, key_text_box):
        try:
            if key_text_box.get() == '':
                    key = KeyCode(char='z')
            else:
                if len(key_text_box.get()) == 1:
                    key = KeyCode(char=key_text_box.get())
                else:
                    key = KeyCode(char='z')
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
            else:
                if key == self.click_thread.key:
                    self.click_thread.running = not self.click_thread.running
            
        except:
            try:
                if key == self.macro_thread.key:
                    self.macro_thread.running = not self.macro_thread.running
            except:
                pass
            
    # Function that adds the command section and buttons to add inputs   
    def add_command(self):
        if self.command_count == 0:
            self.command_count += 1
            self.row_count += 1
        
            remove_command_button = tk.Button(self.display_frame, text="Remove Command", command=lambda: self.remove_command(remove_command_button))
            remove_command_button.grid(row=self.row_count, column=1, sticky='ew', pady=5)

            consolidate_button = tk.Button(self.display_frame, text='Confirm Before Running Command', command=lambda: self.consolidate())
            consolidate_button.grid(row=self.row_count, column=2, sticky='ew')

            self.row_count += 1

            add_delay_button = tk.Button(self.display_frame, text="Add Delay", command=lambda: self.add_delay_text_box(add_delay_button))
            add_delay_button.grid(row=self.row_count, column=2, sticky='ew', pady=10)

            self.row_count += 1

            add_key_button = tk.Button(self.display_frame, text="Add Keyboard Input", command=lambda: self.add_key_text_box(add_delay_button))
            add_key_button.grid(row=self.row_count, column=2, sticky='ew', pady=10)

            self.row_count += 1

            add_mouse_button = tk.Button(self.display_frame, text="Add Mouse Input", command=lambda: self.add_mouse_text_box(add_delay_button))
            add_mouse_button.grid(row=self.row_count, column=2, sticky='ew', pady=10)

            self.command_boxes.append([remove_command_button, add_delay_button, add_key_button, add_mouse_button, consolidate_button])
            
            self.display_frame.pack()
        

    # Function to destroy a the entire command section
    def remove_command(self, remove_button):
        for command_section in self.command_boxes:
            if command_section[0] == remove_button:
                self.row_count -= 4
                if self.command_count > 0:
                    self.command_count -= 1
                for element in command_section:
                    element.destroy()
                self.command_boxes.remove(command_section)
                self.command_row = 0
                self.command_types.clear()
                self.command_vars.clear()
                self.command_vals.clear()
                break
            
    # Function to add a text box for a delay to be entered
    def add_delay_text_box(self, add_delay_button):
        if self.command_row == 0:
            self.command_row = add_delay_button.grid_info()['row']
        
        for command_section in self.command_boxes:
            if command_section[1] == add_delay_button:
                delay_text_box = tk.Entry(self.display_frame)
                delay_text_box.grid(row=self.command_row, column=0, sticky='ew', pady=5)
                delay_text_box.insert(0, "Delay in seconds")

                command_section.append(delay_text_box)
                self.command_types.append('delay')
                self.command_vars.append(delay_text_box)
                self.command_row += 1
                break
        self.display_frame.pack()

    # Function that adds a key input section
    def add_key_text_box(self, key_button):
        if self.command_row == 0:
            self.command_row = key_button.grid_info()['row']
        
        press_var = tk.IntVar()
        release_var = tk.IntVar()
        click_var = tk.IntVar()


        for command_section in self.command_boxes:
            if command_section[1] == key_button:
                key_text_box = tk.Entry(self.display_frame)
                key_text_box.grid(row=self.command_row, column=0, sticky='ew', pady=5)
                key_text_box.insert(0, "Keyboard key")

                key_press = tk.Checkbutton(self.display_frame, text="Press", variable=press_var)
                key_press.grid(row=self.command_row, column=1, sticky='w')

                self.command_row += 1

                key_release = tk.Checkbutton(self.display_frame, text="Release", variable=release_var)
                key_release.grid(row=self.command_row, column=1, sticky='w')

                self.command_row += 1

                key_click = tk.Checkbutton(self.display_frame, text="Click", variable=click_var)
                key_click.grid(row=self.command_row, column=1, sticky='w')
                self.command_row += 1

                command_section.append(key_text_box)
                command_section.append(key_press)
                command_section.append(key_release)
                command_section.append(key_click)
                self.command_types.append('key_text')
                self.command_types.append('key_press')
                self.command_types.append('key_release')
                self.command_types.append('key_click')
                self.command_vars.append(key_text_box)
                self.command_vars.append(press_var)
                self.command_vars.append(release_var)
                self.command_vars.append(click_var)
                break
        self.display_frame.pack()

    # Function that adds a mouse input section
    def add_mouse_text_box(self, mouse_button):
        if self.command_row == 0:
            self.command_row = mouse_button.grid_info()['row']
        
        press_var = tk.IntVar()
        release_var = tk.IntVar()
        click_var = tk.IntVar()
        button_var = tk.IntVar()


        for command_section in self.command_boxes:
            if command_section[1] == mouse_button:
                mouse_button = tk.Checkbutton(self.display_frame, text="Right mouse button", variable=button_var)
                mouse_button.grid(row=self.command_row, column=0)
                
                mouse_press = tk.Checkbutton(self.display_frame, text="Press", variable=press_var)
                mouse_press.grid(row=self.command_row, column=1, sticky='w')

                self.command_row += 1

                mouse_text_box = tk.Entry(self.display_frame)
                mouse_text_box.insert(0, "Type one: Right(pixels), Left(pixels), Up(pixels), Down(pixels), To(X_pixels, Y_pixels)")
                mouse_text_box.grid(row=self.command_row, column=0)
                

                mouse_release = tk.Checkbutton(self.display_frame, text="Release", variable=release_var)
                mouse_release.grid(row=self.command_row, column=1, sticky='w')

                self.command_row += 1

                mouse_click = tk.Checkbutton(self.display_frame, text="Click", variable=click_var)
                mouse_click.grid(row=self.command_row, column=1, sticky='w')
                self.command_row += 1


                command_section.append(mouse_button)
                command_section.append(mouse_press)
                command_section.append(mouse_text_box)
                command_section.append(mouse_release)
                command_section.append(mouse_click)
                self.command_types.append('mouse_button')
                self.command_types.append('mouse_press')
                self.command_types.append('mouse_text')
                self.command_types.append('mouse_release')
                self.command_types.append('mouse_click')
                self.command_vars.append(button_var)
                self.command_vars.append(press_var)
                self.command_vars.append(mouse_text_box)
                self.command_vars.append(release_var)
                self.command_vars.append(click_var)
                break
        self.display_frame.pack()

    # Function to get rid of the input gui but save the values
    def consolidate(self):
        self.command_boxes[0].reverse()
        self.command_types.reverse()
        self.command_vals.reverse()
        self.command_vars.reverse()
        i = 0
        for element in range(len(self.command_boxes[0])):
            if self.command_boxes[0][0] != self.command_boxes[0][-5]:
                command_val = str(self.command_vars[i].get())
                self.command_vals.insert(i, command_val)

                self.command_boxes[0][0].destroy()
                self.command_boxes[0].remove(self.command_boxes[0][0])
                i += 1
            else:
                break
            
        self.command_boxes[0].reverse()
        self.command_vals.reverse()
        self.command_vars.reverse()
        self.command_types.reverse()

        self.command_count = 0
        self.command_row = 0

    # Function to save the current values of the inputs for the current macro
    def save_macro(self, name_of_file):
        try:
            if not os.path.exists(name_of_file + '.csv'):
                with open((name_of_file + '.csv'), 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.command_types)
                    writer.writerow(self.command_vals)
            else:
                with open((name_of_file + '.csv'), 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.command_types)
                    writer.writerow(self.command_vals)
            messagebox.showinfo("Saved", "Macro Saved!")
        except:
            messagebox.showwarning("Not Saved", "Make sure to type a name for the file!")

    # Function to load previously saved macros
    def load_macro(self, name_of_file):
        try:
            with open((name_of_file + '.csv'), 'r') as f:
                reader = csv.reader(f)
                row_list = list(reader)

                self.command_types = row_list[0]
                self.command_vals = row_list[1]
            print(self.command_types)
            print(self.command_vals)
            messagebox.showinfo("Loaded", "Macro Loaded!")

        except:
            messagebox.showwarning("Not Loaded", "Make sure to file exists!")

    # Function to display a help message box
    def help(self):
        messagebox.showinfo("Help", """How to use: \n
        1. You can just run the autoclicker by entering a delay between clicks and pressing the Autoclick button then the key to start and stop the autoclicker is defaulted to z. You can specify a different key to start and stop it if you want.
        2. When you add a command to be able to run it by pressing your specified key. You must click Confirm Before Running Command and then click Apply Macro Settings. Then the macro will be able to be activated by your specified key.
        3. When you hit Confirm Before Running Command it will make the commands you entered disappear don't worry the commands are stored within the program until you exit out. If you wish to save your macro type in a name without special characters and hit Save Macro. Macros can be loaded as long as you know know the name of the file which you saved before.
        4. When adding a delay, key input, or mouse input after you've already confirmed the commands it will be added to the end of your macro this works with loaded macros as well.
        5. Clicking on Remove Command will get rid of your current entered macro or loaded macro.
        6. My recommendation is if your are creating a large macro to save after every few inputs you add.
        7. If you have a really large macro running and you press the start/stop key the macro will stop after it has completely run through.
        8. If your macro isn't working the way you want make sure to add delays in between key and mouse inputs.
        9. Seriously even a short delay in between inputs could fix your macro. The Delays are in seconds and you can do decimals for the delays too so 0.001, 0.5, 1.25, etc.
        10. Enjoy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        https://github.com/PurifiedBananaWater/Macro-Click""")

# Function to make sure the entire program is exited on close
def quit_after_window_closed():
    quit()


window = tk.Tk()
window.protocol("WM_DELETE_WINDOW", quit_after_window_closed)
program = MacroClickGUI(window)
with Listener(on_press=program.on_press) as listener:
    window.mainloop()
    listener.join()