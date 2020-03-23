import pyaudio , audioop , autopy 
import numpy as np
import win32gui, win32ui,win32con
import time

from cv2 import cv2 as cv
from utils import *
from matplotlib import pyplot as plt
from PIL import ImageGrab

FISH_REPEAT = 200 #执行次数
SKILL_THRESHOLD = 0.55 #技能图标匹配度
FLOAT_THRESHOLD = 0.55  #鱼漂图标匹配度
AUDIO_THRESHOLD = 50   #声音监听阈值
GLOBAL_DELAY=2 #全局Delay
STEP_DELAY=0.5 #步骤delay
SKILL_DIR = 'skill.png' #技能图片
FLOAT_DIR = 'float.png' #鱼漂图片
WINDOW_TITLE = '魔兽世界'
DEBUG_IT = 0

class gofishing():

    def __init__(self):
        pass
    def _convert_pil_to_opencv(self,img):
        '''
        把图像转换成opencv流
        '''
        cv2img = np.array(img)
        return cv2img[:,:,::-1].copy()

    def _get_window(self,handle=None,title=None):
        '''
        获取窗口句柄，返回窗口位置
        '''
        search_hd = win32gui.FindWindow(None,title)
        if not search_hd:
            return False
        hd = handle or search_hd
        left, top, right, bott = win32gui.GetWindowRect(hd)
        return (left,top,right,bott)
    def _pillow_pic(self,rect):
        '''
        根据位置截图，返回CV2的图像格式
        '''
        l,t,r,b = rect
        img = ImageGrab.grab(bbox=(l,t,r,b))
        return self._convert_pil_to_opencv(img)

    def _matchtemplate(self,img,template,threshold):
        '''
        param:img, type:cv2, 原图，截图得到
        param:template, type:cv2, 小图
        param:threshold, 阈值
        '''
        # win = self.get_window(title = WINDOW_TITLE)
        # if win:
        #     left,top,right,bott = win
        # else:
        #     print("get window error")
        #     return
        res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)
        loc = np.where(res>=threshold)
        for pt in zip(*loc[::-1]):
            return pt #匹配成功
        return None
    def do_skill(self,img):
        '''
        game_rect:游戏窗口位置
        扔鱼竿
        '''
        template = cv.imread(SKILL_DIR)
        pt = self._matchtemplate(img,template,SKILL_THRESHOLD)
        if pt:
            autopy.mouse.smooth_move(pt[0]+10, pt[1]+10)
            time.sleep(STEP_DELAY)
            autopy.mouse.click(autopy.mouse.Button.LEFT)
            time.sleep(STEP_DELAY)
            autopy.mouse.smooth_move(pt[0] -50, pt[1] - 50)
        else:
            print("寻找鱼竿失败")
            return False
        if DEBUG_IT:
            h,w = template.shape[:2]
            if pt:cv.rectangle(img, pt, (pt[0]+w,pt[1]+h), (0, 0, 255), 2)
            cv.imwrite('debug/do_skill_img.png',img)
            cv.imwrite('debug/do_skill_template.png',template)
        return True

    def find_float(self,game_rect):
        time.sleep(STEP_DELAY)
        img = self._convert_pil_to_opencv(ImageGrab.grab(game_rect))
        template = cv.imread(FLOAT_DIR)
        pt = self._matchtemplate(img,template,FLOAT_THRESHOLD)
        if pt:
            autopy.mouse.smooth_move(pt[0]+5,pt[1]+5)
        else:
            print('寻找鱼漂失败')
            return False
        if DEBUG_IT:
            h,w = template.shape[:2]
            if pt:cv.rectangle(img, pt, (pt[0]+w,pt[1]+h), (0, 0, 255), 2)
            cv.imwrite('debug/find_float_img.png',img)
            cv.imwrite('debug/find_float_template.png',template)
        return True


class recoding():
    BUFFER = 1024
    SAMPLING_RATE = 2000
    FISH_SHRESHOLD = 200 #大于这个值则有鱼
    def __init__(self):
        pass
    def recode(self, fish_time = 30, sample_interval = 0.3, start_delay=2,threshold = FISH_SHRESHOLD):
        '''
        param:fish_time,最大录音时间
        param:sample_interval,采样率检测间隔时间
        param:start_delay,运行前延时
        '''
        time.sleep(start_delay)
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=self.SAMPLING_RATE,
                input=True,
                frames_per_buffer=self.BUFFER)
        time_start = time.time()
        while True:
            time_end = time.time()
            dec = time_end-time_start
            if dec>fish_time:
                break
            stream_data = stream.read(self.BUFFER) 
            rms = audioop.rms(stream_data, 2)
            if DEBUG_IT: myprint(rms)
            if rms>=threshold:
                stream.stop_stream()
                stream.close()
                return True
            time.sleep(sample_interval)
        stream.stop_stream()
        stream.close()
        return False


def main():
    print('start...')
    time.sleep(GLOBAL_DELAY)
    gofish = gofishing()
    rec = recoding()
    game_rect = gofish._get_window(title=WINDOW_TITLE)
    if not game_rect:
        print('窗口未找到')
        return
    #截图
    img = gofish._convert_pil_to_opencv(ImageGrab.grab(game_rect))


    for x in range(FISH_REPEAT):
        time.sleep(GLOBAL_DELAY+2)
        #扔鱼竿
        ret = gofish.do_skill(img)
        if not ret:
            continue
        time.sleep(GLOBAL_DELAY)
        #找鱼漂
        ret = gofish.find_float(game_rect)
        if not ret :
            continue

        #延迟2s监听声音变化
        
        ret = rec.recode(threshold=AUDIO_THRESHOLD,sample_interval=0.5)
        if ret:
            print('[%s] Success...' % x)
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
        else:
            print("[%s] Failed..." % x)
            continue
    
main()