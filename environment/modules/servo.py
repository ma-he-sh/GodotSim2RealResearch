from gpiozero import Servo, AngularServo
from time import sleep
from modules.logs import Logs
import math
from gpiozero.pins.pigpio import PiGPIOFactory

pigpio_factory = PiGPIOFactory()

class DriveGimbal:
    XServo = None
    YServo = None
    ZServo = None
    Xpwm = None
    Ypwm = None
    Zpwm = None
    min_angle = 0.0
    max_angle = 0.0
    min_pulse_width = 0.0
    max_pulse_width = 0.0

    min_range = 0.0
    mid_range = 0.0
    max_range = 0.0

    axisX = 'X'
    axisY = 'Y'
    axisZ = 'Z'

    def __init__(self, config={}):
        self.config = config
        self.logs = Logs('drivegimbal')

    def init(self):
        self.logs.set('initializing')
        fieldsRequired = ['x_pwm', 'y_pwm', 'z_pwm', 'min_angle', 'max_angle', 'min_pulse', 'max_pulse', 'min_range',
                          'max_range']
        for key in fieldsRequired:
            if self.config[key] is None:
                raise ValueError(key + ' Not defined')

        self.XServo = AngularServo(self.config['x_pwm'], min_angle=self.config['min_angle'],
                                   max_angle=self.config['max_angle'], min_pulse_width=self.config['min_pulse'],
                                   max_pulse_width=self.config['max_pulse'], pin_factory=pigpio_factory)
        self.YServo = AngularServo(self.config['y_pwm'], min_angle=self.config['min_angle'],
                                   max_angle=self.config['max_angle'], min_pulse_width=self.config['min_pulse'],
                                   max_pulse_width=self.config['max_pulse'], pin_factory=pigpio_factory)
        self.ZServo = AngularServo(self.config['z_pwm'], min_angle=self.config['min_angle'],
                                   max_angle=self.config['max_angle'], min_pulse_width=self.config['min_pulse'],
                                   max_pulse_width=self.config['max_pulse'], pin_factory=pigpio_factory)

        self.min_range = self.config['min_range']
        self.max_range = self.config['max_range']
        self.mid_range = (self.max_range - self.min_range) / 2.0

    def drive(self, XAngle, YAngle, ZAngle, time=2):
        print(XAngle, YAngle, ZAngle)
        self.XServo.angle = XAngle
        self.YServo.angle = YAngle
        self.ZServo.angle = ZAngle
        sleep(time)

    def move(self, axis, pos, time=2):
        driver = None
        if axis == self.axisX:
            driver = self.XServo
        elif axis == self.axisY:
            driver = self.YServo
        elif axis == self.axisZ:
            driver = self.ZServo

        driver.angle = pos
        sleep(time)

    def max(self, axis, time=2):
        self.move(axis, self.max_range, time)

    def min(self, axis, time=2):
        self.move(axis, self.min_range, time)

    def mid(self, axis, time=2):
        self.move(axis, self.mid_range, time)

    def home(self, time=2):
        self.drive(self.mid_range, self.mid_range, self.mid_range, time)
        return True

    def stop(self):
        self.XServo.detach()
        self.YServo.detach()
        self.ZServo.detach()

    def close(self):
        # self.XServo.is_active=False
        # self.YServo.is_active=False
        # self.ZServo.is_active=False
        pass