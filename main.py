import pickle
import os
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
# contained in OpenCV HAAR Cascades algorithm
# Dlib module contains CNN(Convolution neural network) algorithm (Extracts facial features and classify them)
# HoG contained in Dlib

# Connecting firebase to the system
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-attenda-78c80-default-rtdb.firebaseio.com/",
    'storageBucket': "face-recognition-attenda-78c80.appspot.com"
})
bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Importing mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load encoding (pickle) file
print("Loading Encode File ...")
file = open("EncodeFile.p", 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()

# extracting staff information from encoded list
encodeListKnown, staffIds = encodeListKnownWithIds

# print(staffIds)
print("Loading Complete")

def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S %d-%m-%Y')
            f.writelines(f'\n{name},{dtString},{dtString}')

modeType = 0
counter = 0
id = -1
imgStaff = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Feed values to system to detect and give output
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            # Extracting least faceDis to use
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = staffIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Scanning", (275, 400))
                    cv2.imshow("Webcam", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # accessing data from real-time db for update
                staffInfo = db.reference(f'Staff/{id}').get()
                print(staffInfo)


                # Get image staff from storage
                blob = bucket.get_blob(f'Images/{id}.jpeg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStaff = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # update attendance data
                datetimeObject1 = datetime.strptime(staffInfo['Time In'], "%Y-%m-%d %H:%M:%S")
                datetimeObject2 = datetime.strptime(staffInfo['Time Out'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject1).total_seconds()
                secondsElapsed2 = (datetime.now() - datetimeObject2).total_seconds()
                timeIn = datetimeObject1
                timeOut = datetimeObject2
                # print(secondsElapsed)

                # Time In
                if timeIn:
                    if timeOut > datetimeObject1:
                        ref = db.reference(f'Staff/{id}')
                        ref.child('Time In').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        # Time Out
                    elif datetime.now() > timeIn:
                        if secondsElapsed2 > 0:
                            ref = db.reference(f'Staff/{id}')
                            staffInfo['Total Attendance'] += 1
                            ref.child('Total Attendance').set(staffInfo['Total Attendance'])
                            ref.child('Time Out').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            continue

                # Continue with identification phase
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(staffInfo['Total Attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(staffInfo['Employment Level']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(staffInfo['Department']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(staffInfo['Years of Employment']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(staffInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(staffInfo['Name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    #imgBackground[175:175 + 216, 909:909 + 216] = imgStaff

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    staffInfo = []
                    imgStaff = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    cv2.imshow("Webcam", imgBackground)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
