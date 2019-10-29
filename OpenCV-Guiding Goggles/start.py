import RPi.GPIO as GPIO
import Configuration.conf as conf
import cv2
import numpy as np
import urllib
import argparse
import sys
import threading
import logging
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
from pynput.keyboard import Key, Listener

logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-9s) %(message)s',)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(21, GPIO.OUT)
GPIO.output(21,GPIO.LOW)
button = 19
camera = 21



def initial():
	args=sys.argv
	showCap=False
	detect=False
	showBounds=False
	stop=False
	videoPath=""
	video=None
	cam=None
	bt=False
	emergency=False
	btn=False
	capturing=False
	direction=None
	print args
	if '-s' in args:showCap=True
	if '-d' in args:detect=True
	if '-b' in args:showBounds=True
	if '-bt' in args:bt=True
	if '-v' in args:
		if len(args)>args.index('-v')+1:
			video=args[args.index('-v')+1]
		else:
			print conf.get('videoList')
			for i in conf.get('videoList'):print i
			video=raw_input()
		if video in conf.get('videoList'):videoPath=conf.get('videoList')[video]
		else:
			print 'no video',video
			exit(1)
		cam=camType('video')
	if '-c' in args:
		if not '-v' in args:
			if len(args)>args.index('-c'):
				cam=camType(args[args.index('-c')+1])
				
	conf.update(locals())
	conf.update(conf.get('cascadeList'))
	conf.initial()

def soundDelay(di,de):
	if de is None: return
	if di==1:
		if de<4 and de>=3:#bleManager.writeDetect(1)#left, 0.50 delay 1
			return 1
		elif de<3 and de>=2:#bleManager.writeDetect(2)#left, 0.25 delay 2
			return 2
		else :#bleManager.writeDetect(3)#left, no delay 3
			return 3
	if di==2:
		if de<4 and de>=3:#bleManager.writeDetect(4)#right, 0.50 delay 4
			return 4
		elif de<3 and de>=2:#bleManager.writeDetect(5)#right, 0.25 delay 5
			return 5
		else :#bleManager.writeDetect(6)#right, no delay 6
			return 6
	if di==3:
		if de<4 and de>=3:#bleManager.writeDetect(7)#center, 0.50 delay 7
			return 7
		elif de<3 and de>=2:#bleManager.writeDetect(8)#center, 0.25 delay 8
			return 8
		else :#bleManager.writeDetect(9)#center, no delay 9
			return 9

def printBounds(frame):
	cv2.rectangle(frame,conf.get('rec')[0],conf.get('rec')[1], (255, 255, 0), 2)
	cv2.rectangle(frame,conf.get('lVer')[0],conf.get('lVer')[1], (255, 255, 0), 2)
	cv2.rectangle(frame,conf.get('rVer')[0],conf.get('rVer')[1], (255, 255, 0), 2)

def destination(real,h):
	specs=conf.get('specs')
	focal_len=specs[0]
	img_hi=specs[1]
	sensor_hi=specs[2]
	d=(focal_len*real*img_hi)/(h*sensor_hi)
	d=round(d/1000,1)
	if d>=4:return None
	else: return d

