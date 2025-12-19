# MediTrack - Hospital Management System  

A complete Hospital Management System with role-based login (Admin, Doctor, Patient), appointment booking, medical records, and performance comparison of QuickSort, MergeSort & HeapSort.

## Features
- Login/Registration for Admin, Doctors & Patients
- Appointment scheduling with conflict detection
- View & sort medical records using HeapSort (Ascending/Descending)
- Real-time sorting algorithm performance timing + Matplotlib graphs
- Beautiful Tkinter GUI with modern theme

## Tech Stack
- Python + Tkinter (Frontend)
- MySQL (Backend)
- Matplotlib (Graphs)
- Custom implementations of HeapSort, MergeSort, QuickSort

## Database Setup (1-click)
1. Install MySQL + create database `jani`
2. Run the file `meditrack_database.sql` → 50 patients, 15 doctors, 60+ appointments ready!

## How to Run
```bash
pip install mysql-connector-python tkcalendar matplotlib
python "PYTHON CODE.py"
