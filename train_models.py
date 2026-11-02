"""Step 2: Clean the data, explore it, train 3 models, evaluate and save charts.
Run:  python train_models.py
"""
import json, warnings, joblib
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
                             confusion_matrix, roc_curve, ConfusionMatrixDisplay)
from sklearn.inspection import permutation_importance
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", font_scale=1.0)
FIG = "outputs/figures/"
log = {}

# ---------------- 1. Load and clean ----------------
raw = pd.read_csv("data/student_data_raw.csv")
log["raw_shape"] = list(raw.shape)
log["missing_before"] = {k: int(v) for k, v in raw.isna().sum().items() if v > 0}
log["duplicates"] = int(raw.duplicated().sum())
log["bad_attendance"] = int((raw.attendance_pct > 100).sum())

df = raw.drop_duplicates().copy()
df["attendance_pct"] = df["attendance_pct"].clip(upper=100)          # attendance cannot exceed 100 %
df.to_csv("data/student_data_clean_input.csv", index=False)
log["clean_shape"] = list(df.shape)
log["at_risk_pct"] = round(df.at_risk.mean() * 100, 1)
log["at_risk_count"] = int(df.at_risk.sum())

# ---------------- 2. EDA charts ----------------
fig, ax = plt.subplots(1, 2, figsize=(9, 3.8))
df.at_risk.map({0: "Not at risk", 1: "At risk"}).value_counts().plot.bar(ax=ax[0], color=["#2a9d8f", "#e76f51"], rot=0)
ax[0].set_title("Class distribution"); ax[0].set_ylabel("Students")
for p in ax[0].patches: ax[0].annotate(int(p.get_height()), (p.get_x() + .3, p.get_height() + 8))
sns.histplot(df.final_score, bins=25, kde=True, color="#264653", ax=ax[1]); ax[1].axvline(50, color="red", ls="--")
ax[1].set_title("Final score distribution (red line = 50 % cut-off)"); ax[1].set_xlabel("Final score (%)")
plt.tight_layout(); plt.savefig(FIG + "01_class_and_score.png", dpi=200); plt.close()

fig, ax = plt.subplots(1, 3, figsize=(11, 3.8))
for a, c, t in zip(ax, ["attendance_pct", "study_hours_week", "prev_gpa"], ["Attendance (%)", "Study hours / week", "Previous GPA"]):
    sns.boxplot(data=df, x="at_risk", y=c, ax=a, palette=["#2a9d8f", "#e76f51"]); a.set_xticklabels(["Not at risk", "At risk"])
    a.set_xlabel(""); a.set_ylabel(t); a.set_title(t + " vs risk")
plt.tight_layout(); plt.savefig(FIG + "02_boxplots.png", dpi=200); plt.close()

num = df.select_dtypes("number").drop(columns=["at_risk"])
plt.figure(figsize=(8.5, 6.5)); sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0, annot_kws={"size": 7})
plt.title("Correlation heatmap of numeric features"); plt.tight_layout(); plt.savefig(FIG + "03_correlation.png", dpi=200); plt.close()

dr = df.groupby("department").at_risk.mean().mul(100).sort_values(ascending=False)
plt.figure(figsize=(6.5, 3.6)); sns.barplot(x=dr.index, y=dr.values, color="#457b9d"); plt.ylabel("At-risk students (%)")
plt.title("At-risk percentage by department"); plt.xlabel("")
for i, v in enumerate(dr.values): plt.text(i, v + .4, f"{v:.1f}", ha="center", fontsize=8)
plt.tight_layout(); plt.savefig(FIG + "04_dept_risk.png", dpi=200); plt.close()

# ---------------- 3. Features and split ----------------
# final_score is NOT used as a feature (it would leak the answer); it only defines the label.
num_cols = ["attendance_pct", "study_hours_week", "prev_gpa", "internal_marks_avg", "assignments_submitted_pct",
            "backlogs", "sleep_hours", "stress_level", "commute_minutes"]
cat_cols = ["department", "gender", "part_time_job", "family_support", "internet_access", "extracurricular"]
X, y = df[num_cols + cat_cols], df["at_risk"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
log["train_rows"], log["test_rows"] = len(Xtr), len(Xte)

pre = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num_cols),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")), ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat_cols)])

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=3, class_weight="balanced", random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, learning_rate=0.05, max_depth=3, random_state=42)}

