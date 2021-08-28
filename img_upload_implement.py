import requests
import cv2
import tkinter as tk
import numpy as np
import time
from PIL import ImageTk, Image


from pathlib import Path
import os

win = tk.Tk()

win.title("CamWatch")
win.geometry("920x640+50+50")
win.resizable(False, False)

lbl = tk.Label(win, text = "Video streaming through tkinter")
lbl.grid(row=0, column=0)

frm = tk.Frame(win, bg="white", width=720, height=480)
frm.grid(row=1, column=0)

lbl1 = tk.Label(frm)
lbl1.grid()
cap = cv2.VideoCapture(0)

def video_play():
    ret, frame = cap.read() # 프레임이 올바르게 읽히면 ret은 True
    if not ret:
        cap.release() # 작업 완료 후 해제
        return
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame) # Image 객체로 변환
    imgtk = ImageTk.PhotoImage(image=img) # ImageTk 객체로 변환


    # print(type(frame), type(img),type(imgtk))
    object = frame.tofile('file')

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    URL = 'http://127.0.0.1:8000/api_img/upload/'
    target = open(os.path.join(BASE_DIR, 'test.gif'), 'rb')
    print(type(target))

    data = {'remark': 'Geon-Ho'}
    upload = {'file': target}

    #response = requests.post(URL, data=data, files = upload)
    # print(response)
        
    # OpenCV 동영상
    lbl1.imgtk = imgtk
    lbl1.configure(image=imgtk)
    lbl1.after(10, video_play)

video_play()
win.mainloop() #GUI 시작