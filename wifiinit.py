#!/usr/bin/python
# apt-get install scapy

import sys
import time
import atexit
import signal
import commands
from subprocess import call
from scapy.all import *

class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

iface='wlan0'
moniface='mon0'
myAPch = 2
scantime = 25
okstring = '[' + color.OKGREEN+'OK' + color.ENDC + ']'

def exit_handler():
	#cleanup
	os.system('sudo airmon-ng stop '+ moniface +' >/dev/nul')
	os.system('sudo airmon-ng stop ' + iface + ' >/dev/nul') 
	#os.system("sudo NetworkManager")
	print 'Clean-up done!'

def scanforAP(p):
     if p.haslayer(Dot11) :
		if p.type == 0 and p.subtype == 8 :
			if p.addr2 not in apList :
				apList.append(p.addr2)
				print "AP MAC: %s with SSID: %s " %(p.addr2, p.info)
				chlist.append(int( ord(p[Dot11Elt:3].info)))
				print int( ord(p[Dot11Elt:3].info))

os.system("sudo ifconfig "+ iface +" up")
os.system("sudo airmon-ng start " + iface + " >/dev/nul"	)

apList = []
chlist = []
mych = [6,1,11,10,9,8,7,2,3,4,5,1,1,1]
print 'scapy starts '+str(scantime)+'s scan...'
sniff(iface=moniface, prn=scanforAP, timeout = scantime )
print 'scan finished ' + okstring 
for i in range(0,10):
	print mych[i]
	if mych[i] not in chlist:
		myAPch = mych[i] 
		break
print 'selected channel: ' + str(myAPch)
print 'Createing AP...' + okstring
os.system('create_ap -c ' + str(myAPch) + ' ' + iface + ' p2p1 4TMM sziaszia123 --no-virt ' )
atexit.register(exit_handler)

