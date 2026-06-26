CREATE TABLE medications (
    cost_code VARCHAR(20) PRIMARY KEY,
    medication_name VARCHAR(100) NOT NULL,
    monthly_cost DECIMAL(10,2) NOT NULL
);

CREATE TABLE procedures (
    cost_code VARCHAR(20) PRIMARY KEY,
    procedure_name VARCHAR(100) NOT NULL,
    procedure_cost DECIMAL(10,2) NOT NULL
);

INSERT INTO medications VALUES
('RX1001', 'Metformin', 15.00),
('RX1002', 'Lisinopril', 10.00),
('RX1003', 'Atorvastatin', 20.00),
('RX1004', 'Levothyroxine', 12.00),
('RX1005', 'Amoxicillin', 18.00),
('RX1006', 'Insulin', 325.00),
('RX1007', 'Omeprazole', 14.00),
('RX1008', 'Warfarin', 16.00);

INSERT INTO procedures VALUES
('PROC2001', 'Blood Panel', 95.00),
('PROC2002', 'Chest X-Ray', 250.00),
('PROC2003', 'Physical Therapy Evaluation', 180.00),
('PROC2004', 'ECG', 175.00),
('PROC2005', 'Echocardiogram', 1200.00);
