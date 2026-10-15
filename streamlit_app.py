"""
College Placement Prediction — Streamlit Dashboard (Enhanced)

Features:
- Premium UI with custom CSS
- Model metadata display
- Feature importance visualization
- Prediction history in session state
- Batch CSV upload prediction
"""

import json
import os

import pandas as pd
import pickle
import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="College Placement Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    h1 {
        background: linear-gradient(120deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    .stButton>button {
        background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }

    .success-banner {
        background: linear-gradient(135deg, #059669 0%, #34d399 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 8px 30px rgba(5, 150, 105, 0.3);
    }

    .fail-banner {
        background: linear-gradient(135deg, #dc2626 0%, #f87171 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 8px 30px rgba(220, 38, 38, 0.3);
    }

    div[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "model.pkl")
metadata_path = os.path.join(base_dir, "model_metadata.json")


@st.cache_resource
def load_model():
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            return pickle.load(f)
    return None


@st.cache_data
def load_metadata():
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            return json.load(f)
    return None


model = load_model()
metadata = load_metadata()

# ---------------------------------------------------------------------------
# Sidebar — Model Info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📊 Model Information")

    if metadata:
        st.markdown(f"**Version:** `{metadata.get('model_version', 'N/A')}`")
        st.markdown(f"**Type:** {metadata.get('model_type', 'N/A')}")
        st.markdown(f"**Trained:** {metadata.get('trained_at', 'N/A')[:10]}")

        eval_data = metadata.get("evaluation", {})
        st.markdown("---")
        st.markdown("### 🎯 Performance Metrics")
        col_a, col_b = st.columns(2)
        col_a.metric("Accuracy", f"{eval_data.get('accuracy', 0):.1%}")
        col_b.metric("F1 Score", f"{eval_data.get('f1_score', 0):.1%}")
        col_c, col_d = st.columns(2)
        col_c.metric("Precision", f"{eval_data.get('precision', 0):.1%}")
        col_d.metric("AUC-ROC", f"{eval_data.get('auc_roc', 0):.1%}")

        # Feature importance chart
        fi = metadata.get("feature_importance", {})
        if fi:
            st.markdown("---")
            st.markdown("### 📈 Feature Importance")
            fi_df = pd.DataFrame(
                list(fi.items()), columns=["Feature", "Importance"]
            ).sort_values("Importance", ascending=True)
            st.bar_chart(fi_df.set_index("Feature"))
    else:
        st.info("No model metadata found. Train the model to see details.")

    st.markdown("---")
    st.markdown("### ⚙️ Navigation")
    page = st.radio(
        "Choose a view:",
        ["🔮 Single Prediction", "📦 Batch Prediction", "📜 Prediction History"],
        label_visibility="collapsed",
    )

# ---------------------------------------------------------------------------
# Initialize session state
# ---------------------------------------------------------------------------
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title("🎓 College Placement Predictor")

if model is None:
    st.error("⚠️ **Model not found!** Please run `python model_building.py` first.")
    st.stop()

# ===== SINGLE PREDICTION =====
if page == "🔮 Single Prediction":
    st.markdown("#### Enter student details to predict placement likelihood")
    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        iq = st.slider("🧠 IQ Score", min_value=50, max_value=150, value=100, step=1)
        prev_sem = st.slider("📝 Previous Semester GPA", min_value=0.0, max_value=10.0, value=7.5, step=0.01)
        cgpa = st.slider("📊 CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.01)
        academic_perf = st.slider("🏫 Academic Performance", min_value=1, max_value=10, value=6, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        extra_curricular = st.slider("🏆 Extra-Curricular Score", min_value=1, max_value=10, value=5, step=1)
        comm_skills = st.slider("🗣️ Communication Skills", min_value=1, max_value=10, value=6, step=1)
        projects = st.slider("💻 Projects Completed", min_value=0, max_value=10, value=2, step=1)
        internship = st.selectbox("💼 Internship Experience", options=["No", "Yes"])
        st.markdown('</div>', unsafe_allow_html=True)

    internship_val = 1.0 if internship == "Yes" else 0.0

    st.markdown("")
    predict_col1, predict_col2, predict_col3 = st.columns([1, 2, 1])
    with predict_col2:
        predict_clicked = st.button("🚀 Predict Placement", use_container_width=True)

    if predict_clicked:
        features = pd.DataFrame([{
            "IQ": iq,
            "Prev_Sem_Result": prev_sem,
            "CGPA": cgpa,
            "Academic_Performance": academic_perf,
            "Extra_Curricular_Score": extra_curricular,
            "Communication_Skills": comm_skills,
            "Projects_Completed": projects,
            "Internship_Experience": internship_val,
        }])

        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1] if hasattr(model, "predict_proba") else None

        # Save to history
        record = features.iloc[0].to_dict()
        record["Prediction"] = "Placed" if prediction == 1 else "Not Placed"
        record["Probability"] = f"{probability:.2%}" if probability is not None else "N/A"
        st.session_state.prediction_history.append(record)

        st.markdown("")
        if prediction == 1:
            st.markdown(
                f'<div class="success-banner">🎉 Prediction: PLACED<br>'
                f'<span style="font-size:1rem;">Confidence: {probability:.1%}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="fail-banner">😔 Prediction: NOT PLACED<br>'
                f'<span style="font-size:1rem;">Confidence: {1 - probability:.1%}</span></div>',
                unsafe_allow_html=True,
            )

        # Show contributing factors
        if hasattr(model, "feature_importances_"):
            st.markdown("")
            st.markdown("#### 🔍 Key Contributing Factors")
            fi = dict(zip(features.columns, model.feature_importances_))
            fi_sorted = dict(sorted(fi.items(), key=lambda x: x[1], reverse=True))
            fi_df = pd.DataFrame(
                list(fi_sorted.items()), columns=["Feature", "Importance"]
            )
            st.bar_chart(fi_df.set_index("Feature"))

# ===== BATCH PREDICTION =====
elif page == "📦 Batch Prediction":
    st.markdown("#### Upload a CSV file for batch predictions")
    st.markdown("CSV must contain columns: `IQ`, `Prev_Sem_Result`, `CGPA`, `Academic_Performance`, "
                "`Extra_Curricular_Score`, `Communication_Skills`, `Projects_Completed`, `Internship_Experience`")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
            required_cols = [
                "IQ", "Prev_Sem_Result", "CGPA", "Academic_Performance",
                "Extra_Curricular_Score", "Communication_Skills",
                "Projects_Completed", "Internship_Experience",
            ]
            missing = [c for c in required_cols if c not in batch_df.columns]
            if missing:
                st.error(f"Missing columns: {missing}")
            else:
                st.markdown(f"**Loaded {len(batch_df)} records**")
                st.dataframe(batch_df.head())

                if st.button("🚀 Run Batch Prediction"):
                    input_features = batch_df[required_cols]
                    predictions = model.predict(input_features)
                    probabilities = (
                        model.predict_proba(input_features)[:, 1]
                        if hasattr(model, "predict_proba")
                        else [None] * len(predictions)
                    )

                    results_df = batch_df.copy()
                    results_df["Prediction"] = ["Placed" if p == 1 else "Not Placed" for p in predictions]
                    results_df["Probability"] = [f"{p:.2%}" if p is not None else "N/A" for p in probabilities]

                    st.markdown("### 📊 Results")
                    st.dataframe(results_df, use_container_width=True)

                    # Summary stats
                    placed = sum(1 for p in predictions if p == 1)
                    total = len(predictions)
                    col_s1, col_s2, col_s3 = st.columns(3)
                    col_s1.metric("Total Students", total)
                    col_s2.metric("Placed", placed)
                    col_s3.metric("Placement Rate", f"{placed / total:.1%}")

                    # Download button
                    csv_output = results_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Results CSV",
                        csv_output,
                        file_name="placement_predictions.csv",
                        mime="text/csv",
                    )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# ===== PREDICTION HISTORY =====
elif page == "📜 Prediction History":
    st.markdown("#### Session Prediction History")

    if st.session_state.prediction_history:
        history_df = pd.DataFrame(st.session_state.prediction_history)
        st.dataframe(history_df, use_container_width=True)

        placed = sum(1 for r in st.session_state.prediction_history if r["Prediction"] == "Placed")
        total = len(st.session_state.prediction_history)

        col_h1, col_h2, col_h3 = st.columns(3)
        col_h1.metric("Total Predictions", total)
        col_h2.metric("Placed", placed)
        col_h3.metric("Not Placed", total - placed)

        if st.button("🗑️ Clear History"):
            st.session_state.prediction_history = []
            st.rerun()
    else:
        st.info("No predictions yet. Go to **Single Prediction** to get started!")
