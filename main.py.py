import tkinter as tk
import random
from tkinter import messagebox, ttk, simpledialog, Toplevel
import mysql.connector
from tkcalendar import DateEntry
from datetime import datetime
import time

# Database Connection Utility
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",  # Update your password as needed
        database="jani"   # Ensure correct database name
    )

# Theme Utility Function
def apply_theme(window):
    style = ttk.Style()
    style.theme_use('clam')
    window.configure(bg="#f0f0f0")
    style.configure("TButton", font=("Arial", 11), padding=8, background="#4CAF50", foreground="white")
    style.map("TButton", background=[("active", "#45a049")])
    style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
    style.configure("TFrame", background="#f0f0f0")
    style.configure("Treeview", font=("Arial", 10), rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

# Role Selection Class
class RoleSelection:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Role Selection")
        master.geometry("300x200")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(expand=True)

        ttk.Label(main_frame, text="Select Your Role:", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)
        self.selected_role = tk.StringVar(value="Admin")
        roles = ["Admin", "Doctors", "Patients"]
        ttk.Combobox(main_frame, textvariable=self.selected_role, values=roles, state="readonly").grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(main_frame, text="Continue", command=self.open_registration_form).grid(row=2, column=0, pady=10)
        ttk.Button(main_frame, text="Back to Login", command=self.back_to_login).grid(row=2, column=1, pady=10)

    def open_registration_form(self):
        role = self.selected_role.get()
        self.master.destroy()
        root = tk.Tk()
        RegistrationForm(root, role)
        root.mainloop()

    def back_to_login(self):
        self.master.destroy()
        root = tk.Tk()
        MediTrackApp(root)
        root.mainloop()

# Registration Form Class
class RegistrationForm:
    def __init__(self, master, role):
        self.master = master
        self.role = role
        master.title(f"MediTrack - {role} Registration")
        master.geometry("400x500")
        apply_theme(master)
        self.entries = {}

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text=f"{role} Registration", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        fields = {
            "Admin": ["full_name", "contact_number", "email", "password"],
            "Doctors": ["first_name", "last_name", "specialization", "working_hours", "contact_number", "email", "password"],
            "Patients": ["first_name", "last_name", "date_of_birth", "gender", "contact_number", "address", "email", "password"]
        }

        for i, field_name in enumerate(fields[role], start=1):
            ttk.Label(main_frame, text=f"{field_name.replace('_', ' ').title()}:").grid(row=i, column=0, pady=10, sticky="e")
            entry = ttk.Entry(main_frame, width=30, show="*" if field_name == "password" else None)
            entry.grid(row=i, column=1, pady=10, sticky="w")
            self.entries[field_name] = entry

        ttk.Button(main_frame, text="Register", command=self.register_user).grid(row=len(fields[role]) + 1, column=0, columnspan=2, pady=20)
        ttk.Button(main_frame, text="Back", command=self.back_to_role_selection).grid(row=len(fields[role]) + 2, column=0, columnspan=2, pady=10)

    def register_user(self):
        db = connect_db()
        cursor = db.cursor()
        data = {field: entry.get().strip() for field, entry in self.entries.items()}
        
        try:
            table = self.role
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            db.commit()
            db.close()
            messagebox.showinfo("Success", f"{self.role} registered successfully!")
            self.master.destroy()
            root = tk.Tk()
            MediTrackApp(root)
            root.mainloop()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")
            db.rollback()
            db.close()

    def back_to_role_selection(self):
        self.master.destroy()
        root = tk.Tk()
        RoleSelection(root)
        root.mainloop()

# Login System
class MediTrackApp:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Login")
        master.geometry("400x300")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(expand=True)

        ttk.Label(main_frame, text="Welcome to MediTrack", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(main_frame, text="Email ID:").grid(row=1, column=0, sticky="e", pady=10)
        self.email_entry = ttk.Entry(main_frame, width=30)
        self.email_entry.grid(row=1, column=1, pady=10)

        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky="e", pady=10)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=10)

        ttk.Button(main_frame, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=20)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter both Email and Password.")
            return
        
        db = connect_db()
        cursor = db.cursor()
        query = """
        SELECT 'Admin' as role FROM Admin WHERE email = %s AND password = %s
        UNION
        SELECT 'Doctors' as role FROM Doctors WHERE email = %s AND password = %s
        UNION
        SELECT 'Patients' as role FROM Patients WHERE email = %s AND password = %s
        """
        cursor.execute(query, (email, password, email, password, email, password))
        result = cursor.fetchone()
        db.close()
        
        if result:
            role = result[0]
            messagebox.showinfo("Success", f"Login successful as {role}!")
            self.redirect_user(role)
        else:
            if messagebox.askyesno("Not Registered", "Email not registered. Do you want to register now?"):
                self.master.destroy()
                root = tk.Tk()
                RoleSelection(root)
                root.mainloop()
            else:
                messagebox.showerror("Error", "Incorrect email or password.")
    
    def redirect_user(self, role):
        self.master.destroy()
        root = tk.Tk()
        if role == "Admin":
            AdminDashboard(root)
        elif role == "Doctors":
            DoctorDashboard(root)
        elif role == "Patients":
            PatientDashboard(root)
        root.mainloop()

# Admin Dashboard Class
class AdminDashboard:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Admin Dashboard")
        master.geometry("700x500")
        apply_theme(master)

        sidebar = ttk.Frame(master, width=200, relief="raised", borderwidth=1)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        header = ttk.Frame(master, height=50)
        header.pack(side="top", fill="x", padx=10, pady=10)
        ttk.Label(header, text="Admin Dashboard", font=("Arial", 18, "bold")).pack(pady=10)

        buttons = [
            ("Manage Patients", self.open_manage_patients),
            ("Sort Appointments", self.open_sort_appointments),
            ("Manage Doctors", self.open_manage_doctors),
            ("View System Reports", self.view_reports),
            ("Logout", self.logout)
        ]
        for text, cmd in buttons:
            ttk.Button(sidebar, text=text, command=cmd, width=20).pack(pady=10, padx=5)

        self.content = ttk.Frame(master)
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(self.content, text="Welcome to the Admin Dashboard", font=("Arial", 14)).pack(pady=20)

        ttk.Button(self.content, text="Back to Login", command=self.back_to_login).pack(pady=10)

    def open_manage_patients(self):
        self.master.destroy()
        root = tk.Tk()
        ManagePatients(root)
        root.mainloop()

    def open_sort_appointments(self):
        self.master.destroy()
        root = tk.Tk()
        SortAppointments(root)
        root.mainloop()

    def open_manage_doctors(self):
        self.master.destroy()
        root = tk.Tk()
        ManageDoctors(root)
        root.mainloop()

    def view_reports(self):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM Patients")
        patient_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Appointments")
        appointment_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Doctors")
        doctor_count = cursor.fetchone()[0]
        db.close()
        messagebox.showinfo("System Reports", f"Total Patients: {patient_count}\nTotal Appointments: {appointment_count}\nTotal Doctors: {doctor_count}")

    def logout(self):
        self.master.destroy()

    def back_to_login(self):
        self.master.destroy()
        root = tk.Tk()
        MediTrackApp(root)
        root.mainloop()

