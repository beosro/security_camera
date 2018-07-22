#!/usr/bin/python

import cgi
import subprocess
import random
import os

PI1 = 0
PI1_NAME = "Family Room"
PI2 = 1
PI2_NAME = "Kitchen"
host = os.environ.get('SERVER_NAME')

form = cgi.FieldStorage()
start_all = form.getvalue("start_all", "")
stop_all = form.getvalue("stop_all", "")


def get_process_status():
	status = subprocess.check_output("sudo -u nick /home/nick/software/security_camera_misc/check_running.sh", shell=True).strip();
	status = status.split()
	return status

def start_all_cameras():
	status = subprocess.check_output("sudo -u nick /home/nick/software/security_camera_misc/start_all.sh", shell=True).strip();

def stop_all_cameras():
	status = subprocess.check_output("sudo -u nick /home/nick/software/security_camera_misc/stop_all.sh", shell=True).strip();


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

	<form method="post" action="" style="display: inline-block;">
		<input type="hidden" name="start_all" value="TRUE">
		<input type="submit" value="Start" style="color: white; background-color: #27c453; border-color: #27c453; font-size: 1.5em; font-weight: bold;">
	</form>

	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

	<form method="post" action="" style="display: inline-block;">
		<input type="hidden" name="stop_all" value="TRUE">
		<input type="submit" value="Stop" style="color: white; background-color: #c13841; border-color: #c13841; font-size: 1.5em; font-weight: bold;">
	</form>

	<br>
"""

print """<div style="display: inline-block; width: 49%; font-style: Bookman; color: white; font-weight: bold;">"""
if status_pi1 == "0":
	print """<img src="/red_x.png" width="75"><br>""" + PI1_NAME
else:
	print """<img src="/green_check.png" width="75"><br>""" + PI1_NAME
print """
<br>
<a href="https://""" + host + """"><img src="/camimg/current_image_pi1.jpg?rnd=""" + str(random.randint(1,999999)) + """" style="width: 100%;"></a>
</div>
"""


print """<div style="display: inline-block; width: 49%; font-style: Bookman; color: white; font-weight: bold;">"""

if status_pi2 == "0":
        print """<img src="/red_x.png" width="75"><br>""" + PI2_NAME
else:
        print """<img src="/green_check.png" width="75"><br>""" + PI2_NAME
print """
	<br>
	<a href="https://""" + host + """"><img src="/camimg/current_image.jpg?rnd=""" + str(random.randint(1,999999)) + """" style="width: 100%;"></a>
	</div>

	</div>

	</body>

</html>
"""