# ---------------- 4. Train and evaluate ----------------
cv = StratifiedKFold(5, shuffle=True, random_state=42)
rows, fitted, probs = [], {}, {}
for name, clf in models.items():
    pipe = Pipeline([("pre", pre), ("clf", clf)]).fit(Xtr, ytr)
    p = pipe.predict_proba(Xte)[:, 1]; pred = (p >= 0.5).astype(int)
    cvf1 = cross_val_score(Pipeline([("pre", pre), ("clf", clf)]), Xtr, ytr, cv=cv, scoring="f1").mean()
    rows.append(dict(Model=name, Accuracy=accuracy_score(yte, pred), Precision=precision_score(yte, pred),
                     Recall=recall_score(yte, pred), F1=f1_score(yte, pred), ROC_AUC=roc_auc_score(yte, p), CV_F1=cvf1))
    fitted[name], probs[name] = pipe, p
res = pd.DataFrame(rows).round(3); res.to_csv("outputs/model_results.csv", index=False)
print(res.to_string(index=False))
best = res.sort_values("F1", ascending=False).iloc[0]["Model"]; log["best_model"] = best
log["results"] = res.to_dict("records")

# model comparison chart
m = res.set_index("Model")[["Accuracy", "Precision", "Recall", "F1", "ROC_AUC"]]
ax = m.plot.bar(figsize=(9, 4), rot=0, colormap="viridis"); ax.set_ylim(0.5, 1.02); ax.set_title("Model comparison on the test set")
ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=8, frameon=False); plt.tight_layout(); plt.savefig(FIG + "05_model_comparison.png", dpi=200); plt.close()

# ROC curves
plt.figure(figsize=(5.5, 4.5))
for n, p in probs.items():
    f, t, _ = roc_curve(yte, p); plt.plot(f, t, label=f"{n} (AUC = {roc_auc_score(yte, p):.3f})")
plt.plot([0, 1], [0, 1], "k--", lw=.8); plt.xlabel("False positive rate"); plt.ylabel("True positive rate"); plt.title("ROC curves"); plt.legend(fontsize=8)
plt.tight_layout(); plt.savefig(FIG + "06_roc.png", dpi=200); plt.close()

# confusion matrix of best model
bp = (probs[best] >= .5).astype(int); cm = confusion_matrix(yte, bp); log["confusion"] = cm.tolist()
fig, ax = plt.subplots(figsize=(4.6, 4)); ConfusionMatrixDisplay(cm, display_labels=["Not at risk", "At risk"]).plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title(f"Confusion matrix – {best}"); ax.grid(False); plt.tight_layout(); plt.savefig(FIG + "07_confusion.png", dpi=200); plt.close()

# feature importance (permutation, on the raw columns, test set)
pi = permutation_importance(fitted[best], Xte, yte, n_repeats=15, random_state=42, scoring="f1")
imp = pd.Series(pi.importances_mean, index=X.columns).sort_values()
plt.figure(figsize=(7, 5)); imp.tail(10).plot.barh(color="#e76f51"); plt.title(f"Top 10 features – permutation importance ({best})")
plt.xlabel("Drop in F1 when the feature is shuffled"); plt.tight_layout(); plt.savefig(FIG + "08_feature_importance.png", dpi=200); plt.close()
log["top_features"] = [[k, round(float(v), 4)] for k, v in imp.sort_values(ascending=False).head(8).items()]

# ---------------- 5. Save model and outputs ----------------
joblib.dump(fitted[best], "models/best_model.joblib")
out = Xte.copy(); out["student_id"] = df.loc[Xte.index, "student_id"]; out["department"] = df.loc[Xte.index, "department"]
out["actual_at_risk"] = yte; out["risk_probability"] = probs[best].round(3)
out.to_csv("outputs/test_predictions.csv", index=False)
json.dump(log, open("outputs/run_log.json", "w"), indent=2, default=str)
print(json.dumps({k: log[k] for k in ["raw_shape", "clean_shape", "at_risk_pct", "best_model", "confusion", "top_features"]}, indent=1))
