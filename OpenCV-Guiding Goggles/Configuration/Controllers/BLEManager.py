from bluepy.btle import Scanner
from bluepy.btle import UUID, Peripheral
from time import sleep
import os, sys


class BLEManager:
	def __init__(self,suuid,duuid,cuuid,addr):
		self.p = None
		self.detect = None
		self.control=None
		self.connected=False
		self.device=None
		self.service_uuid=suuid
		self.detect_uuid=duuid
		self.control_uuid=cuuid
		self.address=addr
		self.scanner = Scanner()
		self.dev_name_uuid = UUID(0x2A00)
	def isConnected(self):return self.connected
	def getDevice(self):return self.device
	def getServiceUUID(self):return self.service_uuid
	def getDetectUUID(self):return self.detect_uuid
	def getControlUUID(self):return self.control_uuid
	def getScanner(self):return self.scanner
	def getDeviceName(self):
		nch = self.p.getCharacteristics(uuid=self.dev_name_uuid)[0]
		if (nch.supportsRead()):return nch.read()
		return "No Name"
	def getDeviceAddress(self):return self.address
	def writeDetect(self,msg):
		if not msg is None:self.detect.write(str(msg),True)
	def writeControl(self,msg):
		if not msg is None:self.control.write(str(msg),True)
	def getDetect(self):
		if self.detect.supportsRead():return int(ord(self.detect.read()))
	def getControl(self):
		if self.control.supportsRead():return int(ord(self.control.read()))
	def scan(self,time=30,show=True):
		try:
			if not self.isConnected():
				print 'Looking for device... ({})'.format(time)
				devices=self.scanner.scan(time)
				for dev in devices:
					if show:print "Device %s (%s) %s" % (dev.addr, dev.addrType,dev.iface)
					for (adtype, desc, value) in dev.getScanData():
						if show:print desc+" = "+value
						if desc=="Complete 128b Services" and value==self.service_uuid:
							try:
								###################################################################
								p = Peripheral(dev.addr,dev.addrType)
								ISceService=p.getServiceByUUID(self.service_uuid)
								self.detect=ISceService.getCharacteristics(self.detect_uuid)[0]
								self.control=ISceService.getCharacteristics(self.control_uuid)[0]#Get device characteristics for communication
								self.p=p
								self.connected=True
								self.device=dev
								print "Connected - Address: %s, Name: %s" % (self.getDeviceAddress(),self.getDeviceName())
								return True
								####################################################################
							except Exception as e:
								print 'scan'
								print e.message
								self.connected=False
								return False
				print 'No device found.'
				return False
		except Exception as e:
			print 'BT Scan'
			print e
			return False
	def disConnect(self):
		if self.isConnected():
			print "Disconnecting from "+self.getDeviceName()+"..."
			self.p.disconnect()
			self.connected=False
			self.device=None
			self.p=None
			self.detect=None
			self.control=None
			print "Device Disconnected."
	def connect(self):
		try:
			###################################################################
			p = Peripheral(self.address,'public')
			ISceService=p.getServiceByUUID(self.service_uuid)
			self.detect=ISceService.getCharacteristics(self.detect_uuid)[0]
			self.control=ISceService.getCharacteristics(self.control_uuid)[0]#Get device characteristics for communication
			self.p=p
			self.connected=True
			print "Connected - Address: %s, Name: %s" % (self.getDeviceAddress(),self.getDeviceName())
			return True
			####################################################################
		except Exception as e:
			print 'scan'
			print e.message
			self.connected=False
			return False
