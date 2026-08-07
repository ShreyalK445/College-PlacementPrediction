import requests
import json

url = "http://127.0.0.1:5000/predict"

# 1. Single sample prediction
single_payload = {
    "IQ": 120,
    "Prev_Sem_Result": 7.97,
    "CGPA": 7.76,
    "Academic_Performance": 1,
    "Extra_Curricular_Score": 9,
    "Communication_Skills": 9,
    "Projects_Completed": 2,
    "Internship_Experience": 1.0
}

print("--- Testing Single Prediction ---")
try:
    response = requests.post(url, json=single_payload)
    print("Status Code:", response.status_code)
    print("Response JSON:\n", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error during single prediction request:", e)

# 2. Batch sample prediction
batch_payload = [
    {
        "IQ": 120,
        "Prev_Sem_Result": 7.97,
        "CGPA": 7.76,
        "Academic_Performance": 1,
        "Extra_Curricular_Score": 9,
        "Communication_Skills": 9,
        "Projects_Completed": 2,
        "Internship_Experience": 1.0
    },
    {
        "IQ": 101,
        "Prev_Sem_Result": 8.34,
        "CGPA": 7.87,
        "Academic_Performance": 9,
        "Extra_Curricular_Score": 7,
        "Communication_Skills": 9,
        "Projects_Completed": 3,
        "Internship_Experience": 0.0
    }
]

print("\n--- Testing Batch Prediction ---")
try:
    response = requests.post(url, json=batch_payload)
    print("Status Code:", response.status_code)
    print("Response JSON:\n", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error during batch prediction request:", e)
