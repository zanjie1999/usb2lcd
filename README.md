# Sparkle USB2LCD (LCD2USB)
Use ATiny85 and LCD1602(Hitachi HD44780) to make a USB2LCD.

Hardware connection image from internet:
![digispark lcd](https://2.bp.blogspot.com/-yOUKKzuKXCk/XCSd8b4-yYI/AAAAAAAAAZU/Ruroqbyzi7UY-M_L1n_TxDsxwBgJ1yHjgCLcBGAs/s1600/Digispark%2B%252B%2BLCD_bb.jpg)

need Python3:

`python3 -m pip install psutil pyusb`

[中文直达](https://space.bilibili.com/9992930/search/video?keyword=USB2LCD)

----------

## How to use
1. Flash `SparkleUSB2LCD.ino` to your ATiny85 with Arduino
2. Choose a program below to use

### Windows or macOS `cpumen.py`
Windows need to install Python3, and  
`python3 -m pip install psutil pyusb`

### Proxmox Virtual Environment (PVE) `pve.py`
install `python3`  
add your pve ssh key to openwrt  
edit file to config

### Openwrt `op.py`
install `python3` and `python3-pip`  
edit file to config, if you use ash, you need change 'bash' to 'ash'

#### If you use Openwrt with `opShell.py`  
edit `/usr/bin/service`
and `chmod +x /usr/bin/service`
```
#!/bin/sh
/etc/init.d/$1 $2
echo $2 $?
```
then you can run `/etc/init.d/network restart` as `service network restart`  
or you can run `/etc/init.d/network restart` as `echo restart|xargs /etc/init.d/network && echo Restart OK` on Openwrt

## font ascii for lcd
![image](https://user-images.githubusercontent.com/16502567/211736311-3740431e-bba9-4aca-b979-d2e0f4fafdb8.png)  
such as "right arrow" font is `00011110`  
then you can use `chr(0b00011110)` or `'\x1e'` in program, the "right arrow" will print to screen
