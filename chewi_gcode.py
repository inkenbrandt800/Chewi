import datetime
import os
path = "/Users/inken/Documents/CHewi/G-Code/"  # Added trailing slash for safety
### Configuration  #############################
###USER INPUT HERE #############################
# either type speeds in manually in list form:
# else set speed list to None to use min, max, increment form:
speed_list = [0.05] # speed_list = [1,2, ...]
if not speed_list:
    speed_min = 50 # in mm/s
    speed_max = 80 # in mm/s
    speed_increment = 1 # in mm/s
else:
    speed_min = min(speed_list)
    speed_max = max(speed_list)
reps_per_speed = 1
min_height =  20  # in mm
max_height =  30  # in mm

# Dwell times in seconds
dwell_time_bottom = 1 # seconds at bottom position
dwell_time_top = 1     # seconds at top position

###### PRINTER SPECIFIC ##############################

fast_speed = 10 * 60 

start_code = f"""; SETUP
G90 ; use absolute coordinates
M220 S100 ; reset speed factor 100%
M104 S0 ; hotend off
M140 S0 ; bed off

; Home und Platz schaffen
G28 ; home all axis
G0 Z65 F{fast_speed} ; Fahre SCHNELL auf Startposition hoch
G4 S30 ; Warte 10 Sekunden vor Beginn des Loops
G0 Z{max_height} F{fast_speed} 

; ----------------------------------------------------
"""
end_code = """\n; END
G0 Z100 ; move z out of way
M220 S100 ; reset speed factor to 100%
M221 S100 ; reset extrusion rate to 100%

; Shut down printer
M106 S0 ; turn-off fan
M104 S0 ; turn-off hotend
M140 S0 ; turn-off bed
M150 P0 ; turn off led
M85 S0 ; deactivate idle timeout
M84 ; disable motors"""
export_time = datetime.datetime.now()
filename = f"chewi_{speed_min}to{speed_max}mms_{reps_per_speed}x_{export_time.strftime('%Y%m%d_%Hh%Mm')}.gcode"
if not os.path.exists(path):
    os.makedirs(path)
with open(path + filename, "w") as gcode_file:
    gcode_file.write(start_code)
    if speed_list:
        for speed in speed_list:
            gcode_file.write(f"\n; Speed: {speed} mm/s\n")
            lines_for_speed = (
                f"G0 Z{max_height} F{speed*60} ; raising\n"
                f"G4 P{dwell_time_top*1000} ; wait {dwell_time_top}s at top\n"
                f"G0 Z{min_height} F{speed*60} ; lowering\n"
                f"G4 P{dwell_time_bottom*1000} ; wait {dwell_time_bottom}s at bottom\n"
            ) * reps_per_speed
            gcode_file.write(lines_for_speed)
    else:
        for speed in range(speed_min, speed_max + 1, speed_increment):
            gcode_file.write(f"\n; Speed: {speed} mm/s\n")
            lines_for_speed = (
                f"G0 Z{min_height} F{speed*60} ; lowering\n"
               f"G4 S{dwell_time_bottom*1000} ; wait {dwell_time_bottom}s at bottom\n"
                f"G0 Z{max_height} F{speed*60} ; raising\n"
                f"G4 S{dwell_time_top*1000} ; wait {dwell_time_top}s at top\n"
            ) * reps_per_speed
            gcode_file.write(lines_for_speed)
    gcode_file.write(end_code)
print("Done!")