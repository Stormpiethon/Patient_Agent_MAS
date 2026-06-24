CREATE TABLE medications (
    medication_id INTEGER PRIMARY KEY,
    medication_name VARCHAR(100),
    monthly_cost DECIMAL(10,2)
);

CREATE TABLE procedures (
    procedure_id INTEGER PRIMARY KEY,
    procedure_name VARCHAR(100),
    procedure_cost DECIMAL(10,2)
);

INSERT INTO medications VALUES
(1,'Levothyroxine',12.00),
(2,'Metformin',15.00),
(3,'Amoxicillin',18.00),
(4,'Lisinopril',10.00),
(5,'Insulin',325.00),
(6,'Omeprazole',14.00),
(7,'Atorvastatin',20.00),
(8,'Warfarin',16.00);

INSERT INTO procedures VALUES
(1,'Physical Therapy Evaluation',180.00),
(2,'Blood Panel',95.00),
(3,'Chest X-Ray',250.00),
(4,'ECG',175.00),
(5,'Echocardiogram',1200.00)

