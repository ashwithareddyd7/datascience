"""Step 3: Interactive dashboard (Streamlit).
Install:  pip install streamlit pandas scikit-learn joblib matplotlib
Run:      streamlit run dashboard.py
(Run generate_data.py and train_models.py once before this.)
"""
import joblib, pandas as pd, streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Student Risk Dashboard", layout="wide")
model = joblib.load("models/best_model.joblib")
data = pd.read_csv("outputs/test_predictions.csv")

page = st.sidebar.radio("Select view", ["Overview", "Predict a student"])

if page == "Overview":
    st.title("Student Academic Risk – Overview")
    dept = st.sidebar.multiselect("Department", sorted(data.department.unique()), default=sorted(data.department.unique()))
    d = data[data.department.isin(dept)]
    c1, c2, c3 = st.columns(3)
    c1.metric("Students", len(d))
    c2.metric("Predicted high risk (>= 50 %)", int((d.risk_probability >= .5).sum()))
    c3.metric("Average attendance", f"{d.attendance_pct.mean():.1f} %")
    left, right = st.columns(2)
    fig, ax = plt.subplots(); (d.groupby("department").risk_probability.mean() * 100).plot.bar(ax=ax, color="#457b9d")
    ax.set_ylabel("Average risk probability (%)"); left.pyplot(fig)
    fig, ax = plt.subplots(); ax.scatter(d.attendance_pct, d.risk_probability * 100, c=d.risk_probability, cmap="RdYlGn_r", s=14)
    ax.set_xlabel("Attendance (%)"); ax.set_ylabel("Risk probability (%)"); right.pyplot(fig)
    st.subheader("Students needing attention")
    st.dataframe(d.sort_values("risk_probability", ascending=False).head(15)
                 [["student_id", "department", "attendance_pct", "prev_gpa", "backlogs", "risk_probability"]])
else:
    st.title("Predict risk for one student")
    c1, c2 = st.columns(2)
    row = {
        "attendance_pct": c1.slider("Attendance (%)", 30, 100, 75),
        "study_hours_week": c1.slider("Study hours per week", 0, 30, 8),
        "prev_gpa": c1.slider("Previous GPA", 3.5, 10.0, 7.0),
        "internal_marks_avg": c1.slider("Internal marks average", 10, 100, 60),
        "assignments_submitted_pct": c1.slider("Assignments submitted (%)", 10, 100, 70),
        "backlogs": c2.slider("Backlogs", 0, 8, 0),
        "sleep_hours": c2.slider("Sleep hours", 3.5, 10.0, 6.5),
        "stress_level": c2.slider("Stress level (1-5)", 1, 5, 3),
        "commute_minutes": c2.slider("Commute (minutes)", 5, 150, 30),
        "department": c2.selectbox("Department", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"]),
        "gender": c2.selectbox("Gender", ["Male", "Female"]),
        "part_time_job": c2.selectbox("Part-time job", ["No", "Yes"]),
        "family_support": c2.selectbox("Family support", ["Low", "Medium", "High"], index=1),
        "internet_access": c2.selectbox("Internet access", ["Yes", "No"]),
        "extracurricular": c2.selectbox("Extracurricular", ["No", "Yes"]),
    }
    p = model.predict_proba(pd.DataFrame([row]))[0, 1]
    st.metric("Risk probability", f"{p * 100:.1f} %")
    st.progress(float(p))
    if p >= .5:
        st.error("HIGH RISK – recommend counselling and extra support.")
    elif p >= .3:
        st.warning("MEDIUM RISK – monitor attendance and internal marks.")
    else:
        st.success("LOW RISK – student is on track.")
