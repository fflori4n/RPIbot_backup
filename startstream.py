import sys
import time
os.system('sudo /usr/local/bin/mjpg_streamer -i "/usr/local/lib/input_uvc.so d /dev/video0 -y -r 320x240 -f 20" -o "/usr/local/lib/output_http.so -p 8081 -w /usr/local/www"')
