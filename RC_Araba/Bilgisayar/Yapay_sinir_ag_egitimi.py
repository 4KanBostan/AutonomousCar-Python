"""
Siddharth Sharma tarafından paylaşılan kodlardır.

Youtube de Self Driving RC Car olarak videosu paylaşılmıştır.

Sadece küçük değişikler yapılarak çalışır hale getirildi.

collect_data.py olarak paylaşılan açık kaynak koddur.

Video açıklamalar kısmında kaynak kodlar linkine bakabilirsiniz:)

"""
import cv2
import numpy as np
import socket
import struct
import pygame
from pygame.locals import *
import time
import os
import sys
import serial

class CollectData(object):
    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind(('192.168.43.56', 8000))
        self.sock.listen(1)
        self.connection = self.sock.accept()[0].makefile('rb')

        try:
            self.ser = serial.Serial('COM7', 115200, timeout=1)
        except IOError as e:
            print(e)
            sys.exit()

        self.ser.flush()
        self.send_instr = True

        self.k = np.zeros((4,4), 'float')
        for i in range(4):
            self.k[i,i] = 1

        pygame.init()
        pygame.display.set_mode((400, 300))

        self.collect_images()

    def collect_images(self):
        saved_frames = 0
        total_frames = 0
        start_time = cv2.getTickCount()

        print('Data verileri kaydetmek icin hazirim...')
        image_array = np.zeros((1, 28800), 'float')
        label_array = np.zeros((1, 4), 'float')
        
        try:
            frame = 1
            complex_cmd = False

            while self.send_instr:
                image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break

                recv_bytes = b''
                recv_bytes += self.connection.read(image_len)
                image = cv2.imdecode(np.fromstring(recv_bytes, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                cv2.imshow('Video', image)
                roi = image[150:240, :]
                cv2.imshow('istenilen alan', roi)

                temp_array = roi.reshape(1, 28800).astype(np.float32)

                frame += 1
                total_frames += 1

                for event in pygame.event.get():
                    if event.type == KEYDOWN or complex_cmd:
                        key = pygame.key.get_pressed()
                        complex_cmd = False
                        #cv2.imwrite('collected_images/frame{:>05}.jpg'.format(frame), image)
                        if key[pygame.K_UP]:
                            print("ileri")
                            self.ser.write(b'1')
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[2]))
                            saved_frames += 1

                        elif key[pygame.K_DOWN]:
                            print("geri")
                            self.ser.write(b'2')
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[3]))
                            saved_frames += 1

                        elif key[pygame.K_RIGHT]:
                            print("sag")
                            self.ser.write(b'5')
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[1]))
                            saved_frames += 1

                        elif key[pygame.K_LEFT]:
                            print("sol")
                            self.ser.write(b'6')
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[0]))
                            saved_frames += 1

                        elif key[pygame.K_x] or key[pygame.K_q]:
                            print("Cikis")
                            self.ser.write(b'0')
                            self.send_instr = False
                            cv2.destroyAllWindows()
                            break

                        else:
                            self.ser.write(b'0')

                    elif event.type == KEYUP:
                        complex_cmd = False
                        self.ser.write(b'0')

            # Save images and labels
            image_array = image_array[1:, :]
            label_array = label_array[1:, :]

            file_name = str(int(time.time()))
            directory = "Data"
            if not os.path.exists(directory):
                os.makedirs(directory)

            try:
                np.savez(directory + '/' + file_name + '.npz', images=image_array,
                         labels=label_array)
            except IOError as e:
                print(e)

            # Print meta data
            end_time = cv2.getTickCount()
            duration = (end_time - start_time) // cv2.getTickFrequency()
            print("Veri kaydetme suresi: {0} saniye".format(duration))
            print(image_array.shape)
            print(label_array.shape)
            print("Raspberry pi den gelen fotograf sayisi: {0}".format(total_frames))
            print("Kaydedilen fotograf: {0}".format(saved_frames))
            print("Kaydedilmeyen fotograf: {0}".format(total_frames - saved_frames))

        finally:
            self.connection.close()
            self.sock.close()


if __name__ == '__main__':
    CollectData()
