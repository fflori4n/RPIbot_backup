import RPi.GPIO as GPIO
import time
import sys
import os

PREVHASH = ''
DIFFAMP = 1.5
MOTORTMOUT  = 50
minpwmval = 50

RHALLPIN = 4; LHALLPIN = 17; PWM1 = 24; PWM2 = 23; DIR1 = 27; DIR2 = 22		# GPIO PINS
PWML = 0; PWMR = 0; DIRR = False; DIRL = False
stopR = True; stopL = True
activeMot = True
starttml = 0; starttmr = 0
HALLERR = False;HALLERL = False;LERno = 0;RERno = 0
analogtmout = int(round(time.time() * 1000))
# setup 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RHALLPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LHALLPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(DIR1, GPIO.OUT)		# DIRR DIR1
GPIO.setup(DIR2, GPIO.OUT)		# DIRL DIR2
GPIO.setup(PWM1, GPIO.OUT)		# PWMR PWM1
GPIO.setup(PWM2, GPIO.OUT)		# PWML PWM2
MOTORR = GPIO.PWM(PWM1, 1000)		# PWMR
MOTORL = GPIO.PWM(PWM2, 1000)		# PWML
MOTORR.start(50)
MOTORL.start(50)

def Setmotorpins():

	print 'PWML:',PWML,' DIRL:',DIRL,'PWMR: ',PWMR,' DIRR:',DIRR
	global minpwmval,PWMR,PWML,DIRR,DIRL
	global stopR,stopL,HALLERR,HALLERL,activeMot

	if PWMR > 90:															# max is 90% 
		PWMR = 90
	if PWML > 90:
		PWML = 90

	if DIRR:
		GPIO.output(DIR1, GPIO.HIGH)
	else:
		GPIO.output(DIR1, GPIO.LOW)
	if DIRL:
		GPIO.output(DIR2, GPIO.LOW)
	else:
		GPIO.output(DIR2, GPIO.HIGH)

	if PWMR > minpwmval:
		stopR = False
		HALLERR = False
	if PWML > minpwmval:
		stopL = False
		HALLERL = False

	if stopR == True:
		MOTORR.ChangeDutyCycle(0)
	if stopL == True:
		MOTORL.ChangeDutyCycle(0)

	if activeMot:
		if not HALLERL:
			if not stopL:
				MOTORL.ChangeDutyCycle(PWML)
			else:
				activeMot = not(activeMot)
		else:
			MOTORR.ChangeDutyCycle(0)
	else:
		if not HALLERR:
			if not stopR:
				MOTORR.ChangeDutyCycle(PWMR)
			else:
				activeMot = not(activeMot)
		else:
			MOTORL.ChangeDutyCycle(0)
	
	#print 'L: ',PWML,' R: ',PWMR
	#print PWML,'',DIRL,' ',PWMR,' ',DIRR
def analogcontrol(rawstr):													# /MA 0000 0000 6059/
	global PWMR,PWML,DIRR,DIRL

	DIFF = rawstr[3:7]
	SPEED = rawstr[8:13]
	ForB = bool(int(SPEED)/1000)			# 1 if forvard 0 if backvard
	LorR = bool(int(DIFF)/1000)
	if not ForB:
		DIRR = False
		DIRL = False
	else:
		DIRR = True
		DIRL = True
	if LorR:
		PWMR =int(float(SPEED)%1000)
		PWML = int(PWMR - (DIFFAMP*(PWMR * (float(DIFF)%1000)/100)))
	else:
		PWML = int(float(SPEED)%1000)
		PWMR = int(PWML - (DIFFAMP*(PWML * (float(DIFF)%1000)/100)))
	if PWML < 0:
		DIRL = not DIRL
		PWML = -(PWML)
	if PWMR < 0:
		DIRR = not DIRR
		PWMR = -(PWMR)

	PWMR = minpwmval + (PWMR / 2)
	PWML = minpwmval + (PWML / 2)

	#print 'PWML:',PWML,' DIRL:',DIRL,'PWMR: ',PWMR,' DIRR:',DIRR
	return
