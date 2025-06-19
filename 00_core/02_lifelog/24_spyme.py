from pynput import mouse, keyboard
import time
import os

clicks = []
key_presses = []
running = True  # Add a flag to control the program

def on_click(x, y, button, pressed):
    if pressed:
        timestamp = time.time()
        clicks.append((timestamp, x, y))
        print(f"Click recorded at X: {x}, Y: {y}")

def on_press(key):
    global running
    timestamp = time.time()
    
    if key == keyboard.Key.esc:
        running = False  # Set flag to stop the program
        mouse_listener.stop()
        keyboard_listener.stop()
        return
        
    try:
        key_presses.append((timestamp, key.char))
        print(f"Key {key.char} pressed")
    except AttributeError:
        key_presses.append((timestamp, str(key)))
        print(f"Special key {key} pressed")

# Start mouse and keyboard listeners
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

print("Recording... Press ESC to exit.")

# Wait until ESC is pressed
while running:
    time.sleep(0.1)

# Output recorded clicks and key presses
print("\nRecorded Clicks:")
for c in clicks:
    print(f"Click, {c[1]}, {c[2]}")

print("\nRecorded Key Presses:")
for k in key_presses:
    print(f"Key Press: {k[1]}")

# Save clicks and key presses to a file after recording
output_file = os.path.join(os.getcwd(), 'clicks_output.ahk')

with open(output_file, 'w') as f:
    for c in clicks:
        f.write(f"Click, {c[1]}, {c[2]}\nSleep, 300\n")
    for k in key_presses:
        f.write(f"Send, {k[1]}\nSleep, 100\n")

print(f"Saved to {output_file}")