import streamlit as st
import pandas as pd
import pickle
import os

# Set page configuration with premium design look
st.set_page_config(
    page_title="College Placement Predictor",
    page_icon="🎓",
    layout="centered"
)

# Custom styling for rich aesthetics
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 College Placement Predictor")
st.markdown("Enter student telemetry and performance features below to predict placement likelihood.")

# Load the model
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'model.pkl')

@st.cache_resource
def load_model():
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    return None

model = load_model()

if model is None:
    st.error("⚠️ Error: `model.pkl` not found! Please run the training script first.")
else:
    # Feature columns layout
    col1, col2 = st.columns(2)
    
    with col1:
        iq = st.slider("IQ", min_value=50, max_value=150, value=100, step=1)
        prev_sem = st.slider("Previous Semester Result (GPA)", min_value=0.0, max_value=10.0, value=7.5, step=0.01)
        cgpa = st.slider("CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.01)
        academic_perf = st.slider("Academic Performance Score", min_value=1, max_value=10, value=6, step=1)
        
    with col2:
        extra_curricular = st.slider("Extra-Curricular Score", min_value=1, max_value=10, value=5, step=1)
        comm_skills = st.slider("Communication Skills", min_value=1, max_value=10, value=6, step=1)
        projects = st.slider("Projects Completed", min_value=0, max_value=10, value=2, step=1)
        internship = st.selectbox("Internship Experience", options=["No", "Yes"])

    # Map internship to float value
    internship_val = 1.0 if internship == "Yes" else 0.0

    st.markdown("---")

    # Predict button
    if st.button("Predict Placement Status"):
        # Make DataFrame with features in correct training order
        features = pd.DataFrame([{
            'IQ': iq,
            'Prev_Sem_Result': prev_sem,
            'CGPA': cgpa,
            'Academic_Performance': academic_perf,
            'Extra_Curricular_Score': extra_curricular,
            'Communication_Skills': comm_skills,
            'Projects_Completed': projects,
            'Internship_Experience': internship_val
        }])
        
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1] if hasattr(model, 'predict_proba') else None
        
        if prediction == 1:
            st.success("### 🎉 Prediction: **Placed**")
            if probability is not None:
                st.metric(label="Confidence Level", value=f"{probability:.2%}")
        else:
            st.warning("### 😢 Prediction: **Not Placed**")
            if probability is not None:
                st.metric(label="Confidence Level (Unplaced)", value=f"{(1 - probability):.2%}")
