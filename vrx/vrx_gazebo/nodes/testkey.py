from pynput import keyboard
import time

global_key = ''

key_w = False
key_s = False
key_d = False
key_a = False

def on_press(key):
    global global_key
    global key_w
    global key_s
    global key_d
    global key_a
    
    if key == keyboard.Key.up:    key_w = True
    if key == keyboard.Key.down:  key_s = True    
    if key == keyboard.Key.left:  key_a = True    
    if key == keyboard.Key.right: key_d = True   
    try:
        global_key = key.char
     
    except AttributeError:
        #print('special key {0} pressed'.format(key))
        return

def on_release(key):
    global global_key
    global key_w
    global key_s
    global key_d
    global key_a
    
    global_key = ''
    if key == keyboard.Key.up:    key_w = False
    if key == keyboard.Key.down:  key_s = False    
    if key == keyboard.Key.left:  key_a = False    
    if key == keyboard.Key.right: key_d = False       
    if key == keyboard.Key.esc:
        # Stop listener
        return False
        

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()


if __name__ == "__main__":
    global_key
    print("Starting")
    val = True
    print(val)
    print(int(val))
    while(True):
        time.sleep(0.1)
        #print("KEY = " + str(global_key))
        print(str(key_w) + "  " + str(key_s) + "  " + str(key_d) + "  "  + str(key_a))
        
