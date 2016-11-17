import cv2, math
import numpy as np
import urllib.request as request

def angle_cos(p0, p1, p2):
	d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
	return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def clearImg(bounds,url):

	resp = request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	img = cv2.imdecode(image, cv2.IMREAD_COLOR)
	b = cv2.imdecode(image, cv2.IMREAD_COLOR)

	#img = cv2.imread("res.png")
	#b = cv2.imread("res.png")
	for i in bounds:
		cv2.rectangle(img,(int(i[0]), int(i[1])),(int(i[0])+int(i[2]),int(i[1])+int(i[3])),(255,255,255), -1)
	cv2.imshow("wee", img)
	img = cv2.medianBlur(img,5)
	img = cv2.GaussianBlur(img, (5,5), 0)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	ret,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
	kernel = np.ones((3,3),np.uint8)
	img = cv2.dilate(img,kernel,iterations = 1)
	bin, contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	symbols = []
	for cnt in contours:
		cnt_len = cv2.arcLength(cnt, True)
		cnt = cv2.approxPolyDP(cnt, 0.04*cnt_len, True)
		cnt = cnt.reshape(-1, 2)
		if len(cnt) < 9 and cv2.contourArea(cnt) > 200 and cv2.contourArea(cnt) < 300000:
			if len(symbols) == 0:
				cv2.drawContours(b,[cnt], -1, (0, 0,255 ), 3 )
				symbols.append([cnt])
			else:
				found = False
				for i in range(0, len(symbols)):
					if cv2.matchShapes(cnt,symbols[i][0],1,0.0) < .1 and not found:
						symbols[i].append(cnt)
						found = True
				if not found:
					symbols.append([cnt])

	color = [50,50,50]
	for i in range(len(symbols)):
		cv2.drawContours(b, symbols[i], -1, tuple(color),3)
		color[i%3] += 100
	
	for i in range(len(symbols)):
		for j in range(len(symbols[i])):
			cX,cY,w,h = cv2.boundingRect(symbols[i][j])
			symbols[i][j] = [cX, cY, w, h]

	for i in range(len(symbols)):
		for j in range(len(symbols[i])):
			this_center = (symbols[i][j][0], symbols[i][j][1])
			for k in range(len(symbols)):
				for l in range(len(symbols[k])):
					if symbols[i][j] != symbols[k][l]:
						curr_center = (symbols[k][l][0], symbols[k][l][1])
						dist = math.hypot(this_center[0] - curr_center[0], this_center[1] - curr_center[1])
						print(dist)
						if dist < 30:
							this_area = symbols[i][j][2] * symbols[i][j][3]
							curr_area = symbols[k][l][2] * symbols[k][l][3]
							if this_area < curr_area:
								symbols[k][l] = [-1,-1,-1,-1]
							else:
								symbols[i][j] = [-1,-1,-1,-1]

	print(symbols)

	for i in symbols:
		for j in i:
			cv2.rectangle(b, (j[0], j[1]), (j[0]+j[2], j[1]+j[3]), (255,0,255))

	cv2.imshow("hi", b)
	#cv2.waitKey()

	print("total list length", len(symbols))
	for i in symbols:
		print("   indiv list length", len(i))

	return symbols		

#clearImg(1,1)