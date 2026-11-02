import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "sunwai.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade TEXT NOT NULL,
        preferred_language TEXT DEFAULT 'en-IN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grade TEXT NOT NULL,
        skill TEXT NOT NULL,
        question_text TEXT NOT NULL,
        expected_answer TEXT NOT NULL,
        hint TEXT
    )
    """)

    # 3. Learning Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        student_reasoning TEXT NOT NULL,
        is_correct BOOLEAN NOT NULL,
        detected_misconception TEXT,
        misconception_category TEXT,
        confidence_score REAL,
        simple_reteaching_explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )
    """)

    # 4. Detected Misconceptions History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detected_misconceptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        skill TEXT NOT NULL,
        misconception_name TEXT NOT NULL,
        misconception_category TEXT NOT NULL,
        frequency INTEGER DEFAULT 1,
        last_detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """)

    # 5. Skill Progress Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        skill TEXT NOT NULL,
        questions_attempted INTEGER DEFAULT 0,
        questions_correct INTEGER DEFAULT 0,
        mastery_percentage REAL DEFAULT 0.0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id),
        UNIQUE(student_id, skill)
    )
    """)

    # Seed initial student if table empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO students (name, grade, preferred_language)
        VALUES ('Aarav Sharma', 'Class 5', 'en-IN')
        """)

    # Seed initial questions if table empty
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        seed_questions = [
            # Flagship Subtraction demo question
            ("Class 5", "Subtraction", "35 - 18 = ?", "17", "Remember to borrow from the tens place when subtracting 8 from 5!"),
            ("Class 5", "Subtraction", "52 - 27 = ?", "25", "Since 2 is smaller than 7, borrow 1 ten from 5 tens."),
            ("Class 6", "Subtraction", "304 - 158 = ?", "146", "Borrow across zero: take from hundreds first."),

            # Addition
            ("Class 5", "Addition", "47 + 38 = ?", "85", "7 + 8 = 15; don't forget to carry over the 1 ten!"),
            ("Class 5", "Addition", "165 + 78 = ?", "243", "Align columns carefully: ones under ones, tens under tens."),

            # Multiplication
            ("Class 5", "Multiplication", "24 × 6 = ?", "144", "Multiply 6 × 4 = 24, carry the 2, then 6 × 2 = 12."),
            ("Class 6", "Multiplication", "23 × 14 = ?", "322", "Remember the zero placeholder when multiplying by the tens digit!"),
            ("Class 5", "Multiplication", "7 × 8 = ?", "56", "Think of (7 × 7) + 7."),

            # Division
            ("Class 5", "Division", "84 ÷ 4 = ?", "21", "Divide each digit starting from left: 8 ÷ 4 then 4 ÷ 4."),
            ("Class 6", "Division", "618 ÷ 6 = ?", "103", "6 goes into 1 zero times! Don't skip the middle zero."),
            ("Class 6", "Division", "13 ÷ 4 = ?", "3.25 or 3 R 1", "The remainder 1 is 1/4 (0.25), not 0.1."),

            # Fractions
            ("Class 6", "Fractions", "1/4 + 2/4 = ?", "3/4", "When denominators are identical, only add the numerators!"),
            ("Class 6", "Fractions", "1/2 + 1/3 = ?", "5/6", "Find common denominator 6 before adding."),
            ("Class 6", "Fractions", "Is 2/4 equal to 1/2?", "Yes, they are equivalent", "Divide numerator and denominator by 2."),

            # Place value
            ("Class 5", "Place value", "What is the place value of 7 in 472?", "70 (or 7 tens)", "7 is in the tens column."),
            ("Class 5", "Place value", "Which is larger: 0.4 or 0.19?", "0.4", "0.4 is 40 hundredths, whereas 0.19 is only 19 hundredths.")
        ]
        cursor.executemany("""
        INSERT INTO questions (grade, skill, question_text, expected_answer, hint)
        VALUES (?, ?, ?, ?, ?)
        """, seed_questions)

    # Initialize skill progress for student 1 if empty
    skills = ["Subtraction", "Addition", "Multiplication", "Division", "Fractions", "Place value"]
    for s in skills:
        cursor.execute("""
        INSERT OR IGNORE INTO skill_progress (student_id, skill, questions_attempted, questions_correct, mastery_percentage)
        VALUES (1, ?, 0, 0, 0.0)
        """, (s,))

    conn.commit()
    conn.close()

def get_questions(skill: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if skill:
        cursor.execute("SELECT * FROM questions WHERE skill = ? ORDER BY id ASC", (skill,))
    else:
        cursor.execute("SELECT * FROM questions ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_question_by_id(question_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_learning_session(
    student_id: int,
    question_id: int,
    student_reasoning: str,
    is_correct: bool,
    detected_misconception: Optional[str],
    misconception_category: Optional[str],
    confidence_score: float,
    simple_reteaching_explanation: Optional[str]
) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    # Insert learning session
    cursor.execute("""
    INSERT INTO learning_sessions 
    (student_id, question_id, student_reasoning, is_correct, detected_misconception, misconception_category, confidence_score, simple_reteaching_explanation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        question_id,
        student_reasoning,
        1 if is_correct else 0,
        detected_misconception,
        misconception_category,
        confidence_score,
        simple_reteaching_explanation
    ))
    session_id = cursor.lastrowid

    # Retrieve skill of question
    cursor.execute("SELECT skill FROM questions WHERE id = ?", (question_id,))
    q_row = cursor.fetchone()
    skill = q_row["skill"] if q_row else "Subtraction"

    # Update or insert detected misconception
    if not is_correct and detected_misconception:
        cursor.execute("""
        SELECT id, frequency FROM detected_misconceptions 
        WHERE student_id = ? AND misconception_name = ?
        """, (student_id, detected_misconception))
        existing_m = cursor.fetchone()
        if existing_m:
            cursor.execute("""
            UPDATE detected_misconceptions 
            SET frequency = frequency + 1, last_detected_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (existing_m["id"],))
        else:
            cursor.execute("""
            INSERT INTO detected_misconceptions (student_id, skill, misconception_name, misconception_category, frequency)
            VALUES (?, ?, ?, ?, 1)
            """, (student_id, skill, detected_misconception, misconception_category or "GENERAL"))

    # Update skill progress
    cursor.execute("""
    SELECT questions_attempted, questions_correct FROM skill_progress 
    WHERE student_id = ? AND skill = ?
    """, (student_id, skill))
    prog = cursor.fetchone()
    if prog:
        attempted = prog["questions_attempted"] + 1
        correct = prog["questions_correct"] + (1 if is_correct else 0)
        mastery = round((correct / attempted) * 100, 1)
        cursor.execute("""
        UPDATE skill_progress 
        SET questions_attempted = ?, questions_correct = ?, mastery_percentage = ?, last_updated = CURRENT_TIMESTAMP
        WHERE student_id = ? AND skill = ?
        """, (attempted, correct, mastery, student_id, skill))
    else:
        attempted = 1
        correct = 1 if is_correct else 0
        mastery = 100.0 if is_correct else 0.0
        cursor.execute("""
        INSERT INTO skill_progress (student_id, skill, questions_attempted, questions_correct, mastery_percentage)
        VALUES (?, ?, ?, ?, ?)
        """, (student_id, skill, attempted, correct, mastery))

    conn.commit()
    conn.close()
    return session_id

def get_student_progress(student_id: int = 1) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    student_name = student["name"] if student else "Aarav Sharma"
    grade = student["grade"] if student else "Class 5"
    pref_lang = student["preferred_language"] if student else "en-IN"

    # Skill breakdown
    cursor.execute("""
    SELECT skill, questions_attempted, questions_correct, mastery_percentage 
    FROM skill_progress 
    WHERE student_id = ?
    ORDER BY mastery_percentage DESC
    """, (student_id,))
    skill_rows = [dict(r) for r in cursor.fetchall()]

    total_attempted = sum(r["questions_attempted"] for r in skill_rows)
    total_correct = sum(r["questions_correct"] for r in skill_rows)
    overall_accuracy = round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0.0

    mastered = [r["skill"] for r in skill_rows if r["mastery_percentage"] >= 80.0 and r["questions_attempted"] >= 2]
    needing_improvement = [r["skill"] for r in skill_rows if r["mastery_percentage"] < 70.0 and r["questions_attempted"] > 0]

    # Recent sessions
    cursor.execute("""
    SELECT s.id, s.question_id, q.question_text, q.skill, s.student_reasoning, 
           s.is_correct, s.detected_misconception, s.confidence_score, s.created_at
    FROM learning_sessions s
    JOIN questions q ON s.question_id = q.id
    WHERE s.student_id = ?
    ORDER BY s.created_at DESC
    LIMIT 6
    """, (student_id,))
    recent_sessions = [dict(r) for r in cursor.fetchall()]

    # Misconceptions breakdown
    cursor.execute("""
    SELECT skill, misconception_name, frequency, last_detected_at 
    FROM detected_misconceptions 
    WHERE student_id = ?
    ORDER BY frequency DESC, last_detected_at DESC
    """, (student_id,))
    common_misconceptions = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "student_name": student_name,
        "grade": grade,
        "preferred_language": pref_lang,
        "total_questions": total_attempted,
        "correct_count": total_correct,
        "accuracy_percentage": overall_accuracy,
        "skills_mastered": mastered,
        "skills_needing_improvement": needing_improvement,
        "skill_breakdown": skill_rows,
        "recent_sessions": recent_sessions,
        "common_misconceptions": common_misconceptions
    }

def get_student_misconceptions(student_id: int = 1) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, skill, misconception_name, misconception_category, frequency, last_detected_at 
    FROM detected_misconceptions 
    WHERE student_id = ?
    ORDER BY frequency DESC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Auto-initialize database on import
init_db()
