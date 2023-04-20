import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import csv
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-attenda-78c80-default-rtdb.firebaseio.com/"
})

ref = db.reference('Staff')

data_dict = ref.get()

data_list = [(key, value['Name'], value['Time In'], value['Time Out']) for key, value in data_dict.items()]

# Write the data to a CSV file
with open('data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'Name', 'Time In', 'Time Out']) # write headers
    writer.writerows(data_list)
