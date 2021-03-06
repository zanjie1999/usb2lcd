#/usr/bin/python

# Sparkle USB to LCD cpumen
# Written for PyUSB 1.0 (w/libusb 1.0.3)
# v2.0

import usb, sys  # 1.0 not 0.4
import time

import psutil

sys.path.append("..")

REQUEST_TYPE_SEND = usb.util.build_request_type(usb.util.CTRL_OUT,
                                                
usb.util.CTRL_TYPE_CLASS,
                                                
usb.util.CTRL_RECIPIENT_DEVICE)

REQUEST_TYPE_RECEIVE = usb.util.build_request_type(
    usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, 
usb.util.CTRL_RECIPIENT_DEVICE)

USBRQ_HID_GET_REPORT = 0x01
USBRQ_HID_SET_REPORT = 0x09
USB_HID_REPORT_TYPE_FEATURE = 0x03

class ArduinoUsbDevice(object):
    """
    """

    def __init__(self, idVendor, idProduct):
        """
        """
        self.idVendor = idVendor
        self.idProduct = idProduct

        # TODO: Make more compliant by checking serial number also.
        self.device = usb.core.find(idVendor=self.idVendor,
                                    idProduct=self.idProduct)

        if not self.device:
            raise Exception("Device not found")

    def write(self, byte):
        """
        """
        # TODO: Return bytes written?
        #print "Write:"+str(byte)
        self._transfer(REQUEST_TYPE_SEND, USBRQ_HID_SET_REPORT, byte,
                       [])  # ignored

    def read(self):
        """
        """
        response = self._transfer(
            REQUEST_TYPE_RECEIVE,
            USBRQ_HID_GET_REPORT,
            0,  # ignored
            1)  # length

        if not response:
            raise Exception("No Data")

        return response[0]

    def _transfer(self, request_type, request, index, value):
        """
        """
        return self.device.ctrl_transfer(
            request_type, request, (USB_HID_REPORT_TYPE_FEATURE << 8) | 
0,
            index, value)

def p(msg):
    sendSleep = 0.04
    # num = 0
    for c in msg:
        # num += 1
        # if (num > 16):
        #      theDevice.write(ord('\n'))
        #      num = 0
        #      time.sleep(sendSleep)
        theDevice.write(ord(c))
        # time.sleep(sendSleep)

def cpu_info():
    num = psutil.cpu_percent(0.5)
    cpu = '%.1f%%'% num
    return {
        'per':cpu,
        'num':num
    }
    # %.2f表示输出浮点数并保留两位小数。%%表示直接输出一个%。
def mem_info():
    mem = psutil.virtual_memory()
    mem_per ='%.1f%%'% mem[2]
    mem_total = '%.2fG'% (mem[0]/1024/1024/1024)
    mem_used = '%.2fG'% (mem[3]/1024/1024/1024)
    info = {                                    
        'mem_per':mem_per,
        'mem_total':mem_total,
        'mem_used':mem_used
    }
    return info
def disk_info():
    c = psutil.disk_usage('c:')
    d = psutil.disk_usage('d:')
    e = psutil.disk_usage('e:')
    f = psutil.disk_usage('f:')
    c_per = '%.2f%%'% c[3]
    d_per = '%.2f%%'% d[3]
    e_per = '%.2f%%'% e[3]
    f_per = '%.2f%%'% f[3]
    info = {
        'c_per': c_per,
        'd_per': d_per,
        'e_per': e_per,
        'f_per': f_per,
    }
    return info

last_sent = 0
last_recv = 0
def network_info(s=1):
    global last_sent,last_recv
    network = psutil.net_io_counters()
    network_sent = '%.3f'% ((network[0] - last_sent)/1024/1024/s)
    network_recv = '%.3f'% ((network[1] - last_recv)/1024/1024/s)
    last_sent = network[0]
    last_recv = network[1]
    info = {
        'network_sent':network_sent,
        'network_recv':network_recv
    }
    return info


if __name__ == "__main__":
    t = True
    while True:
        try:
            theDevice = ArduinoUsbDevice(idVendor=0x16c0, idProduct=0x05df)
            led = False
            p("¬")
            while True:
                cpu = cpu_info()
                # if cpu['num'] >= 70 and not led:
                #     p("¬")
                #     led = True
                # elif cpu['num'] < 70 and led:
                #     p("¬")
                #     led = False
                if t:
                    p("U:")
                    p(cpu['per'].ljust(6))
                else:
                    p(time.strftime("%I:%M:%S", time.localtime()))
                # p(mem_info()["mem_per"].ljust(6))
                if t:
                    net = network_info(0.7)
                    p(("^:" + net["network_sent"]).rjust(8))
                    p(("M:" + mem_info()["mem_used"]).ljust(8))
                    p(("v:" + net["network_recv"]).rjust(8))
                else:
                    p(("M:" + mem_info()["mem_used"]).rjust(8))
                    p("[")
                    p(('=' * int(cpu['num'] * 0.14)).ljust(14))
                    p("]")
                p("\r")

                btm = False
                try:
                    while True:
                        theDevice.read()
                        btm = True
                except:
                    pass
                if btm:
                    t = not t
        except Exception as e:
            print(e)
        time.sleep(5)

