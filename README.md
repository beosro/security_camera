# Security Camera

## Overview

Security camera software designed for (but not limited to) a Raspberry Pi with a USB webcam.

Detects motion and sends an alert email to a specified address.  Flagged images can also be transferred to AWS.

## Dependencies

- Python 2.7
- Web server of your choice
- fswebcam
- dig

## Getting Started

```python security_camera.py [AWAY_MODE]```

Parameter | Value | Description
--- | --- | ---
AWAY_MODE | 1 or 0 | 0 turns off motion detection and alerts.

Point a web browser at the web server running on the security camera box to see a stream of images.

## Configuration

Copy `params-example.cfg` to `params.cfg`.  Open with a text editor and modify to suit your environment.

Copy `index.html` to the document root of your web server. 

## About the Author

https://nickbild79.firebaseapp.com

