import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import cv2
from lxml import etree
import xml.dom.minidom

class Marker:
	should_continue = True
	isPressing = False
	buttonPressed = None
	# selectedPoints contains points that are selected but not saved.
	# Such as if one draws a side of an edge after he has drawn the other already,
	# The side drawn would be
	selectedPoints = []
	fig = ax = None
	# a tuple storing 3 elements: first is the location of the mark, seoncd is the color of the image previously
	previousMark = []
	image = None
	__ori_image = None
	# mouse click handler
	def click_event(event):
		if event.button == 2:
			Marker.export()

		Marker.isPressing = True
		Marker.buttonPressed = event.button
	def release_event(event):
		Marker.isPressing = False
		Marker.buttonPressed = None
	def motion_event(event):
		if not 	Marker.isPressing: return
		if event.button == 1:
			x,y = int(event.xdata),int(event.ydata)
			Marker.mark(y,x)
			Marker.update()
		elif event.button == 3:
			#remove index on top of cursor
			x,y = int(event.xdata),int(event.ydata)
			Marker.unmark(y,x)
			Marker.update()
	def key_event(event):
		if event.key == 'x':
			Marker.should_continue = False
		else:
			Marker.revert()
	@staticmethod
	def update():
		Marker.show.set_data(Marker.image)
		Marker.fig.canvas.draw()
	@staticmethod
	def unmark(x,y):
		if (x,y) in Marker.selectedPoints:
			Marker.selectedPoints.remove((x,y))
			Marker.previousMark.append(((x,y),Marker.__ori_image[x,y],False))
			Marker.image[x,y] = Marker.__ori_image[x,y]
	@staticmethod
	def mark(x,y):
		Marker.selectedPoints.append((x,y))
		Marker.previousMark.append(((x,y),Marker.image[x,y],True))
		Marker.image[x,y] = [255,0,0]

	@staticmethod
	def revert():
		Marker.selectedPoints = Marker.selectedPoints[0:-1]
		coord,color = Marker.previousMark[-1]
		Marker.previousMark = Marker.previousMark[0:-1]
		#revert color
		if coord and color:
			Marker.image[coord[0],coord[1]] = color
		Marker.update()
	@staticmethod
	def isInRange(x,y):
		if not x >= 0 and y >= 0 and x < Marker.image.shape[0] and y < Marker.image.shape[1]:
			print (x,y) + "fail"
			return False
		else:
			return True
	@staticmethod
	def getPatch(x,y,size):
		if not Marker.isInRange(x,y):
			return None
		else:
			# prepare padded image
			half = int(size/2)
			resimg = cv2.cvtColor(cv2.copyMakeBorder(Marker.__ori_image,half,half,half,half,cv2.BORDER_REPLICATE),cv2.COLOR_BGR2GRAY)
			return resimg[(x - half):(x + half) + 1,(y - half):(y + half) + 1]
	@staticmethod
	def export():
		'''
			export as xml file with name *outputpath*
			sample content of such file is as follows:
				<data>
					<point x=10 y=20>
						<patch>
							0 0 0 255 0 255 0 0 0 0 255 ....
						</patch>
					</point>
					<point x=44 y=30>
						<patch>
							......
						</patch>
					</point>
					...
				</data>
		'''
		data = etree.Element('data')
		padding_size = 5
		half = int(padding_size/2)
		for (x,y) in Marker.selectedPoints:
			point = etree.Element('point',x = str(x),y = str(y))
			patch = Marker.getPatch(x + half,y + half,padding_size)
			#if not patch:	raise ValueError("the selected patch at (%d,%d) is invalid" % (x,y))
			patchnode = etree.Element('patch')
			patchnode.text = np.array_str(patch)
			point.append(patchnode)
			data.append(point)
		xmlstr = etree.tostring(data)
		#TODO: append the xml tree instead of overwriting the entire thing
		outstr = xml.dom.minidom.parseString(xmlstr).toprettyxml()
		with open(Marker.outputpath, 'w+') as f:
			f.write(outstr)
	@staticmethod
	def load_image():
		try:
			Marker.image = cv2.imread(Marker.inputfilename)
			Marker.__ori_image = np.copy(Marker.image)
			Marker.show = Marker.ax.imshow(Marker.image)
			plt.show()
		except IOError:
			print "File " + Marker.inputfilename + " not found."
			return

	@staticmethod
	def __mul_split(string,pos):
		pos = filter(lambda x: x < len(pos),pos)
		arr = list(set(pos.sort()))
		ret = []
		last = 0
		for i in range(len(arr)):
			ret.append(string[last:arr[i]])
			last = arr[i]
		ret.append(string[last:])
		return ret

	@staticmethod
	def __increment():
		# increment the filename, provided that the filename has the format "image-0xxxx.jpg"
		num = int(Marker.inputfilename[6:11]) + 1
		Marker.inputfilename = "image-" + str(num).zfill(5) + ".jpg"
	@staticmethod
	def main():
		# handle argument
		if len(sys.argv) == 1:
			print "usage: python mark.py <video-path> [<output-path>]"
			return

		Marker.inputfilename = sys.argv[1]
		Marker.outputpath = ""
		if len(sys.argv) >= 3:
			for i in range(2,len(sys.argv)):
				Marker.outputpath = Marker.outputpath + sys.argv[i] + " "

			Marker.outputpath = Marker.outputpath.strip() + ".xml"
		else:
			Marker.outputpath = "out.xml"

		# prepare matplotlib display
		Marker.fig = plt.figure()
		Marker.ax = Marker.fig.add_subplot(111)

		# bind event handler
		Marker.fig.canvas.mpl_connect('button_press_event',Marker.click_event)
		Marker.fig.canvas.mpl_connect('button_release_event',Marker.release_event)
		Marker.fig.canvas.mpl_connect('motion_notify_event',Marker.motion_event)
		Marker.fig.canvas.mpl_connect('key_press_event',Marker.key_event)
		#fetch input
		while Marker.should_continue:
			Marker.load_image()
			Marker.__increment()

if __name__ == "__main__":
	Marker.main()
