import time
import random
import math
import os
import subprocess  # For launching the UI
import schedule     # (Optional, but could be useful for more complex scheduling later)

# MTTH_MONTHS = 1  # Mean Time To Happen in months (adjust for testing)
MTTH_MONTHS = 1/ (60 * 24 * 30) # Approximately every minute
SECONDS_IN_MONTH = 30 * 24 * 60 * 60 # Approximation for MTTH calculation
DRILL_UI_EXECUTABLE = "drill.exe" #  <--- UPDATED to "drill.exe"

def getRandomInterval():
    """Calculates a random interval in seconds based on MTTH."""
    lambda_val = 1 / (MTTH_MONTHS * SECONDS_IN_MONTH) # Lambda in events per second
    return -math.log(1 - random.random()) / lambda_val

def schedule_next_drill():
    """Schedules the next fire drill and returns the scheduled time."""
    interval_seconds = getRandomInterval()
    next_drill_time = time.time() + interval_seconds
    print(f"Next fire drill scheduled in approximately {interval_seconds:.0f} seconds ({interval_seconds/3600/24:.2f} days).") # More informative output
    return next_drill_time

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

if __name__ == "__main__":
    print("Fire Drill Scheduler started in background...") # Indicate background start
    main_loop()