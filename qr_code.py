import qrcode
import cv2
import numpy as np


def draw_qr_code(code, filepath):
    img = qrcode.make(code)
    img.save(filepath)



def qr_cam(quit_on_find=True):
    webcam = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        img = webcam.read()[1]

        # find and mark code
        data, bbox, straight_qrcode = detector.detectAndDecode(img)
        if not data == "":
            if quit_on_find:
                cv2.destroyAllWindows()
                webcam.release()
                return data
            else:
                img = cv2.polylines(img, np.int32([bbox]), True, (0,255,0), 3)

        # mirror and show
        img = cv2.flip(img, 1)
        cv2.imshow("QR Code Detector", img)

        # Close and break the loop after pressing escape key
        if cv2.waitKey(1) &0XFF == 27:
            cv2.destroyAllWindows()
            webcam.release()
            break

if __name__ == '__main__':
    qr_cam(False)
