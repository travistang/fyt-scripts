from scipy.misc import imread,imresize,imsave

label_file = 'labels.txt'

with open(label_file,'r') as f:
	lines = f.readlines()
	print len(lines)
	# remove newline characters
	lines = map(lambda l: l.replace('\n',''),lines)
	prev = '../Car/images/'
	img = None
	name = None
	count = 0
	for l in lines:
		if l[-1] == '{':
			count = 0
			name = l.split(' ')[0]
			print "processing %s..." % name
			img = imread(prev + name)
			img = imresize(img,0.5)
		elif l[0] == '(' and l[-1] == ')':
			box_loc = eval(l)
			x,y,h,w = box_loc
			oname,ext = name.split('.')
			bname = oname + '-n' + str(count) + '.' + ext
			count += 1
			print "writing to %s" % bname
			imsave(bname,img[x:(x + h),y:(y + w)])
				
			
			
