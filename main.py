import win32api, win32gui, win32con, time, threading, ctypes.wintypes, os
from pynput.mouse import Button, Controller
from pynput import mouse, keyboard
import configparser

var = 1
dd = 0
dx = 0
dy = 0
dbutton = 0
ddy = 0
dkey = 0
threads = []
applist=[]         # 存储ini里app的名称
listlen=0      # app变量的个数
EXIT = False
pause=0

user32 = ctypes.windll.user32
pmouse = Controller()
threadLock = threading.Lock()
cf = configparser.ConfigParser()
cf.read("C:\Python\project\screen\screen.ini")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

secs = cf.sections()  # 获取文件中所有的section(一个配置文件中可以有多个配置，如数据库相关的配置，邮箱相关的配置，
                        # 每个section由[]包裹，即[section])，并以列表的形式返回
items = cf.items("app")  # 获取section名为app所对应的全部键值,如1=222，显示2
dtime =cf.getint("sleeptime","time")

applist=[]
for i in items:
    applist+=[i[1]]   #app.find("Word") == bi

listlen=len(applist) #获取列表数量

#######################################################################
def on_move(x, y):
    global dx, dy
    threadLock.acquire()
    dx, dy = x, y
    threadLock.release()
#     获取鼠标的坐标值

def on_click(x, y, button, pressed):
    # print('{0} at {1}'.format(
    #     'Pressed' if pressed else 'Released',
    #     (x, y)))
    global dbutton
    threadLock.acquire()
    dbutton = 1
    threadLock.release()
    # button显示哪个按钮被按下，eg:Button.left Button.right


def on_scroll(x, y, dx, dy):
    # print('Scrolled {0} at {1}'.format(
    #     'down' if dy < 0 else 'up',
    #     (x, y)))
    global ddy
    threadLock.acquire()
    ddy = 1
    threadLock.release()
    # dy等于0时，没有滚动滚轮


def on_press(key):
    global dkey
    threadLock.acquire()
    dkey = 1
    threadLock.release()
#     当有键盘输入是，dkey全局变量等于1

# # 监听键盘按键
def start_keylisten():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# 停止监听,或者在回调中返回False


# Collect events until released
def start_mouselisten():
    print("program start")
    with mouse.Listener(
            on_move=on_move, on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()


def screen():
    time.sleep(8)
#     避免已启动就打开屏保
    while var == 1:
        hwnd = win32gui.GetForegroundWindow()
        app = win32gui.GetWindowText(hwnd)
        global dx, dy, dbutton, ddy, dkey
        pdx = dx
        pdy = dy
        pdbutton = dbutton
        pddy = ddy
        pdkey = dkey
        # 先将获取的输入状态存到一个局部变量
        threadLock.acquire()
        dx = 0
        dy = 0
        dbutton = 0
        ddy = 0
        dkey = 0
        threadLock.release()

        bi=0
        for i in applist:
                bi+=app.find(i) 
        print(bi+listlen)       
        if bi+listlen == 0:         #如果找到一个程序，那么bi+listlen应该不等于0
            x1, y1 = pmouse.position
            # 此处获取鼠标坐标的目的是为了屏保启动后，将进程锁定在一个循环里，而不反复启动屏保
            if pdx == 0 and pdy == 0 and pdbutton == 0 and pddy == 0 and pdkey == 0:
                win32api.ShellExecute(0, 'open',
                                      r'Mystify.scr',
                                      '', '', 1)
                print("show time")
                x2, y2 = pmouse.position
                while x1 == x2 and y1 == y2 and ddy == 0 and dbutton == 0 and dkey == 0:
                    x2, y2 = pmouse.position
                    # 加入dkey主要是解决只敲键盘退出屏保以后，无法退出while循环的问题
                print("it's my show")
        time.sleep(dtime)
        
class Hotkey(threading.Thread):  #创建一个Thread.threading的扩展类  
   
    def run(self):  
        global EXIT  #定义全局变量，这个可以在不同线程见共用。  
        # user32 = ctypes.windll.user32  #加载user32.dll  
        if not user32.RegisterHotKey(None, 99, win32con.MOD_ALT, win32con.VK_F3):   # 注册快捷键 alt + f3 并判断是否成功。
            raise        # 返回一个错误信息  
    #以下为判断快捷键冲突，释放快捷键  
        try:  
            msg = ctypes.wintypes.MSG()  
            #print msg  
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:  
                if msg.message == win32con.WM_HOTKEY:  
                    if msg.wParam == 99:  
                        ctypes.windll.user32.MessageBoxW(0, u"已退出", u"程序已经退出",0) 
                        EXIT = True  
                        os._exit(0)
                        return  
                user32.TranslateMessage(ctypes.byref(msg))  
                user32.DispatchMessageA(ctypes.byref(msg))  
        finally:  
            user32.UnregisterHotKey(None, 1)  

t1 = threading.Thread(target=start_mouselisten)
threads.append(t1)
t2 = threading.Thread(target=start_keylisten)
threads.append(t2)
t3 = threading.Thread(target=screen)
threads.append(t3)
threads.append(Hotkey())

if __name__ == "__main__":
    for t in threads:
        t.start()
