import json


# Basic function to load the JSON data for a specific patient
def load_patient(patient_id):
    try:
        with open("data/john_doe.json", "r") as f:
            patient = json.load(f)
        
        if patient.get("patient_id") == patient_id:
            return patient
        else:
            print(f"Error: Patient ID '{patient_id}' does not match.")
            return None
            
    except FileNotFoundError:
        print("Error: The patient data file was not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
        return None


# Pull the patient's basic information
def get_patient_info(patient_id):
    try:
        patient = load_patient(patient_id)
        if patient:
            # Returns a dictionary of basic info
            return {
                "patient_id": patient["patient_id"],
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"]
            }
    except KeyError as e:
        print(f"Data Error: Missing expected field {e} in patient record.")
    return None


# Pull the information that is from the patient's lab visits
def get_labs(patient_id):
    try:
        patient = load_patient(patient_id)
        if patient:
            return patient["labs"]
    except KeyError:
        print("Data Error: 'labs' field not found for this patient.")
    return None


# Pull a list of the patient's current medications
def get_medications(patient_id):
    try:
        patient = load_patient(patient_id)
        if patient:
            return patient["medications"]
    except KeyError:
        print("Data Error: 'medications' field not found for this patient.")
    return None


# Pull a list of any procedures the patient has had
def get_procedures(patient_id):
    try:
        patient = load_patient(patient_id)
        if patient:
            return patient["procedures"]
    except KeyError:
        print("Data Error: 'procedures' field not found for this patient.")
    return None


# Pull a list of written observations of the patient
def get_observations(patient_id):
    try:
        patient = load_patient(patient_id)

        if patient:
            return patient["observations"]

    except KeyError:
        print("Data Error: 'observations' field not found for this patient.")

    return None