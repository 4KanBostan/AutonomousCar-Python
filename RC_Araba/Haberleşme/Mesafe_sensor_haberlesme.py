"""
Siddharth Sharma tarafından paylaşılan kodlardır.

Youtube de Self Driving RC Car olarak videosu paylaşılmıştır.

Sadece küçük değişikler yapılarak çalışır hale getirildi.

capture_sensor_data_server_test.py olarak paylaşılan açık kaynak koddur.

Video açıklamalar kısmında kaynak kodlar linkine bakabilirsiniz:)

"""
import socket
import time

class CaptureSensorDataTest(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('192.168.43.56', 8002))
        self.sock.listen(1)
        self.connection, self.client_address = self.sock.accept()
        self.capture_data()

    def capture_data(self):
        try:
            print("Baglanti bilgisi IP numarasi: {0}".format(self.client_address))
            start = time.time()

            while True:
                sensor_data = float(self.connection.recv(1024))
                print("Mesafe: {0:.1f} cm".format(sensor_data))

                # Test for 1 min
                if time.time() - start > 300:
                    break
        finally:
            self.connection.close()
            self.sock.close()


if __name__ == '__main__':
    CaptureSensorDataTest()