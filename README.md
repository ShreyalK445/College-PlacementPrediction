# 🎓 College Placement Prediction API

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API-black?style=for-the-badge&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Random Forest](https://img.shields.io/badge/Model-Random%20Forest-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

</p>

---

## 📌 Overview

The **College Placement Prediction API** is a Machine Learning-powered REST API built using **Flask** and **Scikit-Learn**. The project predicts whether a student is likely to be placed based on academic performance, communication skills, internships, extracurricular activities, and other placement-related attributes.

The model is trained using a **Random Forest Classifier** and deployed as a RESTful API capable of handling both **single** and **batch** prediction requests.

---

# ✨ Features

- 🎯 Predict student placement status
- 📊 Returns prediction probability
- 🤖 Random Forest Machine Learning model
- 🚀 Flask REST API
- 📦 Supports Batch Predictions
- 🔥 Easy deployment
- 🧪 Python test client included
- 📈 Model serialized using Pickle

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Programming Language |
| Flask | REST API |
| Scikit-Learn | Machine Learning |
| Pandas | Data Processing |
| NumPy | Numerical Computing |
| Pickle | Model Serialization |

---

# 📁 Project Structure

```text
College-Placement-Prediction/
│
├── College_placement.csv      # Dataset
├── requirements.txt           # Dependencies
├── model_building.py          # Model training script
├── model.pkl                  # Trained model
├── app.py                     # Flask API
├── test_client.py             # API testing script
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/College-Placement-Prediction.git

cd College-Placement-Prediction
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🧠 Train the Machine Learning Model

Run

```bash
python model_building.py
```

This script:

- Loads the dataset
- Performs preprocessing
- Splits training/testing data
- Trains a Random Forest Classifier
- Evaluates the model
- Saves the trained model as

```text
model.pkl
```

---

# 🚀 Run the Flask API

```bash
python app.py
```

Server starts at

```text
http://127.0.0.1:5000
```

---

# 📡 API Endpoint

## POST `/predict`

Predicts student placement.

---

## Request Headers

```http
Content-Type: application/json
```

---

## Single Prediction Request

```json
{
  "IQ": 120,
  "Prev_Sem_Result": 7.97,
  "CGPA": 7.76,
  "Academic_Performance": 1,
  "Extra_Curricular_Score": 9,
  "Communication_Skills": 9,
  "Projects_Completed": 2,
  "Internship_Experience": 1.0
}
```

---

## Successful Response

```json
{
  "results": {
    "placement_prediction": 1,
    "placement_probability": 0.97,
    "status": "Placed"
  }
}
```

---

# 📦 Batch Prediction

The API also supports multiple predictions in one request.

```json
[
  {
    "IQ":120,
    "Prev_Sem_Result":7.97,
    "CGPA":7.76,
    "Academic_Performance":1,
    "Extra_Curricular_Score":9,
    "Communication_Skills":9,
    "Projects_Completed":2,
    "Internship_Experience":1.0
  },
  {
    "IQ":101,
    "Prev_Sem_Result":8.34,
    "CGPA":7.87,
    "Academic_Performance":9,
    "Extra_Curricular_Score":7,
    "Communication_Skills":9,
    "Projects_Completed":3,
    "Internship_Experience":0.0
  }
]
```

---

# 🧪 Testing the API

## PowerShell

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/predict `
-Method Post `
-ContentType "application/json" `
-Body '{
"IQ":120,
"Prev_Sem_Result":7.97,
"CGPA":7.76,
"Academic_Performance":1,
"Extra_Curricular_Score":9,
"Communication_Skills":9,
"Projects_Completed":2,
"Internship_Experience":1.0
}'
```

---

## cURL

```bash
curl -X POST http://127.0.0.1:5000/predict \
-H "Content-Type: application/json" \
-d '{
"IQ":120,
"Prev_Sem_Result":7.97,
"CGPA":7.76,
"Academic_Performance":1,
"Extra_Curricular_Score":9,
"Communication_Skills":9,
"Projects_Completed":2,
"Internship_Experience":1.0
}'
```

---

## Python Client

```bash
python test_client.py
```

---

# 🏗 Model Workflow

```text
                Dataset
                   │
                   ▼
          Data Preprocessing
                   │
                   ▼
          Feature Selection
                   │
                   ▼
      Random Forest Classifier
                   │
                   ▼
            Trained Model
               model.pkl
                   │
                   ▼
              Flask API
                   │
                   ▼
        Placement Prediction
```

---

# 📊 Input Features

| Feature | Description |
|----------|-------------|
| IQ | Student IQ Score |
| Prev_Sem_Result | Previous Semester GPA |
| CGPA | Overall CGPA |
| Academic_Performance | Academic Rating |
| Extra_Curricular_Score | Extracurricular Score |
| Communication_Skills | Communication Rating |
| Projects_Completed | Number of Projects |
| Internship_Experience | Internship Experience |

---

# 📈 Prediction Output

| Value | Meaning |
|--------|---------|
| 1 | Placed |
| 0 | Not Placed |

---

# 🔮 Future Improvements

- Docker Support
- CI/CD Pipeline
- Model Versioning
- Swagger Documentation
- Authentication
- Cloud Deployment (AWS/Azure/GCP)
- Streamlit Dashboard

---

# 👨‍💻 Author

**Your Name**

Machine Learning • Data Science • Flask API Development

---

## ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub to support the project.

---

<p align="center">
Made with ❤️ using Python, Flask & Scikit-Learn
</p>
