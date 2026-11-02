"""
generate_data.py
-----------------
Creates the SQLite database (student_marks.db) with schema:

    students(student_id, name, roll_no, section)
    subjects(subject_id, sem, subject_name)
    marks(mark_id, student_id, sem, subject_id, marks_obtained, max_marks)

Then fills it with realistic synthetic data for:
    4 sections (A, B, C, D) x 60 students x 4 semesters x 6 subjects/sem

Run this once (or whenever you want to regenerate demo data):
    python generate_data.py
"""

import sqlite3
import random

DB_PATH = "student_marks.db"

SECTIONS = ["A", "B", "C", "D"]
STUDENTS_PER_SECTION = 60
SEMESTERS = [1, 2, 3, 4]

# Subjects offered each semester (customize freely per your curriculum)
SUBJECTS_BY_SEM = {
    1: ["Mathematics-I", "Physics", "Programming in C", "English", "Engineering Graphics", "Basic Electronics"],
    2: ["Mathematics-II", "Data Structures", "Digital Logic Design", "OOP with Java", "Environmental Science", "Communication Skills"],
    3: ["Discrete Mathematics", "DBMS", "Operating Systems", "Computer Networks", "Python Programming", "Probability & Statistics"],
    4: ["Design & Analysis of Algorithms", "Software Engineering", "Machine Learning Basics", "Web Technologies", "Automata Theory", "Data Science Fundamentals"],
}

MAX_MARKS = 100

FIRST_NAMES = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Krishna","Ishaan","Rohan",
               "Ananya","Diya","Isha","Aadhya","Kavya","Meera","Riya","Saanvi","Tara","Zara",
               "Karan","Nikhil","Rahul","Suresh","Manoj","Deepak","Pooja","Neha","Priya","Sneha",
               "Vikram","Sanjay","Anil","Ramesh","Sunil","Kiran","Latha","Divya","Swathi","Harini",
               "Yash","Dev","Kabir","Aryan","Shaurya","Om","Advait","Arnav","Dhruv","Reyan",
               "Anjali","Bhavya","Chitra","Deepika","Esha","Farha","Gita","Hema","Indira","Jaya"]

LAST_NAMES = ["Sharma","Verma","Reddy","Rao","Naidu","Iyer","Nair","Gupta","Kumar","Singh",
              "Patel","Chowdary","Mishra","Das","Bose","Menon","Pillai","Shetty","Kulkarni","Joshi"]


def build_schema(conn):
    cur = conn.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS marks;
    DROP TABLE IF EXISTS students;
    DROP TABLE IF EXISTS subjects;

    CREATE TABLE students (
        student_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        roll_no     TEXT NOT NULL UNIQUE,
        section     TEXT NOT NULL
    );

    CREATE TABLE subjects (
        subject_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        sem          INTEGER NOT NULL,
        subject_name TEXT NOT NULL
    );

    CREATE TABLE marks (
        mark_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id     INTEGER NOT NULL,
        sem            INTEGER NOT NULL,
        subject_id     INTEGER NOT NULL,
        marks_obtained INTEGER NOT NULL,
        max_marks      INTEGER NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    );
    """)
    conn.commit()


def seed_subjects(conn):
    cur = conn.cursor()
    subject_ids = {}  # (sem, subject_name) -> subject_id
    for sem, subs in SUBJECTS_BY_SEM.items():
        for s in subs:
            cur.execute("INSERT INTO subjects (sem, subject_name) VALUES (?, ?)", (sem, s))
            subject_ids[(sem, s)] = cur.lastrowid
    conn.commit()
    return subject_ids


def seed_students_and_marks(conn, subject_ids):
    cur = conn.cursor()
    for section in SECTIONS:
        for i in range(1, STUDENTS_PER_SECTION + 1):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            roll_no = f"IT{section}{i:03d}"
            cur.execute(
                "INSERT INTO students (name, roll_no, section) VALUES (?, ?, ?)",
                (name, roll_no, section),
            )
            student_id = cur.lastrowid

            # Give each student a "skill level" so marks trend realistically
            # across semesters instead of being pure random noise.
            base_ability = random.gauss(70, 12)  # average ability out of 100
            improvement_trend = random.uniform(-3, 6)  # some improve, some decline slightly

            for sem in SEMESTERS:
                sem_ability = base_ability + improvement_trend * (sem - 1)
                for subject_name in SUBJECTS_BY_SEM[sem]:
                    subj_id = subject_ids[(sem, subject_name)]
                    noise = random.gauss(0, 8)
                    marks = int(round(sem_ability + noise))
                    marks = max(18, min(MAX_MARKS, marks))  # clamp between 18 and 100
                    cur.execute(
                        """INSERT INTO marks (student_id, sem, subject_id, marks_obtained, max_marks)
                           VALUES (?, ?, ?, ?, ?)""",
                        (student_id, sem, subj_id, marks, MAX_MARKS),
                    )
    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)
    build_schema(conn)
    subject_ids = seed_subjects(conn)
    seed_students_and_marks(conn, subject_ids)
    conn.close()
    print(f"Database created: {DB_PATH}")
    print(f"Sections: {SECTIONS} | Students/section: {STUDENTS_PER_SECTION} | Semesters: {SEMESTERS}")


if __name__ == "__main__":
    main()