# Manage Patients with QuickSort Timing
class ManagePatients:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Manage Patients")
        master.geometry("800x600")
        apply_theme(master)

        header = ttk.Frame(master)
        header.pack(fill="x", padx=10, pady=10)
        ttk.Label(header, text="Manage Patients", font=("Arial", 16, "bold")).pack(pady=5)

        control_frame = ttk.Frame(master)
        control_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(control_frame, text="Search Patient by ID:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.search_var).pack(side="left", padx=5)
        self.search_var.trace("w", self.dynamic_search)

        ttk.Label(control_frame, text="Sort By:").pack(side="left", padx=5)
        self.sort_var = tk.StringVar(value="ID")
        sort_options = ["ID", "First Name", "Last Name", "DOB", "Email", "Address", "Contact"]
        ttk.Combobox(control_frame, textvariable=self.sort_var, values=sort_options, state="readonly").pack(side="left", padx=5)

        self.sort_direction = tk.BooleanVar(value=True)
        ttk.Radiobutton(control_frame, text="Ascending", variable=self.sort_direction, value=True).pack(side="left", padx=5)
        ttk.Radiobutton(control_frame, text="Descending", variable=self.sort_direction, value=False).pack(side="left", padx=5)

        ttk.Button(control_frame, text="Sort Now", command=self.sort_patients).pack(side="left", padx=5)

        self.tree = ttk.Treeview(master, columns=("ID", "First Name", "Last Name", "DOB", "Email", "Address", "Contact"), show="headings")
        for col in ["ID", "First Name", "Last Name", "DOB", "Email", "Address", "Contact"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(master)
        button_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(button_frame, text="View All Patients", command=self.load_all_patients).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Patient", command=self.open_update_window).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Patient", command=self.open_delete_window).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Dashboard", command=self.back_to_dashboard).pack(side="right", padx=5)

    def compare(self, a, b, key_index):
        try:
            if key_index == 0:  # ID (integer)
                val_a, val_b = int(a[key_index]), int(b[key_index])
            elif key_index == 3:  # DOB (date)
                val_a = datetime.strptime(str(a[key_index]), "%Y-%m-%d")
                val_b = datetime.strptime(str(b[key_index]), "%Y-%m-%d")
            else:  # Strings
                val_a, val_b = str(a[key_index]).lower(), str(b[key_index]).lower()
            return val_a <= val_b if self.sort_direction.get() else val_a >= val_b
        except (ValueError, TypeError):
            return True if self.sort_direction.get() else False

    def partition(self, data, low, high, key_index):
        pivot_idx = random.randint(low, high)
        data[pivot_idx], data[high] = data[high], data[pivot_idx]
        pivot = data[high]
        i = low - 1
        for j in range(low, high):
            if self.compare(data[j], pivot, key_index):
                i += 1
                data[i], data[j] = data[j], data[i]
        data[i + 1], data[high] = data[high], data[i + 1]
        return i + 1

    def quicksort(self, data, low, high, key_index):
        if low < high:
            pivot_idx = self.partition(data, low, high, key_index)
            self.quicksort(data, low, pivot_idx - 1, key_index)
            self.quicksort(data, pivot_idx + 1, high, key_index)

    def sort_patients(self):
        data = [list(self.tree.item(item)["values"]) for item in self.tree.get_children()]
        if not data:
            return

        key_map = {"ID": 0, "First Name": 1, "Last Name": 2, "DOB": 3, "Email": 4, "Address": 5, "Contact": 6}
        key_index = key_map.get(self.sort_var.get(), 0)

        # Measure time for half and full data
        half_data = data[:len(data)//2]
        start_time = time.time()
        self.quicksort(half_data, 0, len(half_data) - 1, key_index)
        half_time = time.time() - start_time

        start_time = time.time()
        self.quicksort(data, 0, len(data) - 1, key_index)
        full_time = time.time() - start_time

        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=row)

        # Log timing results
        with open("sorting_times.txt", "a") as f:
            f.write(f"QuickSort - Half: {half_time:.6f}s, Full: {full_time:.6f}s, Size: {len(data)}\n")

    def dynamic_search(self, *args):
        search_id = self.search_var.get().strip()
        self.tree.delete(*self.tree.get_children())
        if search_id:
            self.load_patients(search_id)

    def load_patients(self, search_id):
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT patient_id, first_name, last_name, date_of_birth, email, address, contact_number FROM Patients WHERE patient_id LIKE %s"
        cursor.execute(query, (search_id + "%",))
        results = cursor.fetchall()
        db.close()
        if results:
            for row in results:
                self.tree.insert("", "end", values=row)
        else:
            self.prompt_register()

    def load_all_patients(self):
        self.tree.delete(*self.tree.get_children())
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT patient_id, first_name, last_name, date_of_birth, email, address, contact_number FROM Patients")
        results = cursor.fetchall()
        db.close()
        for row in results:
            self.tree.insert("", "end", values=row)

    def prompt_register(self):
        if messagebox.askyesno("Not Registered", "Patient not registered! Do you want to register?"):
            self.master.destroy()
            root = tk.Tk()
            RoleSelection(root)
            root.mainloop()

    def open_update_window(self):
        root = tk.Toplevel(self.master)
        UpdatePatient(root)

    def open_delete_window(self):
        root = tk.Toplevel(self.master)
        DeletePatient(root)

    def back_to_dashboard(self):
        self.master.destroy()
        root = tk.Tk()
        AdminDashboard(root)
        root.mainloop()

# Update Patient Window
class UpdatePatient:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Update Patient")
        master.geometry("400x400")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Patient ID:").grid(row=0, column=0, pady=10, sticky="e")
        self.patient_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.patient_id_var).grid(row=0, column=1, pady=10)
        ttk.Button(main_frame, text="Search", command=self.load_patient_data).grid(row=1, column=0, columnspan=2, pady=10)

    def load_patient_data(self):
        patient_id = self.patient_id_var.get().strip()
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT first_name, last_name, date_of_birth, email, address, contact_number FROM Patients WHERE patient_id = %s"
        cursor.execute(query, (patient_id,))
        result = cursor.fetchone()
        db.close()
        
        if result:
            self.display_update_form(patient_id, result)
        else:
            messagebox.showerror("Error", "Patient not found!")

    def display_update_form(self, patient_id, data):
        update_window = tk.Toplevel(self.master)
        update_window.title("MediTrack - Edit Patient Details")
        update_window.geometry("400x400")
        apply_theme(update_window)

        main_frame = ttk.Frame(update_window, padding=20)
        main_frame.pack(fill="both", expand=True)

        labels = ["First Name", "Last Name", "DOB", "Email", "Address", "Contact"]
        fields = ["first_name", "last_name", "date_of_birth", "email", "address", "contact_number"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(main_frame, text=f"{label} (Old: {data[i]})").grid(row=i, column=0, pady=5, sticky="e")
            entry = ttk.Entry(main_frame)
            entry.insert(0, data[i])
            entry.grid(row=i, column=1, pady=5)
            self.entries[fields[i]] = entry

        ttk.Button(main_frame, text="Update", command=lambda: self.update_patient(patient_id)).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def update_patient(self, patient_id):
        db = connect_db()
        cursor = db.cursor()
        update_query = "UPDATE Patients SET first_name=%s, last_name=%s, date_of_birth=%s, email=%s, address=%s, contact_number=%s WHERE patient_id=%s"
        cursor.execute(update_query, (
            self.entries["first_name"].get(),
            self.entries["last_name"].get(),
            self.entries["date_of_birth"].get(),
            self.entries["email"].get(),
            self.entries["address"].get(),
            self.entries["contact_number"].get(),
            patient_id
        ))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Patient updated successfully.")

# Delete Patient Window
class DeletePatient:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Delete Patient")
        master.geometry("400x200")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Patient ID to Delete:").grid(row=0, column=0, pady=10, sticky="e")
        self.patient_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.patient_id_var).grid(row=0, column=1, pady=10)
        ttk.Button(main_frame, text="Search", command=self.confirm_delete).grid(row=1, column=0, columnspan=2, pady=10)

    def confirm_delete(self):
        patient_id = self.patient_id_var.get().strip()
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Patients WHERE patient_id = %s", (patient_id,))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Patient not found!")
            db.close()
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete patient ID {patient_id}?")
        if confirm:
            cursor.execute("DELETE FROM Patients WHERE patient_id = %s", (patient_id,))
            db.commit()
            messagebox.showinfo("Success", "Patient deleted successfully.")
        db.close()

