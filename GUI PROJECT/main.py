from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import datetime
import csv
import os
import cv2
import face_recognition
import winsound
import re

#############################################   FUNCTION   ##############################################

attendance_saved = False

#------------------------------------------------------TAKE ATTENDANCE
def take_attendance():

    folder = "students_picture"
    if not os.path.exists(folder):
        messagebox.showerror("Error", "No student pictures found.")
        return

    attendance_folder = "attendance"
    if not os.path.exists(attendance_folder):
        os.mkdir(attendance_folder)

    # ======== Load known faces and names ==========
    known_faces = []
    known_names = []

    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            path = os.path.join(folder, filename)
            name = os.path.splitext(filename)[0]
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

    # ======== Open webcam ==========
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Error", "Camera not detected.")
        return

    messagebox.showinfo("Info", "Attendance mode started.\nPress ESC to stop.")

    # ======== Start detecting faces ==========
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

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.45)
            name = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]


                parts = name.split("_", 2)
                if len(parts) >= 2:
                    _ID = parts[0]
                    _NAME = parts[1]
                else:
                    _ID = "N/A"
                    _NAME = name


                # ======== Record attendance ==========
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
                    winsound.Beep(2000, 300)
                    print(f"Attendance recorded for {_NAME} ({_ID})")


                    # ======== AUTO SAVE FACE PICTURE FOR VALIDATION ==========
                    picture_folder = os.path.join("attendance_pictures", date)
                    if not os.path.exists(picture_folder):
                        os.makedirs(picture_folder)

                    timestamp = now.strftime("%H-%M-%S")
                    pic_filename = f"{_ID}_{_NAME}_{timestamp}.jpg"
                    pic_path = os.path.join(picture_folder, pic_filename)

                    # TAKE PICTURE AFTER RECOGNIZING FACE FOR VALIDATION
                    cv2.imwrite(pic_path, frame)
                    print(f"Saved validation image: {pic_path}")


            # ======== Draw box sa mukha ==========
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
active_button = None

def set_active_button(button):
    global active_button

    if active_button:
        active_button.config(bg='#2D2D2D')

    button.config(bg='#545353')
    active_button = button

def show_frame1():
    frame1.tkraise()
    set_active_button(btn1)

def show_frame2():
    frame2.tkraise()
    set_active_button(btn2)

def show_frame3():
    frame3.tkraise()
    set_active_button(btn3)
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

#--------------------------------------------------------------SAVE ATTENDANCE TO CSV
def save_attendance_to_csv():
    global attendance_saved

    if len(table_register.get_children()) == 0:
        messagebox.showinfo("Info", "No registered students to save.")
        return

    attendance_folder = "attendance"
    if not os.path.exists(attendance_folder):
        os.mkdir(attendance_folder)

    now = datetime.datetime.now()
    date = now.strftime("%m-%d-%Y")
    filename = os.path.join(attendance_folder, f"attendance_{date}.csv")

    # --- Collect present and absent students ---
    present_students = []
    absent_students = []

    # Registered students
    registered_students = {}
    for item in table_register.get_children():
        reg_id, reg_name = table_register.item(item, "values")
        registered_students[reg_id] = reg_name

    # Present students
    present_ids = set()
    for item in table_attendace.get_children():
        _ID, _NAME, _DATE, _TIME = table_attendace.item(item, "values")
        present_students.append([_ID, _NAME, _DATE, _TIME, "PRESENT"])
        present_ids.add(_ID)

    # Absent students
    for reg_id, reg_name in registered_students.items():
        if reg_id not in present_ids:
            absent_students.append([reg_id, reg_name, date, "", "ABSENT"])

    # --- Write to CSV ---
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Date", "Time", "Status"])

        # Write present students first
        for row in present_students:
            writer.writerow(row)

        # Add blank line before absent
        if absent_students:
            writer.writerow([])

        # Write absent students
        for row in absent_students:
            writer.writerow(row)

    attendance_saved = True
    messagebox.showinfo("Success", f"Attendance saved to {filename}")


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

                data[i], data[j] = data[j], data[i]

    for item in items:
        table_register.delete(item)

    for row in data:
        table_register.insert("", "end", values=row)


#------------------------------------------------------SUBMIT NEW REGISTER STUDENT
def add_to_table():
    _ID = ID.get()
    _NAME = NAME.get().upper()

    if _ID == "" or _NAME == "":
        messagebox.showwarning("Warning", "Please fill out both ID and NAME")
        return
    
    # VALIDATE NAME FORMAT: LASTNAME, FIRSTNAME MIDDLENAME
    name_pattern = r"^[A-Za-zÑñ .'’-]+,\s*[A-Za-zÑñ .'’-]+\s+[A-Za-zÑñ .'’-]+$"

    if not re.fullmatch(name_pattern, _NAME):
        messagebox.showerror(
            "Invalid Name Format",
            "Please follow format:\n\nLASTNAME, FIRSTNAME MIDDLENAME\n\nExample:\nDELA CRUZ, JUAN REYES"
        )
        return


    if not re.fullmatch(r"01-\d{6}", _ID):
        messagebox.showerror("Invalid ID", "Please follow the ID format: 01-xxxxxx (6 digits)")
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
            winsound.Beep(1000, 200)

        # ESC = exit
        elif key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()


