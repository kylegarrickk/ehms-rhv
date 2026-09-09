CREATE DATABASE IF NOT EXISTS ehms_rhv;

USE ehms_rhv;

CREATE TABLE Patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(20),
    phone VARCHAR(15),
    village VARCHAR(100)
);

CREATE TABLE Health_Centre (
    centre_id INT PRIMARY KEY AUTO_INCREMENT,
    centre_name VARCHAR(100) NOT NULL,
    location VARCHAR(150),
    total_beds INT DEFAULT 0,
    available_beds INT DEFAULT 0
);

CREATE TABLE Ambulance (
    ambulance_id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_number VARCHAR(30) UNIQUE NOT NULL,
    status VARCHAR(30) DEFAULT 'Available',
    current_location VARCHAR(150)
);

CREATE TABLE Doctor (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    status VARCHAR(30) DEFAULT 'Available',
    centre_id INT,
    FOREIGN KEY (centre_id) REFERENCES Health_Centre(centre_id)
);

CREATE TABLE Emergency (
    emergency_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    priority INT NOT NULL,
    emergency_type VARCHAR(100),
    status VARCHAR(30) DEFAULT 'Pending',
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id)
);

CREATE TABLE Road_Status (
    road_id INT PRIMARY KEY AUTO_INCREMENT,
    village VARCHAR(100),
    destination VARCHAR(100),
    status VARCHAR(30) DEFAULT 'Open'
);

CREATE TABLE Emergency_Log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    emergency_id INT NOT NULL,
    action VARCHAR(255),
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emergency_id) REFERENCES Emergency(emergency_id)
);