# Manage Doctors
class ManageDoctors:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Manage Doctors")
        master.geometry("800x600")
        apply_theme(master)

        header = ttk.Frame(master)
        header.pack(fill="x", padx=10, pady=10)
        ttk.Label(header, text="Manage Doctors", font=("Arial", 16, "bold")).pack(pady=5)

        control_frame = ttk.Frame(master)
        control_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(control_frame, text="Search Doctor by ID:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.search_var).pack(side="left", padx=5)
        self.search_var.trace("w", self.dynamic_search)

        ttk.Label(control_frame, text="Sort By:").pack(side="left", padx=5)
        self.sort_var = tk.StringVar(value="ID")
        sort_options = ["ID", "First Name", "Last Name", "Specialization", "Email", "Contact"]
        ttk.Combobox(control_frame, textvariable=self.sort_var, values=sort_options, state="readonly").pack(side="left", padx=5)

        self.sort_direction = tk.BooleanVar(value=True)
        ttk.Radiobutton(control_frame, text="Ascending", variable=self.sort_direction, value=True).pack(side="left", padx=5)
        ttk.Radiobutton(control_frame, text="Descending", variable=self.sort_direction, value=False).pack(side="left", padx=5)

        ttk.Button(control_frame, text="Sort Now", command=self.sort_doctors).pack(side="left", padx=5)

        self.tree = ttk.Treeview(master, columns=("ID", "First Name", "Last Name", "Specialization", "Email", "Contact"), show="headings")
        for col in ["ID", "First Name", "Last Name", "Specialization", "Email", "Contact"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(master)
        button_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(button_frame, text="View All Doctors", command=self.load_all_doctors).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Add New Doctor", command=self.open_add_doctor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Doctor", command=self.open_update_window).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Doctor", command=self.open_delete_window).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Dashboard", command=self.back_to_dashboard).pack(side="right", padx=5)

    def compare(self, a, b, key_index):
        try:
            if key_index == 0:  # ID (integer)
                val_a, val_b = int(a[key_index]), int(b[key_index])
            else:  # Strings
                val_a, val_b = str(a[key_index]).lower(), str(b[key_index]).lower()
            return val_a <= val_b if self.sort_direction.get() else val_a >= val_b
        except (ValueError, TypeError):
            return True if self.sort_direction.get() else False

    def partition(self, data, low, high, key_index):
        pivot_idx = random.randint(low, high)
        data[pivot_idx], data[high] = data[high], data[pivot_idx]
        pivot = data[high]
        i = low - 1
        for j in range(low, high):
            if self.compare(data[j], pivot, key_index):
                i += 1
                data[i], data[j] = data[j], data[i]
        data[i + 1], data[high] = data[high], data[i + 1]
        return i + 1

    def quicksort(self, data, low, high, key_index):
        if low < high:
            pivot_idx = self.partition(data, low, high, key_index)
            self.quicksort(data, low, pivot_idx - 1, key_index)
            self.quicksort(data, pivot_idx + 1, high, key_index)

    def sort_doctors(self):
        data = [list(self.tree.item(item)["values"]) for item in self.tree.get_children()]
        if not data:
            return

        key_map = {"ID": 0, "First Name": 1, "Last Name": 2, "Specialization": 3, "Email": 4, "Contact": 5}
        key_index = key_map.get(self.sort_var.get(), 0)

        half_data = data[:len(data)//2]
        start_time = time.time()
        self.quicksort(half_data, 0, len(half_data) - 1, key_index)
        half_time = time.time() - start_time

        start_time = time.time()
        self.quicksort(data, 0, len(data) - 1, key_index)
        full_time = time.time() - start_time

        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=row)

        with open("sorting_times.txt", "a") as f:
            f.write(f"QuickSort (Doctors) - Half: {half_time:.6f}s, Full: {full_time:.6f}s, Size: {len(data)}\n")

    def dynamic_search(self, *args):
        search_id = self.search_var.get().strip()
        self.tree.delete(*self.tree.get_children())
        if search_id:
            self.load_doctors(search_id)

    def load_doctors(self, search_id):
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT doctor_id, first_name, last_name, specialization, email, contact_number FROM Doctors WHERE doctor_id LIKE %s"
        cursor.execute(query, (search_id + "%",))
        results = cursor.fetchall()
        db.close()
        if results:
            for row in results:
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showerror("Error", "Doctor not found!")

    def load_all_doctors(self):
        self.tree.delete(*self.tree.get_children())
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT doctor_id, first_name, last_name, specialization, email, contact_number FROM Doctors")
        results = cursor.fetchall()
        db.close()
        for row in results:
            self.tree.insert("", "end", values=row)

    def open_add_doctor(self):
        self.master.destroy()
        root = tk.Tk()
        RoleSelection(root)
        root.mainloop()

    def open_update_window(self):
        root = tk.Toplevel(self.master)
        UpdateDoctor(root)

    def open_delete_window(self):
        root = tk.Toplevel(self.master)
        DeleteDoctor(root)

    def back_to_dashboard(self):
        self.master.destroy()
        root = tk.Tk()
        AdminDashboard(root)
        root.mainloop()

# Update Doctor Window
class UpdateDoctor:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Update Doctor")
        master.geometry("400x400")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Doctor ID:").grid(row=0, column=0, pady=10, sticky="e")
        self.doctor_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.doctor_id_var).grid(row=0, column=1, pady=10)
        ttk.Button(main_frame, text="Search", command=self.load_doctor_data).grid(row=1, column=0, columnspan=2, pady=10)

    def load_doctor_data(self):
        doctor_id = self.doctor_id_var.get().strip()
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT first_name, last_name, specialization, email, contact_number FROM Doctors WHERE doctor_id = %s"
        cursor.execute(query, (doctor_id,))
        result = cursor.fetchone()
        db.close()
        
        if result:
            self.display_update_form(doctor_id, result)
        else:
            messagebox.showerror("Error", "Doctor not found!")

    def display_update_form(self, doctor_id, data):
        update_window = tk.Toplevel(self.master)
        update_window.title("MediTrack - Edit Doctor Details")
        update_window.geometry("400x400")
        apply_theme(update_window)

        main_frame = ttk.Frame(update_window, padding=20)
        main_frame.pack(fill="both", expand=True)

        labels = ["First Name", "Last Name", "Specialization", "Email", "Contact"]
        fields = ["first_name", "last_name", "specialization", "email", "contact_number"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(main_frame, text=f"{label} (Old: {data[i]})").grid(row=i, column=0, pady=5, sticky="e")
            entry = ttk.Entry(main_frame)
            entry.insert(0, data[i])
            entry.grid(row=i, column=1, pady=5)
            self.entries[fields[i]] = entry

        ttk.Button(main_frame, text="Update", command=lambda: self.update_doctor(doctor_id)).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def update_doctor(self, doctor_id):
        db = connect_db()
        cursor = db.cursor()
        update_query = "UPDATE Doctors SET first_name=%s, last_name=%s, specialization=%s, email=%s, contact_number=%s WHERE doctor_id=%s"
        cursor.execute(update_query, (
            self.entries["first_name"].get(),
            self.entries["last_name"].get(),
            self.entries["specialization"].get(),
            self.entries["email"].get(),
            self.entries["contact_number"].get(),
            doctor_id
        ))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Doctor updated successfully.")

# Delete Doctor Window
class DeleteDoctor:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Delete Doctor")
        master.geometry("400x200")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Doctor ID to Delete:").grid(row=0, column=0, pady=10, sticky="e")
        self.doctor_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.doctor_id_var).grid(row=0, column=1, pady=10)
        ttk.Button(main_frame, text="Search", command=self.confirm_delete).grid(row=1, column=0, columnspan=2, pady=10)

    def confirm_delete(self):
        doctor_id = self.doctor_id_var.get().strip()
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Doctors WHERE doctor_id = %s", (doctor_id,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Doctor not found!")
            db.close()
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Doctor ID {doctor_id}?")
        if confirm:
            cursor.execute("DELETE FROM Doctors WHERE doctor_id = %s", (doctor_id,))
            db.commit()
            messagebox.showinfo("Success", "Doctor deleted successfully.")
        db.close()

