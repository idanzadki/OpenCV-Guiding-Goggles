import os
import cv2
path=os.path.dirname(os.path.abspath(__file__))+'/'
dirs = os.listdir( path )

"""
def getCascadeList():
	temp={}
	for i in dirs:
		filename=i.split('.')
		h=filename[0].split('_')
		if h[0]=='haarcascade':
			name='_'.join(h[1:len(h):])
			p=path+i
			temp[name]=cv2.CascadeClassifier(p)
			#temp[name]=self.cascadePath+fullname
	return temp
"""

def getCascadeList():
	temp={}
	for i in dirs:
		if i.startswith('haarcascade') and i.endswith('.xml'):
			filename=i.split('.')
			h=filename[0].split('_')
			name='_'.join(h[1:len(h):])
			p=path+i
			temp[name]=cv2.CascadeClassifier(p)
			#temp[name]=self.cascadePath+fullname
	return temp
