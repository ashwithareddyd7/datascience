"""
app.py — IT Branch Student Marks Portal
-----------------------------------------
Flow:
  1. Pick Section (A/B/C/D)
  2. Pick Student (60 per section)
  3. Click a Semester tab (Sem 1 / Sem 2 / Sem 3 / Sem 4)
     -> Subject-wise marks table appears
     -> "Download Memo (PDF)" button at the bottom generates that semester's marksheet
  4. Scroll down for the performance visualization across all completed semesters

Run with:
    streamlit run app.py
"""

import io
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DB_PATH = "student_marks.db"
SECTIONS = ["A", "B", "C", "D"]
SEMESTERS = [1, 2, 3, 4]

st.set_page_config(page_title="IT Branch Marks Portal", layout="wide")


# ---------- Data access ----------

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def get_students(section: str) -> pd.DataFrame:
    conn = get_conn()
    return pd.read_sql_query(
        "SELECT student_id, name, roll_no FROM students WHERE section = ? ORDER BY roll_no",
        conn, params=(section,),
    )


def get_marks_for_sem(student_id: int, sem: int) -> pd.DataFrame:
    conn = get_conn()
    return pd.read_sql_query(
        """
        SELECT sub.subject_name AS Subject, m.marks_obtained AS "Marks Obtained",
               m.max_marks AS "Max Marks"
        FROM marks m
        JOIN subjects sub ON sub.subject_id = m.subject_id
        WHERE m.student_id = ? AND m.sem = ?
        ORDER BY sub.subject_id
        """,
        conn, params=(student_id, sem),
    )


def get_all_sem_summary(student_id: int) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT sem, SUM(marks_obtained) AS total_obtained, SUM(max_marks) AS total_max
        FROM marks WHERE student_id = ? GROUP BY sem ORDER BY sem
        """,
        conn, params=(student_id,),
    )
    df["percentage"] = (df["total_obtained"] / df["total_max"] * 100).round(2)
    return df


# ---------- PDF memo generation ----------

def build_memo_pdf(student_name: str, roll_no: str, section: str, sem: int, marks_df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=16)
    elements = []

    elements.append(Paragraph("IT Branch — Semester Marks Memo", title_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Name:</b> {student_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Roll No:</b> {roll_no} &nbsp;&nbsp;&nbsp; <b>Section:</b> {section}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Semester:</b> {sem}", styles["Normal"]))
    elements.append(Spacer(1, 14))

    total_obtained = int(marks_df["Marks Obtained"].sum())
    total_max = int(marks_df["Max Marks"].sum())
    percentage = round(total_obtained / total_max * 100, 2)

    table_data = [["Subject", "Marks Obtained", "Max Marks"]]
    for _, row in marks_df.iterrows():
        table_data.append([row["Subject"], str(row["Marks Obtained"]), str(row["Max Marks"])])
    table_data.append(["Total", str(total_obtained), str(total_max)])

    tbl = Table(table_data, colWidths=[80 * mm, 45 * mm, 45 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecf0f1")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f7f9fa")]),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 14))
    elements.append(Paragraph(f"<b>Percentage: {percentage}%</b>", styles["Normal"]))

    doc.build(elements)
    buf.seek(0)
    return buf.read()


# ---------- UI ----------

st.title("🎓 IT Branch — Student Marks Portal")
st.caption("4 Sections × 60 Students × 4 Semesters — click through to view marks, download memos, and see performance trends.")

col1, col2 = st.columns([1, 2])

with col1:
    section = st.selectbox("Select Section", SECTIONS)

students_df = get_students(section)

with col2:
    student_label = st.selectbox(
        "Select Student",
        students_df.apply(lambda r: f"{r['roll_no']} — {r['name']}", axis=1),
    )

selected_row = students_df.iloc[
    students_df.apply(lambda r: f"{r['roll_no']} — {r['name']}", axis=1) == student_label
].index[0]
student = students_df.loc[selected_row]
student_id = int(student["student_id"])

st.markdown("---")
st.subheader(f"📄 {student['name']} ({student['roll_no']}) — Section {section}")

tabs = st.tabs([f"Sem {s}" for s in SEMESTERS])

for sem, tab in zip(SEMESTERS, tabs):
    with tab:
        marks_df = get_marks_for_sem(student_id, sem)
        if marks_df.empty:
            st.info("No marks recorded for this semester yet.")
        else:
            st.dataframe(marks_df, width="stretch", hide_index=True)

            total_obtained = int(marks_df["Marks Obtained"].sum())
            total_max = int(marks_df["Max Marks"].sum())
            pct = round(total_obtained / total_max * 100, 2)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total", f"{total_obtained}/{total_max}")
            m2.metric("Percentage", f"{pct}%")
            m3.metric("Subjects", len(marks_df))

            pdf_bytes = build_memo_pdf(student["name"], student["roll_no"], section, sem, marks_df)
            st.download_button(
                label="⬇️ Download Memo (PDF)",
                data=pdf_bytes,
                file_name=f"{student['roll_no']}_Sem{sem}_Memo.pdf",
                mime="application/pdf",
                key=f"download_sem_{sem}",
            )

# ---------- Visualization ----------

st.markdown("---")
st.subheader("📈 Performance Across Semesters")

summary_df = get_all_sem_summary(student_id)
summary_df = summary_df[summary_df["total_max"] > 0]

if summary_df.empty:
    st.info("No data available yet for visualization.")
else:
    vcol1, vcol2 = st.columns(2)

    with vcol1:
        fig1, ax1 = plt.subplots(figsize=(5, 3.5))
        ax1.plot(summary_df["sem"], summary_df["percentage"], marker="o", linewidth=2, color="#2980b9")
        for x, y in zip(summary_df["sem"], summary_df["percentage"]):
            ax1.annotate(f"{y}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
        ax1.set_xticks(summary_df["sem"])
        ax1.set_xlabel("Semester")
        ax1.set_ylabel("Percentage")
        ax1.set_title("Percentage Trend")
        ax1.set_ylim(0, 100)
        ax1.grid(alpha=0.3)
        st.pyplot(fig1)

    with vcol2:
        fig2, ax2 = plt.subplots(figsize=(5, 3.5))
        ax2.bar(summary_df["sem"].astype(str), summary_df["percentage"], color="#27ae60")
        ax2.set_xlabel("Semester")
        ax2.set_ylabel("Percentage")
        ax2.set_title("Semester-wise Comparison")
        ax2.set_ylim(0, 100)
        ax2.grid(axis="y", alpha=0.3)
        st.pyplot(fig2)

    best_sem = summary_df.loc[summary_df["percentage"].idxmax()]
    worst_sem = summary_df.loc[summary_df["percentage"].idxmin()]
    st.success(
        f"Best performance: **Sem {int(best_sem['sem'])}** ({best_sem['percentage']}%) — "
        f"Needs attention: **Sem {int(worst_sem['sem'])}** ({worst_sem['percentage']}%)"
    )
