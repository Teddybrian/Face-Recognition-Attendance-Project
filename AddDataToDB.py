import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-attenda-78c80-default-rtdb.firebaseio.com/"
})

ref = db.reference('Staff')

data = {
    "3001":
        {
            "Name": "Teddy Brian",
            "Department": "Information Technology",
            "Employment Level": "Senior Manager IT",
            "Total Attendance": 10,
            "Time In": "2023-03-26 21:12:56",
            "Time Out": "2023-03-26 21:15:00",
            "Years of Employment": 6
        },
    "2001":
        {
            "Name": "Joy Langat",
            "Department": "Business Information and Analysis",
            "Employment Level": "Director",
            "Total Attendance": 12,
            "Time In": "2023-03-24 13:02:21",
            "Time Out": "2023-03-12 13:08:31",
            "Years of Employment": 4
        },
    "4001":
        {
            "Name": "Irene Mawia",
            "Department": "Assurance",
            "Employment Level": "Senior Manager",
            "Total Attendance": 10,
            "Time In": "2023-03-24 9:17:56",
            "Time Out": "2023-03-24 9:21:09",
            "Years of Employment": 5
        }
}

for key, value in data.items():
    # send data to specific directory
    ref.child(key).set(value)
