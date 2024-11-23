import serial
import serial.tools.list_ports
from PIL import ImageGrab, Image, ImageDraw
import pystray
from pystray import MenuItem as item
import time
import threading
import ctypes
import sys

running = True
brightness = 16

def find_arduino_leonardo():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino Leonardo" in port.description:
            return port.device
    return None

def capture_crop_resize_screenshot(new_width, crop_height=40):
    # Capture the entire screen (all monitors)
    screenshot = ImageGrab.grab(all_screens=True)
    current_width, current_height = screenshot.size
    # Crop the image to only the bottom 40 pixels
    cropped_screenshot = screenshot.crop((0, current_height - crop_height, current_width, current_height))
    # Resize the cropped image to 144x1 pixels
    resized_screenshot = cropped_screenshot.resize((new_width, 1), Image.ANTIALIAS)
    # Get the RGB values of the resized image
    bottom_line = [resized_screenshot.getpixel((x, 0)) for x in range(new_width)]
    bottom_line = [(min(r, 254), min(g, 254), min(b, 254)) for (r, g, b) in bottom_line]
    return bottom_line

def send_rgb_values(port_name, rgb_values):
    # Check if the pixel array has enough data (144 pixels * 3 values = 432 values)
    if len(rgb_values) != 144:
        return
    
    try:
        with serial.Serial(port_name, 9600, timeout=1) as ser:
            # Send reset signal as a special sequence of bytes
            reset_signal = bytearray([255, 255, 255])
            ser.write(reset_signal)
            ser.write(bytearray([brightness]))

            for r, g, b in rgb_values:
                data = bytearray([r, g, b])
                ser.write(data)
            
            # Send an extra value to ensure data alignment
            ser.write(bytearray([0, 0, 0]))

    except serial.SerialException as e:
        pass

def main_program(port_name):
    global running
    while running:
        # Capture, crop, and resize the screenshot
        bottom_line_rgb_values = capture_crop_resize_screenshot(144)

        # Send the RGB values of the bottom line to the Arduino
        send_rgb_values(port_name, bottom_line_rgb_values)

def create_image():
    # Create an image for the system tray icon
    image = Image.new('RGB', (64, 64), color='white')
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill='black')
    return image

def on_exit(icon, item):
    global running
    running = False
    icon.stop()

def minimize_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

if __name__ == "__main__":
    minimize_console()
    
    port_name = find_arduino_leonardo()
    if port_name:
        # Create a thread to run the main program
        thread = threading.Thread(target=main_program, args=(port_name,))
        thread.start()

        # Create and start the system tray icon
        icon = pystray.Icon("RGB LED Controller")
        icon.icon = create_image()
        icon.menu = pystray.Menu(item('Exit', on_exit))
        icon.run()
        
        # Wait for the main thread to finish
        thread.join()
    else:
        print("Arduino Leonardo not found")
