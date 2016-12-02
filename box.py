import numpy as np
import cv2,os,sys
from scipy.misc import imread,imresize,imshow
from random import choice

if len(sys.argv) < 5 or len(sys.argv) > 8:
	print "gg"
	exit(1)

fn = sys.argv[1]
target = sys.argv[2:5]
target = map(int,target)
min_area = None
resize = None
label = None
if len(sys.argv) >= 6:
	min_area = int(sys.argv[5])
if len(sys.argv) >= 7:
	resize = float(sys.argv[6])
if len(sys.argv) == 8:
	label = sys.argv[7]
#img = imread('labels/00036.png')
eq = lambda pa,pb: np.array_equal(pa,pb)

def grow_region(img,x,y,t = target):
	h,w,_ = img.shape
	# range check
	if x not in range(h) or y not in range(w): return []
	# alg. check
	if not eq(img[x,y],t): return []
	visited = [(x,y)]
	queue = get_neighbours((x,y),img)
	res = [(x,y)]
	while len(queue) > 0:
		pics = queue.pop(0)
		u,v = pics
		visited.append(pics)
		if eq(img[u,v],t):
			res.append(pics)
			to_be_visited = filter(lambda x: x not in visited and x not in queue,get_neighbours(pics,img))
			queue = queue + to_be_visited
	return res

def area(xmin,ymin,xmax,ymax):
	return (xmax - xmin) * (ymax - ymin)

def get_neighbours(c,im):
	h,w,_ = im.shape
	in_range = lambda (i,j): i in range(h) and j in range(w)
	dif = [-1,0,1]
	res = []
	u,v = c
	for dx in dif:
		for dy in dif:
			if (dx,dy) == (0,0): continue
			res.append((u + dx,v + dy))
	return filter(in_range,res)

def bounding_box(clus):
	xs = map(lambda x: x[0],clus)
	ys = map(lambda x: x[1],clus)
	xmin,xmax = min(xs),max(xs)
	ymin,ymax = min(ys),max(ys)
	return (xmin,ymin,xmax, ymax)

def box_area(clus):
	_,_,h,w = bounding_box(clus)
	return h * w

def get_bounding_boxes(fn,target,min_area = None,resize = None):
	img = imread(fn)
	if resize:
		img = imresize(img,resize)

	im_h,im_w,_ = img.shape
	clusters = []
	visited = []
	eq = lambda pa,pb: np.array_equal(pa,pb)
	# gather pixels
	xs,ys = np.where(np.all(img == target,axis = -1))
	interested = zip(xs,ys)
	while len(interested) > 0:
		x,y = interested[0]
		clus = grow_region(img,x,y)
		clusters.append(clus)
		[interested.remove(c) for c in clus if c in interested]
#	for i in range(im_h):
#		for j in range(im_w):
##			print '%s is %s' % (str((i,j)),'visited' if (i,j) in visited else 'not visited')
#			if (i,j) not in visited and eq(img[i,j],target):
#				clus = grow_region(img,i,j)
#				visited = visited + clus
#				clusters.append(clus)	
			# else: do nothing


	res = map(bounding_box,clusters)
	if min_area:
		res = filter(lambda (_,__,h,w): h * w >= min_area,res)

	return res

if __name__ == '__main__':
	items = get_bounding_boxes(fn,target,min_area,resize)	
	print len(items)
	[print a,b,c,d for a,b,c,d in items]
#	folder = 'labels_2'
#	fn = os.listdir(folder)
#	with open('labels.txt','w+') as file:
#		for f in fn:
#			file.write('%s {\n' % f)
#			print 'getting bounding boxes for %s...' % os.path.join('labels',f)
#			boxes = get_bounding_boxes(os.path.join(folder,f),target,90,0.5)
#			print 'writing to file...'
#			print boxes
#			if len(boxes) > 0:
#				[file.write('%s\n' % str(b)) for b in boxes]
#			file.write('}\n')

		
