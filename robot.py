import socket


class Robot():

    def __init__(self, number=33, debug=False):
        self.number = number
        self.left = 0
        self.right = 0
        self.led = 0
        self.msg_out = '[000000]'
        self.msg_in = ''
        if not debug:
            self.ip = "192.168.2." + str(self.number)
            self.port = 8000
        else:
            self.ip = 'localhost'
            self.port = 9999

    @staticmethod
    def convert_speed(x):
        if x < 0:
            x = 256 + x

        return x

    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.ip, self.port))
        except OSError:
            return -1

    def disconnect(self):
        self.msg_out = '[000000]'
        self.s.send(self.msg_out.encode())
        self.s.close()

    def update_left(self, left):
        if -128 <= left <= 127:
            self.left = left
            return 0
        else:
            return -1

    def update_right(self, right):
        if -128 <= right <= 127:
            self.right = right
            return 0
        else:
            return -1

    def update_led(self, led):
        if led == 'off' or led == 0:
            self.led = 0
        elif led == 'green' or led == 'g' or led == 1:
            self.led = 1
        elif led == 'red' or led == 'r' or led == 2:
            self.led = 2
        elif led == 3:
            self.led = 3
        else:
            pass

    def update_message(self):
        left = self.convert_speed(self.left)
        right = self.convert_speed(self.right)
        left = format(left, '02x')
        right = format(right, '02x')
        led = format(self.led, '02x')
        self.msg_out = '[' + led + left + right + ']'

    def send(self):
        self.update_message()
        self.s.send(self.msg_out.encode())

    def receive(self):
        msg = self.s.recv(28).decode('ascii')
        self.msg_in = msg
        self.status = int(msg[1:3], 16)
        self.battery = int(msg[3:7], 16)
        self.sensor1 = int(msg[7:11], 16)
        self.sensor2 = int(msg[11:15], 16)
        self.sensor3 = int(msg[15:19], 16)
        self.sensor4 = int(msg[19:23], 16)
        self.sensor5 = int(msg[23:27], 16)
