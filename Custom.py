import pandas as pd
import cv2
from datetime import datetime
import numpy as np
import face_recognition
import os
from tkinter import *
from PIL import Image, ImageTk
import customtkinter


path = 'Students/'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
  curImg = cv2.imread(f'{path}/{cl}')
  images.append(curImg)
  classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images):
  encodeList = []
  for pic in images:
    pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(pic)[0]
    encodeList.append(encode)
  return encodeList

def markAttendance(name,course):
  with open(course + '.csv', 'r+') as f:
    myDataList = f.readlines()
    nameList = []
    for line in myDataList:
      entry = line.split(',')
      nameList.append(entry[0])
    if name not in nameList:
      now = datetime.now()
      dtString = now.strftime('%H:%M:%S')
      f.writelines(f'\n{name},{dtString}')


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)
width, height = 800, 600
# Set the width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
# Create a GUI app
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

app = customtkinter.CTk()
app.title("Attendance System")
app.geometry("500x500")
app.bind('<Escape>', lambda e: app.quit())
# Create a label and display it on app
label_widget = Label(app)
label_widget.pack()

def display_csv():
  app.destroy()
  df = pd.read_csv(entry1.get() + '.csv')

  root = customtkinter.CTk()
  root.title("Records")
  root.geometry("500x500")
  root.bind('<Escape>', lambda e: app.quit())

  table = Frame(root)
  table.pack(pady=10)

  # Create column labels
  for col_idx, column in enumerate(df.columns):
    label = Label(table, text=column, relief=customtkinter.RIDGE, width=15)
    label.grid(row=0, column=col_idx)

  # Display data rows
  for row_idx, row in df.iterrows():
    for col_idx, value in enumerate(row):
      label = Label(table, text=value, relief=customtkinter.RIDGE, width=15)
      label.grid(row=row_idx + 1, column=col_idx)

  # Run the Tkinter event loop
  root.mainloop()
def open_camera():
  course = entry1.get()
  success, img = cap.read()

  imgS = cv2.resize(img,(0,0),None,0.25,0.25)
  imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

  facesCurFrame = face_recognition.face_locations(imgS)
  encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

  for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
    print(faceDis)
    matchIndex = np.argmin(faceDis)
    y1, x2, y2, x1 = faceLoc
    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    #MAKE RECTANGLES:
    if matches[matchIndex] and faceDis[matchIndex] < 0.4:
      name = classNames[matchIndex].upper()
      print(name)
      cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
      #cv2.rectangle(img, (x2, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
      cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),1)
      markAttendance(name,course)
    else:
      cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
      #cv2.rectangle(img, (x2, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
      cv2.putText(img, "Unknown", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 1)
    #----------------------
  opencv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
  captured_image = Image.fromarray(opencv_image)
  photo_image = ImageTk.PhotoImage(image=captured_image)
  label_widget.photo_image = photo_image
  label_widget.configure(image=photo_image)
  label_widget.after(10, open_camera)

frame = customtkinter.CTkFrame(master=app)
frame.pack(pady = 20, padx = 60, fill = "both", expand = True)

label = customtkinter.CTkLabel(master=app, text="Attendance System",font=("Roboto",24))
label.pack(pady=12, padx=10)

button1 = customtkinter.CTkButton(app, text="Open Camera", command=open_camera)
button1.pack(pady=12, padx=10)

button2 = customtkinter.CTkButton(app, text="Show Attendance", command=display_csv)
button2.pack(pady=12, padx=10)

options = ["TOA","CCN","CAAL","AI","Pak. Hist"]
entry1 = customtkinter.CTkOptionMenu(master=app, values=options)
entry1.pack(pady = 12, padx = 10)

app.mainloop()