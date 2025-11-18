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

<img width="1200" src="https://github.com/user-attachments/assets/03a82458-e503-4282-a5ce-2081a1eefd6a" />

<img width="1200" src="https://github.com/user-attachments/assets/966bce4c-1a8e-4bdc-a1fe-9694328bb37c" />

<img width="1200" src="https://github.com/user-attachments/assets/0e3a54ed-6b6d-46cb-9959-3c67392bfee1" />

<img width="1200" src="https://github.com/user-attachments/assets/9ef2ee64-23f0-47c5-aa45-4548f5506275" />


---

## **🔁 Flowchart**

<img width="834" src="https://github.com/user-attachments/assets/699e187a-1b3e-4b9d-835e-06ec7381821a" />

<img width="822" src="https://github.com/user-attachments/assets/c6a9e22a-7024-4013-9eae-24ed14857541" />

<img width="523" src="https://github.com/user-attachments/assets/f241fee2-c624-4fdd-a8c6-bfbe2291080f" />

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

