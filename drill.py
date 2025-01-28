import tkinter as tk
from tkinter import messagebox
import time
import os
import keyboard
import threading
import winsound
import comtypes

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    VOLUME_CONTROL_ENABLED = True
except ImportError:
    VOLUME_CONTROL_ENABLED = False
    print("Warning: pycaw library not found. Volume control will be disabled. Install it with: pip install pycaw")


DRILL_DURATION_SECONDS = 15 * 60
DRILL_ACTIVE = True
SOUND_PLAYING = False
FIRE_ALARM_SOUND_FILE = "fire_alarm.wav"
DRILL_OVER_MESSAGE_DURATION_MS = 5000


def set_volume_to_100():
    if VOLUME_CONTROL_ENABLED:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)

            if volume.GetMute():  # Check if muted
                volume.SetMute(0, None)  # Unmute (0 for False, 1 for True in SetMute)
                print("Unmuted system volume.") # Optional feedback

            volume.SetMasterVolumeLevelScalar(1.0, None)  # 1.0 is 100% volume
        except Exception as e:
            print(f"Error setting volume or unmuting: {e}")


def play_fire_alarm_sound():
    global SOUND_PLAYING
    try:
        winsound.PlaySound(FIRE_ALARM_SOUND_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        SOUND_PLAYING = True
    except Exception as e:
        messagebox.showerror("Error Playing Sound", f"Could not play fire alarm sound file '{FIRE_ALARM_SOUND_FILE}'. Please ensure it exists in the same directory and is a valid WAV file. Error: {e}")
        SOUND_PLAYING = False


def stop_fire_alarm_sound():
    global SOUND_PLAYING
    winsound.PlaySound(None, winsound.SND_ASYNC)
    SOUND_PLAYING = False


def end_fire_drill():
    global DRILL_ACTIVE
    if DRILL_ACTIVE:
        DRILL_ACTIVE = False
        stop_fire_alarm_sound()
        drill_text.config(text="FIRE DRILL OVER.\n\nYou may now return to your work area.", font=("Arial", 30))
        filemenu.entryconfig("Exit Program", state=tk.NORMAL)
        root.after(DRILL_OVER_MESSAGE_DURATION_MS, root.destroy)


def safety_exit_program(e=None):
    global DRILL_ACTIVE
    if DRILL_ACTIVE:
        DRILL_ACTIVE = False
        stop_fire_alarm_sound()
        drill_text.config(text="FIRE DRILL CANCELED (Safety Exit)", font=("Arial", 24), fg="yellow")
        filemenu.entryconfig("Exit Program", state=tk.NORMAL)
        root.after(DRILL_OVER_MESSAGE_DURATION_MS, root.destroy)


def update_timer():
    global DRILL_ACTIVE
    if DRILL_ACTIVE:
        set_volume_to_100()  # Set volume and unmute at each timer update
        elapsed_time = time.time() - start_time
        if elapsed_time >= DRILL_DURATION_SECONDS:
            end_fire_drill()
        else:
            remaining_seconds = int(DRILL_DURATION_SECONDS - elapsed_time)
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            timer_text.config(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")
            root.after(1000, update_timer)


def disable_close_button():
    root.protocol("WM_DELETE_WINDOW", safety_exit_program)


root = tk.Tk()
root.title("Fire Drill Program")
root.attributes('-fullscreen', True)
root.overrideredirect(True)
root.configure(bg='red')
disable_close_button()


drill_text = tk.Label(root,
                      text="FIRE DRILL\n\nTHIS IS A FIRE DRILL. YOU MUST EVACUATE FOR 15 MINUTES.\n\nTHIS WINDOW CANNOT BE CLOSED UNTIL THE DRILL IS OVER.\n\nDO NOT ATTEMPT TO TURN OFF YOUR SPEAKERS.",
                      fg="white",
                      bg="red",
                      font=("Arial", 48, "bold"),
                      wraplength=root.winfo_screenwidth() * 0.9)
drill_text.pack(pady=50)


timer_text = tk.Label(root,
                      text="",
                      fg="white",
                      bg="red",
                      font=("Arial", 24, "bold"))
timer_text.pack(pady=20)


root.bind('=', safety_exit_program)
root.bind('<Escape>', safety_exit_program)


start_time = time.time()


sound_thread = threading.Thread(target=play_fire_alarm_sound)
sound_thread.daemon = True
sound_thread.start()

update_timer()


menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Safety Exit", command=safety_exit_program)
filemenu.add_command(label="Exit Program", command=root.destroy)
filemenu.entryconfig("Exit Program", state=tk.DISABLED)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)


root.mainloop()