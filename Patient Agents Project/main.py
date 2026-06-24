# Import all relevant agent tools
from agents.Records_Agent import *

print("*** success on imports ***\n")

print(get_patient_info("jd-001"))
print(get_labs("jd-001"))
print(get_medications("jd-001"))
print(get_procedures("jd-001"))
print(get_observations("jd-001"))