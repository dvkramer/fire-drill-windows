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
FLASH_INTERVAL_MS = 30
GRADIENT_STEPS = 20
GRADIENT_DIRECTION = 1
CURRENT_GRADIENT_STEP = 0


def set_volume_to_100():
    if VOLUME_CONTROL_ENABLED:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)

            if volume.GetMute():
                volume.SetMute(0, None)
                print("Unmuted system volume.")

            volume.SetMasterVolumeLevelScalar(1.0, None)
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
    global DRILL_ACTIVE, CURRENT_GRADIENT_STEP
    if DRILL_ACTIVE:
        DRILL_ACTIVE = False
        stop_fire_alarm_sound()
        root.after_cancel(flash_schedule_id)
        root.configure(bg='SystemButtonFace')
        drill_text.config(text="FIRE DRILL OVER.\n\nYou may now return to your work area.", fg="black", bg='SystemButtonFace', font=drill_font)
        timer_text.config(bg='SystemButtonFace', fg='black', font=timer_font)
        CURRENT_GRADIENT_STEP = 0
        filemenu.entryconfig("Exit Program", state=tk.NORMAL)
        root.after(DRILL_OVER_MESSAGE_DURATION_MS, root.destroy)


def safety_exit_program(e=None):
    global DRILL_ACTIVE, CURRENT_GRADIENT_STEP
    if DRILL_ACTIVE:
        DRILL_ACTIVE = False
        stop_fire_alarm_sound()
        root.after_cancel(flash_schedule_id)
        root.configure(bg='SystemButtonFace')
        drill_text.config(text="FIRE DRILL CANCELED (Safety Exit)", font=drill_font, fg="yellow", bg='SystemButtonFace')
        timer_text.config(bg='SystemButtonFace', fg='black', font=timer_font)
        CURRENT_GRADIENT_STEP = 0
        filemenu.entryconfig("Exit Program", state=tk.NORMAL)
        root.after(DRILL_OVER_MESSAGE_DURATION_MS, root.destroy)


def update_timer():
    global DRILL_ACTIVE
    if DRILL_ACTIVE:
        set_volume_to_100()
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


def get_gradient_color(step):
    r_start, g_start, b_start = 255, 0, 0
    r_end, g_end, b_end = 255, 255, 255

    progress = step / float(GRADIENT_STEPS)

    r = int(r_start + (r_end - r_start) * progress)
    g = int(g_start + (g_end - g_start) * progress)
    b = int(b_start + (b_end - b_start) * progress)

    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def gradient_flash_screen():
    global CURRENT_GRADIENT_STEP, GRADIENT_DIRECTION, flash_schedule_id

    if DRILL_ACTIVE:
        current_color = get_gradient_color(CURRENT_GRADIENT_STEP)
        opposite_color_step = GRADIENT_STEPS - CURRENT_GRADIENT_STEP
        opposite_color = get_gradient_color(opposite_color_step)

        root.configure(bg=current_color)
        drill_text.config(fg=opposite_color, bg=current_color)
        timer_text.config(fg=opposite_color, bg=current_color)


        CURRENT_GRADIENT_STEP += GRADIENT_DIRECTION

        if CURRENT_GRADIENT_STEP > GRADIENT_STEPS:
            GRADIENT_DIRECTION = -1
            CURRENT_GRADIENT_STEP = GRADIENT_STEPS
        elif CURRENT_GRADIENT_STEP < 0:
            GRADIENT_DIRECTION = 1
            CURRENT_GRADIENT_STEP = 0

        flash_schedule_id = root.after(FLASH_INTERVAL_MS, gradient_flash_screen)


root = tk.Tk()
root.title("Fire Drill Program")
root.attributes('-fullscreen', True)
root.overrideredirect(True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


drill_font_size = int(screen_width / 35)
timer_font_size = int(screen_width / 55)
drill_font = ("Arial", drill_font_size, "bold")
timer_font = ("Arial", timer_font_size, "bold")


root.configure(bg='red')
disable_close_button()


drill_text = tk.Label(root,
                      text="FIRE DRILL\n\nTHIS IS A FIRE DRILL. YOU MUST EVACUATE FOR 15 MINUTES.\n\nTHIS WINDOW CANNOT BE CLOSED UNTIL THE DRILL IS OVER.\n\nDO NOT ATTEMPT TO TURN OFF YOUR SPEAKERS.",
                      fg="white",
                      bg="red",
                      font=drill_font,
                      wraplength=screen_width * 0.9)

timer_text = tk.Label(root,
                      text="",
                      fg="white",
                      bg="red",
                      font=timer_font)


# Move drill_text slightly higher - ADJUST rely VALUE
drill_text.place(relx=0.5, rely=0.45, anchor=tk.CENTER) # Changed rely from 0.5 to 0.45

timer_text.place(relx=0.5, rely=0.9, anchor=tk.CENTER)


root.bind('=', safety_exit_program)
root.bind('<Escape>', safety_exit_program)


start_time = time.time()


sound_thread = threading.Thread(target=play_fire_alarm_sound)
sound_thread.daemon = True
sound_thread.start()

update_timer()

flash_schedule_id = root.after(FLASH_INTERVAL_MS, gradient_flash_screen)


menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Safety Exit", command=safety_exit_program)
filemenu.add_command(label="Exit Program", command=root.destroy)
filemenu.entryconfig("Exit Program", state=tk.DISABLED)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)


root.mainloop()