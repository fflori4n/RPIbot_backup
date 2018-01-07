#!/usr/bin/python

import socket
import select
import time

msdelay = 5
wdata = 'proba'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)				# Init socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	
sock.bind(("192.168.12.1", 8234))
sock.listen(2)

while True:
	exit = False
	(client, (ip, port)) = sock.accept()									#connect to client
	print 'client connected!	[ OK ]'

	def COM():
		global exit
		data = client.recv(2048)
		print format(data)
		if len(data) == 0:
			client.close()
			print 'client disconnected!		[ ER ]'
			exit = True
		#print len(data)
		return format(data)
	def Write2file(wdata):
		f = open("motordata","w") 											#opens file with name of "motordata"
		f.write(wdata)
		f.close()
	msclk = int(round(time.time() * 1000))
	while True:
		wdata = COM()
		Write2file(wdata)
		if(exit):
			break
print "Closing the Socket!!"
sock.close()
