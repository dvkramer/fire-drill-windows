# Fire Drill for Windows - A Home Fire Safety Tool

## Overview
Fire Drill is a desktop application for Windows designed to enhance fire safety preparedness by simulating surprise fire drills. While still in development, the program aims to help users practice their home fire escape plans in a realistic and engaging way.

## Current Features
- **Drill Simulation (`drill.py`)**: Handles the core functionality of the fire drill, including:
  - Fullscreen flashing red screen.
  - Loud fire alarm sound to mimic a real emergency.
- **Scheduler (`scheduler.py`)**: Manages the automatic scheduling of fire drills.
  - Adds itself to the system startup.
  - Uses a mean time to happen (MTTH) of 1 month to randomly determine when drills will occur.

## Usage
1. Download and unzip the release
2. Place the fire drill folder wherever you want i.e. inside your documents folder. There is no installer.
3. Run scheduler.exe
4. Everything should be set up! To verify, you can check the startup tab in your task manager. The scheduler should add itself to this list, so the software can persist between reboots and deliver random, realistic fire drills.

## Why Fire Drill?
Practicing fire escape plans can be a lifesaver in emergencies. Fire Drill encourages users to prepare effectively by simulating the stress and urgency of a real fire scenario.

## Contribute
This project is a work in progress, and contributions are welcome! If you'd like to help with the scheduler or other features, please submit an issue or pull request.

## Stay Safe
The goal of Fire Drill is to help you be better prepared for emergencies. Even though the app is still in development, practicing early could make all the difference when seconds count.

---
### License
This project is licensed under the [Apache-2.0 License](LICENSE).
