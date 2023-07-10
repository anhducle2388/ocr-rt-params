import cv2
import os
import numpy as np
import easyocr

os.system("clear")


# Capture Video
VID_PATH = r'./data/IMG_5920.MOV'

cap 	  = cv2.VideoCapture(VID_PATH)
fps_cap = cap.get(cv2.CAP_PROP_FPS)
len_cap = cap.get(cv2.CAP_PROP_FRAME_COUNT)
height, width = cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FRAME_WIDTH)

# Video metadata
print(fps_cap, len_cap)
print(height, width )

# Init EasyOCR
reader = easyocr.Reader(['en'])

idx = 0
if (cap.isOpened()== False):
	print("Error opening video file")

else:
	while(cap.isOpened()):
		ret, frame = cap.read()
		if ret == True:

			x_top, y_top = 1600, 340
			x_bot, y_bot = 1700, 420

			viewFrame = frame[y_top:y_bot, x_top:x_bot]
			cv2.imshow('Frame', viewFrame)
			cv2.imwrite(r'./proc/img.png', viewFrame)

			txtOcr = reader.readtext(viewFrame)
			txtMsg = "{}/{}, {}, {}, {}".format(int(idx), int(len_cap), np.round(cap.get(cv2.CAP_PROP_POS_MSEC),2), int(fps_cap), txtOcr)
			print(txtMsg)

			with open(r'./log.txt', 'a') as f:
				f.write(txtMsg + "\n")
				
			idx = idx + 1
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break

		else:
			break

cap.release()
cv2.destroyAllWindows()
