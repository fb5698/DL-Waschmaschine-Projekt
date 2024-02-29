from machine import Pin, I2C, Timer
from imu import MPU6050
import time
import network
import machine
import socket
import uio
import os, time

ssid = 'FRITZ!Box 7530 TU' #Wlan Name eingeben
pwd = '88083193306802660053' #Wlan passwort eingeben
device_name = 'ESP8266'

accel_data = []

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, pwd) # Eigene Wlan Daten nochmal eingeben
time.sleep(3)
if sta_if.isconnected():
    print("Erfolgreich mit dem Wlan verbunden.")
else:
    print("Es konnte keine Verbindung zum Wlan hergestellt werden.")
print(sta_if.ifconfig())

DataCounter = 0
imuReadingsAccel = []
imuReadingsGyro = []
led = machine.Pin(2, machine.Pin.OUT)

BUFFER_SIZE = 1024

udp_server = '192.168.178.21'
udp_port = 8800

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
mpu6050 = MPU6050(i2c)
accel = mpu6050.accel
gyro = mpu6050.gyro

tim = machine.Timer(-1)

def read_imu(tim):
   global DataCounter, led

   led.off()
   accel = mpu6050.accel
   dt = machine.RTC().datetime()

   s = '{0:3.5f},{1:3.5f},{2:3.5f}'.format(accel.x, accel.y, accel.z)
   
   serverAddress = (udp_server, udp_port)
   bufferSize = 1024

   UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   msgFromClient = str.encode(s)
   UDPClientSocket.sendto(msgFromClient, serverAddress)
   msgFromServer = UDPClientSocket.recvfrom(bufferSize)
   msg = "Message from Server: {}".format(msgFromServer[0].decode())
   print(msg)

   DataCounter += 1

   accel_data.append((accel.x, accel.y, accel.z))


tim.init(period=5, mode=machine.Timer.PERIODIC, callback=read_imu)

print("Acquiring Data...")


active = True

while active:
    led.on()

    if DataCounter >= 400:
        print("Acquiring finished.")
        active = False
        tim.deinit()
        with open('Zustand X.csv', 'w') as data_file: #JE NACH ZUSTAND ANPASSEN
            data_file.write('  A_X,   A_Y,   A_Z\n')
            for data_point in accel_data:
                data_file.write('{:f},{:f},{:f}\n'.format(data_point[0], data_point[1], data_point[2]))
            print("Data saved.")

led.on()

print("\nReady for Acquiring.")
