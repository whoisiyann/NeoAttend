from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import datetime
import csv
import os
import cv2
import face_recognition
import dlib
import numpy as np
from scipy.spatial import distance


#############################################   FUNCTION   ##############################################

#----------------------------------------------------Load the facial landmark predictor
predictor_path = "shape_predictor_68_face_landmarks.dat"
if not os.path.exists(predictor_path):
    messagebox.showerror("Error", f"Facial landmark predictor file not found: {predictor_path}")
    exit(1)
predictor = dlib.shape_predictor(predictor_path)
detector = dlib.get_frontal_face_detector()

#--------------------------------------------------Function to calculate Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

#-----------------------hresholds for blink detection
EAR_THRESHOLD = 0.25
CONSECUTIVE_FRAMES = 3

#------------------------------------------------------TAKE ATTENDANCE
def take_attendance():

    folder = "students_picture"
    if not os.path.exists(folder):
        messagebox.showerror("Error", "No student pictures found.")
        return

    attendance_folder = "attendance"
    if not os.path.exists(attendance_folder):
        os.mkdir(attendance_folder)

    # ======== 3. Load known faces and names ==========
    known_faces = []
    known_names = []

    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            path = os.path.join(folder, filename)
            name = os.path.splitext(filename)[0]  # remove .jpg/.png
            try:
                image = face_recognition.load_image_file(path)
                encoding = face_recognition.face_encodings(image)[0]
                known_faces.append(encoding)
                known_names.append(name)
            except:
                print(f"Skipped unreadable image: {filename}")

    if not known_faces:
        messagebox.showerror("Error", "No known faces found in folder.")
        return

    # ======== 4. Open webcam ==========
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Error", "Camera not detected.")
        return

    messagebox.showinfo(
                        "Info",
                        'Attendance mode started.\n\nPress ESC to stop.\n\nNote:"Please blink to be recognized."'
                        )

    # ======== 5. Start detecting faces ==========
    blink_counters = {}  # To track blinks per face
    blink_flags = {}     # To track if blink has been detected for attendance

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        # Resize frame 
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Detect faces with dlib for landmarks
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_dlib = detector(gray)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.5)
            name = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]

                # Split filename para makuha ang ID at Name
                parts = name.split("_", 2)
                if len(parts) >= 2:
                    _ID = parts[0]
                    _NAME = parts[1]
                else:
                    _ID = "N/A"
                    _NAME = name

                # Anti-spoofing: Check for blink
                face_key = _ID  # Use ID as key
                if face_key not in blink_counters:
                    blink_counters[face_key] = 0
                    blink_flags[face_key] = False

                # Find corresponding dlib face
                for face in faces_dlib:
                    x, y, w, h = face.left(), face.top(), face.width(), face.height()
                    # Approximate match with face_recognition location (scaled back)
                    if abs(x - left*4) < 50 and abs(y - top*4) < 50:  # Tolerance for matching
                        landmarks = predictor(gray, face)
                        landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])

                        # Extract eye coordinates
                        left_eye = landmarks[36:42]
                        right_eye = landmarks[42:48]

                        left_ear = eye_aspect_ratio(left_eye)
                        right_ear = eye_aspect_ratio(right_eye)
                        ear = (left_ear + right_ear) / 2.0

                        if ear < EAR_THRESHOLD:
                            blink_counters[face_key] += 1
                        else:
                            if blink_counters[face_key] >= CONSECUTIVE_FRAMES:
                                blink_flags[face_key] = True
                            blink_counters[face_key] = 0

                        break

                # Only record attendance if blink detected
                if blink_flags.get(face_key, False):
                    # ======== 6. Record attendance ==========
                    now = datetime.datetime.now()
                    date = now.strftime("%m-%d-%Y")
                    time = now.strftime("%I:%M %p")

                    # Avoid duplicate attendance sa table
                    already_present = False
                    for item in table_attendace.get_children():
                        values = table_attendace.item(item, "values")
                        if values[0] == _ID and values[2] == date:
                            already_present = True
                            break

                    if not already_present:
                        # Add to GUI table
                        table_attendace.insert("", "end", values=(_ID, _NAME, date, time))
                        present_count.config(text=str(int(present_count.cget("text")) + 1))
                        window.update()
                        print(f"Attendance recorded for {_NAME} ({_ID})")

                        # ======== 7. Save attendance sa CSV file ==========
                        filename = os.path.join(attendance_folder, f"attendance_{date}.csv")
                        file_exists = os.path.isfile(filename)

                        with open(filename, "a", newline="", encoding="utf-8") as file:
                            writer = csv.writer(file)
                            if not file_exists:
                                writer.writerow(["ID", "Name", "Date", "Time"])
                            writer.writerow([_ID, _NAME, date, time])

                        # Reset blink flag after recording
                        blink_flags[face_key] = False

            # ======== 8. Draw box sa mukha ==========
            for (top, right, bottom, left) in face_locations:
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Attendance", frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC key
            break

    cam.release()
    cv2.destroyAllWindows()

    #ABSENT
    update_absent_count()




