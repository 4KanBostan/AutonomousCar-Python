"""
Siddharth Sharma tarafından paylaşılan kodlardır.

Youtube de Self Driving RC Car olarak videosu paylaşılmıştır.

Sadece küçük değişikler yapılarak çalışır hale getirildi.

auto_driver.py olarak paylaşılan açık kaynak koddur.

Video açıklamalar kısmında kaynak kodlar linkine bakabilirsiniz:)

"""
import cv2
import math
import numpy as np
import threading
import socketserver
import struct
import serial

sensor_data = None

class SensorStreamHandler(socketserver.BaseRequestHandler):
    
    data = " "

    def handle(self):
        global sensor_data
        try:
            while self.data:
                self.data = self.request.recv(1024)
                sensor_data = round(float(self.data), 1)
                #print(f"Mesafe: {sensor_data} cm")
        finally:
            print("Mesafe sensoru icin baglanti ve veri alisverisine son verildi!")


class NeuralNetwork():
    def __init__(self):
        self.model = cv2.ml.ANN_MLP_load('XML/aksam1596313779.xml')

    def predict(self, samples):
        ret, resp = self.model.predict(samples)
        return resp.argmax(-1)


class RCControl(object):
    def __init__(self):
        self.ser = serial.Serial('COM10', 115200, timeout=1)
        
    def stop(self):
        self.ser.write(b'0')
        
    def steer(self, prediction):
        if prediction == 0:
            self.ser.write(b'6')
            print("Sola Don")
        elif prediction == 1:
            self.ser.write(b'5')
            print("Saga Don")
        elif prediction == 2:
            self.ser.write(b'1')
            print("ileri git")
        
        #elif prediction == 3:
            #print("Geri gel")
            #self.ser.write(b'2')
        
        else:
            self.stop()
            
class ObjectDetection(object):
    def __init__(self):
        self.red_light = False
        self.green_light = False
        self.yellow_light = False

    def detect(self, classifier, gray, image):
    
        v = 0

        threshold = 150

        objects = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))
        for (x, y, w, h) in objects:
            
            cv2.rectangle(image, (x+5, y+5), (x+w-5, y+h-5), (0, 255, 0), 2)
            v = y + h - 5

            if w / h == 1:
                cv2.putText(image, 'DUR', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            else:
                roi = gray[y+10: y+h-10, x+10: x+w-10]
                mask = cv2.GaussianBlur(roi, (25,25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)

                    if 1.0/8*(h - 30) < maxLoc[1] < 4.0/8*(h - 30):
                        cv2.putText(image, 'Kirmizi', (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        self.red_light = True

                    elif 5.5/8*(h-30) < maxLoc[1] < h - 30:
                        cv2.putText(image, 'Yesil', (x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        self.green_light = True
        
            
        return v


class DistanceToCamera(object):
    def __init__(self):
        
        self.alpha = 8.0 * math.pi / 180
        self.v0 = 119.865631
        self.ay = 332.262498

    def calculate(self, v, h, x_shift, image):
        
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))

        if d > 0:
            cv2.putText(image, f"{d:.1f}cm", (image.shape[1] - x_shift, image.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return d


class VideoStreamHandler(socketserver.StreamRequestHandler):

    stop_classifier = cv2.CascadeClassifier('Cascade/stop_sign.xml')
    light_classifier = cv2.CascadeClassifier('Cascade/traffic_light.xml')

    obj_detection = ObjectDetection()

    dist_to_camera = DistanceToCamera()
    h_stop = 4.5 
    h_light = 4.5 
    d_stop = 35
    d_light = 35
    stop_start = 0
    stop_finish = 0
    stop_time = 0
    model = NeuralNetwork()
    drive_time_after_stop = 0
    car = RCControl()

    def handle(self):
        global sensor_data
        stop_sign_active = True
        stop_flag = False
        
        try:
            while True:
                image_len = struct.unpack('<L', self.rfile.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                
                recv_bytes = b''
                recv_bytes += self.rfile.read(image_len)

                gray = cv2.imdecode(np.fromstring(recv_bytes, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                image = cv2.imdecode(np.fromstring(recv_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                roi = gray[150:240, :]
                cv2.imshow('istenilen alan', roi)

                image_array = roi.reshape(1, 28800).astype(np.float32)
                
                
                v_stop = self.obj_detection.detect(self.stop_classifier ,gray, image)
                v_light = self.obj_detection.detect(self.light_classifier ,gray, image )

                if v_stop > 0.0 or v_light > 0.0 :
                    d_stop = self.dist_to_camera.calculate(v_stop, self.h_stop, 300, image)
                    d_light = self.dist_to_camera.calculate(v_light, self.h_light, 100, image)
                    self.d_stop = d_stop
                    self.d_light = d_light
                    
                
                prediction = self.model.predict(image_array)
                
                if sensor_data and int(sensor_data) < 30.0:
                    self.car.stop()
                    print("Engel algilandi. Mesafe: {0:.1f} cm".format(sensor_data))
                    #sensor_data = None
                    
                                    
                elif 0.0 < self.d_stop < 35.0 and stop_sign_active:
                    print('Dur isareti algilandi 5 sn duracak :)')
                    self.car.stop()

                    if stop_flag is False:
                        stop_start = cv2.getTickCount()
                        stop_flag = True

                    stop_finish = cv2.getTickCount()
                    stop_time = (stop_finish - stop_start)/cv2.getTickFrequency()
                    print(f"Durma suresi: {stop_time}")

                    if stop_time > 5:
                        stop_flag = False
                        stop_sign_active = False
                        print("5 sn tamamlandi. Harekete geciyor...")

                elif 0.0 < self.d_light < 35.0:
                    if self.obj_detection.red_light:
                        print("Kirmizi isik")
                        self.car.stop()
                    elif self.obj_detection.green_light:
                        print("Yesil isik")
                        pass
                        
                    self.obj_detection.red_light = False
                    self.obj_detection.green_light = False
                    self.d_light = 35.0
                    
                else:
                    self.car.steer(prediction)
                    self.d_stop = 35.0
                    stop_start = cv2.getTickCount()

                    if stop_sign_active is False:
                        drive_time_after_stop = (stop_start - stop_finish) / cv2.getTickFrequency()
                        if drive_time_after_stop > 5:
                            stop_sign_active = True
                
                cv2.imshow('Video', image)
                
                if (cv2.waitKey(5) & 0xFF) == ord('q'):
                    cv2.destroyAllWindows()
                    break
        finally:
            self.car.stop()
            print("Kamera icin baglanti ve veri alisverisine son verildi!")

class ThreadServer():
    def server_video_thread(host, port):
        server = socketserver.TCPServer((host, port), VideoStreamHandler)
        server.serve_forever()

    def ultrasonic_server_thread(host, port):
        server = socketserver.TCPServer((host, port), SensorStreamHandler)
        server.serve_forever()

    ultrasonic_sensor_thread = threading.Thread(target=ultrasonic_server_thread, args=('192.168.43.56',8002))
    ultrasonic_sensor_thread.daemon = True
    ultrasonic_sensor_thread.start()
    
    video_thread = threading.Thread(target=server_video_thread, args=('192.168.43.56',8000))
    video_thread.start()


if __name__ == '__main__':
    ThreadServer()