# Get latest image from Pi1.
scp nick@192.168.1.170:/var/www/html/camimg/current_image.jpg /var/www/html/camimg/current_image_pi1.jpg

# Check each Pi for a running instance of the security camera software.
pi2=$(ps ax | grep "[s]ecurity_camera.py" | wc -l)
pi1=$(ssh nick@192.168.1.170 'ps ax | grep "[s]ecurity_camera.py" | wc -l')

echo $pi1" "$pi2