#------------------------------------------------------CLOCK
def clock():
    now = datetime.datetime.now()
    day = now.strftime('%B %d, %Y')
    time = now.strftime('%I:%M:%S %p')
    date_label.config(text=f'{day}  |  {time}')
    date_label.after(1000, clock)

#------------------------------------------------------SHOW FRAME_1,2,3
def show_frame1():
    frame1.tkraise()

def show_frame2():
    frame2.tkraise()

def show_frame3():
    frame3.tkraise()

#------------------------------------------------------SAVE STUDENTS TO CSV FILE
def save_students_to_csv_file():

    folder = "Students_Register"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, "students.csv")

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "NAME"])  # header

        for item in table_register.get_children():
            writer.writerow(table_register.item(item, "values"))

#------------------------------------------------------LOAD STUDENT FROM FILE
def load_students_from_file():
    folder = "Students_Register"
    file_path = os.path.join(folder, "students.csv")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) == 2:
                    table_register.insert("", "end", values=(row[0], row[1]))

        update_total_count()


#------------------------------------------------------UPDATE TOTAL STUDENTS
def update_total_count():
    total = len(table_register.get_children())
    total_count.config(text=str(total))

#------------------------------------------------------SORT NAME TO ALPHABETICAL
def sort_name_alphabetical():
    items = table_register.get_children()
    data = []

    for item in items:
        row = table_register.item(item, "values")
        data.append(row)

    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i][1].lower() > data[j][1].lower():
                # Palitan ng pwesto kung hindi alphabetically
                data[i], data[j] = data[j], data[i]

    for item in items:
        table_register.delete(item)

    for row in data:
        table_register.insert("", "end", values=row)


#------------------------------------------------------SUBMIT NEW REGISTER STUDENT
def add_to_table():
    _ID = ID.get()
    _NAME = NAME.get()

    if _ID == "" or _NAME == "":
        messagebox.showwarning("Warning", "Please fill out both ID and NAME")
        return

    if " " in _ID:
        messagebox.showerror("Invalid Input", "ID must not contain spaces!")
        return

    for num in _ID:
        if not (num.isdigit() or num in "-"):
            messagebox.showerror("Invalid Input", "ID must contain numbers only!" )
            return

    for char in _NAME:
        if not (char.isalpha() or char in " .,'ñÑ"):
            messagebox.showerror("Invalid Input", "NAME must contain Letters only!")
            return
    
    #----------- CHECK DUPLICATE ID 
    for item in table_register.get_children():
        if table_register.item(item, "values")[0] == _ID:
            messagebox.showerror("Duplicate ID", "This ID already exists! Please use a unique ID." )
            return

    if _ID.strip() != "" and _NAME.strip() != "":
        table_register.insert("", "end", values=(_ID, _NAME))
        sort_name_alphabetical()
        messagebox.showinfo("Success", f'"{_NAME}" registered successfully!')

    save_students_to_csv_file()

    ID.delete(0, END)
    NAME.delete(0, END)

#------------------------------------------------------DELETE STUDENT
def delete_student():
    selected_item = table_register.selection()

    if not selected_item:
        messagebox.showwarning("Warning", "Please select a student to delete.")
        return
    
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?")
    
    if confirm:
        for item in selected_item:
            values = table_register.item(item, "values")
            student_id = values[0]
            student_name = values[1]
            #DELETE RECORD IN TABLE
            table_register.delete(item)

            #DELETE STUDENT PICTURE
            folder = "students_picture"
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    if filename.startswith(f"{student_id}_") or student_name in filename:
                        file_path = os.path.join(folder, filename)
                        
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")

        messagebox.showinfo("Deleted", "Student record deleted successfully!")

        save_students_to_csv_file()   # <<< SAVE after adding
        update_total_count()      # <<< UPDATE total count

