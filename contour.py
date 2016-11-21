import cv2
import sys
import process
import Queue
import matplotlib.pyplot as plt
import numpy.linalg as lin
import numpy as np
# globals
img = None
marked = []
bound = []
window = None
fig = None

def rgb2hsv(rgb):
	rgb = rgb/255
	r,g,b = rgb
	v = max(rgb)
	d = v - min(rgb)
	s = 0 if v == 0 else d/v
	h = 0
	if d != 0:
		if v == r:
			h = 60 * ((g - b)/d) % 6
		if v == g:
			h = 60 * (b - r)/d + 2
		else:
			h = 60 * (r - g)/d + 4
	res = np.array([h,s,v])
	return res
def click_event(event,y,x,flag,img):
	if event == cv2.EVENT_LBUTTONDOWN:
		start_coord = (x,y)
		#start_coord = (int(event.ydata),int(event.xdata))
	# start the process
		visited = []
		global bound
		bound = [] # empty the bound
		queue = [start_coord]
		tar = rgb2hsv(img[start_coord[0],start_coord[1]])
		'''
			select a pixel p
			let tar = hsv(p)
			push p into the queue q
			while q is not empty:
				p = pop q
				mark p as visited
				if p is at the boundary of the image:
					mark coord(p) as bound
				if hsv(p) is in range with tar:
					push all pixels nearby to q
				else:
					mark coord(p) as bound
			return bound
		'''
		while len(queue) > 0:
			pix = queue[0] # touch
			queue = queue[1:] # pop
			# check if the given pixel is visited
			if pix in visited: continue
			visited.append(pix)
			try:
				if pix[0] == 0 or pix[1] == 0 or pix[0] == img.shape[0] - 1 or pix[1] == img.shape[1] - 1:
					bound.append(pix)
					continue

				if np.array_equal(tar,rgb2hsv(img[pix[0],pix[1]])):
					# handle the boundary
					for i in [-1,0,1]:
						for j in [-1,0,1]:
							queue.append((pix[0] + i, pix[1] + j))

				else:
					bound.append(pix)

			except:
				continue

def draw_bound(copy_img):
	global window,fig
	if bound:
		for (x,y) in bound:
			copy_img[x,y] = [255, 0, 0]


def func(img):
	copy_img = img
	draw_bound(copy_img)
	return copy_img
if __name__ == '__main__':
	rip = process.RealTimeImageProcessor(0)
	rip.set_key_listener(click_event)
	rip.set_process_function(func)
	rip.run('win')
'''
if len(sys.argv) < 2:
	print "Please specify the filename of the input image"
else:
	fn = ''.join(sys.argv[1:])
	img = cv2.imread(fn)
	ret,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
	# configure pyplot
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.axis('off')
	# bind event handler
	fig.canvas.mpl_connect('button_press_event',click_event)
	window = ax.imshow(img)
	plt.show()
'''
