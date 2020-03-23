import cv2
import numpy as np
from matplotlib import pyplot as plt
import win32gui, win32ui,win32con
from PIL import ImageGrab
import autopy
import time


def convert_pil_to_opencv(img):
    temp = np.array(img)
    return temp[:,:,::-1].copy()

def get_window():
    hWnd = 0x150AAA#win32gui.FindWindow("魔兽世界",None)
    left, top, right, bot = win32gui.GetWindowRect(hWnd)
    img = ImageGrab.grab(bbox=(left,top,right,bot))
    return convert_pil_to_opencv(img)
    #img.save('search.png')

def check_fish(rect, target):
    img = convert_pil_to_opencv(ImageGrab.grab(rect))
    res = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    threshold = 0.55
    loc = np.where( res >= threshold)
    # cv2.imwrite('fish.png',img)
    # cv2.imwrite('tttt.png',target)
    for pt in zip(*loc[::-1]):
        #检测一致，没有鱼上钩
        return True
    return False

def do_skill(img, search):
    time.sleep(2)
    res = cv2.matchTemplate(search,img,cv2.TM_CCOEFF_NORMED)
    threshold = 0.55
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        autopy.mouse.move(pt[0] + 20, pt[1] + 20)
        time.sleep(0.5)
        autopy.mouse.click(autopy.mouse.Button.LEFT)
        time.sleep(0.5)
        autopy.mouse.move(pt[0] -100, pt[1] - 50)
        break

count = 200
time.sleep(2)

skill = cv2.imread('skill.png')
# imgs = ["target.png","target1.png","target2.png","target3.png","target4.png"]
imgs = ["target.png","target1.png"]
cvimgs = []
for i in imgs:
    cvimgs.append(cv2.imread(i))

while count > 0:
    count -= 1
    print(count)
    screen = get_window()
    do_skill(skill,screen)
    time.sleep(5)
    for item in cvimgs:
        template = item
        img_rgb = get_window()
        res = cv2.matchTemplate(img_rgb,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.55
        loc = np.where( res >= threshold)
        flag = False
        for pt in zip(*loc[::-1]):
            flag = True
            #cv2.rectangle(img_rgb, pt, (pt[0] + template.shape[0], pt[1] + template.shape[1]), (0,0,255), 2)
            autopy.mouse.move(pt[0] - 50,pt[1] - 50)
            while check_fish((pt[0] - template.shape[0]*0.3,pt[1] -template.shape[1]*0.3, pt[0] + template.shape[0]*2,pt[1]+template.shape[1]),template):
                time.sleep(0.5)
            autopy.mouse.move(pt[0] + 20,pt[1] + 20)
            time.sleep(0.5)
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
            time.sleep(2)
            break
        if flag:
            break