#------------------------------------------------------EDIT STUDENT
def edit_student():
    selected_item = table_register.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to edit.")
        return

    id_val = ID.get()
    name_val = NAME.get()

    if not id_val or not name_val:
        messagebox.showerror("Error", "Please fill out both ID and NAME")
        return

    if " " in id_val:
        messagebox.showerror("Invalid Input", "ID must not contain spaces!")
        return

    allowed_symbols_id = "-"
    for num in id_val:
        if not (num.isdigit() or num in allowed_symbols_id):
            messagebox.showerror("Invalid Input", "ID must contain numbers only!" )
            return

    allowed_symbols_name = " .,'ñÑ"
    for char in name_val:
        if not (char.isalpha() or char in allowed_symbols_name):
            messagebox.showerror("Invalid Input", "NAME must contain Letters only!")
            return
        
    #----------- CHECK DUPLICATE ID 
    for item in table_register.get_children():
        if item != selected_item[0]:
            existing_id = table_register.item(item, "values")[0]
            if existing_id == id_val:
                messagebox.showerror("Duplicate ID", "This ID already exists! Please use a unique ID.")
                return

    table_register.item(selected_item, values=(id_val, name_val))
    messagebox.showinfo("Success", "Record updated successfully!")

    save_students_to_csv_file()   # <<< SAVE after adding
    update_total_count()      # <<< UPDATE total count

    ID.delete(0, END)
    NAME.delete(0, END)

#------------------------------------------------------TAKE IMAGE
def take_picture():

    _ID = simpledialog.askstring("Enter ID", "Please enter your ID to take an image:")
    if not _ID:
        messagebox.showwarning("Warning", "You must enter an ID before taking a picture.")
        return


    student_found = False
    student_name = ""

    folder = "Students_Register"
    file_path = os.path.join(folder, "students.csv")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) == 2 and row[0] == _ID:
                    student_found = True
                    student_name = row[1]
                    break

    if not student_found:
        messagebox.showerror("Error", f"ID '{_ID}' is not registered. Please register the student first.")
        return


    _NAME = student_name

    # --- Open the webcam ---
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Error", "Camera not detected or cannot be opened.")
        return

    # --- Show instructions ---
    messagebox.showinfo(
        "Info",
        f"Taking picture for:\n\n"
        f"ID: {_ID}\n"
        f"Name: {_NAME}\n\n"
        "♦ Press 'SPACE' to take a picture\n"
        "♦ Press 'ESC' to exit camera window"
    )


    # --- Create folder if it doesn't exist ---
    folder = "students_picture"
    if not os.path.exists(folder):
        os.mkdir(folder)

    count = 1  # picture counter

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        cv2.imshow("Camera", frame)
        key = cv2.waitKey(1)

        # SPACE = take picture
        if key == 32:
            filename = f"{folder}/{_ID}_{_NAME}_{count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved as {_ID}_{_NAME}_{count}.jpg")
            count += 1

        # ESC = exit
        elif key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

#------------------------------------------------------SAVE PROFILE
def _SAVE_():
    save_students_to_csv_file()
    messagebox.showinfo("Success", "Save Profile Successfully")

    update_total_count()




###########################################   GUI FRONT-END   ###########################################   
window = Tk()
window.title('BSIT1-07')
window.geometry('1280x720')
window.config(bg='#3A3938')

#------------------------------------------------------TITLE NAME
Label(window, 
    text='📅 NeoAttend',
    font=('ink free', 55, 'bold'),
    fg='white', 
    bg='#3A3938'
).pack(fill='x', pady=20)

#------------------------------------------------------DATE AND TIME

date_label = Label(window, 
    fg='orange',
    bg='#3A3938',
    font=('Times', 20, 'bold'),
    anchor='e',
    padx=20)
date_label.place(relx=0.59, rely=0.16)
clock()

#------------------------------------------------------ MENU FRAME

menu_frame = Frame(window, bg='#1E1E1E', bd=2, relief='raised')
menu_frame.place(relx=0.09, rely=0.22, relwidth=0.22, relheight=0.70)
menu_frame.pack_propagate(False)

#------------------------------------------------------ CONTENT FRAME
content_frame = Frame(window, bg='#1E1E1E', bd=2, relief='raised')
content_frame.place(relx=0.32, rely=0.22, relwidth=0.59, relheight=0.70)

#------------------------------------------------------ WINDOW 1,2,3
frame1 = Frame(content_frame, bg='#1E1E1E')
frame2= Frame(content_frame, bg='#1E1E1E')
frame3 = Frame(content_frame, bg='#1E1E1E')

for frame in (frame1, frame2, frame3):
    frame.place(relwidth=1, relheight=1)
#------------------------------------------------------ MENU
frame_title = Frame(menu_frame, bg='#545353', bd=2)
frame_title.pack(fill='x', pady=(0,5))

