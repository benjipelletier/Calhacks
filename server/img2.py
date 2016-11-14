import cv2
import numpy as np
import urllib.request

def angle_cos(p0, p1, p2):
	d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
	return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def clearImg(bounds,url):
	circles = []
	squares = []
	diamonds = []
	triangles = []

	resp = urllib.request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	img = cv2.imdecode(image, cv2.IMREAD_COLOR)
	b = cv2.imdecode(image, cv2.IMREAD_COLOR)

	#img = cv2.imread("test.jpg")
	#b = cv2.imread("test.jpg")
	for i in bounds:
		cv2.rectangle(img,(int(i[0]), int(i[1])),(int(i[0])+int(i[2]),int(i[1])+int(i[3])),(255,255,255), -1)
	img = cv2.medianBlur(img,5)
	img = cv2.GaussianBlur(img, (5,5), 0)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	ret,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
	kernel = np.ones((3,3),np.uint8)
	img = cv2.dilate(img,kernel,iterations = 1)
	bin, contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:
		cnt_len = cv2.arcLength(cnt, True)
		if cv2.contourArea(cnt) > 200:
			print("first",len(cnt))
		cnt = cv2.approxPolyDP(cnt, 0.067*cnt_len, True)
		cnt = cnt.reshape(-1, 2)
		if len(cnt) < 9 and cv2.contourArea(cnt) > 200 and cv2.contourArea(cnt) < 300000 and cv2.isContourConvex(cnt):
			print(len(cnt))
			cX,cY,w,h = cv2.boundingRect(cnt)
			cv2.circle(b, (cX, cY), 3, (0, 255, 255), -1)
			if len(cnt) == 3:
				#Blue Trianlges
				print("Triangle")
				cv2.drawContours(b, [cnt], -1, (0, 0, 255), 3 )
				triangles.append(cY)
			elif len(cnt) == 4:
				max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % len(cnt)], cnt[(i+2) % len(cnt)] ) for i in range(len(cnt))])
				if max_cos < 0.25:
					#Green Squares
					print("Square")
					cv2.drawContours(b, [cnt], -1, (0, 255,0 ), 3 )
					squares.append(cY)
				elif max_cos > .65:
					print(max_cos)
					#Purple Diamonds
					print("Diamond")
					cv2.drawContours(b, [cnt], -1, (255, 200,200 ), 3 )
					diamonds.append(cY)
				else:
					cv2.drawContours(b, [cnt], -1, (255, 200,300 ), 3 )
					triangles.append(cY)
			else:
				print(len(cnt))
				cv2.drawContours(b, [cnt], -1, (255, 255,0 ), 3 )
				circles.append(cY)
			
	return circles, squares, diamonds, triangles