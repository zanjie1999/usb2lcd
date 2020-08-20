
# 咩时间
# 系统监视器
# Sparkle v1.0

import socket,time
import psutil

s = None

def p(msg):
    s.send(bytes(msg.encode('utf-8')))

def cpu_info():
    num = psutil.cpu_percent(1)
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
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("192.168.102.16", 50803))
            print("connect ok")
            while True:
                p("CPU:")
                p(cpu_info()['per'].ljust(7))
                p("内存:")
                p(mem_info()["mem_used"].ljust(7))
                sp = network_info(1)
                if sp["network_sent"] > sp["network_recv"]:
                    p("↑")
                    p(sp["network_sent"])
                else:
                    p("↓")
                    p(sp["network_recv"])
                p("M/s")
                p("\n")
                if s.recv(10) != b'ok\n':
                    break
            s.close()
            print("connect close")
        except Exception as e:
            pass
        time.sleep(5)