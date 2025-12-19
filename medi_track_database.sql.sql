-- 1️⃣ Create Admin Table
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,  -- Plain text password storage
    full_name VARCHAR(100),
    contact_number VARCHAR(15),
    email VARCHAR(100) UNIQUE, 
    role ENUM('Admin') NOT NULL DEFAULT 'Admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2️⃣ Create Doctors Table
CREATE TABLE Doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    password VARCHAR(50) NOT NULL,  -- Plain text password storage
    working_hours VARCHAR(100) NOT NULL, -- Example: '09:00-17:00'
    contact_number VARCHAR(15),
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('Doctor') NOT NULL DEFAULT 'Doctor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3️⃣ Create Patients Table
CREATE TABLE Patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    password VARCHAR(50) NOT NULL,  -- Plain text password storage
    contact_number VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE,
    address TEXT,
    role ENUM('Patient') NOT NULL DEFAULT 'Patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4️⃣ Create Appointments Table
CREATE TABLE Appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Scheduled',
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE CASCADE
);

-- 5️⃣ Create Medical History Table
CREATE TABLE Medical_History (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    diagnosis TEXT NOT NULL,
    prescribed_medications TEXT,
    treatment_plan TEXT,
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);
ALTER TABLE admin DROP username;
ALTER TABLE appointments add appointment_time time not null;
ALTER TABLE appointments MODIFY COLUMN appointment_date DATE NOT NULL;

