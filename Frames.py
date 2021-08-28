import tkinter as tk
import requests
import cv2
from PIL import ImageTk, Image
from pathlib import Path
import os

from controller import Controller


DEV_PATH_ARDUINO_LINUX  = '/dev/ttyUSB0'
DEV_PATH_ARDUINO_WIN    = 'COM4'

MS_PASS_TO_RESTORE      = 2000
MS_RESTORE_TO_QR        = 2000
MS_HTTP_REQUEST_INTERVAL = 1000

NUM_VIDEO_CAP           = 50
NUM_HTTP_RETRY          = 10

URL_SERVER_REQ          = 'http://127.0.0.1:8000/api_img/state/'
URL_SERVER_CLOSE        = 'http://127.0.0.1:8000/api_img/close/'
URL_SERVER_UPLOAD       = 'http://127.0.0.1:8000/api_img/upload/'

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.controller = Controller(DEV_PATH_ARDUINO_LINUX)

        self.switch_frame(Frame_restore)

    def switch_frame(self, frame_class):
        frame_new = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()

        self._frame = frame_new
        self._frame.pack()


class Frame_qr(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        tk.Label(self, text="Please scan Qr", font=
                 ('Helvetica', 24)).pack()

        self.bind('<Key>', self.handler_qr)
        self.focus_set()

        master.controller.update('RelayOnMotorOff')

        self.list_qr = []
        self.str_qr = tk.StringVar()
        tk.Label(self, textvariable=self.str_qr, font=
                 ('Helvetica', 12)).pack(side="bottom")


    def handler_qr(self, event):
        c = event.char
        if c == '\r':
            temp_str = ''.join(self.list_qr)
            self.str_qr.set(temp_str)
            self.list_qr = []

            print(temp_str + ' logged in')
            self.master.after(MS_RESTORE_TO_QR, self.master.switch_frame, Frame_wait)
        else:
            self.list_qr.append(c)


class Frame_wait(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        tk.Label(self, text="Wait until captured", font=
                 ('Helvetica', 20)).pack(side="top")

        self.win_cap = tk.Label(self)
        self.win_cap.pack(side="top")
        print(type(self.win_cap))

        self.str_info = tk.StringVar()
        tk.Label(self, textvariable=self.str_info, font=
                 ('Helvetica', 20)).pack(side="bottom")
        self.str_info.set("Capturing.....")
        
        '''
        tk.Button(self, text="Scan bottle", command=
                  lambda: master.switch_frame(Frame_pass)).pack(side="bottom")
        '''

        self.cap = cv2.VideoCapture(0)
        self.video_play(NUM_VIDEO_CAP)

    def handler_http(self, num_retry):
        if num_retry == 0:
            self.master.switch_frame(Frame_qr)
            return

        r = requests.get(URL_SERVER_REQ)
        if r.status_code == 200:
            r = requests.get(URL_SERVER_CLOSE)
            print('http ok')
            self.master.switch_frame(Frame_pass)
        else:
            print('http failed retry remain : %d' % num_retry)
            self.after(MS_HTTP_REQUEST_INTERVAL, self.handler_http, num_retry-1)

    def video_play(self, num):        
        ret, image = self.cap.read()

        if not ret:
            self.cap.release()
            return

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(image)

        if num == 0:
            cv2.imwrite('__tmp_img.jpg', image)
            BASE_DIR = Path(__file__).resolve().parent
            target = open(os.path.join(BASE_DIR, '__tmp_img.jpg'), 'rb')

            data = {'remark': 'jetson'}
            upload = {'file': target}

            response = requests.post(URL_SERVER_UPLOAD, data=data, files = upload)
            print(response)

            self.cap.release()

            if response.status_code == 201:
                self.str_info.set("Captured!")
                self.after(MS_HTTP_REQUEST_INTERVAL, self.handler_http, NUM_HTTP_RETRY)
            else:
                self.str_info.set("Server Error!")
            return

        imgtk = ImageTk.PhotoImage(image=img)

        self.win_cap.imgtk = imgtk
        self.win_cap.configure(image=imgtk)
        self.after(10, self.video_play, num-1)

class Frame_pass(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Video passed", font=
                 ('Helvetica', 28)).pack()

        self.timer = MS_PASS_TO_RESTORE
        self.str_timer = tk.StringVar()
        self.str_timer.set("%d sec remain" % (self.timer / 1000))

        tk.Label(self, textvariable=self.str_timer, font=
                 ('Helvetica', 12)).pack(side="bottom")

        master.controller.update('RelayOffMotorOn')
        self.update_clock()
        self.master.after(MS_PASS_TO_RESTORE, self.master.switch_frame, Frame_restore)

    def update_clock(self):
        if self.timer > 999:
            self.timer -= 1000
            self.str_timer.set("%d sec remain" % (self.timer / 1000))
            self.after(1000, self.update_clock)
            

class Frame_restore(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        tk.Label(self, text="Restoring", font=
                 ('Helvetica', 28, "bold")).pack()

        self.timer = MS_RESTORE_TO_QR
        self.str_timer = tk.StringVar()
        self.str_timer.set("%d sec remain" % (self.timer / 1000))

        tk.Label(self, textvariable=self.str_timer, font=
                 ('Helvetica', 20)).pack(side="bottom")

        master.controller.update('RelayOffMotorOff')
        self.update_clock()
        self.master.after(MS_RESTORE_TO_QR, self.master.switch_frame, Frame_qr)

    def update_clock(self):
        if self.timer > 999:
            self.timer -= 1000
            self.str_timer.set("%d sec remain" % (self.timer / 1000))
            self.after(1000, self.update_clock)



if __name__ == "__main__":
    root = Application()
    root.title("Brave guys")
    root.geometry("1280x800")
    root.mainloop()
