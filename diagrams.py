"""Draws the architecture and UML diagrams used in the report."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle, FancyArrowPatch
FIG = "outputs/figures/"

def box(ax, x, y, w, h, text, fc="#dbeafe", ec="#1e3a8a", fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else None, wrap=True)

def arrow(ax, p, q, style="-|>", ls="-", color="#333"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=12, lw=1.2, ls=ls, color=color))

# ---------- 1. Architecture ----------
fig, ax = plt.subplots(figsize=(10, 4.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")
layers = [("Data Layer", ["Simulated student\nrecords (CSV)\n1,208 rows"], "#fde68a"),
          ("Preparation Layer", ["Remove duplicates\nFix invalid values", "Impute missing\nvalues", "Scale numbers\nOne-hot encode"], "#bbf7d0"),
          ("Modelling Layer", ["Logistic\nRegression", "Random\nForest", "Gradient\nBoosting"], "#bfdbfe"),
          ("Evaluation Layer", ["Accuracy, Precision,\nRecall, F1, ROC-AUC", "Confusion matrix\nFeature importance"], "#fbcfe8"),
          ("Presentation Layer", ["Streamlit dashboard:\nOverview + Predict"], "#ddd6fe")]
y = 3.75
for i, (name, items, col) in enumerate(layers):
    ax.text(0.1, y + .35, name, fontsize=9.5, fontweight="bold", va="center")
    n = len(items); w = 2.2; gap = .25; x0 = 2.5
    for j, t in enumerate(items): box(ax, x0 + j * (w + gap), y, w, .7, t, fc=col, fs=8.3)
    if i < len(layers) - 1: arrow(ax, (5.4, y), (5.4, y - .33))
    y -= 1.0
plt.tight_layout(); plt.savefig(FIG + "d1_architecture.png", dpi=200); plt.close()

# ---------- 2. Use case ----------
fig, ax = plt.subplots(figsize=(9, 5.4)); ax.set_xlim(0, 9); ax.set_ylim(0, 5.4); ax.axis("off")
ax.add_patch(Rectangle((2.2, .2), 4.6, 5.0, fc="#f8fafc", ec="#334155", lw=1.4)); ax.text(4.5, 4.95, "Student Risk Prediction System", ha="center", fontweight="bold", fontsize=10)
ucs = ["Upload / load student data", "Clean and prepare data", "Train and compare models", "View evaluation results", "View overview dashboard", "Predict risk for a student", "Get support recommendation"]
pos = {}
for i, u in enumerate(ucs):
    cy = 4.4 - i * 0.62; ax.add_patch(Ellipse((4.5, cy), 3.5, .5, fc="#dbeafe", ec="#1e3a8a")); ax.text(4.5, cy, u, ha="center", va="center", fontsize=8.5); pos[i] = cy
def actor(x, y, name):
    ax.add_patch(plt.Circle((x, y + .45), .15, fc="white", ec="k")); ax.plot([x, x], [y + .3, y - .1], "k", lw=1.3)
    ax.plot([x - .25, x + .25], [y + .15, y + .15], "k", lw=1.3); ax.plot([x, x - .2], [y - .1, y - .4], "k", lw=1.3); ax.plot([x, x + .2], [y - .1, y - .4], "k", lw=1.3)
    ax.text(x, y - .65, name, ha="center", fontsize=9, fontweight="bold")
actor(1.0, 3.3, "Data Analyst\n(Student)"); actor(8.0, 3.3, "Faculty /\nMentor"); actor(8.0, 1.1, "Admin / HOD")
for i in [0, 1, 2, 3]: ax.plot([1.25, 2.75], [3.3, pos[i]], color="#555", lw=.9)
for i in [4, 5, 6]: ax.plot([7.75, 6.25], [3.3, pos[i]], color="#555", lw=.9)
for i in [4, 3]: ax.plot([7.75, 6.25], [1.1, pos[i]], color="#555", lw=.9)
plt.tight_layout(); plt.savefig(FIG + "d2_usecase.png", dpi=200); plt.close()

# ---------- 3. Class diagram ----------
fig, ax = plt.subplots(figsize=(10, 4.8)); ax.set_xlim(0, 10); ax.set_ylim(0, 4.8); ax.axis("off")
def cls(x, y, w, name, attrs, meths, fc="#e0f2fe"):
    h = .42 + .22 * (len(attrs) + len(meths)) + .3
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec="#0c4a6e", lw=1.3)); ax.text(x + w / 2, y + h - .22, name, ha="center", fontweight="bold", fontsize=9)
    ax.plot([x, x + w], [y + h - .42, y + h - .42], color="#0c4a6e", lw=1)
    yy = y + h - .62
    for a in attrs: ax.text(x + .08, yy, a, fontsize=7.6, va="center"); yy -= .22
    ax.plot([x, x + w], [yy + .11, yy + .11], color="#0c4a6e", lw=1); yy -= .1
    for m in meths: ax.text(x + .08, yy, m, fontsize=7.6, va="center"); yy -= .22
    return (x + w / 2, y + h / 2, x, y, w, h)
a = cls(.2, 2.3, 2.4, "DataLoader", ["+ path : str", "+ raw_df : DataFrame"], ["+ load()", "+ remove_duplicates()", "+ fix_invalid()"])
b = cls(3.0, 2.3, 2.5, "Preprocessor", ["+ num_cols : list", "+ cat_cols : list"], ["+ impute()", "+ scale()", "+ encode()"], "#dcfce7")
c = cls(5.9, 2.3, 2.0, "ModelTrainer", ["+ models : dict", "+ best : Pipeline"], ["+ train()", "+ cross_validate()", "+ save()"], "#fef9c3")
d = cls(8.2, 2.3, 1.7, "Evaluator", ["+ metrics : dict"], ["+ score()", "+ confusion()", "+ importance()"], "#fce7f3")
e = cls(3.4, .1, 3.2, "Dashboard", ["+ model : Pipeline", "+ data : DataFrame"], ["+ show_overview()", "+ predict_student()"], "#ede9fe")
for p, q in [((2.6, 3.2), (3.0, 3.2)), ((5.5, 3.2), (5.9, 3.2)), ((7.9, 3.2), (8.2, 3.2))]: arrow(ax, p, q)
arrow(ax, (6.9, 2.3), (5.6, 1.35), ls="--"); ax.text(6.6, 1.7, "uses saved\nmodel", fontsize=7.5)
plt.tight_layout(); plt.savefig(FIG + "d3_class.png", dpi=200); plt.close()

# ---------- 4. Sequence ----------
fig, ax = plt.subplots(figsize=(10, 5.2)); ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")
names = ["User", "Dashboard", "Model\n(Pipeline)", "Data Store"]; xs = [1.2, 3.8, 6.4, 8.9]
for n, x in zip(names, xs):
    box(ax, x - .8, 4.5, 1.6, .55, n, fc="#e0e7ff", fs=9, bold=True); ax.plot([x, x], [4.5, .2], "--", color="#64748b", lw=1)
msgs = [(0, 1, 4.0, "1. Select 'Predict a student'"), (0, 1, 3.45, "2. Enter attendance, GPA, backlogs ..."), (1, 2, 2.9, "3. predict_proba(row)"),
        (2, 1, 2.35, "4. risk probability"), (1, 3, 1.8, "5. read overview data (optional)"), (3, 1, 1.3, "6. return records"), (1, 0, .7, "7. Show risk level + advice")]
for s, t, yy, txt in msgs:
    arrow(ax, (xs[s], yy), (xs[t], yy), ls="-" if s < t else "--"); ax.text((xs[s] + xs[t]) / 2, yy + .1, txt, ha="center", fontsize=8.3)
plt.tight_layout(); plt.savefig(FIG + "d4_sequence.png", dpi=200); plt.close()
print("diagrams done")