Label(
    frame_title,
    text='🏠︎ MENU',
    font=('Segoe UI', 25, 'bold'),
    bg='#545353',
    fg='#FFFFFF',
).pack(fill='x')

#------------------------------------------------------ MENU BUTTONS
Button(
    menu_frame,
    text='📸 Take Attendance',
    font=('Calibri', 18, 'bold'),
    bg='#2D2D2D',
    fg='#00C851',
    relief='flat',
    command=show_frame1
).pack(padx=15, pady=15, fill='x')

Button(
    menu_frame,
    text='📊 Attendance Reports',
    font=('Calibri', 18, 'bold'),
    bg='#2D2D2D',
    fg='#2196F3',
    relief='flat',
    command=show_frame2
).pack(padx=15, pady=(5,15), fill='x')

Frame(menu_frame, bg='#545353', width=300, height=5).pack(padx=15)

Button(
    menu_frame,
    text='👤 New Registration',
    font=('Calibri', 18, 'bold'),
    bg='#2D2D2D',
    fg='#FFC107',
    relief='flat',
    command=show_frame3
).pack(padx=15, pady=15, fill='x')


#-------------------------------------------------------------------------WINDOW 1
frame_title = Frame(frame1, bg='#545353', bd=2)
frame_title.pack(fill='x', pady=(0,5))

Label(
    frame_title,
    text='📸 Take Attendance',
    fg='white',
    bg='#545353',
    font=('Comic Sans', 28,'bold')
).pack()


photo = PhotoImage(file='pic.png')
pic_icon = Frame(frame1, bg='#2D2D2D', )
pic_icon.place(relx=0.05, rely=0.15, relheight=0.50, relwidth=0.50)

TAKE_ATTENDANCE__PIC_BTN = Button(pic_icon, image=photo, command=take_attendance)
TAKE_ATTENDANCE__PIC_BTN.pack()

TAKE_ATTENDANCE_BTN = Button(frame1, 
    text='📸Take attendance',
    font=('Comic Sans', 20, 'bold'),
    bg='#2D2D2D',
    fg='#00C851',
    command=take_attendance
)
TAKE_ATTENDANCE_BTN.place(relx=0.05, rely=0.68, relwidth=0.50)

#-------------------------------------------------------------------
present = Frame(frame1, bg='#54B749', bd=5, relief='sunken')
present.place(relx=0.60, rely=0.15, relheight=0.25, relwidth=0.35)

absent = Frame(frame1, bg='#DB2E2E', bd=5, relief='sunken')
absent.place(relx=0.60, rely=0.44, relheight=0.25, relwidth=0.35)

total = Frame(frame1, bg='#0400FF',  bd=5, relief='sunken')
total.place(relx=0.60, rely=0.73, relheight=0.25, relwidth=0.35)
#-------------------------------------------------------------------

Label(present,
    text='PRESENT',
    fg='#FFFFFF',
    bg='#54B749',
    font=('times', 20, 'bold')).pack()

present_count =Label(present,
    text='0',
    fg='#FFFFFF',
    bg='#54B749',
    font=('times', 50, 'bold'))
present_count.pack()

#-------------------------------------------------------------------
Label(absent,
    text='ABSENT',
    fg='#FFFFFF',
    bg='#DB2E2E',
    font=('times', 20, 'bold')).pack()

absent_count =Label(absent,
    text='0',
    fg='#FFFFFF',
    bg='#DB2E2E',
    font=('times', 50, 'bold'))
absent_count.pack()

#-------------------------------------------------------------------
Label(total,
    text='STUDENT TOTAL',
    fg='#FFFFFF',
    bg='#0400FF',
    font=('times', 20, 'bold')).pack()

total_count =Label(total,
    text='0',
    fg='#FFFFFF',
    bg='#0400FF',
    font=('times', 50, 'bold'))
total_count.pack()


#-------------------------------------------------------------------------WINDOW 2


#------------------------------------ATTENDANCE TABLE
frame_title = Frame(frame2, bg='#545353', bd=2)
frame_title.pack(fill='x', pady=(0,5))

Label(
    frame_title,
    text='📊 Attendance Reports',
    fg='white',
    bg='#545353',
    font=('Comic Sans', 28, 'bold')).pack()


table_attendace = ttk.Treeview(frame2, columns=('ID', 'NAME', 'DATE', 'TIME'), show='headings')

table_attendace.heading('ID', text='ID')
table_attendace.heading('NAME', text='NAME')
table_attendace.heading('DATE', text='DATE')
table_attendace.heading('TIME', text='TIME')

