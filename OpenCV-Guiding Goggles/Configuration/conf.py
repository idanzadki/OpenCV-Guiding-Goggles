import cv2
import numpy as np
from bluepy.btle import UUID, Peripheral
from bluepy.btle import Scanner, DefaultDelegate
import os, sys
from time import sleep
import urllib
import struct


from Controllers.BLEManager import BLEManager
from HaarCascade import builder
from Video import getVideoList
fixDim=lambda x,y:tuple([a/y for a in x])

attrs={}


def initial():
	
	dim=fixDim((640,480),2)
	#dim=fixDim((320,240),2)
	specs=(3.04,dim[1],2.76)
	#specs=(3,dim[1],2.2)
	suuid = "df6a8b89-32d1-486d-943a-1a1f6b0b52ed"
	duuid = "fb958909-f26e-43a9-927c-7e17d8fb2d8d"
	cuuid="fb958909-f26e-43a9-927c-7e17d8fb2d8e"
	address='d0:7f:a0:74:6e:c2'
	videoList=getVideoList.getList()
	cascadeList=builder.getCascadeList()
	bleManager=BLEManager(suuid,duuid,cuuid,address)
	m5Path="http://192.168.4.1/jpg_stream"
	attrs.update(Bounds(dim))
	attrs.update(locals())

def Bounds(dim):
	w=dim[0]
	h=dim[1]
	startFrameX=w/3
	endFrameX=w-w/3
	startFrameY=h/6
	endFrameY=h-h/6
	startL=w*4/9
	startR=w-startL
	center=(startL,startR)
	lenFrameX=endFrameX-startFrameX
	lenFrameY=endFrameY-startFrameY
	lVer=(startL,endFrameY),(startL,startFrameY)
	rVer=(startR,endFrameY),(startR,startFrameY)
	rec=(startFrameX,startFrameY),(endFrameX,endFrameY)
	#center=(w/2,h/2)
	return locals()
	
def update(att):attrs.update(att)
def get(get):
	if get in attrs:return attrs[get]
def getConf():return attrs
def set(key,val):attrs[key]=val

initial()