# Sort Appointments with MergeSort Timing
class SortAppointments:
    def __init__(self, root):
        self.root = root
        self.root.title("MediTrack - Sort Appointments")
        self.root.geometry("800x600")
        apply_theme(self.root)

        self.conn = connect_db()
        self.cursor = self.conn.cursor()

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Sort Appointments", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

        ttk.Label(main_frame, text="Sort By:").grid(row=1, column=0, pady=5, sticky="e")
        self.sort_var = tk.StringVar(value="Time")
        sort_options = ["Time", "Status", "Doctor"]
        ttk.Combobox(main_frame, textvariable=self.sort_var, values=sort_options, state="readonly").grid(row=1, column=1, pady=5)

        self.sort_direction = tk.BooleanVar(value=True)
        ttk.Radiobutton(main_frame, text="Ascending", variable=self.sort_direction, value=True).grid(row=1, column=2, pady=5, padx=5)
        ttk.Radiobutton(main_frame, text="Descending", variable=self.sort_direction, value=False).grid(row=1, column=3, pady=5)

        ttk.Button(main_frame, text="Sort Now", command=self.sort_appointments).grid(row=2, column=0, columnspan=4, pady=10)

        self.tree = ttk.Treeview(main_frame, columns=("ID", "Patient", "Date", "Time", "Status", "Doctor"), show="headings")
        for col in ["ID", "Patient", "Date", "Time", "Status", "Doctor"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.grid(row=3, column=0, columnspan=4, pady=10, sticky="nsew")

        ttk.Button(main_frame, text="Schedule New", command=self.schedule_appointment).grid(row=4, column=0, pady=5)
        ttk.Button(main_frame, text="Cancel", command=self.cancel_appointment).grid(row=4, column=1, pady=5)
        ttk.Button(main_frame, text="Reschedule", command=self.reschedule_appointment).grid(row=4, column=2, pady=5)
        ttk.Button(main_frame, text="Back to Dashboard", command=self.back_to_dashboard).grid(row=4, column=3, pady=5)

        self.load_data()

    def merge(self, left, right):
        result = []
        sort_key = self.sort_var.get()
        i = j = 0

        while i < len(left) and j < len(right):
            if sort_key == "Time":
                left_dt = datetime.strptime(f"{left[i][2]} {left[i][3]}", "%Y-%m-%d %H:%M:%S")
                right_dt = datetime.strptime(f"{right[j][2]} {right[j][3]}", "%Y-%m-%d %H:%M:%S")
                comparison = left_dt <= right_dt if self.sort_direction.get() else left_dt >= right_dt
            elif sort_key == "Status":
                comparison = left[i][4] <= right[j][4] if self.sort_direction.get() else left[i][4] >= right[j][4]
            else:  # Doctor
                comparison = left[i][5] <= right[j][5] if self.sort_direction.get() else left[i][5] >= right[j][5]

            if comparison:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def merge_sort(self, data):
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = self.merge_sort(data[:mid])
        right = self.merge_sort(data[mid:])
        return self.merge(left, right)

    def sort_appointments(self):
        data = [list(self.tree.item(item)["values"]) for item in self.tree.get_children()]
        if not data:
            return

        half_data = data[:len(data)//2]
        start_time = time.time()
        self.merge_sort(half_data)
        half_time = time.time() - start_time

        start_time = time.time()
        sorted_data = self.merge_sort(data)
        full_time = time.time() - start_time

        self.tree.delete(*self.tree.get_children())
        for row in sorted_data:
            self.tree.insert("", "end", values=row)

        with open("sorting_times.txt", "a") as f:
            f.write(f"MergeSort - Half: {half_time:.6f}s, Full: {full_time:.6f}s, Size: {len(data)}\n")

    def load_data(self):
        query = """
            SELECT a.appointment_id, CONCAT(p.first_name, ' ', p.last_name) AS patient_name, 
                   a.appointment_date, a.appointment_time, a.status, 
                   CONCAT(d.first_name, ' ', d.last_name) AS doctor_name
            FROM Appointments a
            JOIN Patients p ON a.patient_id = p.patient_id
            JOIN Doctors d ON a.doctor_id = d.doctor_id
        """
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=row)

    def schedule_appointment(self):
        window = Toplevel(self.root)
        window.title("Schedule New Appointment")
        window.geometry("300x300")

        ttk.Label(window, text="Patient ID:").pack(pady=5)
        patient_id_entry = ttk.Entry(window)
        patient_id_entry.pack(pady=5)

        ttk.Label(window, text="Doctor ID:").pack(pady=5)
        doctor_id_entry = ttk.Entry(window)
        doctor_id_entry.pack(pady=5)

        ttk.Label(window, text="Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(window)
        date_entry.pack(pady=5)

        ttk.Label(window, text="Time (HH:MM):").pack(pady=5)
        time_entry = ttk.Entry(window)
        time_entry.pack(pady=5)

        def save_appointment():
            patient_id = patient_id_entry.get().strip()
            doctor_id = doctor_id_entry.get().strip()
            date = date_entry.get().strip()
            time = time_entry.get().strip()

            if not all([patient_id, doctor_id, date, time]):
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                patient_id = int(patient_id)
                doctor_id = int(doctor_id)
                datetime.strptime(date, "%Y-%m-%d")
                datetime.strptime(time, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid ID or date/time format!")
                return

            self.cursor.execute("""
                SELECT COUNT(*) FROM Appointments 
                WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s 
                AND status != 'Cancelled'
            """, (doctor_id, date, time))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Doctor is already booked at this time!")
                return

            query = """
                INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
                VALUES (%s, %s, %s, %s, 'Scheduled')
            """
            self.cursor.execute(query, (patient_id, doctor_id, date, time))
            self.conn.commit()
            messagebox.showinfo("Success", "Appointment scheduled!")
            window.destroy()
            self.load_data()

        ttk.Button(window, text="Save", command=save_appointment).pack(pady=10)

    def cancel_appointment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an appointment to cancel!")
            return

        appointment_id = self.tree.item(selected[0])["values"][0]
        query = "UPDATE Appointments SET status = 'Cancelled' WHERE appointment_id = %s"
        self.cursor.execute(query, (appointment_id,))
        self.conn.commit()
        messagebox.showinfo("Success", "Appointment cancelled!")
        self.load_data()

    def reschedule_appointment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an appointment to reschedule!")
            return

        appt = self.tree.item(selected[0])["values"]
        appointment_id = appt[0]
        current_date = appt[2]
        current_time = appt[3]

        window = Toplevel(self.root)
        window.title("Reschedule Appointment")
        window.geometry("300x200")

        ttk.Label(window, text=f"Current Date: {current_date}").pack(pady=5)
        ttk.Label(window, text="New Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(window)
        date_entry.pack(pady=5)

        ttk.Label(window, text=f"Current Time: {current_time}").pack(pady=5)
        ttk.Label(window, text="New Time (HH:MM):").pack(pady=5)
        time_entry = ttk.Entry(window)
        time_entry.pack(pady=5)

        def save_reschedule():
            new_date = date_entry.get().strip()
            new_time = time_entry.get().strip()

            if not all([new_date, new_time]):
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                datetime.strptime(new_date, "%Y-%m-%d")
                datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid date/time format!")
                return

            self.cursor.execute("""
                SELECT doctor_id FROM Appointments WHERE appointment_id = %s
            """, (appointment_id,))
            doctor_id = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM Appointments 
                WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s 
                AND appointment_id != %s AND status != 'Cancelled'
            """, (doctor_id, new_date, new_time, appointment_id))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Doctor is already booked at this time!")
                return

            query = """
                UPDATE Appointments 
                SET appointment_date = %s, appointment_time = %s 
                WHERE appointment_id = %s
            """
            self.cursor.execute(query, (new_date, new_time, appointment_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Appointment rescheduled!")
            window.destroy()
            self.load_data()

        ttk.Button(window, text="Save", command=save_reschedule).pack(pady=10)

    def back_to_dashboard(self):
        self.root.destroy()
        root = tk.Tk()
        AdminDashboard(root)
        root.mainloop()
#________________----------------------------------------------------------------------------------------------------------
# Doctor Dashboard
class DoctorDashboard:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Doctor Dashboard")
        master.geometry("800x500")
        apply_theme(master)

        sidebar = ttk.Frame(master, width=200, relief="raised", borderwidth=1)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        header = ttk.Frame(master, height=50)
        header.pack(side="top", fill="x", padx=10, pady=10)
        ttk.Label(header, text="Doctor Dashboard", font=("Arial", 18, "bold")).pack(pady=10)

        # Updated button list with consolidated "Patient Info"
        buttons = [
            ("Patient Info", self.manage_patient_info),  # Combined button
            ("Manage Appointments", self.manage_appointments),
            ("View All Appointments", self.view_all_appointments),
            ("View Patient Records", self.view_patient_records),
            ("Logout", self.logout)
        ]
        for text, cmd in buttons:
            ttk.Button(sidebar, text=text, command=cmd, width=20).pack(pady=10, padx=5)

        self.content = ttk.Frame(master)
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(self.content, text="Welcome to the Doctor Dashboard", font=("Arial", 14)).pack(pady=20)

        ttk.Button(self.content, text="Back to Login", command=self.back_to_login).pack(pady=10)

    def manage_patient_info(self):
        root = tk.Toplevel(self.master)
        PatientInfoManager(root, self.master)

    def manage_appointments(self):
        root = tk.Toplevel(self.master)
        ManageAppointments(root, self.master)

    def view_all_appointments(self):
        root = tk.Toplevel(self.master)
        ViewAllAppointments(root)

    def view_patient_records(self):
        root = tk.Toplevel(self.master)
        ViewPatientRecords(root)

    def logout(self):
        self.master.destroy()

    def back_to_login(self):
        self.master.destroy()
        root = tk.Tk()
        MediTrackApp(root)
        root.mainloop()

# View Patient Info
class PatientInfoManager:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        master.title("MediTrack - Patient Info Manager")
        master.geometry("1000x600")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Doctor ID prompt (temporary until session management is added)
        ttk.Label(main_frame, text="Enter Your Doctor ID:").grid(row=0, column=0, pady=5, sticky="e")
        self.doctor_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.doctor_id_var).grid(row=0, column=1, pady=5)

        # Patient ID search
        ttk.Label(main_frame, text="Search Patient ID:").grid(row=0, column=2, pady=5, padx=10, sticky="e")
        self.patient_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.patient_id_var).grid(row=0, column=3, pady=5)
        self.patient_id_var.trace("w", self.dynamic_search)

        # Patient List Treeview
        columns = ("ID", "Name", "DOB", "Contact", "Address", "Email", "Last Appointment")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")

        # Button Panel
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=2, pady=10, sticky="ns")
        ttk.Button(button_frame, text="View Records", command=self.view_records).pack(pady=5)
        ttk.Button(button_frame, text="Manage Appointments", command=self.manage_appointments).pack(pady=5)
        ttk.Button(button_frame, text="Back", command=self.master.destroy).pack(pady=5)

        # Load initial patient list
        ttk.Button(main_frame, text="Load Patients", command=self.load_patients).grid(row=2, column=0, columnspan=4, pady=10)

    def load_patients(self):
        doctor_id = self.doctor_id_var.get().strip()
        if not doctor_id or not doctor_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Doctor ID (numeric).")
            return

        doctor_id = int(doctor_id)
        db = connect_db()
        cursor = db.cursor()

        # Verify doctor exists
        cursor.execute("SELECT COUNT(*) FROM Doctors WHERE doctor_id = %s", (doctor_id,))
        if cursor.fetchone()[0] == 0:
            messagebox.showerror("Error", "Doctor ID not found!")
            db.close()
            return

        # Fetch all patients assigned to this doctor
        query = """
            SELECT DISTINCT p.patient_id, CONCAT(p.first_name, ' ', p.last_name) AS name, p.date_of_birth, 
                   p.contact_number, p.address, p.email, MAX(CONCAT(a.appointment_date, ' ', a.appointment_time)) AS last_appointment
            FROM Patients p
            JOIN Appointments a ON p.patient_id = a.patient_id
            WHERE a.doctor_id = %s
            GROUP BY p.patient_id, p.first_name, p.last_name, p.date_of_birth, p.contact_number, p.address, p.email
        """
        cursor.execute(query, (doctor_id,))
        patients = cursor.fetchall()
        db.close()

        self.tree.delete(*self.tree.get_children())
        if not patients:
            messagebox.showinfo("No Patients", "No patients assigned to this doctor.")
            return

        for patient in patients:
            self.tree.insert("", "end", values=patient)

    def dynamic_search(self, *args):
        doctor_id = self.doctor_id_var.get().strip()
        search_id = self.patient_id_var.get().strip()
        if not doctor_id or not doctor_id.isdigit():
            return

        doctor_id = int(doctor_id)
        db = connect_db()
        cursor = db.cursor()

        query = """
            SELECT DISTINCT p.patient_id, CONCAT(p.first_name, ' ', p.last_name) AS name, p.date_of_birth, 
                   p.contact_number, p.address, p.email, MAX(CONCAT(a.appointment_date, ' ', a.appointment_time)) AS last_appointment
            FROM Patients p
            JOIN Appointments a ON p.patient_id = a.patient_id
            WHERE a.doctor_id = %s AND p.patient_id LIKE %s
            GROUP BY p.patient_id, p.first_name, p.last_name, p.date_of_birth, p.contact_number, p.address, p.email
        """
        cursor.execute(query, (doctor_id, search_id + "%"))
        patients = cursor.fetchall()
        db.close()

        self.tree.delete(*self.tree.get_children())
        for patient in patients:
            self.tree.insert("", "end", values=patient)

    def view_records(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a patient to view records.")
            return

        patient_id = self.tree.item(selected[0])["values"][0]
        root = tk.Toplevel(self.master)
        ViewPatientMedicalRecords(root, patient_id)

    def manage_appointments(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a patient to manage appointments.")
            return

        patient_id = self.tree.item(selected[0])["values"][0]
        root = tk.Toplevel(self.master)
        ManageAppointments(root, self.parent)  # Reuse existing class; patient_id could be passed if needed

# New ViewPatientMedicalRecords Class
class ViewPatientMedicalRecords:
    def __init__(self, master, patient_id):
        self.master = master
        self.patient_id = patient_id
        master.title(f"MediTrack - Medical Records for Patient ID: {patient_id}")
        master.geometry("800x500")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Sort options
        ttk.Label(main_frame, text="Sort By:").grid(row=0, column=0, pady=5, sticky="e")
        self.sort_var = tk.StringVar(value="Record Date")
        ttk.Combobox(main_frame, textvariable=self.sort_var, values=["Record Date", "Diagnosis"], state="readonly").grid(row=0, column=1, pady=5)

        ttk.Button(main_frame, text="Sort Records", command=self.sort_records).grid(row=0, column=2, pady=5, padx=10)

        # Records Treeview
        columns = ("History ID", "Diagnosis", "Medications", "Treatment", "Record Date")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        # Buttons
        ttk.Button(main_frame, text="Update Record", command=self.update_record).grid(row=2, column=0, pady=5)
        ttk.Button(main_frame, text="Create New Record", command=self.create_new_record).grid(row=2, column=1, pady=5)
        ttk.Button(main_frame, text="Back", command=master.destroy).grid(row=2, column=2, pady=5)

        self.load_records()

    def load_records(self):
        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT history_id, diagnosis, prescribed_medications, treatment_plan, record_date
            FROM Medical_History
            WHERE patient_id = %s
        """
        cursor.execute(query, (self.patient_id,))
        records = list(cursor.fetchall())
        db.close()

        self.tree.delete(*self.tree.get_children())
        if not records:
            messagebox.showinfo("No Records", "No medical records found for this patient.")
            return

        for record in records:
            self.tree.insert("", "end", values=record)

    def heapify(self, arr, n, i, sort_key):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if sort_key == "Record Date":
            if left < n and arr[left][4] > arr[largest][4]:  # record_date (TIMESTAMP)
                largest = left
            if right < n and arr[right][4] > arr[largest][4]:
                largest = right
        elif sort_key == "Diagnosis":
            if left < n and arr[left][1] > arr[largest][1]:  # diagnosis (TEXT)
                largest = left
            if right < n and arr[right][1] > arr[largest][1]:
                largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self.heapify(arr, n, largest, sort_key)

    def heap_sort(self, arr, sort_key):
        n = len(arr)
        for i in range(n // 2 - 1, -1, -1):
            self.heapify(arr, n, i, sort_key)
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            self.heapify(arr, i, 0, sort_key)

    def sort_records(self):
        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT history_id, diagnosis, prescribed_medications, treatment_plan, record_date
            FROM Medical_History
            WHERE patient_id = %s
        """
        cursor.execute(query, (self.patient_id,))
        records = list(cursor.fetchall())
        db.close()

        if not records:
            return

        sort_key = self.sort_var.get()
        start_time = time.time()
        self.heap_sort(records, sort_key)
        sort_time = time.time() - start_time

        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", "end", values=record)

        with open("sorting_times.txt", "a") as f:
            f.write(f"HeapSort (Medical Records) - Time: {sort_time:.6f}s, Size: {len(records)}, Key: {sort_key}\n")
        messagebox.showinfo("Success", f"Records sorted by {sort_key} in {sort_time:.6f} seconds.")

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a record to update.")
            return

        history_id = self.tree.item(selected[0])["values"][0]
        root = tk.Toplevel(self.master)
        UpdateMedicalHistory(root, self.patient_id, history_id)

    def create_new_record(self):
        root = tk.Toplevel(self.master)
        CreateMedicalRecord(root, self.patient_id, self)

# Modified UpdateMedicalHistory Class (adjusted for history_id)
class UpdateMedicalHistory:
    def __init__(self, master, patient_id, history_id):
        self.master = master
        self.patient_id = patient_id
        self.history_id = history_id
        master.title("MediTrack - Update Medical History")
        master.geometry("500x500")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text=f"Update Medical History (ID: {history_id})", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)
        self.entries = {}
        fields = ["diagnosis", "prescribed_medications", "treatment_plan"]

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT diagnosis, prescribed_medications, treatment_plan FROM Medical_History WHERE history_id = %s", (history_id,))
        result = cursor.fetchone()
        db.close()

        for i, field in enumerate(fields, start=1):
            ttk.Label(main_frame, text=f"{field.replace('_', ' ').title()}:").grid(row=i, column=0, pady=5, sticky="e")
            entry = ttk.Entry(main_frame, width=40)
            if result:
                entry.insert(0, result[i-1])
            entry.grid(row=i, column=1, pady=5)
            self.entries[field] = entry

        ttk.Button(main_frame, text="Update Record", command=self.update_record).grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)
        ttk.Button(main_frame, text="Back", command=master.destroy).grid(row=len(fields) + 2, column=0, columnspan=2, pady=5)

    def update_record(self):
        db = connect_db()
        cursor = db.cursor()
        query = """
            UPDATE Medical_History 
            SET diagnosis=%s, prescribed_medications=%s, treatment_plan=%s
            WHERE history_id=%s
        """
        cursor.execute(query, (
            self.entries["diagnosis"].get(),
            self.entries["prescribed_medications"].get(),
            self.entries["treatment_plan"].get(),
            self.history_id
        ))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Medical history updated successfully.")
        self.master.destroy()

# New CreateMedicalRecord Class
class CreateMedicalRecord:
    def __init__(self, master, patient_id, parent):
        self.master = master
        self.patient_id = patient_id
        self.parent = parent
        master.title("MediTrack - Create New Medical Record")
        master.geometry("500x500")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text=f"New Medical Record for Patient ID: {patient_id}", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)
        self.entries = {}
        fields = ["diagnosis", "prescribed_medications", "treatment_plan"]

        for i, field in enumerate(fields, start=1):
            ttk.Label(main_frame, text=f"{field.replace('_', ' ').title()}:").grid(row=i, column=0, pady=5, sticky="e")
            entry = ttk.Entry(main_frame, width=40)
            entry.grid(row=i, column=1, pady=5)
            self.entries[field] = entry

        ttk.Button(main_frame, text="Save Record", command=self.save_record).grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)
        ttk.Button(main_frame, text="Back", command=master.destroy).grid(row=len(fields) + 2, column=0, columnspan=2, pady=5)

    def save_record(self):
        db = connect_db()
        cursor = db.cursor()
        query = """
            INSERT INTO Medical_History (patient_id, diagnosis, prescribed_medications, treatment_plan, record_date)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        cursor.execute(query, (
            self.patient_id,
            self.entries["diagnosis"].get(),
            self.entries["prescribed_medications"].get(),
            self.entries["treatment_plan"].get()
        ))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "New medical record created successfully.")
        self.master.destroy()
        self.parent.load_records()  # Refresh records in parent window
# View All Appointments
class ViewAllAppointments:
    def __init__(self, master):
        self.master = master
        self.master.title("MediTrack - View Appointments")
        self.master.geometry("800x500")
        apply_theme(self.master)

        self.main_frame = ttk.Frame(self.master, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        ttk.Label(self.main_frame, text="Enter Your Doctor ID:", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky="e")
        self.doctor_id_var = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.doctor_id_var).grid(row=0, column=1, pady=5)
        ttk.Button(self.main_frame, text="Load Appointments", command=self.load_appointments).grid(row=0, column=2, pady=5, padx=10)

        ttk.Label(self.main_frame, text="Sort By:").grid(row=1, column=0, pady=5, sticky="e")
        self.sort_var = tk.StringVar(value="Date")
        ttk.Combobox(self.main_frame, textvariable=self.sort_var, values=["Patient Name", "Date", "Time", "Status"], state="readonly").grid(row=1, column=1, pady=5)

        self.tree = ttk.Treeview(self.main_frame, columns=("Patient Name", "Date", "Time", "Status"), show="headings")
        for col in ["Patient Name", "Date", "Time", "Status"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")
        self.tree.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

        ttk.Button(self.main_frame, text="Back", command=self.master.destroy).grid(row=3, column=0, columnspan=3, pady=10)

    def load_appointments(self):
        doctor_id = self.doctor_id_var.get().strip()
        if not doctor_id or not doctor_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Doctor ID (numeric).")
            return

        doctor_id = int(doctor_id)
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT doctor_id FROM Doctors WHERE doctor_id = %s", (doctor_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Doctor ID not found!")
            db.close()
            return

        query = """SELECT CONCAT(p.first_name, ' ', p.last_name), a.appointment_date, a.appointment_time, a.status 
                   FROM Appointments a 
                   JOIN Patients p ON a.patient_id = p.patient_id 
                   WHERE a.doctor_id = %s"""
        cursor.execute(query, (doctor_id,))
        rows = cursor.fetchall()
        db.close()

        if not rows:
            messagebox.showinfo("No Appointments", "No appointments found for this doctor.")
            return

        sort_by = self.sort_var.get()
        if sort_by == "Patient Name":
            sorted_rows = sorted(rows, key=lambda x: x[0])
        elif sort_by == "Date":
            sorted_rows = sorted(rows, key=lambda x: x[1])
        elif sort_by == "Time":
            sorted_rows = sorted(rows, key=lambda x: x[2])
        elif sort_by == "Status":
            sorted_rows = sorted(rows, key=lambda x: x[3])
        else:
            sorted_rows = rows

        self.tree.delete(*self.tree.get_children())
        for row in sorted_rows:
            self.tree.insert("", "end", values=row)

# Manage Appointments
class ManageAppointments:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        master.title("MediTrack - Manage Appointments")
        master.geometry("600x400")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Manage Appointments", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10)
        ttk.Button(main_frame, text="Modify Appointment", command=self.modify_appointment).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="Back", command=self.back).grid(row=2, column=0, pady=10)

    def modify_appointment(self):
        root = tk.Toplevel(self.master)
        ModifyAppointment(root, self.master)

    def back(self):
        self.master.destroy()
        self.parent.deiconify()

# Modify Appointment
class ModifyAppointment:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        master.title("MediTrack - Modify Appointment")
        master.geometry("600x400")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Appointment ID:").grid(row=0, column=0, pady=10, sticky="e")
        self.appointment_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.appointment_id_var).grid(row=0, column=1, pady=10)
        ttk.Button(main_frame, text="Load Appointment", command=self.load_appointment).grid(row=1, column=0, columnspan=2, pady=10)

        self.details_frame = ttk.Frame(main_frame)
        self.details_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Label(self.details_frame, text="Status:").grid(row=0, column=0, pady=5, sticky="e")
        self.status_var = tk.StringVar()
        ttk.Combobox(self.details_frame, textvariable=self.status_var, values=["Scheduled", "Completed", "Cancelled"]).grid(row=0, column=1, pady=5)

        ttk.Label(self.details_frame, text="Select New Date:").grid(row=1, column=0, pady=5, sticky="e")
        self.date_entry = DateEntry(self.details_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.details_frame, text="Select New Time:").grid(row=2, column=0, pady=5, sticky="e")
        self.time_var = tk.StringVar()
        ttk.Combobox(self.details_frame, textvariable=self.time_var, values=["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"]).grid(row=2, column=1, pady=5)

        ttk.Button(self.details_frame, text="Update Appointment", command=self.update_appointment).grid(row=3, column=0, columnspan=2, pady=10)

    def load_appointment(self):
        appointment_id = self.appointment_id_var.get().strip()
        if not appointment_id:
            messagebox.showerror("Error", "Please enter an appointment ID!")
            return
        
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT appointment_date, appointment_time, status FROM appointments WHERE appointment_id = %s", (appointment_id,))
        result = cursor.fetchone()
        db.close()

        if result:
            self.date_entry.set_date(result[0])
            self.time_var.set(result[1])
            self.status_var.set(result[2])
        else:
            messagebox.showerror("Error", "Appointment not found!")

    def update_appointment(self):
        appointment_id = self.appointment_id_var.get()
        new_status = self.status_var.get()

        if not appointment_id:
            messagebox.showerror("Error", "Please enter an Appointment ID!")
            return

        conn = connect_db()
        cursor = conn.cursor()

        if new_status in ["Scheduled", "Completed", "Cancelled"]:
            new_date = self.date_entry.get()
            new_time = self.time_var.get()

            if not new_date or not new_time:
                messagebox.showerror("Error", "Please select a new date and time!")
                conn.close()
                return

            formatted_date = datetime.strptime(new_date, "%m/%d/%y").strftime("%Y-%m-%d")
            try:
                formatted_time = datetime.strptime(new_time, "%I:%M %p").strftime("%H:%M:%S")
            except ValueError:
                formatted_time = datetime.strptime(new_time, "%H:%M:%S").strftime("%H:%M:%S")

            cursor.execute("""
                UPDATE appointments 
                SET appointment_date = %s, appointment_time = %s, status = %s
                WHERE appointment_id = %s
            """, (formatted_date, formatted_time, new_status, appointment_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Appointment {new_status} successfully!")
        else:
            messagebox.showerror("Error", "Invalid status selected!")
            conn.close()
            
class ViewPatientRecords:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - View Patient Records")
        master.geometry("1000x600")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Doctor ID input (temporary; ideally from login session)
        ttk.Label(main_frame, text="Enter Your Doctor ID:").grid(row=0, column=0, pady=5, sticky="e")
        self.doctor_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.doctor_id_var).grid(row=0, column=1, pady=5)

        # Sort options
        ttk.Label(main_frame, text="Sort By:").grid(row=0, column=2, pady=5, padx=10, sticky="e")
        self.sort_var = tk.StringVar(value="Record Date")
        ttk.Combobox(main_frame, textvariable=self.sort_var, values=["Record Date", "Patient ID", "Patient Name"], state="readonly").grid(row=0, column=3, pady=5)

        ttk.Button(main_frame, text="Load & Sort Records", command=self.load_and_sort_records).grid(row=1, column=0, columnspan=4, pady=10)

        # Treeview for displaying records
        columns = ("Patient ID", "Patient Name", "Diagnosis", "Medications", "Treatment", "Record Date")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.grid(row=2, column=0, columnspan=4, pady=10, sticky="nsew")

        ttk.Button(main_frame, text="Back", command=master.destroy).grid(row=3, column=0, columnspan=4, pady=10)

    def heapify(self, arr, n, i, sort_key):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if sort_key == "Record Date":
            if left < n and datetime.strptime(str(arr[left][5]), "%Y-%m-%d %H:%M:%S") > datetime.strptime(str(arr[largest][5]), "%Y-%m-%d %H:%M:%S"):
                largest = left
            if right < n and datetime.strptime(str(arr[right][5]), "%Y-%m-%d %H:%M:%S") > datetime.strptime(str(arr[largest][5]), "%Y-%m-%d %H:%M:%S"):
                largest = right
        elif sort_key == "Patient ID":
            if left < n and int(arr[left][0]) > int(arr[largest][0]):
                largest = left
            if right < n and int(arr[right][0]) > int(arr[largest][0]):
                largest = right
        elif sort_key == "Patient Name":
            if left < n and arr[left][1] > arr[largest][1]:
                largest = left
            if right < n and arr[right][1] > arr[largest][1]:
                largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self.heapify(arr, n, largest, sort_key)

    def heap_sort(self, arr, sort_key):
        n = len(arr)
        for i in range(n // 2 - 1, -1, -1):
            self.heapify(arr, n, i, sort_key)
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            self.heapify(arr, i, 0, sort_key)

    def load_and_sort_records(self):
        doctor_id = self.doctor_id_var.get().strip()
        if not doctor_id or not doctor_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Doctor ID (numeric).")
            return

        doctor_id = int(doctor_id)
        db = connect_db()
        cursor = db.cursor()

        # Verify doctor exists
        cursor.execute("SELECT COUNT(*) FROM Doctors WHERE doctor_id = %s", (doctor_id,))
        if cursor.fetchone()[0] == 0:
            messagebox.showerror("Error", "Doctor ID not found!")
            db.close()
            return

        # Fetch records for all patients under this doctor
        query = """
            SELECT DISTINCT mh.patient_id, CONCAT(p.first_name, ' ', p.last_name), 
                   mh.diagnosis, mh.prescribed_medications, mh.treatment_plan, mh.record_date
            FROM Medical_History mh
            JOIN Patients p ON mh.patient_id = p.patient_id
            JOIN Appointments a ON mh.patient_id = a.patient_id
            WHERE a.doctor_id = %s
        """
        cursor.execute(query, (doctor_id,))
        records = list(cursor.fetchall())
        db.close()

        if not records:
            messagebox.showinfo("No Records", "No patient records found for this doctor.")
            return

        # Apply Heap Sort
        sort_key = self.sort_var.get()
        start_time = time.time()
        self.heap_sort(records, sort_key)
        sort_time = time.time() - start_time

        # Update Treeview
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", "end", values=record)

        # Log sorting time
        with open("sorting_times.txt", "a") as f:
            f.write(f"HeapSort (Doctor Records) - Time: {sort_time:.6f}s, Size: {len(records)}, Key: {sort_key}\n")

        messagebox.showinfo("Success", f"Records loaded and sorted by {sort_key} in {sort_time:.6f} seconds.")
#---------------------------------------------------------------------------------------------------------------------------------------------------------
# Patient Dashboard Class
class PatientDashboard:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Patient Dashboard")
        master.geometry("800x600")
        apply_theme(master)

        sidebar = ttk.Frame(master, width=200, relief="raised", borderwidth=1)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        header = ttk.Frame(master, height=50)
        header.pack(side="top", fill="x", padx=10, pady=10)
        ttk.Label(header, text="Patient Dashboard", font=("Arial", 18, "bold")).pack(pady=10)

        buttons = [
            ("View Personal Info", self.view_personal_info),
            ("View Appointments", self.view_appointments),
            ("Request Appointment", self.request_appointment),
            ("View Medical Records", self.view_medical_records),
            ("Logout", self.logout)
        ]
        for text, cmd in buttons:
            ttk.Button(sidebar, text=text, command=cmd, width=20).pack(pady=10, padx=5)

        self.content = ttk.Frame(master)
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(self.content, text="Welcome to the Patient Dashboard", font=("Arial", 14)).pack(pady=20)

        ttk.Button(self.content, text="Back to Login", command=self.back_to_login).pack(pady=10)

    def view_personal_info(self):
        root = tk.Toplevel(self.master)
        ViewPersonalInfo(root)

    def view_appointments(self):
        ViewAppointments(self.master)

    def request_appointment(self):
        root = tk.Toplevel(self.master)
        RequestAppointment(root)

    def view_medical_records(self):
        ViewMedicalRecords(self.master)

    def logout(self):
        self.master.destroy()

    def back_to_login(self):
        self.master.destroy()
        root = tk.Tk()
        MediTrackApp(root)
        root.mainloop()

# View Personal Info with Password Reset
class ViewPersonalInfo:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Personal Info")
        master.geometry("500x400")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Your Personal Information", font=("Arial", 14)).grid(row=0, column=0, pady=10)
        self.info_text = tk.Text(main_frame, height=10, width=50)
        self.info_text.grid(row=1, column=0, pady=10)

        ttk.Button(main_frame, text="Change Password", command=self.change_password).grid(row=2, column=0, pady=5)
        ttk.Button(main_frame, text="Back", command=self.master.destroy).grid(row=3, column=0, pady=5)

        self.load_personal_info()

    def load_personal_info(self):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT first_name, last_name, email, address, contact_number FROM patients WHERE patient_id = 1")
        result = cursor.fetchone()
        db.close()

        if result:
            info = f"Name: {result[0]} {result[1]}\nEmail: {result[2]}\nAddress: {result[3]}\nContact: {result[4]}"
            self.info_text.insert(tk.END, info)
        else:
            messagebox.showerror("Error", "Failed to load personal information")

    def change_password(self):
        root = tk.Toplevel(self.master)
        ChangePassword(root)

# Change Password Window
class ChangePassword:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Change Password")
        master.geometry("400x250")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Old Password:").grid(row=0, column=0, pady=5, sticky="e")
        self.old_pass = ttk.Entry(main_frame, show="*")
        self.old_pass.grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Enter New Password:").grid(row=1, column=0, pady=5, sticky="e")
        self.new_pass = ttk.Entry(main_frame, show="*")
        self.new_pass.grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="Confirm New Password:").grid(row=2, column=0, pady=5, sticky="e")
        self.confirm_pass = ttk.Entry(main_frame, show="*")
        self.confirm_pass.grid(row=2, column=1, pady=5)

        ttk.Button(main_frame, text="Update Password", command=self.update_password).grid(row=3, column=0, columnspan=2, pady=10)

    def update_password(self):
        old_pass = self.old_pass.get().strip()
        new_pass = self.new_pass.get().strip()
        confirm_pass = self.confirm_pass.get().strip()

        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New passwords do not match!")
            return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT password FROM patients WHERE patient_id = 1")
        result = cursor.fetchone()

        if result and result[0] == old_pass:
            cursor.execute("UPDATE patients SET password = %s WHERE patient_id = 1", (new_pass,))
            db.commit()
            messagebox.showinfo("Success", "Password updated successfully!")
            self.master.destroy()
        else:
            messagebox.showerror("Error", "Old password is incorrect!")
        db.close()


# View Appointments with MergeSort and No Arguments
# View Appointments with MergeSort
import time  # Add this import at the top if not already present

class ViewAppointments:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.title("MediTrack - Your Appointments")
        self.window.geometry("800x500")
        apply_theme(self.window)

        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Patient ID:").grid(row=0, column=0, pady=5, sticky="e")
        self.patient_id_entry = ttk.Entry(main_frame)
        self.patient_id_entry.grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Sort By:").grid(row=1, column=0, pady=5, sticky="e")
        self.sort_var = tk.StringVar(value="Date")
        ttk.Combobox(main_frame, textvariable=self.sort_var, values=["Date", "Time", "Status", "Doctor"], state="readonly").grid(row=1, column=1, pady=5)

        # Sort direction buttons
        ttk.Button(main_frame, text="Sort Ascending", command=lambda: self.load_appointments(True)).grid(row=2, column=0, pady=5)
        ttk.Button(main_frame, text="Sort Descending", command=lambda: self.load_appointments(False)).grid(row=2, column=1, pady=5)

        columns = ("Appointment ID", "Doctor", "Date", "Time", "Status")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

        ttk.Button(main_frame, text="Back", command=self.window.destroy).grid(row=4, column=0, columnspan=2, pady=10)

        # Track sort direction
        self.sort_direction = True  # Default to ascending

    def merge(self, left, right, sort_key):
        result = []
        i = j = 0
        ascending = self.sort_direction

        while i < len(left) and j < len(right):
            if sort_key == "Date":
                comparison = left[i][2] <= right[j][2] if ascending else left[i][2] >= right[j][2]
            elif sort_key == "Time":
                comparison = left[i][3] <= right[j][3] if ascending else left[i][3] >= right[j][3]
            elif sort_key == "Status":
                comparison = left[i][4] <= right[j][4] if ascending else left[i][4] >= right[j][4]
            elif sort_key == "Doctor":
                comparison = left[i][1] <= right[j][1] if ascending else left[i][1] >= right[j][1]

            if comparison:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def merge_sort(self, arr, sort_key):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid], sort_key)
        right = self.merge_sort(arr[mid:], sort_key)
        return self.merge(left, right, sort_key)

    def load_appointments(self, direction=None):
        if direction is not None:
            self.sort_direction = direction

        patient_id = self.patient_id_entry.get().strip()
        if not patient_id or not patient_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Patient ID (numeric).")
            return

        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT a.appointment_id, CONCAT(d.first_name, ' ', d.last_name) AS doctor_name, 
                   a.appointment_date, a.appointment_time, a.status
            FROM Appointments a
            JOIN Doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
        """
        cursor.execute(query, (patient_id,))
        appointments = list(cursor.fetchall())
        db.close()

        self.tree.delete(*self.tree.get_children())
        if not appointments:
            messagebox.showinfo("No Appointments", "No appointments found for this patient.")
            return

        sort_by = self.sort_var.get()

        half_data = appointments[:len(appointments) // 2]
        start_time = time.time()
        self.merge_sort(half_data, sort_by)
        half_time = time.time() - start_time

        start_time = time.time()
        sorted_appointments = self.merge_sort(appointments, sort_by)
        full_time = time.time() - start_time

        for appt in sorted_appointments:
            self.tree.insert("", "end", values=appt)

        with open("sorting_times.txt", "a") as f:
            f.write(f"MergeSort (Appointments) - Half: {half_time:.6f}s, Full: {full_time:.6f}s, Size: {len(appointments)}, Direction: {'Ascending' if self.sort_direction else 'Descending'}\n")
            
class RequestAppointment:
    def __init__(self, master):
        self.master = master
        master.title("MediTrack - Request Appointment")
        master.geometry("400x400")
        apply_theme(master)

        main_frame = ttk.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Request New Appointment", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(main_frame, text="Patient ID:").grid(row=1, column=0, pady=5, sticky="e")
        self.patient_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.patient_id_var).grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="Doctor ID:").grid(row=2, column=0, pady=5, sticky="e")
        self.doctor_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.doctor_id_var).grid(row=2, column=1, pady=5)

        ttk.Label(main_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, pady=5, sticky="e")
        self.date_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.date_var).grid(row=3, column=1, pady=5)

        ttk.Label(main_frame, text="Time (HH:MM):").grid(row=4, column=0, pady=5, sticky="e")
        self.time_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.time_var).grid(row=4, column=1, pady=5)

        ttk.Button(main_frame, text="Submit Request", command=self.submit_request).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(main_frame, text="Back", command=self.master.destroy).grid(row=6, column=0, columnspan=2, pady=5)

    def submit_request(self):
        patient_id = self.patient_id_var.get().strip()
        doctor_id = self.doctor_id_var.get().strip()
        date = self.date_var.get().strip()
        time = self.time_var.get().strip()

        if not all([patient_id, doctor_id, date, time]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            patient_id = int(patient_id)
            doctor_id = int(doctor_id)
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid ID or date/time format!")
            return

        db = connect_db()
        cursor = db.cursor()
        
        # Check if patient and doctor exist
        cursor.execute("SELECT COUNT(*) FROM Patients WHERE patient_id = %s", (patient_id,))
        if cursor.fetchone()[0] == 0:
            messagebox.showerror("Error", "Patient ID not found!")
            db.close()
            return
        
        cursor.execute("SELECT COUNT(*) FROM Doctors WHERE doctor_id = %s", (doctor_id,))
        if cursor.fetchone()[0] == 0:
            messagebox.showerror("Error", "Doctor ID not found!")
            db.close()
            return

        # Check doctor availability
        cursor.execute("""
            SELECT COUNT(*) FROM Appointments 
            WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s 
            AND status != 'Cancelled'
        """, (doctor_id, date, time))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "Doctor is already booked at this time!")
            db.close()
            return

        # Insert appointment request
        query = """
            INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, %s, 'Scheduled')
        """
        cursor.execute(query, (patient_id, doctor_id, date, time))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Appointment request submitted successfully!")
        self.master.destroy()
        
# View Medical Records with Treeview and HeapSort
# View Medical Records with Treeview, HeapSort, and No Arguments
class ViewMedicalRecords:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.title("MediTrack - Your Medical Records")
        self.window.geometry("800x500")
        apply_theme(self.window)

        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter Patient ID:").grid(row=0, column=0, pady=5, sticky="e")
        self.patient_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.patient_id_var).grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Sort By:").grid(row=1, column=0, pady=5, sticky="e")
        self.sort_var = tk.StringVar(value="Date")
        ttk.Combobox(main_frame, textvariable=self.sort_var, values=["Date", "Diagnosis", "Medications", "Treatment"], state="readonly").grid(row=1, column=1, pady=5)

        # Sort direction buttons
        ttk.Button(main_frame, text="Sort Ascending", command=lambda: self.load_records(True)).grid(row=2, column=0, pady=5)
        ttk.Button(main_frame, text="Sort Descending", command=lambda: self.load_records(False)).grid(row=2, column=1, pady=5)

        columns = ("Date", "Diagnosis", "Medications", "Treatment")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=190, anchor="center")
        self.tree.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

        ttk.Button(main_frame, text="Back", command=self.window.destroy).grid(row=4, column=0, columnspan=2, pady=5)

        # Track sort direction
        self.sort_direction = True  # Default to ascending

    def heapify(self, arr, n, i, sort_key):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        ascending = self.sort_direction

        if sort_key == "Date":
            key_idx = 3
            if left < n and ((arr[left][key_idx] > arr[largest][key_idx]) if ascending else (arr[left][key_idx] < arr[largest][key_idx])):
                largest = left
            if right < n and ((arr[right][key_idx] > arr[largest][key_idx]) if ascending else (arr[right][key_idx] < arr[largest][key_idx])):
                largest = right
        elif sort_key == "Diagnosis":
            key_idx = 0
            if left < n and ((arr[left][key_idx] > arr[largest][key_idx]) if ascending else (arr[left][key_idx] < arr[largest][key_idx])):
                largest = left
            if right < n and ((arr[right][key_idx] > arr[largest][key_idx]) if ascending else (arr[right][key_idx] < arr[largest][key_idx])):
                largest = right
        elif sort_key == "Medications":
            key_idx = 1
            if left < n and ((arr[left][key_idx] > arr[largest][key_idx]) if ascending else (arr[left][key_idx] < arr[largest][key_idx])):
                largest = left
            if right < n and ((arr[right][key_idx] > arr[largest][key_idx]) if ascending else (arr[right][key_idx] < arr[largest][key_idx])):
                largest = right
        elif sort_key == "Treatment":
            key_idx = 2
            if left < n and ((arr[left][key_idx] > arr[largest][key_idx]) if ascending else (arr[left][key_idx] < arr[largest][key_idx])):
                largest = left
            if right < n and ((arr[right][key_idx] > arr[largest][key_idx]) if ascending else (arr[right][key_idx] < arr[largest][key_idx])):
                largest = right

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self.heapify(arr, n, largest, sort_key)

    def heap_sort(self, arr, sort_key):
        n = len(arr)
        for i in range(n // 2 - 1, -1, -1):
            self.heapify(arr, n, i, sort_key)
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            self.heapify(arr, i, 0, sort_key)

    def load_records(self, direction=None):
        if direction is not None:
            self.sort_direction = direction

        patient_id = self.patient_id_var.get().strip()
        if not patient_id or not patient_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Patient ID (numeric).")
            return

        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT diagnosis, prescribed_medications, treatment_plan, record_date 
            FROM Medical_History 
            WHERE patient_id = %s
        """
        cursor.execute(query, (patient_id,))
        records = list(cursor.fetchall())
        db.close()

        self.tree.delete(*self.tree.get_children())
        if not records:
            messagebox.showinfo("No Records", "No medical records found for this patient.")
            return

        sort_by = self.sort_var.get()

        half_data = records[:len(records) // 2]
        start_time = time.time()
        self.heap_sort(half_data, sort_by)
        half_time = time.time() - start_time

        start_time = time.time()
        self.heap_sort(records, sort_by)
        full_time = time.time() - start_time

        for rec in records:
            self.tree.insert("", "end", values=(rec[3], rec[0], rec[1], rec[2]))

        with open("sorting_times.txt", "a") as f:
            f.write(f"HeapSort (Medical Records) - Half: {half_time:.6f}s, Full: {full_time:.6f}s, Size: {len(records)}, Direction: {'Ascending' if self.sort_direction else 'Descending'}\n")
            
if __name__ == "__main__":
    root = tk.Tk()
    MediTrackApp(root)
    root.mainloop()