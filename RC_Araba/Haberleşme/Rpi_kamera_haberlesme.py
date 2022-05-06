"""
Siddharth Sharma tarafından paylaşılan kodlardır.

Youtube de Self Driving RC Car olarak videosu paylaşılmıştır.

Sadece küçük değişikler yapılarak çalışır hale getirildi.

capture_video_server_test.py olarak paylaşılan açık kaynak koddur.

Video açıklamalar kısmında kaynak kodlar linkine bakabilirsiniz:)

"""
import cv2
import numpy as np
import socket
import struct


class VideoStreamingTest:
    def __init__(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('192.168.43.56', 8000))
        #self.server_socket.bind(('169.254.41.222', 8000))
        self.server_socket.listen(1)
        print('Raspberry pi ile bağlantı kuruluyor.')
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.stream_video()

    def stream_video(self):
        frame = 0
        try:
            print('Bağlantı bilgileri: {0}'.format(self.client_address))
            print('Bağlantı gerçekleşti...')
            print("'q' basarak döngüden çıkabilirsiniz")

            while True:
                
                image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    cv2.destroyAllWindows()
                    break
                
                recv_bytes = b''
                recv_bytes += self.connection.read(image_len)
                
                image = cv2.imdecode(np.fromstring(recv_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)

                frame += 1
                
                cv2.imshow('Video', image)
                if (cv2.waitKey(5) & 0xFF) == ord('q'):
                    cv2.destroyAllWindows()
                    break

        finally:
            print('Bağlantı sonlandırıldı.')
            self.connection.close()
            self.server_socket.close()
            print("Raspberry piden gelen toplam fotoğraf sayısı: {0}".format(frame))


if __name__ == '__main__':
    VideoStreamingTest()
