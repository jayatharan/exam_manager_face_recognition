

from tkinter import *
import PIL
from PIL import Image, ImageTk
import cv2
from tkinter import *
from pyzbar import pyzbar
import requests
import face_recognition
import numpy
import re
from tkinter import messagebox

TOLERANCE = 0.5

FRAME_THICKNESS = 2
FONT_THICKNESS = 2
MODEL = "cnn"

color = [0, 255, 0]

known_faces = []

cap = cv2.VideoCapture(0)
std_id = ""
std_data = {"Name": "None",
            "Reg_No": "None",
            "Index_No": "None",
            "Faculty": "None",
            "Department": "None"
            }

camara = 1
got_qr = False

frame_img = None


def getStudentData(id):
    global std_data
    global camara
    global std_id
    global known_faces

    exam_id = qr_Entry_exam.get()
    if (exam_id == ""):
        messagebox.showerror(
            "Exam Id Error", "Exam ID Not found \n Please enter EXAM ID")
        return

    std_id = id
    try:
        response = requests.get(
            url_entry.get()+"/api/student/"+str(id)+"/"+qr_Entry_exam.get())

    except Exception:
        messagebox.showerror(
            "Connection Error", "Server Connection Error Check your internet connection")
        return

    std_data = response.json()

    if(response.status_code == 200):
        showStudentData()
        readImage()
        if (len(known_faces) != 0):
            qr_frame.grid_forget()
            std_frame.grid(row=0, column=0)
            camara = 0
            face_frame()
        else:
            camara = 2
            sample_frame()

    else:
        messagebox.showerror(
            "Error", "Exam OR Student not found Try Again!")
        return


def getStudentButton():
    stu_id_regex = re.compile(r's+\d\d\d\d\d')
    stu_id = stu_id_regex.search(qr_Entry.get())
    try:
        stu_id = stu_id.group()
        if stu_id is not None:
            getStudentData(stu_id)
        else:
            messagebox.showerror("Student Id Error", "Student id not matched")
    except Exception:
        messagebox.showerror("Error", "Something went wrong Try Again!")


def readImage():
    global known_faces
    global frame_img

    known_faces = []
    url = url_entry.get()+"/images/studentImages/"+str(std_data['image'])
    im = PIL.Image.open(requests.get(url, stream=True).raw)
    image = numpy.asarray(im)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    try:
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)

    except Exception:
        known_faces = []

    imgtk = ImageTk.PhotoImage(image=im)
    frame_img = imgtk
    std_img_l.imgtk = imgtk
    std_img_l.configure(image=imgtk)


def mark_attandance(id):
    url = url_entry.get()+"/api/exam/"+id
    response = requests.get(url)


def face_matched():
    global camara
    mark_attandance(str(std_data["student_exam_id"]))
    atd_img_l.imgtk = frame_img
    atd_img_l.configure(image=frame_img)

    std_frame.grid_forget()
    atd_id.config(text=std_id)
    atd_frame.grid(row=0, column=0)
    camara = 2
    sample_frame()


def try_again():
    global camara
    global known_faces
    global std_id

    std_id = ""
    known_faces = []

    std_frame.grid_forget()
    atd_frame.grid_forget()
    qr_frame.grid(row=0, column=0)
    camara = 1
    qrcode_frame()


def showStudentData():
    std_name.config(text=std_data['Name'])
    std_reg.config(text=std_data['Reg_No'])
    std_index.config(text=std_data['Index_No'])
    std_faculty.config(text=std_data['Faculty'])
    std_dept.config(text=std_data['Department'])


def face_frame():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(cv2image)
    encodings = face_recognition.face_encodings(cv2image, locations)

    for face_encoding in encodings:
        results = face_recognition.compare_faces(
            known_faces, face_encoding, TOLERANCE)
        if True in results:
            face_matched()

    img = PIL.Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)

    if (camara == 0):
        lmain.after(10, face_frame)


def qrcode_frame():
    global got_qr
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)

    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:

        got_qr = True

        (x, y, w, h) = barcode.rect

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)

        barcodeData = barcode.data.decode('utf-8')

        barcodeType = barcode.type

        if (got_qr):
            getStudentData(barcodeData)

        text = "Barcode:{} Type:{}".format(barcodeData, barcodeType)

        cv2.putText(frame, text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = PIL.Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)

    if (camara == 1):
        lmain.after(10, qrcode_frame)


def sample_frame():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = PIL.Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    if (camara == 2):
        lmain.after(10, sample_frame)


root = Tk()
root.title("Universities Exam manager")
root.bind('<Escape>', lambda e: root.quit())

