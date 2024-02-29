from machine import Pin, I2C, Timer
from imu import MPU6050
import time
import network
import machine
import utime
from umqtt.simple import MQTTClient
import usocket as socket
import socket
import uio
#import pymongo


ssid = 'FRITZ!Box 7530 TU'
pwd = '88083193306802660053'
device_name = 'TEST'

accel_data = []

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('FRITZ!Box 7530 TU', '88083193306802660053')
time.sleep(2)
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
tcp_server = '192.168.178.21'
tcp_port = 8000

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

    s = '{0:3.5f},{1:3.5f},{2:3.5f}\n'.format(accel.x, accel.y, accel.z)

    s_socket = socket.socket()
    addrinfos = socket.getaddrinfo(tcp_server, tcp_port)
    s_socket.connect(addrinfos[0][4])
    s_socket.send(s.encode())
    s_socket.close()
    
    DataCounter += 1

    accel_data.append((accel.x, accel.y, accel.z))


tim.init(period=250, mode=machine.Timer.PERIODIC, callback=read_imu)

print("Acquiring Data...")

active = True

while active:
    led.on()

    if DataCounter >= 50:
        print("Acquiring finished.")
        active = False
        tim.deinit()
        with open('imu.csv', 'w') as data_file:
            data_file.write('  A_X,   A_Y,   A_Z\n')
            for data_point in accel_data:
                data_file.write('{:6.2f},{:6.2f},{:6.2f}\n'.format(data_point[0], data_point[1], data_point[2]))
            print("Data saved.")

led.on()

print("\nReady for Acquiring.")

client = MongoClient("localhost:27017")
db = client.manufacture

