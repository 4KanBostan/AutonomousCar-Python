"""
Siddharth Sharma tarafından paylaşılan kodlardır.

Youtube de Self Driving RC Car olarak videosu paylaşılmıştır.

Sadece küçük değişikler yapılarak çalışır hale getirildi.

car_control_test.py olarak paylaşılan açık kaynak koddur.

Video açıklamalar kısmında kaynak kodlar linkine bakabilirsiniz:)

"""

import serial
import pygame
from pygame.locals import *
import sys

class CarControlTest:
    def __init__(self):
        try:
            self.ser = serial.Serial('COM7', 115200, timeout=1)
        except IOError as e:
            print(e)
            sys.exit()

        self.ser.flush()
        pygame.init()

        pygame.display.set_mode((400, 300))
        self.send_inst = True
        self.steer()

    def steer(self):
        complex_cmd = False

        while self.send_inst:
            for event in pygame.event.get():
                if (event.type == KEYDOWN) or (complex_cmd):
                    key_input = pygame.key.get_pressed()
                    complex_cmd = False

                    if key_input[pygame.K_UP] and key_input[pygame.K_RIGHT]:
                        print("ileri sag")
                        complex_cmd = True
                        self.ser.write(b'5')

                    elif key_input[pygame.K_UP] and key_input[pygame.K_LEFT]:
                        print("ileri sol")
                        complex_cmd = True
                        self.ser.write(b'6')

                    elif key_input[pygame.K_DOWN] and key_input[pygame.K_RIGHT]:
                        print("geri sag")
                        complex_cmd = True
                        self.ser.write(b'7')

                    elif key_input[pygame.K_DOWN] and key_input[pygame.K_LEFT]:
                        print("geri sol")
                        complex_cmd = True
                        self.ser.write(b'8')

                    elif key_input[pygame.K_UP]:
                        print("ileri")
                        self.ser.write(b'1')

                    elif key_input[pygame.K_DOWN]:
                        print("geri")
                        self.ser.write(b'2')

                    elif key_input[pygame.K_RIGHT]:
                        print("sag")
                        self.ser.write(b'3')

                    elif key_input[pygame.K_LEFT]:
                        print("sol")
                        self.ser.write(b'4')

                    elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                        self.close_serial_connection()
                        break

                elif event.type == pygame.KEYUP:
                    self.ser.write(b'0')

                elif event.type == pygame.QUIT:
                    self.close_serial_connection()
                    break

    def close_serial_connection(self):
        print('Çikis yapıldı.')
        self.ser.write(b'0')
        self.ser.close()
        self.send_inst = False


if __name__ == "__main__":
    CarControlTest()
