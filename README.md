# **NeoAttend**

A Smart Facial Recognition Attendance System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.7.0.72-red)
![Face\_Recognition](https://img.shields.io/badge/face__recognition-Enabled-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## **📖 Table of Contents**

* [About the Project](#about-the-project)
* [Features](#features)
* [Wireframe](#wireframe)
* [Flowchart](#flowchart)
* [How It Works](#how-it-works)
* [Installation](#installation)

---

## **📌 About the Project**

**NeoAttend** is a desktop-based attendance system using **facial recognition** to automatically detect students, log attendance, and store proof images for verification and anti-spoofing.
Built with **Python, OpenCV, and face_recognition**, it is designed for classrooms and small groups needing fast and organized attendance tracking.

---

## **🚀 Features**

* Automatically detects and recognizes students through the webcam and records attendance with the correct date and time.

* Saves a photo of each recognized student for proof, validation, and anti-spoofing review, allowing teachers to verify if the image was taken live or from a phone screen.

* Allows users to register students, validate their information, and capture images directly through the webcam for recognition.

* Displays recorded attendance in a table and allows saving daily attendance into a CSV file for easy tracking and documentation.

* Includes tools to edit or delete student information. When a student is removed, their stored images are also deleted automatically to keep the files clean.

* Shows a live clock and date on the main window for easy monitoring.

---

## **🧩 Wireframe**

<img width="1200" src="https://github.com/user-attachments/assets/4688c683-6831-4adc-918f-7546d54feae1" />

<img width="1200" src="https://github.com/user-attachments/assets/7dbce89b-7112-4fcf-97fe-5c2de1123107" />

<img width="1200" src="https://github.com/user-attachments/assets/c468273c-c049-4cdf-93b2-968f655c6fde" />

<img width="1200" src="https://github.com/user-attachments/assets/24d0992c-7959-4b8d-b928-d276007aa6f4" />


---

## **🔁 Flowchart**

<img width="834" src="https://github.com/user-attachments/assets/2cf44bbb-9e9f-4aff-99a6-7cfb3a0ea2ef" />

<img width="824" src="https://github.com/user-attachments/assets/38f400ce-8c23-4ece-b479-943416ec5acd" />

<img width="532" src="https://github.com/user-attachments/assets/0b7e37d2-db31-40ab-941a-1d5e2352da5c" />

---

## **⚙️ How It Works**

1. **Load Student Encodings**
   Student images are processed and converted into encodings for face matching.

2. **Start Webcam Feed**
   The system detects faces in real time.

3. **Face Recognition**

   * Matches detected faces with stored encodings.
   * Logs attendance automatically when a match is found.

4. **Attendance Logging**
   Saves student name, date, time, and a captured proof image.

5. **Data Management**
   Students can be added, updated, deleted, and attendance can be exported.

---

## **📦 Installation**

Install the required libraries:

```sh
pip install opencv-python==4.7.0.72
pip install numpy==1.26.4
pip install cmake
pip install path        # (copy the path of the Dlib-library installation)
pip install face_recognition
```