def detector(frame):
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#for (x,y,w,h) in conf.get('cars').detectMultiScale(gray,1.1,2):
	#	cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
	#	cv2.putText(frame,'car', (x-10,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 210)
	#	print 'car',destination(2400,h),'M'
		
			
	for (x,y,w,h) in conf.get('full_body').detectMultiScale(gray,1.5,1):
		bounds=inBounds(x,y,w,h)
		if not bounds is None:
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 215, 0),2)
			cv2.putText(frame,'full body', (x-10,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 210)
			print 'full_body',destination(1600,h),'M',bounds
			conf.set('direction',soundDelay(bounds,destination(1600,h)))
			
	
	#for (x,y,w,h) in conf.get('upper_body').detectMultiScale(frame,1.1,1):
	#	cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
	#	print 'upper_body',destination(600,h)

	#for (x,y,w,h) in conf.get('lower_body').detectMultiScale(frame,1.1,1):
	#	cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
	#	print 'lower_body',destination(800,h)
	
	
	for (x,y,w,h) in conf.get('frontal_face').detectMultiScale(gray,2,1):
		bounds=inBounds(x,y,w,h)
		if not bounds is None:
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 220, 0), 1)
			cv2.putText(frame,'frontal_face', (x-10,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 210)
			print 'frontal_face',destination(190,h)
			conf.set('direction',soundDelay(bounds,destination(190,h)))
	
	#for (x,y,w,h) in conf.get('two_wheeler').detectMultiScale(gray,1.1,1):
	#	cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), 2)
	#	cv2.putText(frame,'bike', (x-10,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 210)
	#	print 'bike',destination(1000,h),'M'
		
	#for (x,y,w,h) in conf.get('bus_front').detectMultiScale(gray,1.1,1):
	#	cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 215, 0), 2)
	#	cv2.putText(frame,'bike', (x-10,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 210)
	#	print 'bus',destination(1000,h),'M'
	

def inBounds(x,y,w,h):
	startFrameX=conf.get('startFrameX')
	startFrameY=conf.get('startFrameY')
	endFrameX=conf.get('endFrameX')
	endFrameX=conf.get('endFrameY')
	startL=conf.get('startL')
	startR=conf.get('startR')
	if y>=conf.get('startFrameY') and y<=conf.get('endFrameY'):
		if x>=conf.get('startFrameX') and x+w<=conf.get('startR'):return 1#left
		elif x>=conf.get('startL') and x+w<=conf.get('endFrameX'):return 2#right
		else:return 3#middle
	return None


def capPi():
	dim=conf.get('dim')
	camera = PiCamera()
	camera.resolution = dim
	#camera.rotation=90
	camera.framerate = 32
	rawCapture = PiRGBArray(camera, size=dim)
	# allow the camera to warmup
	time.sleep(0.1)
	# capture frames from the camera
	for fram in camera.capture_continuous(rawCapture, format="bgr"):
		#print 'frame'
		if conf.get('stop'):
			conf.set('capturing',False)
			break
		
		try:
			# grab the raw NumPy array representing the image, then initialize the timestamp
			# and occupied/unoccupied text
			frame = fram.array
			conf.set('capturing',True)
			if conf.get('showBounds'):printBounds(frame)
			if conf.get('detect'):detector(frame)
			# Display the resulting frame
			if conf.get('showCap'):
				cv2.imshow('Frame',frame)
				# Press Q on keyboard to  exit
			if cv2.waitKey(25) & 0xFF == ord('q'):break
			# clear the stream in preparation for the next frame
			rawCapture.truncate(0)

		except Exception as e:
			print( 'Capture()')
			conf.set('capturing',False)
			break


def camType(cap):
	if cap=='rasp':return threading.Thread(name='capPi', target=capPi)


			
def on_press(key):
	print('{0} pressed'.format(key))

def on_release(key):
	print('{0} release'.format(key))
	if key == Key.esc:
		conf.set('stop',True)
		# Stop listener
		return False
	#elif not push():bleManager.writeControl(0)


def keyListener():
    logging.debug('Starting')
    with Listener(on_press=on_press,on_release=on_release) as listener:listener.join()
    logging.debug('Exited')
    


initial()
bleManager=conf.get('bleManager')
mainThread = threading.Thread(name='keyListener', target=keyListener)
mainThread.setDaemon(True)
mainThread.start()

camThread = threading.Thread(name='camThread', target=capPi)
camThread.start()


#btnThread = threading.Thread(name='btnListener', target=push)
#btnThread.setDaemon(True)
#btnThread.start()


def handler():
	print bleManager.getControl()
	if not GPIO.input(button):
		print 'pushed'
		bleManager.writeControl(0)
	if bleManager.getControl()==2:
		print 'Preparing to disconnect from',bleManager.getDeviceName()
		bleManager.writeControl(3)
		bleManager.disConnect()
		conf.set('stop',True)
	if bleManager.getControl()==143:
		if not conf.get('emergency'):
			print 'emergency'
			conf.set('emergency',True)
			GPIO.output(camera,GPIO.HIGH)
			time.sleep(3)
			GPIO.output(camera,GPIO.LOW)
			time.sleep(0.5)
			GPIO.output(camera,GPIO.HIGH)
	if bleManager.getControl()==145:
		if not conf.get('detect'):
			conf.set('detect',True)
			print 'detect is on'
			bleManager.writeControl(-1)
	if bleManager.getControl()==144:
		if conf.get('emergency'):
			conf.set('emergency',False)
			print 'emergency off'
			GPIO.output(camera,GPIO.LOW)
		#time.sleep(3)
	else:
		bleManager.writeControl(-1)


try:
	if conf.get('bt'):
		if bleManager.scan(25,False):
			while bleManager.isConnected():
				if conf.get('stop'):break
				if conf.get('detect'):
					print conf.get('direction')
					bleManager.writeDetect(conf.get('direction'))
					conf.set('direction',None)
				handler()
				
				
except Exception as e:
	print 'Main exception - ',e
	bleManager.disConnect()
	exit(1)
finally:
	 bleManager.disConnect()
	 GPIO.output(camera,GPIO.LOW)
	 exit(0)




