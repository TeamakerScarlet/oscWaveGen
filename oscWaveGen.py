'''
MIT License

Copyright (c) 1998-2021 RIGOL co.,ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Vector WaveForm Converter 
Based On Python,OpenCV,Numpy
Powered By Dave Xue 

'''

import cv2 as cv
import numpy as np
from numpy.core.defchararray import count
from numpy.lib.function_base import append

#Target Video Path and Name
videoPaths = "./source.mp4"
#Images Output Path
imgPaths = "./img/"
#Quantity Of Points Per Frame
ptsPerFrame = 300*1000
#Prefix Of File Name Of WaveForm Output
fileName = "WFM"

imgShape = []
xData = []
yData = []
FrameCountEnd = 0
FrameCountStart = 1

#Converd Video To Images
def v2p(videoPath, imgPath):
    global FrameCountAll
    videoObj = cv.VideoCapture(videoPath)
    frameCount = 1
    saveCountDown = 1
    saveCount = 0

    if videoObj.isOpened():
        rval, frame = videoObj.read()
        FrameCountAll = videoObj.get(cv.CAP_PROP_FRAME_COUNT)
    else:
        print("Video Err")
        rval = False
    
    while rval:
        rval, frame = videoObj.read()
        if (not rval):
            break
        if (frameCount % saveCountDown == 0):
            saveCount += 1
            print("NOW Frame is " + str(saveCount) + " Of All Frame " +
             str(FrameCountAll) + " " + str(100*(saveCount/FrameCountAll)) + " % ",end='\r' )
            cv.imwrite(imgPath+str(saveCount)+".jpg", frame)
        frameCount += 1
        cv.waitKey(1)
    videoObj.release()


#Use OpenCV To Find Contours In Each Frame
def contours(image):
    dst = cv.GaussianBlur(image, (3, 3), 0) #Use Gaussian Blur To Against Noises
    gray = cv.cvtColor(dst, cv.COLOR_RGB2GRAY)
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU) #Binaryzation The Image By OSTU
    c_canny_img  = cv.Canny(gray,10,150)#Use Canny Algorithm To Find Edges
    cv.imshow("canny image", c_canny_img)
    contours, heriachy = cv.findContours(c_canny_img, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)#Get Contours
    print("Find "+str(np.size(contours))+" Contours",end = '')
    cv.drawContours(image, contours, -1, (0, 0, 255), 2)
    cv.imshow("COU",image)
    cv.waitKey(2)
    return contours


#Write Points Into Buffer
def write2data(ptsList):
    global xData,yData
    ptsCount = 0
    ptsloop = 0
    xTmp = []
    yTmp = []
    for pts in ptsList:
        pts = np.transpose([pts]).tolist()
        for ptC in range(0,np.size(pts[0][0])-1): 
            xTmp.append(int(((pts[0][0][ptC][0]/(imgShape[1]/2))-1.0)*65535))
            yTmp.append(int(((pts[1][0][ptC][0]/(imgShape[0]/2))-1.0)*65535))
            ptsCount += 1
    if (ptsCount < ptsPerFrame and ptsCount > 0):
        ptsloop = int(ptsPerFrame/ptsCount)
        ptsCount = (ptsPerFrame-(ptsloop*ptsCount))
        for i in range(0,ptsloop+1):
            xData += xTmp
            yData += yTmp
    elif(ptsCount >= ptsPerFrame and ptsCount > 0):
        xData += xTmp
        yData += yTmp
    else:
        xData.append(0)
        yData.append(0)
    print("pts: "+str(ptsCount*ptsloop))


#Config File Names
def contoursAll(imgsPath,filaName):
    global imgShape,FrameCountAll
    for i in range(int(FrameCountStart),int(FrameCountEnd)):
        ipath = imgsPath+str(i)+".jpg"
        src = cv.imread(ipath)
        imgShape = src.shape
        ptL = contours(src)
        write2data(ptL)
    xFile = open(filaName+'x.txt', 'a', newline='')
    yFile = open(filaName+'y.txt', 'a', newline='')
    
    for i in range(np.size(xData)-1):
        xFile.writelines(str(xData[i])+'\n')
        yFile.writelines(str(yData[i])+'\n')
    
    xFile.close()
    yFile.close()
    


if __name__ == "__main__":
    print("Input Frame Num To Start From Images Or 'c' From Video")
    frame = input()
    if (frame != 'c'):
        FrameCountStart = int(frame)
        print("Input The End  Of Frames")
        FrameTotal = int(input())
    else:       
        v2p(videoPaths, imgPaths)
    FrameCountEnd = FrameTotal
    contoursAll(imgPaths, fileName)