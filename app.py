import re
import pathlib
import time
from typing import List

import pyautogui
import pytesseract
import unicodedata
from pytesseract import Output
from pynput import keyboard
from pynput import mouse


SCROLL_DISTANCE = -4
LINE_TOLERANCE = 5
EXISTING_FILE = "./lines.txt"
NEW_FILE = "./lines.txt"


def ocr_image(img):
    data = pytesseract.image_to_data(img, output_type=Output.DICT)
    return data


def on_press(key):
    if not key in [keyboard.Key.space]:
        print("try again")
    if key in [keyboard.Key.space]: 
        return False
        

def on_click(x, y, button, pressed):
    global pos1
    global pos2
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    if pressed:
        pos1 = mouse_controller.position
    if not pressed:
        pos2 = mouse_controller.position
        return False


def press_to_close(key):
    global break_program
    print (key)
    if key == keyboard.Key.esc and not break_program:
        print ('end pressed')
        break_program = True
        

def is_img_line(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError:
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    if re.match(r'^[A-Za-z0-9_-]+$', text):
        return True
    else:
        return False
    

def is_within_range(check, value, tolerance):
    high = value + tolerance
    low = value - tolerance
    if check <= high and check >= low:
        return True
    else:
        return False


def read_lines_from_file(f_name: str) -> List:
    f_path = pathlib.Path(f_name)
    lines = []
    if f_path.exists():
        with open(f_path, 'r') as f:
            lines = f.readlines()
    return lines
        
    
mouse_controller = mouse.Controller()
# For drag
#with mouse.Listener(on_click=on_click) as listener:
#    print('Click, drag and release from top left to bottom right rectangle of interest')    
#    listener.join()

with keyboard.Listener(on_press=on_press) as listener:
    print('position pointer 1 and hit space to proceed')
    listener.join()
    
with keyboard.Listener(on_press=on_press) as listener:
    pos1 = mouse_controller.position
    print('position pointer 2 and hit space to proceed')
    listener.join()

with keyboard.Listener(on_press=on_press) as listener:
    pos2 = mouse_controller.position
    print('position pointer on window to scroll')
    listener.join()

X = abs(pos2[0] - pos1[0])
Y = abs(pos2[1] - pos1[1])

break_program = False

print("Press 'ESC' key to stop the program.")

listener = keyboard.Listener(on_press=press_to_close)
listener.start()
lines = dict()
starttime=time.time()

num_lines = 0
count = 0
while not break_program:
    im = pyautogui.screenshot(region=(pos1[0],pos1[1], X, Y))
    mouse_controller.scroll(0, SCROLL_DISTANCE)
    data = ocr_image(im)
    screenshot_lines = dict()
    word_pos = 0
    line_num = 0
    prev_pos = 0
    for t in data.get('text'):
        if is_img_line(t) and len(t) >= 2:
            cur_pos = data.get('top')[word_pos]
            if not is_within_range(cur_pos, prev_pos, LINE_TOLERANCE):
                line_num+=1
            if not screenshot_lines.get(line_num):
                screenshot_lines[line_num] = dict()
            screenshot_lines[line_num][f'{t}'] = None
            prev_pos = cur_pos                
        word_pos+=1
    for l, n in screenshot_lines.items():
        s = " "
        img_line = "{n} \n".format(n=s.join(n.keys()))
        lines[img_line] = None
    
    if num_lines == 0:
        num_lines = len(lines.keys())
    elif len(lines.keys()) > num_lines:
        num_lines = len(lines.keys())
    else:
        print('left clicking...')
        mouse_controller.press(mouse.Button.left)
        mouse_controller.release(mouse.Button.left)
    
    print("lines collected({c}): {n}".format(c=count, n=len(lines.keys())), end="\r")
    time.sleep(0.1 - ((time.time() - starttime) % 0.1))
    time.sleep(1)
    count+=1
else:
    current_lines = read_lines_from_file(EXISTING_FILE)
    for n in lines:
        if not n in current_lines:
            with open(NEW_FILE, "a") as file1:
                file1.write(n)
    #with open(NEW_FILE, "w") as file1:
    #    file1.write("lines: \n")
    #    file1.writelines(lines)