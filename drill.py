import tkinter as tk
from tkinter import messagebox
import time
import os
import keyboard  # Install with: pip install keyboard
import threading  # For non-blocking sound playback
import winsound  # For simple WAV playback on Windows (no external dependency for basic sound)

# --- Configuration ---
DRILL_DURATION_SECONDS = 15 * 60  # 15 minutes
DRILL_ACTIVE = True
SOUND_PLAYING = False
FIRE_ALARM_SOUND_FILE = "fire_alarm.wav"  # Replace with your fire alarm sound file (WAV recommended for winsound)
DRILL_OVER_MESSAGE_DURATION_MS = 5000  # 5 seconds for "Drill Over" message

# --- Functions ---

def play_fire_alarm_sound():
    """Plays the fire alarm sound in a loop in a separate thread."""
    global SOUND_PLAYING
    try:
        winsound.PlaySound(FIRE_ALARM_SOUND_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        SOUND_PLAYING = True
    except Exception as e:
        messagebox.showerror("Error Playing Sound", f"Could not play fire alarm sound file '{FIRE_ALARM_SOUND_FILE}'. Please ensure it exists in the same directory and is a valid WAV file. Error: {e}")
        SOUND_PLAYING = False

def stop_fire_alarm_sound():
    """Stops the fire alarm sound."""
    global SOUND_PLAYING
    winsound.PlaySound(None, winsound.SND_ASYNC)  # Stop any currently playing sound
    SOUND_PLAYING = False

def end_fire_drill():
    """Ends the fire drill, stops sound, shows 'Drill Over' message, and closes."""
    global DRILL_ACTIVE
    if DRILL_ACTIVE: # Check again in case safety exit was already triggered
        DRILL_ACTIVE = False
        stop_fire_alarm_sound()
        drill_text.config(text="FIRE DRILL OVER.\n\nYou may now return to your work area.", font=("Arial", 30)) # Smaller font for end message
        root.after(DRILL_OVER_MESSAGE_DURATION_MS, root.destroy) # Close window after message display

def safety_exit_program(e=None): # e=None to allow keyboard listener or menu trigger
    """Immediately exits the program when safety key '=' is pressed or via menu."""
    global DRILL_ACTIVE
    if DRILL_ACTIVE:
        DRILL_ACTIVE = False
        stop_fire_alarm_sound()
        drill_text.config(text="FIRE DRILL CANCELED (Safety Exit)", font=("Arial", 24), fg="yellow") # Indicate safety exit
        root.after(DRILL_OVER_MESSAGE_DURATION_MS, root.destroy) # Close window after message display

def update_timer():
    """Updates the timer and checks if drill duration is over."""
    global DRILL_ACTIVE
    if DRILL_ACTIVE:
        elapsed_time = time.time() - start_time
        if elapsed_time >= DRILL_DURATION_SECONDS:
            end_fire_drill()
        else:
            remaining_seconds = int(DRILL_DURATION_SECONDS - elapsed_time)
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            timer_text.config(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")
            root.after(1000, update_timer) # Check again after 1 second

# --- Tkinter Setup ---
root = tk.Tk()
root.title("Fire Drill Program") # Set a title (will be hidden in fullscreen but good for development)
root.attributes('-fullscreen', True) # Go fullscreen
root.overrideredirect(True) # Remove window decorations (title bar, borders)
root.configure(bg='red') # Red background

# --- UI Elements ---
drill_text = tk.Label(root,
                      text="FIRE DRILL\n\nTHIS IS A FIRE DRILL. YOU MUST EVACUATE FOR 15 MINUTES.\n\nTHIS WINDOW CANNOT BE CLOSED UNTIL THE DRILL IS OVER.",
                      fg="white",
                      bg="red",
                      font=("Arial", 48, "bold"),
                      wraplength=root.winfo_screenwidth() * 0.9) # Wrap text to 90% of screen width
drill_text.pack(pady=50) # Add some vertical padding

timer_text = tk.Label(root,
                      text="", # Timer will be updated here
                      fg="white",
                      bg="red",
                      font=("Arial", 24, "bold"))
timer_text.pack(pady=20)

# --- Safety Exit Binding ---
root.bind('=', safety_exit_program) # Bind '=' key to safety exit
root.bind('<Escape>', safety_exit_program) # Bind Escape key as well for easy exit during testing

# --- Start Drill ---
start_time = time.time()

# Start sound in a separate thread to prevent blocking the GUI
sound_thread = threading.Thread(target=play_fire_alarm_sound)
sound_thread.daemon = True  # Allow the main thread to exit even if sound thread is running
sound_thread.start()

update_timer() # Start the timer loop

# --- Menu (Optional - for debugging/alternative exit) ---
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Safety Exit", command=safety_exit_program)
filemenu.add_separator()
filemenu.add_command(label="Exit Program", command=root.destroy) # Regular exit
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar) # Attach menu to the root window

# --- Start Tkinter Main Loop ---
root.mainloop()