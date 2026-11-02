"""Renders the two dashboard views to PNG (same data and model the Streamlit app uses).
Used for the report's output screens."""
import joblib, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
FIG = "outputs/figures/"
data = pd.read_csv("outputs/test_predictions.csv"); model = joblib.load("models/best_model.joblib")
BG, SIDE = "#ffffff", "#f0f2f6"

def frame(title, w=12, h=7):
    fig = plt.figure(figsize=(w, h)); fig.patch.set_facecolor(BG)
    bar = fig.add_axes([0, .955, 1, .045]); bar.set_facecolor("#e5e7eb"); bar.axis("off")
    bar.text(.01, .5, "●  ●  ●     localhost:8501", fontsize=8, va="center", color="#555")
    side = fig.add_axes([0, 0, .2, .955]); side.set_facecolor(SIDE); side.set_xticks([]); side.set_yticks([])
    for s in side.spines.values(): s.set_visible(False)
    fig.text(.225, .915, title, fontsize=17, fontweight="bold")
    return fig, side

def kpi(fig, x, label, val):
    ax = fig.add_axes([x, .76, .17, .11]); ax.axis("off"); ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=.05", fc="#f8fafc", ec="#d1d5db", transform=ax.transAxes))
    ax.text(.08, .68, label, fontsize=8.5, color="#555", transform=ax.transAxes); ax.text(.08, .22, val, fontsize=18, fontweight="bold", transform=ax.transAxes)

# ---------- View 1: Overview ----------
fig, side = frame("Student Academic Risk – Overview")
side.text(.08, .94, "Select view", fontsize=9, fontweight="bold", transform=side.transAxes)
side.text(.1, .89, "◉  Overview", fontsize=9, transform=side.transAxes); side.text(.1, .85, "○  Predict a student", fontsize=9, transform=side.transAxes)
side.text(.08, .76, "Department", fontsize=9, fontweight="bold", transform=side.transAxes)
for i, d in enumerate(sorted(data.department.unique())):
    side.text(.1, .715 - i * .045, d, fontsize=8, transform=side.transAxes, bbox=dict(boxstyle="round", fc="#ff4b4b", ec="none", alpha=.9), color="white")
kpi(fig, .225, "Students", f"{len(data)}"); kpi(fig, .42, "Predicted high risk (>= 50 %)", f"{int((data.risk_probability >= .5).sum())}")
kpi(fig, .615, "Average attendance", f"{data.attendance_pct.mean():.1f} %"); kpi(fig, .81, "Departments", f"{data.department.nunique()}")
a1 = fig.add_axes([.26, .42, .29, .27]); (data.groupby("department").risk_probability.mean() * 100).plot.bar(ax=a1, color="#457b9d", rot=0); a1.set_ylabel("Avg risk probability (%)", fontsize=8); a1.set_xlabel(""); a1.tick_params(labelsize=8); a1.set_title("Average risk by department", fontsize=9)
a2 = fig.add_axes([.64, .42, .33, .27]); sc = a2.scatter(data.attendance_pct, data.risk_probability * 100, c=data.risk_probability, cmap="RdYlGn_r", s=10); a2.set_xlabel("Attendance (%)", fontsize=8); a2.set_ylabel("Risk probability (%)", fontsize=8); a2.tick_params(labelsize=8); a2.set_title("Attendance vs risk", fontsize=9)
fig.text(.225, .355, "Students needing attention", fontsize=12, fontweight="bold")
top = data.sort_values("risk_probability", ascending=False).head(7)[["student_id", "department", "attendance_pct", "prev_gpa", "backlogs", "risk_probability"]]
tb = fig.add_axes([.225, .04, .75, .3]); tb.axis("off")
t = tb.table(cellText=top.values, colLabels=list(top.columns), loc="upper center", cellLoc="center"); t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.45)
for (r, c), cell in t.get_celld().items():
    cell.set_edgecolor("#d1d5db")
    if r == 0: cell.set_facecolor("#f0f2f6"); cell.set_text_props(fontweight="bold")
