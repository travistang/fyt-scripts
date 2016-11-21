import cv2,numpy as np,caffe,sys
from scipy.misc import imread,imresize,imsave
from os import mkdir,listdir
from os.path import basename,isfile,join

training_images_dir = ''
training_labels_dir = ''
output_dir = 'data'

S = 7
B = 2
C = 1

args = sys.argv
if len(args) < 3:
	print 'usage: python build_training_data.py image_dir labels_dir [output_dir]'
	exit(1)

training_images_dir,training_labels_dir = args[1:3]

if len(args) == 4:
	output_dir = args[3]

imgs = listdir(training_images_dir)

def getLabel(n):
	n = n.replace('jpg','').replace('txt','').replace('.','')
	n = n + '.txt'
	return None if not isfile(join(training_labels_dir,n)) else join(training_labels_dir,n)

labels = map(getLabel,imgs)
if None in labels:
	print 'missing labels in ' + training_labels_dir
	exit(1)

# get an vector of (S * S * (5 * B + C)) * 1 according to the given label (x,y,h,w),category(in range(C))
# the previous output (as input) can be provided for modifying 
def getOutput(labels,cat,imgh = 448,imgw = 448,input = None):
	# check...
	x,y,h,w = labels
	if S not in range(min(imgh,imgw)) or imgh <= 0 or imgw <= 0 or cat not in range(C) \
			or x not in range(imgh) or y not in range(imgw) \
			or x + h not in range(imgh) or y + w not in range(imgw):
				return None
	res = np.zero(S * S * (5 * B + C))
	if input: res = input
	cat1 = S * S * C
	cat2 = S * S * B
	cat3 = S * S * 4 * B
	# value preparation
	# decide which grid does the label belong to
	Sh = imgh % S
	Sw = imgw % S

	# normalize the coordinates w.r.t (Sh,Sw)
	nx,ny = float(x - Sh) / float(S), float(y - Sw) / float(S)
	nh,nw = float(h) / h,float(w) / w
	# filling the vector
	cat1_base = (Sh * S + Sw) * C # this is at most (S * S - S + S - 1) * C = S * S * C - C
	res[cat1_base + cat] = 1
	# scan through the bounding box and calculate the correspondence
	recorded = False
	for i in range(B):
		if res[cat1 + i] == 0:
			recorded = True
			res[cat1 + i] = 1
			break
	# record the box
	if recorded:
		cat3_base = cat1 + cat2 + 4 * i
		box = [nx,ny,nh,nw]
		for i in range(4):
			res[cat3_base + i] = box[i]
	return res

def generate_labels(imgh,imgw):
	# get all labels files
	global labels
	for l in labels:
		l = open(l)
		boxes = l.readlines()
		l.close()
		print boxes
		exit(0)
		# helper function to help interpreting the line
		def f(line):
			box,cat = line.split(' ')
			return eval(box),int(cat)
		info = map(f,boxes)
		res = None
		for box,cat in info: res = getOutput(box,cat,imgh,imgw,res)
		
		# write the vector to output
		path = join(output_dir,basename(l))
		with open(path,'w+') as lab:
			lab.write(res)

	map(lambda f: f.close(),labels)

			
if __name__ == '__main__':
	print 'generating labels...'
	generate_labels(448,448)
	print 'output files are written to %s' % output_dir
