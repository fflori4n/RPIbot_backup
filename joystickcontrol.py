from time import sleep
import pygame
import socket
import select
import random
import time
import sys
import os

host = '192.168.12.1'
port = 8234
joypadpos = []
rand_no = []
stopsig = 0
class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
OK = '[' + color.OKGREEN+' OK ' + color.ENDC + ']'
ER = '[' + color.WARNING+' ER ' + color.ENDC + ']'
FT = '[' + color.FAIL+' FT ' + color.ENDC + ']'

def sendviaTCP(Data_out):
		try:
			readable, writable, exceptional = select.select([],[client_socket], [],2)
			if client_socket in writable:
				print 'Writeable'
				client_socket.send((str(Data_out) + '\n'))
				writable = []
			else:
				print 'ERROR'
			#print 'sent:' + 'MM '+ str(Data_out) + OK
			#client_socket.close() #goes into cleanup if I ever make one...
			return 0
		except: 
			print 'Error sending!' + ER
			return -1

pygame.joystick.init()
if pygame.joystick.get_count() > 0:
	pygame.joystick.Joystick(0).init()
else:
	print 'no joystick!' + FT
	exit(0)			
while True:
	pygame.display.init()							
	pygame.event.pump()														# send tick to pygame to read values
	joypadpos = []
	for i in range(0,4):													# only x,y joypad
		position = (pygame.joystick.Joystick(0).get_axis(i)) 				# right one
		if position < 0:
			joypadpos.append(abs(int((round(position,2))*100)) + 1000)
		else:
			joypadpos.append(int((round(position,2))*100))
	analogjoyx = joypadpos[2]
	analogjoyy = joypadpos[3]
	
	rand_no = []
	for i in range (0, 4):
		rand_no.append(random.randint(0, 9))
		#print '--->',position

	if (('MA ' + str(format(analogjoyx, '04d')) + ' ' + str(format(analogjoyy, '04d'))) != 'MA 0000 0000'):
		stopsig = 0
	else:
		stopsig = stopsig + 1

	if stopsig < 10:														# send stop frame 10 times then stop
		Er = sendviaTCP('MA ' + str(format(analogjoyx, '04d')) + ' ' + str(format(analogjoyy, '04d')) + ' ' + (''.join(str(x) for x in rand_no)))
		if Er < 0:
			print 'send error' + ER
			try:
				#print 'INIT CONNECTION'
				client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			#create tcp socket
				client_socket.connect((host, port))							#port 5000 localhos for now
			except:
				print 'Error creating TCP socket! ' + FT
	sleep(0.5)
