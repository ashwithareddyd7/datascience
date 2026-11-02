# IT Branch — Student Marks Portal

A working prototype for your idea: track marks for 4 sections × 60 students across
4 semesters, drill down subject-wise, download a PDF memo, and visualize performance trends.

## 1. Architecture

```
Browser (Streamlit UI)
        |
        v
   app.py  ── queries ──>  student_marks.db (SQLite)
        |
        └── generates ──> PDF memo (ReportLab, in-memory, no files saved to disk)
```

- **Database**: SQLite (file-based, zero setup). Swap for MySQL/PostgreSQL later just by
  changing the connection string — the SQL queries stay almost the same.
- **Backend + Frontend**: Streamlit handles both — no separate API server needed for a
  student/college-scale project like this.
- **PDF memo**: generated on the fly with ReportLab when the user clicks "Download",
  not stored on disk.
- **Charts**: Matplotlib, rendered inline in the app.

## 2. Database Schema

| Table      | Columns                                                              |
|------------|-----------------------------------------------------------------------|
| `students` | student_id (PK), name, roll_no, section                              |
| `subjects` | subject_id (PK), sem, subject_name                                   |
| `marks`    | mark_id (PK), student_id (FK), sem, subject_id (FK), marks_obtained, max_marks |

This normalized design means:
- Adding a new semester = insert rows into `subjects` + `marks`, no schema change.
- Adding a new section/student = just insert into `students`.
- You can compute totals, percentages, and trends purely with SQL aggregation.

## 3. Setup & Run

```bash
pip install streamlit pandas matplotlib reportlab

# 1. Generate the database with sample data (240 students, 4 sems, 6 subjects/sem)
python generate_data.py

# 2. Launch the app
streamlit run app.py
```

It'll open in your browser at `http://localhost:8501`.

## 4. How it matches your idea

| Your requirement | Where it's implemented |
|---|---|
| 4 sections, 60 members each | `SECTIONS` + section dropdown → filtered student list |
| Click a student → see sem 1, sem 2... | Tabs for Sem 1–4 under each student |
| Marks shown subject-wise | Table inside each semester tab |
| Download memo at the bottom | "Download Memo (PDF)" button under each semester's table |
| Visualization of performance across semesters | Line chart (trend) + bar chart (comparison) at the bottom, with best/weakest semester called out |

## 5. Realistic sample data

`generate_data.py` doesn't just fill random numbers — each student gets a hidden
"ability" score plus a per-student improvement/decline trend, so the percentage
graphs actually look like real academic trends (some students improving,
some dipping) instead of random noise. Replace this generator with your real
marks data whenever you have it (see Section 6).

## 6. Next steps to make it production-ready

1. **Load real data**: replace `generate_data.py` with a script that reads your actual
   marks (e.g., from Excel/CSV exports from your college ERP) and inserts them into the
   same schema — no changes needed to `app.py`.
2. **Authentication**: add a login page (e.g., `streamlit-authenticator`) so each student
   only sees their own marks, and faculty/admin see all.
3. **CGPA/SGPA**: if your college uses grade points instead of raw percentage, add a
   `grade_points` column and compute SGPA/CGPA instead of (or alongside) percentage.
4. **Class-level analytics**: add a "Section Overview" page showing average performance,
   toppers, and at-risk students per subject/section — useful for faculty.
5. **Deploy**: Streamlit Community Cloud (free) or a college server — just push this
   folder to GitHub and connect it.

## 7. Files in this project

- `generate_data.py` — builds the SQLite database + sample data
- `app.py` — the Streamlit application (all UI + logic)
- `student_marks.db` — generated SQLite database (created after running step 1)
- `README.md` — this file