h_frame = Frame(root)
h_frame.grid(row=0, column=0, columnspan=2)
heading = Label(h_frame, text="Universities Exam Management System",
                font=('Helvetica bold', 25))
heading.grid(row=0, column=0)

url_entry = Entry(root, width=80)
url_entry.insert(END, 'http://localhost:8000')
url_entry.grid(row=1, column=0, columnspan=2)

l_frame = Frame(root)
l_frame.grid(row=2, column=0)

r_frame = Frame(root)
r_frame.grid(row=2, column=1)

lmain = Label(l_frame)
lmain.pack()

# QR Code Frame
qr_frame = Frame(r_frame)
qr_frame.grid(row=0, column=0)
h1 = Label(qr_frame, text="Scan your QR Code", font=('Helvetica bold', 15))
h1.grid(row=0, column=0, columnspan=2)
qr_img = ImageTk.PhotoImage(PIL.Image.open("./images.jpeg"))
qr_imgL = Label(qr_frame, image=qr_img)
qr_imgL.grid(row=1, column=0, columnspan=2)
qr_label = Label(qr_frame, text="Enter Reg_No")
qr_label.grid(row=2, column=0)
qr_Entry = Entry(qr_frame)
qr_Entry.grid(row=2, column=1)
qr_button = Button(qr_frame, text="Get Student Data",
                   bg="green", command=getStudentButton)
qr_button.grid(row=3, column=0, columnspan=2)
Label(qr_frame).grid(row=4, column=0)
h2 = Label(qr_frame, text="Exam Details", font=('Helvetica bold', 15))
h2.grid(row=5, column=0, columnspan=2)
qr_label_exam = Label(qr_frame, text="Enter Exam_ID")
qr_label_exam.grid(row=6, column=0)
qr_Entry_exam = Entry(qr_frame)
qr_Entry_exam.grid(row=6, column=1)


# Student Data Frame
std_frame = Frame(r_frame)
#std_frame.grid(row=0, column=0)
h2 = Label(std_frame, text="Student Data", font=('Helvetica bold', 15))
h2.grid(row=0, column=0, columnspan=2)
std_img = ImageTk.PhotoImage(PIL.Image.open("./download.png"))
std_img_l = Label(std_frame, image=std_img)
std_img_l.grid(row=1, column=0, columnspan=2)
std_name_l = Label(std_frame, text="Name : ")
std_name_l.grid(row=2, column=0)
std_reg_l = Label(std_frame, text="Reg_No : ")
std_reg_l.grid(row=3, column=0)
std_index_l = Label(std_frame, text="Index_No : ")
std_index_l.grid(row=4, column=0)
std_faculty_l = Label(std_frame, text="Faculty : ")
std_faculty_l.grid(row=5, column=0)
std_dept_l = Label(std_frame, text="Department : ")
std_dept_l.grid(row=6, column=0)
std_img_l.grid(row=1, column=0, columnspan=2)

std_name = Label(std_frame, text=std_data['Name'])
std_name.grid(row=2, column=1)
std_reg = Label(std_frame, text=std_data['Reg_No'])
std_reg.grid(row=3, column=1)
std_index = Label(std_frame, text=std_data['Index_No'])
std_index.grid(row=4, column=1)
std_faculty = Label(std_frame, text=std_data['Faculty'])
std_faculty.grid(row=5, column=1)
std_dept = Label(std_frame, text=std_data['Department'])
std_dept.grid(row=6, column=1)
b2 = Button(std_frame, text="Try Again || Next Student",
            command=try_again, bg="yellow")
b2.grid(row=7, column=0, columnspan=2)

# Student Attandance
atd_frame = Frame(r_frame)
#atd_frame.grid(row=0, column=0)
h3 = Label(atd_frame, text="Student Exam Attandance",
           font=('Helvetica bold', 15))
h3.grid(row=0, column=0, columnspan=2)
atd_img = ImageTk.PhotoImage(PIL.Image.open("./download.png"))
atd_img_l = Label(atd_frame, image=std_img)
atd_img_l.grid(row=1, column=0, columnspan=2)
atd_id_l = Label(atd_frame, text="Student_Id ")
atd_id_l.grid(row=2, column=0)
atd_id = Label(atd_frame, text="")
atd_id.grid(row=2, column=1)
atd_status_l = Label(atd_frame, text="Status ")
atd_status_l.grid(row=3, column=0)
atd_status = Label(atd_frame, text="PASS", fg="green")
atd_status.grid(row=3, column=1)
b1 = Button(atd_frame, text="Next Student",
            command=try_again, bg="yellow")
b1.grid(row=4, column=0, columnspan=2)

qrcode_frame()
root.mainloop()
