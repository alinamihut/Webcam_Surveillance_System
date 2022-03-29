import cv2, pandas
from datetime import datetime
from cv2 import imwrite
import winsound
background = None

duration = 1000  # milliseconds
frequency = 3000  # Hz



motionList = [None, None]


time = []


dataframe = pandas.DataFrame(columns=["Start", "End"])


video = cv2.VideoCapture(0)

while True:

    grabbed, frame = video.read()


    motion = 0


    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Converting gray scale image to GaussianBlur
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if background is None:
        background = gray
        continue

    # Difference between static background and current frame
    difference = cv2.absdiff(background, gray)

    threshold = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None, iterations=2)

    # Finding contour of moving object
    contours, _ = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        motion = 1

        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(frame, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (255, 0, 0), 3)


    motionList.append(motion)
    motionList = motionList[-2:]


    if motionList[-1] == 1 and motionList[-2] == 0:
        time.append(datetime.now())
        winsound.Beep(frequency, duration)
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%Y%m%d%H%M%S")
        filename = "images/im_" + timestampStr + ".jpg"
        imwrite(filename, frame)

    if motionList[-1] == 0 and motionList[-2] == 1:
        time.append(datetime.now())

    cv2.imshow("Alarm System", frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        if motion == 1:
            time.append(datetime.now())
        break

for i in range(0, len(time), 2):
    dataframe = dataframe.append({"Start": time[i], "End": time[i + 1]}, ignore_index=True)

dataframe.to_csv("Movement_Times.csv")

video.release()

cv2.destroyAllWindows()