table_attendace.column('ID', width=125, anchor='center')
table_attendace.column('NAME', width=250, anchor='w')
table_attendace.column('DATE', width=125, anchor='center')
table_attendace.column('TIME', width=125, anchor='center')

table_attendace.place(relx=0.02, rely=0.15, relheight=0.80, relwidth=0.95)

scroll = Scrollbar(frame2, orient=VERTICAL, command=table_attendace.yview)
table_attendace.configure(yscrollcommand=scroll.set)
scroll.pack(side=RIGHT, fill=Y)


#------------------------------------------------------ WINDOW 3
frame_title = Frame(frame3, bg='#545353', bd=2)
frame_title.pack(fill='x', pady=(0,5))

Label(
    frame_title,
    text='👤 Registration Page',
    fg='white',
    bg='#545353',
    font=('Comic Sans', 28, 'bold')).pack()


Label(
    frame3,
    text='Enter ID',
    fg='#FFFFFF',
    bg='#1E1E1E',
    font=('times', 25, 'bold')
).place(relx=0.03, rely=0.15)

Label(
    frame3,
    text='Enter Name',
    fg='#FFFFFF',
    bg='#1E1E1E',
    font=('times', 25, 'bold')
).place(relx=0.03, rely=0.35)

Label(
    frame3,
    text='1)Take Images  >>>  2)Save Profile',
    fg='#FFFFFF',
    bg='#1E1E1E',
    font=('times', 15, 'bold')
).place(relx=0.05, rely=0.68,relwidth=0.41)


ID = Entry(frame3,
    font=('times', 20),
    bg='#4A4949',
    fg='#FFFFFF')
ID.place(relx=0.06, rely=0.24, relwidth=0.40)

NAME = Entry(frame3,
    font=('times', 20),
    bg='#4A4949',
    fg='#FFFFFF')
NAME.place(relx=0.06, rely=0.44, relwidth=0.40)


SUBMIT = Button(frame3,
    text='📩Submit',
    font=('times', 17, 'bold'),
    fg='#00FF00',
    bg='#4A4949',
    command=add_to_table
)
SUBMIT.place(relx=0.05, rely=0.56, relwidth=0.16)

DELETE = Button(frame3,
    text='🗑Delete Student',
    font=('times', 17, 'bold'),
    fg='#FF4C4C',
    bg='#4A4949',
    command=delete_student
)
DELETE.place(relx=0.22, rely=0.56, relwidth=0.24)

TAKE = Button(frame3,
    text='🤳Take Images',
    font=('times', 17, 'bold'),
    fg='#FEA310',
    bg='#4A4949',
    command=take_picture
)
TAKE.place(relx=0.05, rely=0.75, relwidth=0.41)

SAVE = Button(frame3,
    text='🔏Save Profile',
    font=('times', 17, 'bold'),
    fg='#FFFFFF',
    bg='#4A4949',
    command=_SAVE_
)
SAVE.place(relx=0.05, rely=0.87, relwidth=0.41)

EDIT = Button(frame3,
    text='🖍EDIT',
    font=('times', 11, 'bold'),
    fg='#FFFFFF',
    bg='#4A4949',
    command=edit_student
)
EDIT.place(relx=0.82, rely=0.93, relwidth=0.15)

#------------------------------------------------------ REGISTER TABLE
style = ttk.Style()
style.theme_use('clam')

style.configure('Treeview',
    background='#4A4949',
    foreground='#FFFFFF',
    rowheight=30,  
    fieldbackground='#4A4949',
    font=('times', 14))

style.configure('Treeview.Heading',
    background='#FFFFFF',
    foreground='#000000',
    font=('Calibri', 16, 'bold'))

table_register = ttk.Treeview(frame3, columns=('ID', 'NAME'), show='headings')

table_register.heading('ID', text='ID')
table_register.heading('NAME', text='NAME')

table_register.column('ID', width=150, anchor='center')
table_register.column('NAME', width=250, anchor='w')

table_register.place(relx=0.48, rely=0.12, relheight=0.80, relwidth=0.49)

scroll = Scrollbar(frame3, orient=VERTICAL, command=table_register.yview)
table_register.configure(yscrollcommand=scroll.set)
scroll.pack(side=RIGHT, fill=Y)

#--------------------------------------------------------------------
load_students_from_file()

show_frame1()

def update_absent_count():
    total = len(table_register.get_children())
    present = int(present_count.cget("text"))
    absent = total - present
    absent_count.config(text=str(absent))


window.mainloop()