plt.savefig(FIG + "v1_dashboard_overview.png", dpi=170); plt.close()

# ---------- View 2: Predict ----------
row = dict(attendance_pct=62, study_hours_week=5, prev_gpa=5.8, internal_marks_avg=45, assignments_submitted_pct=55, backlogs=2, sleep_hours=5.5, stress_level=4,
           commute_minutes=60, department="IT", gender="Female", part_time_job="No", family_support="Medium", internet_access="Yes", extracurricular="No")
p = float(model.predict_proba(pd.DataFrame([row]))[0, 1])
fig, side = frame("Predict risk for one student")
side.text(.08, .94, "Select view", fontsize=9, fontweight="bold", transform=side.transAxes)
side.text(.1, .89, "○  Overview", fontsize=9, transform=side.transAxes); side.text(.1, .85, "◉  Predict a student", fontsize=9, transform=side.transAxes)
def slider(x, y, label, val, lo, hi, fmt="{}"):
    ax = fig.add_axes([x, y, .3, .05]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0, .95, label, fontsize=8.5); f = (val - lo) / (hi - lo)
    ax.plot([0, 1], [.35, .35], color="#d1d5db", lw=3); ax.plot([0, f], [.35, .35], color="#ff4b4b", lw=3); ax.plot(f, .35, "o", color="#ff4b4b", ms=8)
    ax.text(f, .62, fmt.format(val), fontsize=8, ha="center", color="#ff4b4b")
L = [("Attendance (%)", 62, 30, 100), ("Study hours per week", 5, 0, 30), ("Previous GPA", 5.8, 3.5, 10), ("Internal marks average", 45, 10, 100), ("Assignments submitted (%)", 55, 10, 100)]
for i, (l, v, lo, hi) in enumerate(L): slider(.235, .8 - i * .085, l, v, lo, hi)
R = [("Backlogs", 2, 0, 8), ("Sleep hours", 5.5, 3.5, 10), ("Stress level (1-5)", 4, 1, 5), ("Commute (minutes)", 60, 5, 150)]
for i, (l, v, lo, hi) in enumerate(R): slider(.6, .8 - i * .085, l, v, lo, hi)
for i, (l, v) in enumerate([("Department", "IT"), ("Family support", "Medium")]):
    ax = fig.add_axes([.6 + i * .16, .42, .14, .06]); ax.axis("off"); ax.text(0, .85, l, fontsize=8.5); ax.add_patch(Rectangle((0, 0), 1, .55, fc="#f0f2f6", ec="#d1d5db")); ax.text(.08, .27, v, fontsize=9, va="center")
fig.text(.235, .345, "Risk probability", fontsize=9, color="#555"); fig.text(.235, .28, f"{p * 100:.1f} %", fontsize=26, fontweight="bold")
pb = fig.add_axes([.235, .22, .6, .025]); pb.axis("off"); pb.add_patch(Rectangle((0, 0), 1, 1, fc="#e5e7eb")); pb.add_patch(Rectangle((0, 0), p, 1, fc="#ff4b4b")); pb.set_xlim(0, 1); pb.set_ylim(0, 1)
lvl = ("HIGH RISK – recommend counselling and extra support.", "#fde2e2", "#9b1c1c") if p >= .5 else (("MEDIUM RISK – monitor attendance and internal marks.", "#fef3c7", "#92400e") if p >= .3 else ("LOW RISK – student is on track.", "#dcfce7", "#166534"))
bn = fig.add_axes([.235, .08, .6, .08]); bn.axis("off"); bn.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=.1", fc=lvl[1], ec="none", transform=bn.transAxes)); bn.text(.03, .5, lvl[0], fontsize=11, color=lvl[2], va="center", transform=bn.transAxes)
plt.savefig(FIG + "v2_dashboard_predict.png", dpi=170); plt.close()
print("risk probability shown:", round(p, 3))
