#!/usr/bin/python

import cgi
import subprocess
import random
import os
import re

PI1 = 0
PI1_NAME = "Family Room"
PI2 = 1
PI2_NAME = "Kitchen"
host_p2 = str(os.environ.get('SERVER_NAME'))

if host_p2 == "192.168.1.171":
	host_p1 = "192.168.1.170"
else:
	host_p1 = host_p2 + ":8990"
	host_p2 = host_p2 + ":8991"

form = cgi.FieldStorage()
start_all = form.getvalue("start_all", "")
stop_all = form.getvalue("stop_all", "")
toggle_light = form.getvalue("toggle_light", "")


def get_process_status():
	status = subprocess.check_output("sudo -u nick /home/nick/software/security_camera_misc/check_running.sh", shell=True).strip();
	status = status.split()
	return status

def start_all_cameras():
	status = subprocess.check_output("sudo -u nick /home/nick/software/security_camera_misc/start_all.sh", shell=True).strip();

def stop_all_cameras():
	status = subprocess.check_output("sudo -u nick /home/nick/software/security_camera_misc/stop_all.sh", shell=True).strip();

def get_light_info():
	lights_str = subprocess.check_output("sudo -u nick /usr/bin/python /home/nick/software/hue_light_control/light_control.py list", shell=True).strip();

	lights = []
	for line in lights_str.split("\n"):
		line = line.split(":")
		lights.append(line)

	return lights

def toggle_light_state(info):
	vals = info.split(":")
	if vals[1] =="True":
		out = subprocess.check_output("sudo -u nick /usr/bin/python /home/nick/software/hue_light_control/light_control.py state " + vals[0] + " off", shell=True).strip();
	elif vals[1] =="False":
		out = subprocess.check_output("sudo -u nick /usr/bin/python /home/nick/software/hue_light_control/light_control.py state " + vals[0] + " on", shell=True).strip();


if toggle_light != "":
	toggle_light_state(toggle_light)

light_info = get_light_info()

if start_all == "TRUE":
	start_all_cameras()
elif stop_all == "TRUE":
	stop_all_cameras()

status = get_process_status()
status_pi1 = status[0]
status_pi2 = status[1]

print "Content-type: text/html\n"

print """
<html>
	<head>
		<title>Home Monitor Buddy</title>
"""
                
# Only auto refresh page if a camera is on.
if int(status_pi1) > 0 or int(status_pi2) > 0:
        print """<meta http-equiv="refresh" content="10">"""

print """
	</head>

	<body style="background-color: #334b70;">

	<div style="width: 100%; text-align: center">
"""

print """<div style="display: inline-block; width: 49%; font-style: Bookman; color: white; font-weight: bold;">"""
if status_pi1 == "0":
	print """<img src="/red_x.png" width="50"><br>""" + PI1_NAME
else:
	print """<img src="/green_check.png" width="50"><br>""" + PI1_NAME
print """
<br>
<a href="https://""" + host_p1 + """"><img src="/camimg/current_image_pi1.jpg?rnd=""" + str(random.randint(1,999999)) + """" style="width: 100%;"></a>
</div>
"""

print """<div style="display: inline-block; width: 49%; font-style: Bookman; color: white; font-weight: bold;">"""

if status_pi2 == "0":
        print """<img src="/red_x.png" width="50"><br>""" + PI2_NAME
else:
        print """<img src="/green_check.png" width="50"><br>""" + PI2_NAME
print """
	<br>
	<a href="https://""" + host_p2 + """"><img src="/camimg/current_image.jpg?rnd=""" + str(random.randint(1,999999)) + """" style="width: 100%;"></a>
	</div>

	<br>

	<form method="post" action="" style="display: inline-block;">
		<br>
                <input type="hidden" name="start_all" value="TRUE">
                <input type="submit" value="Start" style="color: white; background-color: #27c453; border-color: #27c453; font-size: 1.5em; font-weight: bold;">
        </form>

	<img src="/chewie.png" style="vertical-align:top">

        <form method="post" action="" style="display: inline-block;">
		<br>
                <input type="hidden" name="stop_all" value="TRUE">
                <input type="submit" value="Stop" style="color: white; background-color: #c13841; border-color: #c13841; font-size: 1.5em; font-weight: bold;">
        </form>



	</div>
	<div align="center">
"""

for light in light_info:
	if light[1] == "True":
		color = "#27c453"
	else:
		color = "#c13841"

	print """
	<form method="post" action="" style="display: inline-block;">
		<input type="hidden" name="toggle_light" value='""" + light[0] + """:""" + light[1] + """'>
		<input type="submit" value=\"""" + light[3] + """\" style="color: white; background-color: """ + color + """; border-color: """ + color + """; font-size: 1.5em; font-weight: bold;">
	</form>
"""

print """
	</div>
	</body>

</html>
"""