def ocvcontrol(rawstr):														# /CV 0000 6060 0595/
	global PWMR,PWML,DIRR,DIRL

	MOTORR.ChangeDutyCycle(0)
	MOTORL.ChangeDutyCycle(0)
	#print 'OCV control'														# CV 1010 6060 5579 forward
	#print rawstr															# 1111 backward 1110 left 1011 jobbra
	MOTORDATA = rawstr[3:7]
	#print MOTORDATA
	PWMR = (minpwmval + 1) * int(MOTORDATA[0])								# PWMR,DIRR,PWML,DIRL
	PWML = (minpwmval + 1) * int(MOTORDATA[2])
	DIRL = (bool(MOTORDATA[1]))
	DIRR = (bool(MOTORDATA[3]))
	
	MOTORR.ChangeDutyCycle(PWMR)
	MOTORL.ChangeDutyCycle(PWML)
	if DIRR:
		GPIO.output(DIR1, GPIO.HIGH)
	else:
		GPIO.output(DIR1, GPIO.LOW)
	if DIRL:
		GPIO.output(DIR2, GPIO.LOW)
	else:
		GPIO.output(DIR2, GPIO.HIGH)
	time.sleep(0.15)
	MOTORR.ChangeDutyCycle(0)
	MOTORL.ChangeDutyCycle(0)
	#time.sleep(0.05)
	#SPEED = rawstr[8:13]
	print PWML,' ',DIRL,' ',PWMR,' ',DIRR,'\n'
	return
	
def RHallinterrupt(channel):  # R hall interrupt
	global starttmr,stopR,activeMot,HALLERR,RERno
	if GPIO.input(RHALLPIN) == 0:
		starttmr = int(round(time.time() * 1000))
		stopR = True
		MOTORR.ChangeDutyCycle(0)
		activeMot = not(activeMot)
		HALLERR = False
		RERno = 0
		#print 'R motor stopped!'
	
def LHallinterrupt(channel): # L hall interrupt
	global starttml,stopL,activeMot,HALLERL,LERno
	if GPIO.input(LHALLPIN) == 0:
		starttml = int(round(time.time() * 1000))
		stopL = True
		MOTORL.ChangeDutyCycle(0)
		activeMot = not(activeMot)
		HALLERL = False
		LERno = 0
		#print 'L motor stopped!'

GPIO.add_event_detect(RHALLPIN, GPIO.FALLING, callback=RHallinterrupt, bouncetime=20) # define interrupt on hall sens. pins
GPIO.add_event_detect(LHALLPIN, GPIO.FALLING, callback=LHallinterrupt, bouncetime=20) 

while True:
	now = int(round(time.time() * 1000))
	if (now - max(starttml,starttmr)) > 1000 and (stopR == False or stopL == False):
		if now - starttml > 1000:
			LERno = LERno + 1 
			starttml = now
		if now - starttmr > 1000:
			RERno = RERno + 1 
			starttmr = now
	if stopR == False and RERno > 10:
		PWMR = 0
		stopR = True
		HALLERR = True
		RERno = 0
		print 'RMOTOR timeout'
		Setmotorpins()
	if stopL == False and LERno > 10:
		PWML = 0
		stopL = True
		HALLERL = True
		LERno = 0
		print 'LMTOR timeout'
		Setmotorpins()

	motordat = open("motordata", "r")
	rawstr = motordat.read(20) 
	motordat.close()
	HASH = rawstr[13:17]
	if HASH != PREVHASH:
		PREVHASH = HASH
		ID = rawstr[:2]
		if ID == 'MA': 				# ANALOG CONTROL
			analogtmout = int(round(time.time() * 1000))
			analogcontrol(rawstr)
		elif ID == 'CV' and now - analogtmout > 3000:			# CV CONTROL
			print 'CV CONTROL ENABLED'
			ocvcontrol(rawstr)
		Setmotorpins()
GPIO.cleanup()           # clean up GPIO on normal exit  

