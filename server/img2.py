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
		print(i)
		cv2.rectangle(img,(int(i[0]), int(i[1])),(int(i[0])+int(i[2]),int(i[1])+int(i[3])),(255,255,255), -1)
	cv2.imshow("his",img)
	img = cv2.medianBlur(img,5)
	img = cv2.GaussianBlur(img, (5,5), 0)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	ret,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
	bin, contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:
		cnt_len = cv2.arcLength(cnt, True)
		cnt = cv2.approxPolyDP(cnt, 0.04*cnt_len, True)
		if len(cnt) < 9 and cv2.contourArea(cnt) > 200 and cv2.contourArea(cnt) < 300000 and cv2.isContourConvex(cnt):
			cX,cY,w,h = cv2.boundingRect(cnt)
			cv2.circle(b, (cX, cY), 3, (0, 255, 255), -1)
			print(cX, cY)
			if len(cnt) == 3:
				cv2.drawContours(b, [cnt], -1, (0, 0, 255), 3 )
				triangles.append(cY)
			elif len(cnt) == 4:
				cnt = cnt.reshape(-1, 2)
				max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % len(cnt)], cnt[(i+2) % len(cnt)] ) for i in range(len(cnt))])
				if max_cos < 0.15:
					cv2.drawContours(b, [cnt], -1, (0, 255,0 ), 3 )
					squares.append(cY)
				else:
					cv2.drawContours(b, [cnt], -1, (255, 0,0 ), 3 )
					diamonds.append(cY)
			else:
				cv2.drawContours(b, [cnt], -1, (255, 255,0 ), 3 )
				circles.append(cY)
	cv2.imshow("hi",b)
	ch = 0xFF & cv2.waitKey()
			
	return circles, squares, diamonds, triangles