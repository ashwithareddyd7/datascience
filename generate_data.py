"""Step 1: Generate the simulated student dataset (1,200 students).
The data is simulated because real student records are confidential.
Run:  python generate_data.py
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
N = 1200

dept = rng.choice(["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"], N, p=[.28, .22, .20, .12, .10, .08])
gender = rng.choice(["Male", "Female"], N, p=[.54, .46])
attendance = np.clip(rng.normal(76, 13, N), 30, 100)
study_hours = np.clip(rng.gamma(4.0, 1.6, N), 0, 30)
prev_gpa = np.clip(rng.normal(6.9, 1.2, N), 3.5, 10)
internal = np.clip(0.55 * prev_gpa * 10 + 0.25 * attendance + rng.normal(0, 8, N), 10, 100)
assign = np.clip(0.6 * attendance + rng.normal(25, 12, N), 10, 100)
backlogs = np.clip(np.round(np.maximum(0, (7.2 - prev_gpa) * 1.1 + rng.normal(0, 1.1, N))), 0, 8).astype(int)
sleep = np.clip(rng.normal(6.6, 1.1, N), 3.5, 10)
stress = np.clip(np.round(2.6 + 0.35 * backlogs - 0.15 * (sleep - 6.6) + rng.normal(0, 0.9, N)), 1, 5).astype(int)
part_job = rng.choice(["Yes", "No"], N, p=[.18, .82])
family_support = rng.choice(["Low", "Medium", "High"], N, p=[.15, .45, .40])
internet = rng.choice(["Yes", "No"], N, p=[.88, .12])
extra = rng.choice(["Yes", "No"], N, p=[.42, .58])
commute = np.clip(rng.gamma(2.2, 14, N), 5, 150)

fs_map = {"Low": -4, "Medium": 0, "High": 3}
score = (-13 + 0.30 * attendance + 0.9 * study_hours + 4.2 * prev_gpa + 0.18 * internal + 0.12 * assign
         - 2.8 * backlogs - 1.2 * (stress - 3) + 0.8 * (sleep - 6.6)
         - 4.0 * (part_job == "Yes") + np.vectorize(fs_map.get)(family_support)
         - 3.0 * (internet == "No") - 0.03 * commute + rng.normal(0, 5.5, N))
final_score = np.clip(score, 5, 100)

df = pd.DataFrame({
    "student_id": [f"S{1000 + i}" for i in range(N)], "department": dept, "gender": gender,
    "attendance_pct": attendance.round(1), "study_hours_week": study_hours.round(1),
    "prev_gpa": prev_gpa.round(2), "internal_marks_avg": internal.round(1),
    "assignments_submitted_pct": assign.round(1), "backlogs": backlogs, "sleep_hours": sleep.round(1),
    "stress_level": stress, "part_time_job": part_job, "family_support": family_support,
    "internet_access": internet, "extracurricular": extra, "commute_minutes": commute.round(0),
    "final_score": final_score.round(1)})

# Definition of "at risk": predicted final score below 50 %
df["at_risk"] = (df["final_score"] < 50).astype(int)

# Make the data messy on purpose (real data is never clean) so the cleaning step has work to do
for col, frac in [("sleep_hours", .04), ("study_hours_week", .03), ("family_support", .02), ("commute_minutes", .03)]:
    df.loc[rng.choice(N, int(N * frac), replace=False), col] = np.nan
df.loc[rng.choice(N, 6, replace=False), "attendance_pct"] = rng.choice([105, 112, 130], 6)   # impossible values
df = pd.concat([df, df.sample(8, random_state=1)], ignore_index=True)                        # duplicate rows
df.to_csv("data/student_data_raw.csv", index=False)
print(df.shape, "\nAt-risk share:", round(df.at_risk.mean() * 100, 1), "%")
