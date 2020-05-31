import socket
import random
import time
import math

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 9999))
s.listen(1)
while True:
    clientsocket, adress = s.accept()
    print(f'Connection from {adress} has been established.')
    while clientsocket.recv(8):
        status = 3
        battery = 60000  # + random.randint(-100, 100)
        sensor1 = int(20000 * math.sin(1 + time.time())) + 20000  # + random.randint(-30, 30)
        sensor2 = int(2000 * math.sin(2 + time.time())) + 2000  # + random.randint(-30, 30)
        sensor3 = int(3000 * math.sin(3 + time.time())) + 3000  # + random.randint(-30, 30)
        sensor4 = int(4000 * math.sin(4 + time.time())) + 4000  # + random.randint(-30, 30)
        sensor5 = int(5000 * math.sin(5 + time.time())) + 5000  # + random.randint(-30, 30)

        status = format(status, '02x')
        battery = format(battery, '04x')
        sensor1 = format(sensor1, '04x')
        sensor2 = format(sensor2, '04x')
        sensor3 = format(sensor3, '04x')
        sensor4 = format(sensor4, '04x')
        sensor5 = format(sensor5, '04x')
        msg = ('[' + status + battery + sensor1 + sensor2 +
               sensor3 + sensor4 + sensor5 + ']')
        clientsocket.send(msg.encode())
    clientsocket.close()
    print(f'Socket closed.')
