####
# Nick Bild
# nick.bild@gmail.com
# 2018-06-20
# Raspberry Pi Security Camera
# v0.9
#
# Usage:
# python security_camera.py [AWAY_MODE]
# AWAY_MODE: [0,1]
# "1" will permanently save images and alert designated email address
# when activity is detected.
####

import sys
import os
import math
import numpy as np
import time
import smtplib
import subprocess
from PIL import Image
import ConfigParser


# Configuration
config = ConfigParser.ConfigParser()
config.read(os.path.abspath(os.path.dirname(sys.argv[0])) + '/params.cfg')

location = config.get('general', 'location')
email_to = config.get('general', 'email_to')
email_from = config.get('general', 'email_from')
email_password = config.get('general', 'email_password')
web_folder_url = config.get('general', 'web_folder_url')
port = config.get('general', 'port')
web_image_folder = config.get('general', 'web_image_folder')
smtp_server = config.get('general', 'smtp_server')
smtp_port = int(config.get('general', 'smtp_port'))

fswebcam_binary = config.get('img-processing', 'fswebcam_binary')
img_resolution = config.get('img-processing', 'img_resolution')
step = int(config.get('img-processing', 'step'))
time_stamp_height = int(config.get('img-processing', 'time_stamp_height'))
regions = int(config.get('img-processing', 'regions'))
threshold = float(config.get('img-processing', 'threshold'))
st_devs_for_significance = int(config.get('img-processing', 'st_devs_for_significance'))

tx_to_amazon = config.get('amazon', 'tx_to_amazon')
amazon_pem = config.get('amazon', 'amazon_pem')
amazon_user = config.get('amazon', 'amazon_user')
amazon_host = config.get('amazon', 'amazon_host')
amazon_dir = config.get('amazon', 'amazon_dir')

external_ip = subprocess.check_output("dig +short myip.opendns.com @resolver1.opendns.com", shell=True).strip()
away_mode = int(sys.argv[1])


def email_alert(email_to, msg):
	server = smtplib.SMTP(smtp_server, smtp_port)
	server.starttls()
	server.login(email_from, email_password)
	server.sendmail(email_from, email_to, msg)
	server.quit()


def calculate_image_distance(file1, file2):
	im1 = Image.open(file1)
	im2 = Image.open(file2)

	pix1 = im1.load()
	pix2 = im2.load()

	# Matrix to store total pixel difference in each region.
	region_matrix = [[0 for x in range(regions)] for y in range(regions)]
	pixels_per_h_region = im1.size[1] / regions
	pixels_per_w_region = im1.size[0] / regions

	for h in range(1, im1.size[1] - time_stamp_height):
		h_region = int(math.ceil(h / float(pixels_per_h_region)))		# Which h region are we in?
		for w in range(1, im1.size[0], step):
			w_region = int(math.ceil(w / float(pixels_per_w_region)))	# Which w region are we in?
			# Add this pixel's difference to the current region's difference value.
			region_matrix[w_region-1][h_region-1] += abs(pix1[w, h][0] - pix2[w, h][0]) + abs(pix1[w, h][1] - pix2[w, h][1]) + abs(pix1[w, h][2] - pix2[w, h][2])

	mean = np.mean(region_matrix)
	stdev = np.std(region_matrix)

	# Find percentage of regions outside of 'st_devs_for_significance' standard deviations from the mean.
	outlier_regions = 0
	cutoff_low = mean - stdev * st_devs_for_significance
	cutoff_high = mean + stdev * st_devs_for_significance
	for h_region in range(regions):
		for w_region in range(regions):
			if region_matrix[w_region][h_region] < cutoff_low or region_matrix[w_region][h_region] > cutoff_high:
				outlier_regions += 1
	outlier_region_pct = (outlier_regions / float(regions * regions)) * 100

	return outlier_region_pct


def clean_up_old_images():
	os.system("find " + web_image_folder + "/image_*.jpg -mtime +0 -exec rm {} \;")


# Main
if len(sys.argv) < 2:
	print "Usage: python " + sys.argv[0] + " [AWAY_MODE]"
	sys.exit()

clean_up_old_images()

cnt = 0
diff = 0
last_image = None

while True:
	cnt += 1

	# Capture new image and calculate "distance" from last image.
	os.system(fswebcam_binary + " -q -r " + img_resolution + " " + web_image_folder + "/current_image.jpg > /dev/null 2>&1")
	if last_image is not None and away_mode == 1:
		diff = calculate_image_distance(web_image_folder + "/current_image.jpg", last_image)

	# Current image becomes last image for next loop iteration.
	if away_mode == 1:
		last_image_save = last_image
		last_image = web_image_folder + "/image_" + str(int(time.time())) + ".jpg"
		os.system("cp " + web_image_folder + "/current_image.jpg " + last_image)

	# Significant image difference detected and in away mode.
	if diff > threshold and away_mode == 1:
		# Keep permanent local copy of saved images.
		os.system("cp " + last_image_save + " " + web_image_folder + "/save/")
		os.system("cp " + last_image + " " + web_image_folder + "/save/")

		# Keep remote copy of saved images.
		if tx_to_amazon == "yes":
			os.system("scp -i " + amazon_pem + " " + last_image_save + " " + amazon_user + "@" + amazon_host + ":" + amazon_dir + "/")
			os.system("scp -i " + amazon_pem + " " + last_image + " " + amazon_user + "@" + amazon_host + ":" + amazon_dir + "/")

		# Send alert email.
		temp = last_image_save.split("/")
		last_image_save_filename = temp[-1]
		temp = last_image.split("/")
		last_image_filename = temp[-1]
		msg = "Subject: " + location + " Security Camera Alert\n\nActivity Detected.\nhttp://" + external_ip + ":" + port + web_folder_url + "/save/" + last_image_save_filename + "\nhttp://" + external_ip + ":" + port + web_folder_url + "/save/" + last_image_filename + "\n" + str(diff)
		email_alert(email_to, msg)

	# Remove images older than 24 hours to conserve disk space.
	if cnt > 250:
		clean_up_old_images()
		cnt = 0

	# Less processing time required when not in away mode. Reduce number of images captured.
	if away_mode == 0:
		time.sleep(3)