# -------------------------------------------------------------RIGHT CLICK TO EDIT AND DELETE

def save_changes(edit_win, selected_item, NEW_ID, NEW_NAME):
    new_id = NEW_ID.get().strip()
    new_name = NEW_NAME.get().strip().upper()

    if not new_id or not new_name:
        messagebox.showerror("Error", "Please fill out both ID and NAME")
        return
    
    # VALIDATE NAME FORMAT: LASTNAME, FIRSTNAME MIDDLENAME
    name_pattern = r"^[A-Za-zÑñ .'’-]+,\s*[A-Za-zÑñ .'’-]+\s+[A-Za-zÑñ .'’-]+$"

    if not re.fullmatch(name_pattern, new_name):
        messagebox.showerror(
            "Invalid Name Format",
            "Please follow format:\n\nLASTNAME, FIRSTNAME MIDDLENAME\n\nExample:\nDELA CRUZ, JUAN REYES"
        )
        return

    

    if not re.fullmatch(r"01-\d{6}", new_id):
        messagebox.showerror("Invalid ID", "Please follow the ID format: 01-xxxxxx (6 digits)")
        return

    # NAME validation
    for char in new_name:
        if not (char.isalpha() or char in " .,'ñÑ"):
            messagebox.showerror("Invalid Input", "NAME must contain letters only!")
            return

    # Check duplicate ID
    for item in table_register.get_children():
        if item != selected_item[0]:
            existing_id = table_register.item(item, "values")[0]
            if existing_id == new_id:
                messagebox.showerror("Duplicate ID", "This ID already exists!")
                return

    # Update table
    table_register.item(selected_item, values=(new_id, new_name))
    save_students_to_csv_file()
    update_total_count()
    messagebox.showinfo("Success", "Record updated successfully!")
    edit_win.destroy()

#------------------------------------------------------EDIT STUDENT
def edit_student():
    selected_item = table_register.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to edit.")
        return

    # Get current values
    current_id, current_name = table_register.item(selected_item, "values")
    

#-------------------------------------------------------WINDOW FOR EDITING ID AND NAME
    # Create a small popup window for editing
    edit_win = Toplevel(window)
    edit_win.title("Edit Student")
    edit_win.geometry("300x200")
    edit_win.config(bg='#3A3938')
    edit_win.grab_set()  # Makes it modal

#----------------------------------------------
    Label(edit_win, 
        text="ID:", 
        bg='#3A3938', 
        fg='#FFFFFF', 
        font=('times', 20, 'bold')).place(relx=0.45, rely=0.05)
    
    NEW_ID = Entry(edit_win, 
                    bg='#4A4949', 
                    fg='#FFFFFF', 
                    font=('times', 15))
    NEW_ID.place(relx=0.25, rely=0.22, relwidth=0.55)
    NEW_ID.insert(0, current_id)

#----------------------------------------------
    Label(edit_win, 
        text="Name:", 
        bg='#3A3938', 
        fg='#FFFFFF', 
        font=('times', 20, 'bold')).place(relx=0.40, rely=0.38)
    
    NEW_NAME = Entry(edit_win, 
                    bg='#4A4949', 
                    fg='#FFFFFF', 
                    font=('times', 15))
    NEW_NAME.place(relx=0.25, rely=0.55, relwidth=0.55)
    NEW_NAME.insert(0, current_name)

#----------------------------------------------SAVE BUTTON FUNCTION FOR EDIT ID & NAME
    def save_button_clicked():
        save_changes(edit_win, selected_item, NEW_ID, NEW_NAME)

    #--------------SAVE BUTTON
    Button(edit_win, text="Save", bg='#4A4949', fg="#FFFFFF", font=('calibri', 15, 'bold'),
        command=save_button_clicked).place(relx=0.35, rely=0.79, relwidth=0.35, relheight=0.15)


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


def show_context_menu(event):
    selected_item = table_register.identify_row(event.y)
    if selected_item:
        table_register.selection_set(selected_item)
        context_menu.entryconfig("Edit", command=edit_student)
        context_menu.entryconfig("Delete", command=delete_student)
        context_menu.post(event.x_root, event.y_root)




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
btn1 = Button(
    menu_frame,
    text='📸 Take Attendance',
    font=('Calibri', 18, 'bold'),
    bg='#2D2D2D',
    fg='#00C851',
    relief='flat',
    command=show_frame1
)
btn1.pack(padx=15, pady=15, fill='x')

btn2 = Button(
    menu_frame,
    text='📊 Attendance Reports',
    font=('Calibri', 18, 'bold'),
    bg='#2D2D2D',
    fg='#2196F3',
    relief='flat',
    command=show_frame2
)
btn2.pack(padx=15, pady=(5,15), fill='x')

Frame(menu_frame, bg='#545353', width=300, height=5).pack(padx=15)

