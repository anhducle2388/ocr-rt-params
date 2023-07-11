# importing libraries
import os
import easyocr
import cv2
import numpy as np

def __do_nothing():
    return

class CoordinateStore:
    def __init__(self):
        self.top = (-1, -1)
        self.bot = (-1, -1)

    def clickGetCoor(self, event, x, y, flags, params):
    
        if event == cv2.EVENT_LBUTTONDOWN:
            self.top = x, y
            print(f'Top Coor: ({self.top})')
    
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.bot = x, y
            print(f'Bot Coor: ({self.bot})')

VID_PATH = r'./data/IMG_5919.MOV'

coorStore = CoordinateStore()

dy, dx = int((coorStore.bot[1]-coorStore.top[1]) / 2), int((coorStore.bot[0]-coorStore.top[0]) / 2)
index = 0


# EasyOCR Init
os.system('cls')
reader = easyocr.Reader(['en'], gpu=True) #, model_storage_directory=r'.\models\easyocr', download_enabled =False)

# Create a VideoCapture object and read from input file
cap = cv2.VideoCapture(VID_PATH)
cap_len,    cap_fps     = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(cap.get(cv2.CAP_PROP_FPS))
cap_height, cap_width   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

win_width  = 1000
win_height = int(win_width/cap_width*cap_height)

print(cap_len, cap_fps)
print(cap_height, cap_width)

# Check if camera opened successfully
if (cap.isOpened()== False):
    print("Error opening video file")

while(cap.isOpened()):
      
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    if ret == True:

        if (coorStore.top == (-1, -1) or coorStore.bot == (-1, -1)):
        
            cv2.namedWindow("main", cv2.WINDOW_NORMAL)
            cv2.resizeWindow('main', win_width, win_height)
            cv2.setMouseCallback('main', coorStore.clickGetCoor)
            cv2.imshow("main", frame)

        else:

            if (dx==0) or (dy==0):

                # Calculate the interested window
                
                dy, dx = int((coorStore.bot[1]-coorStore.top[1]) / 2), int((coorStore.bot[0]-coorStore.top[0]) / 2)
                y0, x0 = coorStore.bot[1], coorStore.bot[0]
                x_ocr, y_ocr = 0, 0

            else:

                y0 = y0 - dy + y_ocr
                x0 = x0 - dx + x_ocr

                frame_cropped = frame[y0-dy:y0+dy, x0-dx:x0+dx]

                try:
                    txtOcr = reader.readtext(frame_cropped)
                
                    centerCoor = np.average(txtOcr[0][0], axis = 0)
                    x_ocr, y_ocr = int(centerCoor[0]), int(centerCoor[1])

                    cv2.drawMarker(frame_cropped, (x_ocr, y_ocr), (0, 255, 0), cv2.MARKER_CROSS, 15, 1)
                    cv2.imshow("main", frame_cropped)

                    if True:
                        msg = "{}/{};{};{};{}".format(index, cap_len, np.round(cap.get(cv2.CAP_PROP_POS_MSEC)/1000, 2) , txtOcr[0][1], np.round(txtOcr[0][2],4))
                        with open(r'./log.txt', 'a') as f:
                            f.write(msg+"\n")

                except: 
                    __do_nothing()

        index = index + 1
        
        # Press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
  
    else:
        break
  
# When everything done, release
# the video capture object
cap.release()
cv2.destroyAllWindows()