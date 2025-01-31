import time
import random
import math
import os
import subprocess  # For launching the UI
import sys         # For command line arguments
import winshell     # For creating shortcuts (you might need to install: pip install winshell)

MTTH_MONTHS = 1  # Mean Time To Happen in months (adjust for testing)
# MTTH_MONTHS = 1/ (60 * 24 * 30) # Approximately every minute
SECONDS_IN_MONTH = 30 * 24 * 60 * 60 # Approximation for MTTH calculation
DRILL_UI_EXECUTABLE = "drill.exe" #  <--- UPDATED to "drill.exe"
SCRIPT_NAME = os.path.basename(sys.argv[0]) # Get script's filename
SCRIPT_PATH = os.path.abspath(sys.argv[0])   # Get script's full path
STARTUP_FOLDER = os.path.join(os.path.expandvars("%APPDATA%"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
SHORTCUT_NAME = "FireDrillScheduler.lnk" # Name for the shortcut in startup
SHORTCUT_PATH = os.path.join(STARTUP_FOLDER, SHORTCUT_NAME)

MIN_DELAY_SECONDS = 15 * 60  # 15 minutes
MAX_DELAY_SECONDS = 3 * SECONDS_IN_MONTH  # 3 months

def getRandomInterval():
    """Calculates a random interval in seconds based on MTTH."""
    lambda_val = 1 / (MTTH_MONTHS * SECONDS_IN_MONTH) # Lambda in events per second
    return -math.log(1 - random.random()) / lambda_val

def schedule_next_drill():
    """Schedules the next fire drill with sanity checks and returns the scheduled time."""
    while True: # Loop until a valid time is generated
        interval_seconds = getRandomInterval()
        next_drill_time_candidate = time.time() + interval_seconds

        min_time = time.time() + MIN_DELAY_SECONDS
        max_time = time.time() + MAX_DELAY_SECONDS

        if min_time <= next_drill_time_candidate <= max_time:
            next_drill_time = next_drill_time_candidate
            interval_days = interval_seconds / (24 * 3600)
            print(f"Next fire drill scheduled in approximately {interval_seconds:.0f} seconds ({interval_days:.2f} days).")
            return next_drill_time
        else:
            print(f"Generated interval ({interval_seconds:.0f} seconds, {interval_seconds / (24 * 3600):.2f} days) out of sanity bounds (min: {MIN_DELAY_SECONDS:.0f}s, max: {MAX_DELAY_SECONDS:.0f}s). Re-rolling...")

def trigger_fire_drill_ui():
    """Launches the Fire Drill UI executable."""
    print("Triggering fire drill UI...")
    try:
        os.startfile(DRILL_UI_EXECUTABLE) # Use os.startfile for simple launch, no console window
        # Alternatively, for more control (e.g., capturing output, waiting for exit):
        # subprocess.Popen([DRILL_UI_EXECUTABLE])
    except FileNotFoundError:
        print(f"Error: Fire drill UI executable '{DRILL_UI_EXECUTABLE}' not found. Make sure it's in the same directory as scheduler.exe.") # <-- Updated error message
    except Exception as e:
        print(f"Error launching UI: {e}")

def main_loop():
    """Main loop of the background scheduler."""
    next_drill_time = schedule_next_drill() # Initial schedule

    while True:
        current_time = time.time()
        if current_time >= next_drill_time:
            trigger_fire_drill_ui()
            next_drill_time = schedule_next_drill() # Schedule the *next* drill *after* triggering this one
        else:
            time_to_sleep = max(1, next_drill_time - current_time) # Ensure sleep is at least 1 second
            time.sleep(time_to_sleep) # Wait until next check or drill time

def add_to_startup():
    """Adds the script to the Windows Startup folder if it's not already there."""
    print("Checking startup...") # Indicate startup check
    try:
        if not os.path.exists(SHORTCUT_PATH): # Check if shortcut already exists
            print("Adding to startup...")
            with winshell.shortcut(SHORTCUT_PATH) as shortcut:
                shortcut.path = sys.executable  # Use the Python interpreter
                shortcut.description = "Fire Drill Scheduler"
                shortcut.arguments = SCRIPT_PATH # Run the script itself
                shortcut.working_directory = os.path.dirname(SCRIPT_PATH)
            print(f"Script added to startup. Shortcut created at: {SHORTCUT_PATH}")
        else:
            print("Already in startup.") # Indicate already in startup
    except Exception as e:
        print(f"Error adding to startup: {e}")

def remove_from_startup(): # Keep this function for potential later use if you want to remove it from startup
    """Removes the script from the Windows Startup folder."""
    try:
        if os.path.exists(SHORTCUT_PATH):
            os.remove(SHORTCUT_PATH)
            print(f"Script removed from startup. Shortcut deleted from: {SHORTCUT_PATH}")
        else:
            print("Script was not found in startup.")
    except Exception as e:
        print(f"Error removing from startup: {e}")

if __name__ == "__main__":
    add_to_startup() # <--- Automatically add to startup when script runs
    print("Fire Drill Scheduler started in background...") # Indicate background start
    main_loop()