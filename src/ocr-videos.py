# importing libraries
import os
import cv2
import numpy as np
import datetime as dt

from sys import platform
from paddleocr import PaddleOCR,draw_ocr
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

class CoordinateStore:
    def __init__(self):
        self.top = (-1, -1)
        self.bot = (-1, -1)

    def clickGetCoor(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.top == (-1,-1):
                self.top = x, y
            else:
                self.bot = x, y

VID_PATH = r'./data/IMG_6054.MOV'
RSZ_SCLE = 0.8

# EasyOCR Init
if platform == "linux" or platform == "linux2": os.system('clear')
elif platform == "darwin":                      os.system('clear')
elif platform == "win32":                       os.system('cls')

strDtNow = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
reader   = PaddleOCR(use_angle_cls = True, show_log=False)

# Create a VideoCapture object and read from input file
cap = cv2.VideoCapture(VID_PATH)
if (cap.isOpened()== False):
    print("Error opening video file")

cap_len,    cap_fps     = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(cap.get(cv2.CAP_PROP_FPS))
cap_height, cap_width   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

with open(r'./proc/log_{}.txt'.format(strDtNow), 'x') as f:
    f.write('VID_PATH = {}\n'.format(VID_PATH))
    f.write('RSZ_SCLE = {}\n'.format(RSZ_SCLE))
    f.write('HGT, WDT = {}, {}\n'.format(cap_height, cap_width))
    f.write('LEN, FPS = {}, {}\n'.format(cap_len,    cap_fps))
    f.write('\n')

coorStore = CoordinateStore()
dy, dx = int((coorStore.bot[1]-coorStore.top[1]) / 2), int((coorStore.bot[0]-coorStore.top[0]) / 2)

win_width  = 1000; win_height = int(win_width/cap_width*cap_height)

idx = 0
while(cap.isOpened()):
      
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    if ret != True:

        break

    else:

        frame = cv2.resize(frame, (0,0), fx=RSZ_SCLE, fy=RSZ_SCLE)
        if (coorStore.top == (-1, -1) or coorStore.bot == (-1, -1)):
        
            cv2.namedWindow("main", cv2.WINDOW_NORMAL)
            cv2.resizeWindow('main', win_width, win_height)
            cv2.setMouseCallback('main', coorStore.clickGetCoor)
            cv2.imshow("main", frame)

        else:

            if (dx==0) or (dy==0):
                
                dy, dx = int((coorStore.bot[1]-coorStore.top[1]) / 2), int((coorStore.bot[0]-coorStore.top[0]) / 2)
                y0, x0 = coorStore.bot[1], coorStore.bot[0]
                x_ocr, y_ocr = 0, 0

            else:

                y0 = y0 - dy + y_ocr
                x0 = x0 - dx + x_ocr

                frame_cropped = frame[y0-dy:y0+dy, x0-dx:x0+dx]

                txtOcr = reader.ocr(frame_cropped, cls=True)
            
                centerCoor = np.average(txtOcr[0][0][0], axis = 0)
                x_ocr, y_ocr = int(centerCoor[0]), int(centerCoor[1])

                cv2.drawMarker(frame_cropped, (x_ocr, y_ocr), (0, 255, 0), cv2.MARKER_CROSS, 15, 1)
                cv2.imshow("main", frame_cropped)

                msg = "{}%\t{}\t{}\t{}".format(np.round((idx+1)/cap_len*100,2), np.round(cap.get(cv2.CAP_PROP_POS_MSEC)/1000, 2) , txtOcr[0][0][1][0], np.round(txtOcr[0][0][1][1],4))
                print(msg)
                with open(r'./proc/log_{}.txt'.format(strDtNow), 'a') as f:
                    f.write(msg+"\n")

        # Press Q on keyboard to exit
        idx = idx + 1
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
  
# When everything done, release the video capture object
cap.release()
cv2.destroyAllWindows()