import socket
import time
from robot import Robot
import kivy
from operator import itemgetter
from kivy.config import Config
Config.set('graphics', 'resizable', False)
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from functools import partial
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.progressbar import ProgressBar
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

import re


class MyGrid(FloatLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.connected = False
        self.r1 = None

    connected = ObjectProperty(None)
    battery_property = NumericProperty(0)
    s1_property = NumericProperty(0)
    s2_property = NumericProperty(0)
    s3_property = NumericProperty(0)
    s4_property = NumericProperty(0)
    s5_property = NumericProperty(0)
    left_motor = NumericProperty(0)
    right_motor = NumericProperty(0)
    number_property = NumericProperty(0)
    led_off = ObjectProperty(None)
    led_red = ObjectProperty(None)
    led_green = ObjectProperty(None)
    msg_out_property = StringProperty('')
    msg_in_property = StringProperty('')
    following = ObjectProperty(False)
    index_property = NumericProperty(0)
    diff = 0
    max_diff = 0

    def submit(self, *args):
        if self.connected:
            try:
                left_input = int(self.ids.left_input.text)
                right_input = int(self.ids.right_input.text)
            except ValueError:
                self.create_popup("Błędna prędkość silnika.")
                return -1

            lu = self.r1.update_left(left_input)
            ru = self.r1.update_right(right_input)

            if lu == -1 or ru == -1:
                self.create_popup("Błędna prędkość silnika.")
                return -1

            led = 0
            if self.ids.led_green.active:
                led += 1
            if self.ids.led_red.active:
                led += 2

            self.r1.update_led(led)
            self.r1.update_message()
        else:
            self.create_popup("Należy najpierw połączyć się z robotem.")

    def submit_manual(self, *args):
        if self.connected:
            frame = self.ids.frame.text.lower()
            m = re.search(r"^\[0[0-3][0-9a-f]{4}\]$", frame)
            if m is not None:
                led = int(frame[2])
                left = int(frame[3:5], 16)
                right = int(frame[5:7], 16)

                if left > 127:
                    left -= 256
                if right > 127:
                    right -= 256

                self.r1.update_led(led)
                self.r1.update_left(left)
                self.r1.update_right(right)
                self.r1.update_message()
            else:
                self.create_popup("Błędna ramka.")
        else:
            self.create_popup("Należy najpierw połączyć się z robotem.")

    def follow(self):
        if self.connected:
            speed = 15
            self.following = True
            self.diff = 0
            self.r1.update_left(speed)
            self.r1.update_right(speed)
            self.r1.update_message()
            self.max_diff = speed
        else:
            self.create_popup("Należy najpierw połączyć się z robotem.")

    def stop_following(self):
        self.following = False

    def update(self, dt):

        if self.connected:
            self.r1.send()
            self.r1.receive()
            self.battery_property = self.r1.battery
            self.s1_property = self.r1.sensor1
            self.s2_property = self.r1.sensor2
            self.s3_property = self.r1.sensor3
            self.s4_property = self.r1.sensor4
            self.s5_property = self.r1.sensor5
            self.number_property = self.r1.number
            self.msg_out_property = self.r1.msg_out
            self.msg_in_property = self.r1.msg_in
            self.left_motor = self.r1.left
            self.right_motor = self.r1.right

            if self.following:
                a = [self.r1.sensor3, self.r1.sensor1, self.r1.sensor2, self.r1.sensor4, self.r1.sensor5]

                # index = min(enumerate(avg), key=itemgetter(1))[0]
                # self.index_property = index

                # if index == 0:
                #     self.r1.update_left(15)
                #     self.r1.update_right(15)
                # elif index == 1:
                #     self.r1.update_left(0)
                #     self.r1.update_right(20)
                # elif index == 2:
                #     self.r1.update_left(5)
                #     self.r1.update_right(15)
                # elif index == 3:
                #     self.r1.update_left(15)
                #     self.r1.update_right(5)
                # elif index == 4:
                #     self.r1.update_left(20)
                #     self.r1.update_right(0)

                suma = -2 * a[1] - a[2] + a[3] + 2 * a[4]
                zmapowana = self.mapowanie(suma)
                print(suma, zmapowana)

                if suma < -10000 and self.diff < self.max_diff:
                    self.diff -= 2
                if suma > 10000 and self.diff > -self.max_diff:
                    self.diff += 2
                if suma < -50000:
                    self.diff = -self.max_diff
                if suma > 50000:
                    self.diff = self.max_diff
                if -10000 < suma < 10000 or self.r1.sensor3 < 20000:
                    self.diff = 0

                self.r1.update_left(self.max_diff - self.diff)
                self.r1.update_right(self.max_diff + self.diff)
                self.r1.update_message()

    def create_connection(self, *args):
        try:
            robot_number = int(self.ids.robot_number_input.text)
        except ValueError:
            self.create_popup("Niepoprawny numer robota.")
            return -1

        self.r1 = Robot(number=robot_number, debug=False)
        c = self.r1.connect()

        if c == -1:
            self.create_popup("Nie udało się nawiązać połączenia.")
            return -1
        self.connected = True

    @staticmethod
    def mapowanie(value):
        return int(20 * value / (2 * 53255))

  
    def disconnect(self, *args):
        self.r1.disconnect()
        self.r1 = None
        self.connected = False
        self.number_property = 0
        self.battery_property = 0
        self.s1_property = 0
        self.s2_property = 0
        self.s3_property = 0
        self.s4_property = 0
        self.s5_property = 0

    def create_popup(self, text):
        layout = GridLayout(cols=1, padding=10, size_hint=(0.5, 1))

        popupLabel = Label(text=text)
        closeButton = Button(text="Zamknij", size_hint=(0.03, 0.03))

        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)
        popup = Popup(title='Błąd',
                      content=layout,
                      size_hint=(0.6, 0.5))
        popup.open()
        closeButton.bind(on_press=popup.dismiss)


class MyApp(App):
    def build(self):
        grid = MyGrid()
        Clock.schedule_interval(grid.update, 1.0 / 30.0)
        return grid


MyApp().run()