btn3 = Button(
    menu_frame,
    text='👤 Registration Page',
    font=('Calibri', 18, 'bold'),
    bg='#2D2D2D',
    fg='#FFC107',
    relief='flat',
    command=show_frame3
)
btn3.pack(padx=15, pady=15, fill='x')


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

table_attendace.place(relx=0.02, rely=0.12, relheight=0.80, relwidth=0.95)

table_attendace.column('ID', width=80, anchor='center')
table_attendace.column('NAME', width=300, anchor='w')
table_attendace.column('DATE', width=80, anchor='center')
table_attendace.column('TIME', width=80, anchor='center')

scroll = Scrollbar(frame2, orient=VERTICAL, command=table_attendace.yview)
table_attendace.configure(yscrollcommand=scroll.set)
scroll.pack(side=RIGHT, fill=Y)


SAVE_ATTENDANCE_BTN1= Button(frame2,
    text='📝SAVE',
    font=('times', 11, 'bold'),
    fg='#FFFFFF',
    bg='#4A4949',
    command=save_attendance_to_csv
)
SAVE_ATTENDANCE_BTN1.place(relx=0.82, rely=0.93, relwidth=0.15)

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
    text='Enter ID:',
    fg='#FFFFFF',
    bg='#1E1E1E',
    font=('times', 25, 'bold')
).place(relx=0.01, rely=0.15)

Label(
    frame3,
    text='(e.g. 01-xxxxx)',
    fg='#800080',
    bg='#1E1E1E',
    font=('calibri', 14, 'bold')
).place(relx=0.05, rely=0.22)


Label(
    frame3,
    text='Enter Full Name:',
    fg='#FFFFFF',
    bg="#1E1E1E",
    font=('times', 25, 'bold')
).place(relx=0.01, rely=0.37)

Label(
    frame3,
    text='(e.g. DELA CRUZ, JUAN REYES)',
    fg='#800080',
    bg='#1E1E1E',
    font=('calibri', 14, 'bold')
).place(relx=0.05, rely=0.44)

Label(
    frame3,
    text='1)Take Images  >>>  2)Save Profile',
    fg='#FFFFFF',
    bg='#1E1E1E',
    font=('times', 15, 'bold')
).place(relx=0.03, rely=0.72,relwidth=0.41)


ID = Entry(frame3,
    font=('times', 20),
    bg='#4A4949',
    fg='#FFFFFF')
ID.place(relx=0.03, rely=0.28, relwidth=0.41)

NAME = Entry(frame3,
    font=('times', 20),
    bg='#4A4949',
    fg='#FFFFFF')
NAME.place(relx=0.03, rely=0.50, relwidth=0.41)


SUBMIT = Button(frame3,
    text='📩Submit',
    font=('times', 17, 'bold'),
    fg='#00FF00',
    bg='#4A4949',
    command=add_to_table
)
SUBMIT.place(relx=0.03, rely=0.60, relwidth=0.41)

DELETE = Button(frame3,
    text='🗑Delete',
    font=('times', 11, 'bold'),
    fg='#FFFFFF',
    bg='#4A4949',
    command=delete_student
)
DELETE.place(relx=0.66, rely=0.93, relwidth=0.15)

TAKE = Button(frame3,
    text='🤳Take Images',
    font=('times', 17, 'bold'),
    fg='#FEA310',
    bg='#4A4949',
    command=take_picture
)
TAKE.place(relx=0.03, rely=0.79, relwidth=0.41)

SAVE = Button(frame3,
    text='🔏Save Profile',
    font=('times', 17, 'bold'),
    fg='#FFFFFF',
    bg='#4A4949',
    command=_SAVE_
)
SAVE.place(relx=0.03, rely=0.89, relwidth=0.41)

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
    font=('times', 12))

style.configure('Treeview.Heading',
    background='#FFFFFF',
    foreground='#000000',
    font=('Calibri', 16, 'bold'))

table_register = ttk.Treeview(frame3, columns=('ID', 'NAME'), show='headings')

table_register.heading('ID', text='ID')
table_register.heading('NAME', text='NAME')

table_register.column('ID', width=85, anchor='center')
table_register.column('NAME', width=300, anchor='w')

table_register.place(relx=0.45, rely=0.12, relheight=0.80, relwidth=0.52)

scroll = Scrollbar(frame3, orient=VERTICAL, command=table_register.yview)
table_register.configure(yscrollcommand=scroll.set)
scroll.pack(side=RIGHT, fill=Y)


# ------------------- Right-click context menu -------------------
context_menu = Menu(window, tearoff=0)
context_menu.add_command(label="Edit", command=None)
context_menu.add_command(label="Delete", command=None)


table_register.bind("<Button-3>", show_context_menu)  # Right-click

#--------------------------------------------------------------------
load_students_from_file()

show_frame1()

def update_absent_count():
    total = len(table_register.get_children())
    present = int(present_count.cget("text"))
    absent = total - present
    absent_count.config(text=str(absent))


def on_closing():
    global attendance_saved
    if len(table_attendace.get_children()) > 0 and not attendance_saved:
        answer = messagebox.askyesno("Save Attendance", "Do you want to save attendance before exiting?")
        if answer:
            save_attendance_to_csv()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()
