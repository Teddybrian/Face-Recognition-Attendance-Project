import os
import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-attenda-78c80-default-rtdb.firebaseio.com/",
    'storageBucket': "face-recognition-attenda-78c80.appspot.com"
})

# importing Staff Images
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
staffIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    staffIds.append(os.path.splitext(path)[0])

# sending data to DB Storage
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


print(staffIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    # Generate encodings
    return encodeList

# Generate image List and save
print("Encoding Started ...")
# generate encodings
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, staffIds]
print(encodeListKnown)
print("Encoding Complete")

# generating pickle file
file = open("EncodeFile.p", 'wb')

# Add encodeListWithIds to the Pickle file
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
