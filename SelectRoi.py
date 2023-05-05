import cv2

video = cv2.VideoCapture('tcc.mp4')
tracker = cv2.TrackerCSRT_create()

check,img = video.read()
bbox = cv2.selectROI('video', img, False)
tracker.init(img,bbox)

while True:
    check,img = video.read()
    check2, bbox = tracker.update(img)
    x,y,w,h = int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
    print(x,y,w,h)
    cv2.imshow('video',img)
    cv2.waitKey(10)

    key = cv2.waitKey(5)
    if key == 27:
            break
    