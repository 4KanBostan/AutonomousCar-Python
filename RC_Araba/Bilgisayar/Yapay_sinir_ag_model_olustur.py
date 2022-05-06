"""
Siddharth Sharma tarafından paylaşılan kodlardır.

Youtube de Self Driving RC Car olarak videosu paylaşılmıştır.

Sadece küçük değişikler yapılarak çalışır hale getirildi.

mlp_training.py olarak paylaşılan açık kaynak koddur.

Video açıklamalar kısmında kaynak kodlar linkine bakabilirsiniz:)

"""
import cv2
import glob
import numpy as np
from sklearn.model_selection import train_test_split
import sys
import time

def retrieve_data_set():

    start_time = cv2.getTickCount()
    print("Data verileri aciliyor...")
    image_array = np.zeros((1, 28800), 'float')
    label_array = np.zeros((1, 4), 'float')
    data_set = glob.glob("Data/*.npz")

    if not data_set:
        print("Data verisi yok cikiliyor...")
        sys.exit()

    for single_npz in data_set:
        with np.load(single_npz) as data:
            temp_images = data["images"]
            temp_labels = data["labels"]

        image_array = np.vstack((image_array, temp_images))
        label_array = np.vstack((label_array, temp_labels))

    X = np.float32(image_array[1:, :])
    Y = np.float32(label_array[1:, :])
    print("Data giriş verileri: {0}".format(X.shape))
    print("Data çıkış verileri: {0}".format(Y.shape))

    end_time = cv2.getTickCount()
    print("Data verilerinin yukleme suresi: {0} sn"
          .format((end_time - start_time) // cv2.getTickFrequency()))

    return X, Y


if __name__ == '__main__':
    X, Y = retrieve_data_set()
    train_X, test_X, train_Y, test_Y = train_test_split(X, Y, test_size=0.2)
    start_time = cv2.getTickCount()
    layer_sizes = np.int32([28800,32, 4])
    model = cv2.ml.ANN_MLP_create()
    model.setLayerSizes(layer_sizes)
    model.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP)
    model.setBackpropMomentumScale(0.0)
    model.setBackpropWeightScale(0.001)
    model.setTermCriteria((cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 0.0001))
    model.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM, 2, 1)

    print("Model giris ve cikis bilgileri olusturuluyor...")
    model.train(train_X, cv2.ml.ROW_SAMPLE, train_Y)

    end_time = cv2.getTickCount()
    duration = (end_time - start_time) // cv2.getTickFrequency()
    print("Model olusma suresi: {0} sn".format(duration))

    ret_train, resp_train = model.predict(train_X)
    train_mean_sq_error = ((resp_train - train_Y) * (resp_train - train_Y)).mean()
    print("Model giris icin hata orani: {0:.2f}".format(train_mean_sq_error * 100))

    ret_test, resp_test = model.predict(test_X)
    test_mean_sq_error = ((resp_test - test_Y) * (resp_test - test_Y)).mean()
    print("Model cikis icin hata orani: {0:.2f}".format(test_mean_sq_error * 100))
    model.save("XML\{0}.xml".format(str(int(time.time()))))

