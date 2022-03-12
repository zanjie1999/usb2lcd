# coding=utf-8

# 在pve虚拟化路由器上的lcd2usb设备 
# Sparkle 20220125
# v1.0

# 装依赖 python3 -m pip install pyusb

import usb, os, subprocess
import time
import timeout_decorator

# 远程端 openwrt ssh 命令
sshOpCmd = "ssh -T root@op"
# 显示网速的网卡名字
netCardName = "ppp"
# 两张网卡的名字用|分隔 不用这功能就留空
netCardName2 = "eth3|eth4"

# 刷新间隔 秒
delay = 3

sshConn = None
bashConn = None
lastCpu = ['0','0']
lastNet = ['0','0','0','0']


REQUEST_TYPE_SEND = usb.util.build_request_type(usb.util.CTRL_OUT,usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_DEVICE)
REQUEST_TYPE_RECEIVE = usb.util.build_request_type(usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_DEVICE)
USBRQ_HID_GET_REPORT = 0x01
USBRQ_HID_SET_REPORT = 0x09
USB_HID_REPORT_TYPE_FEATURE = 0x03

class ArduinoUsbDevice(object):
    def __init__(self, idVendor, idProduct):
        self.idVendor = idVendor
        self.idProduct = idProduct
        # TODO: Make more compliant by checking serial number also.
        self.device = usb.core.find(idVendor=self.idVendor,
                                    idProduct=self.idProduct)
        if not self.device:
            raise Exception("Device not found")

    def write(self, byte):
        # TODO: Return bytes written?
        #print "Write:"+str(byte)
        self._transfer(REQUEST_TYPE_SEND, USBRQ_HID_SET_REPORT, byte,
                       [])  # ignored

    def read(self):
        response = self._transfer(
            REQUEST_TYPE_RECEIVE,
            USBRQ_HID_GET_REPORT,
            0,  # ignored
            1)  # length
        if not response:
            raise Exception("No Data")
        return response[0]

    def _transfer(self, request_type, request, index, value):
        return self.device.ctrl_transfer(request_type, request, (USB_HID_REPORT_TYPE_FEATURE << 8) | 0, index, value)

def p(msg):
    for c in msg:
        theDevice.write(ord(c))

@timeout_decorator.timeout(5)
def ssh(cmd):
    global sshConn
    sshConn.stdin.write(cmd+"\n")
    sshConn.stdin.flush()
    time.sleep(0.01)
    return os.read(sshConn.stdout.fileno(), 10240).decode()[:-1]

@timeout_decorator.timeout(5)
def bash(cmd):
    global bashConn
    bashConn.stdin.write(cmd+"\n")
    bashConn.stdin.flush()
    time.sleep(0.01)
    return os.read(bashConn.stdout.fileno(), 10240).decode()[:-1]

def cpuPercent():
    global lastCpu
    now = bash("awk '/cpu /{print $2+$4,$2+$4+$5}' /proc/stat").split(' ')
    percent = (float(now[0]) - float(lastCpu[0])) / (float(now[1]) - float(lastCpu[1])) * 100
    lastCpu[0] = now[0]
    lastCpu[1] = now[1]
    return percent

def netSpeed():
    global lastNet
    now = ssh("awk '/" + netCardName + "/{print $2,$10}' /proc/net/dev").split(' ')
    speed = [(float(now[0]) - float(lastNet[2])) / 1024 / 1024, (float(now[1]) - float(lastNet[3])) / 1024 / 1024]
    lastNet[2] = now[0]
    lastNet[3] = now[1]
    return speed

def netSpeed2():
    global lastNet
    now = ssh("awk '/" + netCardName2 + "/{printf $2\" \"$10\" \"}' /proc/net/dev").split(' ')
    speed = [(float(now[0]) - float(lastNet[0])) / 1024 / 1024, (float(now[1]) - float(lastNet[1])) / 1024 / 1024, (float(now[2]) - float(lastNet[2])) / 1024 / 1024, (float(now[3]) - float(lastNet[3])) / 1024 / 1024]
    lastNet[0] = now[0]
    lastNet[1] = now[1]
    lastNet[2] = now[2]
    lastNet[3] = now[3]
    return speed

def cpuTemp():
    return float(bash("cat /sys/class/thermal/thermal_zone1/temp")) / 1000

def memUse():
    return bash("free|awk '/M/{print $3/1024/1024}'")

def loadavg():
    return bash("awk '{print $1}' /proc/loadavg")

if __name__ == "__main__":
    t = 2 if bool(netCardName2) else 1
    while True:
        try:
            theDevice = ArduinoUsbDevice(idVendor=0x16c0, idProduct=0x05df)
            if bashConn:
                bashConn.terminate()
            if sshConn:
                sshConn.terminate()
            bashConn = subprocess.Popen('bash', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            sshConn = subprocess.Popen(sshOpCmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            p("¬")
            while True:
                cpu = cpuPercent()
                temp = cpuTemp()
                if t==1:
                    net = netSpeed()
                    p("U:" + str(cpu)[:5] + '% ')
                    p("^" + str(net[1] / delay)[:6])
                    p(str(temp)[:2] + "c ")
                    p(memUse()[:3] + "G")
                    p(" v" + str(net[0] / delay)[:6])
                elif t==2:
                    net = netSpeed2()
                    p(str(net[0] / delay)[:4])
                    p('^')
                    p(str(net[3] / delay)[:4])
                    p(' ')
                    p(str(temp)[:2])
                    p('c')
                    p(loadavg()[:3])
                    p(str(net[1] / delay)[:4])
                    p('v')
                    p(str(net[2] / delay)[:5])
                    p(' ')
                    p(str(cpu)[:4])
                    p('%')

                elif t==3:
                    p(time.strftime("%I:%M:%S ", time.localtime()))
                    p(memUse()[:3] + "G ")
                    p(str(temp)[:2])
                    p("[")
                    p(('=' * int(cpu * 0.14)).ljust(14))
                    p("]")

                p("\r")

                # 刷新需要时间
                time.sleep(0.75 + delay -1 if t!=3 else 0.77)

                # 按键切换
                btm = False
                try:
                    while True:
                        theDevice.read()
                        btm = True
                except:
                    pass
                if btm:
                    if t == 3:
                        t=1
                    elif bool(netCardName2):
                        t+=1
                    else:
                        t=3
                
        except Exception as e:
            print(e)
            time.sleep(10)

