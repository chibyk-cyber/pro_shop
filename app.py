import streamlit as st
import sqlite3
from datetime import datetime, date, time, timedelta
import pandas as pd
import random
import json
from typing import List, Dict, Any

DB_PATH = "teens_app.db"
APP_NAME = "Teens App"

############################
# Database Utilities
############################

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        # Store Social Links
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS social_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                username TEXT,
                url TEXT NOT NULL,
                added_at TEXT NOT NULL
            )
            """
        )
        # Tasks / Schedule
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                subject TEXT,
                due_date TEXT NOT NULL,
                due_time TEXT,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
            """
        )
        # Exam Questions bank
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL CHECK (correct_option IN ('A','B','C','D')),
                created_at TEXT NOT NULL
            )
            """
        )
        # Quiz attempts
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                total INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                taken_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


############################
# Seed Sample Data (idempotent)
############################

SAMPLE_QUESTIONS = [
    # Biology (SS1/SS2 level)
    {
        "subject": "Biology",
        "question": "Which organelle is known as the powerhouse of the cell?",
        "options": ["Ribosome", "Mitochondrion", "Nucleus", "Chloroplast"],
        "answer": "B",
    },
    {
        "subject": "Biology",
        "question": "What is the basic unit of heredity?",
        "options": ["Gene", "Chromosome", "DNA", "Protein"],
        "answer": "A",
    },
    # Chemistry
    {
        "subject": "Chemistry",
        "question": "What is the chemical symbol for Sodium?",
        "options": ["S", "Na", "So", "Sn"],
        "answer": "B",
    },
    {
        "subject": "Chemistry",
        "question": "pH 7 at 25°C is considered?",
        "options": ["Acidic", "Basic", "Neutral", "Alkaline"],
        "answer": "C",
    },
    # Physics
    {
        "subject": "Physics",
        "question": "The SI unit of force is _____",
        "options": ["Joule", "Newton", "Pascal", "Watt"],
        "answer": "B",
    },
    {
        "subject": "Physics",
        "question": "Speed is defined as _____",
        "options": [
            "Rate of change of displacement",
            "Rate of change of distance",
            "Distance travelled",
            "Displacement per unit time",
        ],
        "answer": "B",
    },
    # Mathematics
    {
        "subject": "Mathematics",
        "question": "What is the value of 7 × 8?",
        "options": ["54", "56", "58", "60"],
        "answer": "B",
    },
    {
        "subject": "Mathematics",
        "question": "The value of π (pi) correct to 2 d.p. is",
        "options": ["3.12", "3.14", "3.16", "3.18"],
        "answer": "B",
    },
]


def seed_questions_if_empty():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM questions")
        (count,) = c.fetchone()
        if count == 0:
            for q in SAMPLE_QUESTIONS:
                c.execute(
                    """
                    INSERT INTO questions (subject, question, option_a, option_b, option_c, option_d, correct_option, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        q["subject"],
                        q["question"],
                        q["options"][0],
                        q["options"][1],
                        q["options"][2],
                        q["options"][3],
                        q["answer"],
                        datetime.utcnow().isoformat(),
                    ),
                )
            conn.commit()


############################
# Helpers
############################

def to_df(rows: List[tuple], columns: List[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)


def tag(text: str, color: str = "blue"):
    st.markdown(
        f"<span style='background:{color};color:white;padding:2px 8px;border-radius:999px;font-size:12px'>{text}</span>",
        unsafe_allow_html=True,
    )


def human_dt(d: str, t: str | None) -> str:
    try:
        if t:
            dt = datetime.fromisoformat(f"{d} {t}")
            return dt.strftime("%a %d %b, %I:%M %p")
        else:
            return datetime.fromisoformat(d).strftime("%a %d %b")
    except Exception:
        return f"{d} {t or ''}"


############################
# UI Sections
############################

def ui_social_hub():
    st.subheader("Social Hub")
    st.caption("Store your favorite social media platforms and quick links.")

    with st.form("add_social"):
        col1, col2 = st.columns(2)
        with col1:
            platform = st.text_input("Platform (e.g., Instagram, TikTok, X)")
            username = st.text_input("Username / Handle", placeholder="@yourname")
        with col2:
            url = st.text_input("Profile URL", placeholder="https://...")
        submitted = st.form_submit_button("Save Platform")
        if submitted and platform and url:
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO social_links (platform, username, url, added_at) VALUES (?, ?, ?, ?)",
                    (platform.strip(), username.strip(), url.strip(), datetime.utcnow().isoformat()),
                )
                conn.commit()
            st.success("Saved!")

    st.divider()

    st.markdown("### Your Platforms")
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, platform, username, url, added_at FROM social_links ORDER BY id DESC"
        ).fetchall()
    if rows:
        for r in rows:
            sid, plat, user, link, added = r
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 4, 2])
                c1.markdown(f"**{plat}**" + (f" — {user}" if user else ""))
                c2.write(link)
                c3.markdown(f"Added: {datetime.fromisoformat(added).strftime('%d %b %Y')}")
                col_a, col_b, col_c = st.columns(3)
                if col_a.link_button("Open", link):
                    pass
                if col_b.button("Copy URL", key=f"copy_{sid}"):
                    st.code(link, language="text")
                if col_c.button("Delete", key=f"del_{sid}"):
                    with get_conn() as conn:
                        conn.execute("DELETE FROM social_links WHERE id=?", (sid,))
                        conn.commit()
                    st.toast("Deleted", icon="🗑️")
                    st.rerun()
    else:
        st.info("No platforms yet. Add your first above ✨")


def ui_scheduler():
    st.subheader("Scheduler")
    st.caption("Create tasks, study sessions, and reminders.")

    with st.form("add_task", clear_on_submit=True):
        t1, t2 = st.columns([3, 2])
        with t1:
            title = st.text_input("Title", placeholder="e.g., Read Biology Ch. 3")
            description = st.text_area("Description", placeholder="Extra details...")
        with t2:
            subject = st.text_input("Subject / Category", placeholder="Biology")
            due_date = st.date_input("Due date", value=date.today())
            due_time = st.time_input("Time (optional)", value=time(17, 0))
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
        submitted = st.form_submit_button("Add Task")
        if submitted and title:
            with get_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO tasks (title, description, subject, due_date, due_time, priority, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)
                    """,
                    (
                        title.strip(),
                        description.strip(),
                        subject.strip(),
                        due_date.isoformat(),
                        due_time.isoformat() if due_time else None,
                        priority,
                        datetime.utcnow().isoformat(),
                    ),
                )
                conn.commit()
            st.success("Task added ✔")

    st.divider()

    # Filters
    fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
    with get_conn() as conn:
        subjects = [r[0] for r in conn.execute("SELECT DISTINCT subject FROM tasks WHERE subject IS NOT NULL AND subject<>''").fetchall()]
    chosen_subject = fc1.selectbox("Filter by subject", ["All"] + subjects)
    chosen_status = fc2.selectbox("Status", ["All", "Pending", "Done"])
    chosen_priority = fc3.selectbox("Priority", ["All", "Low", "Medium", "High"])
    show_overdue = fc4.toggle("Overdue only", value=False)

    # Query
    query = "SELECT id, title, subject, due_date, due_time, priority, status FROM tasks"
    where = []
    params: List[Any] = []
    if chosen_subject != "All":
        where.append("subject=?")
        params.append(chosen_subject)
    if chosen_status != "All":
        where.append("status=?")
        params.append(chosen_status)
    if chosen_priority != "All":
        where.append("priority=?")
        params.append(chosen_priority)
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY due_date ASC, due_time ASC"

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()

    # Cards
    if rows:
        for r in rows:
            tid, title, subject, d, t, pri, status = r
            if show_overdue:
                dt_due = datetime.fromisoformat(d + (f" {t}" if t else " 00:00:00"))
                if dt_due >= datetime.now():
                    continue
            with st.container(border=True):
                c1, c2 = st.columns([4, 3])
                c1.markdown(f"**{title}**")
                subbits = []
                if subject:
                    subbits.append(subject)
                subbits.append(human_dt(d, t))
                c1.caption(" • ".join(subbits))
                c2.write("Priority:")
                tag(pri, "#4f46e5")
                tag(status, "#059669" if status == "Done" else "#f59e0b")
                b1, b2, b3 = st.columns(3)
                if b1.button("Mark Done", key=f"done_{tid}"):
                    with get_conn() as conn:
                        conn.execute("UPDATE tasks SET status='Done' WHERE id=?", (tid,))
                        conn.commit()
                    st.toast("Marked done ✅")
                    st.rerun()
                if b2.button("Edit", key=f"edit_{tid}"):
                    edit_task_dialog(tid)
                if b3.button("Delete", key=f"del_t_{tid}"):
                    with get_conn() as conn:
                        conn.execute("DELETE FROM tasks WHERE id=?", (tid,))
                        conn.commit()
                    st.toast("Deleted 🗑️")
                    st.rerun()
    else:
        st.info("No tasks yet. Add one above ✍️")


def edit_task_dialog(task_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT title, description, subject, due_date, due_time, priority, status FROM tasks WHERE id=?",
            (task_id,),
        ).fetchone()
    if not row:
        st.error("Task not found")
        return

    title, desc, subj, d, t, pri, status = row
    st.markdown("### Edit Task")
    with st.form(f"edit_form_{task_id}"):
        e1, e2 = st.columns([3, 2])
        with e1:
            n_title = st.text_input("Title", value=title)
            n_desc = st.text_area("Description", value=desc or "")
        with e2:
            n_subj = st.text_input("Subject", value=subj or "")
            n_date = st.date_input("Due date", value=date.fromisoformat(d))
            n_time = st.time_input("Time", value=time.fromisoformat(t) if t else time(17, 0))
            n_pri = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low","Medium","High"].index(pri))
            n_status = st.selectbox("Status", ["Pending", "Done"], index=["Pending","Done"].index(status))
        if st.form_submit_button("Save Changes"):
            with get_conn() as conn:
                conn.execute(
                    """
                    UPDATE tasks SET title=?, description=?, subject=?, due_date=?, due_time=?, priority=?, status=?
                    WHERE id=?
                    """,
                    (
                        n_title.strip(),
                        (n_desc or "").strip(),
                        (n_subj or "").strip(),
                        n_date.isoformat(),
                        n_time.isoformat() if n_time else None,
                        n_pri,
                        n_status,
                        task_id,
                    ),
                )
                conn.commit()
            st.success("Updated ✔")
            st.rerun()


def ui_exam_prep():
    st.subheader("Exam Prep")
    st.caption("Take quizzes, add your own questions, and track progress.")

    tab1, tab2, tab3 = st.tabs(["Take Quiz", "Question Bank", "Performance"])

    with tab1:
        with get_conn() as conn:
            subjects = [r[0] for r in conn.execute("SELECT DISTINCT subject FROM questions ORDER BY subject").fetchall()]
        if not subjects:
            st.info("No questions yet. Add some in the Question Bank tab.")
        else:
            subject = st.selectbox("Subject", subjects)
            num = st.slider("Number of questions", 1, 20, 5)
            if st.button("Start Quiz"):
                run_quiz(subject, num)

    with tab2:
        st.markdown("### Add Question")
        with st.form("add_q", clear_on_submit=True):
            subject = st.text_input("Subject", placeholder="Mathematics")
            question = st.text_area("Question")
            col = st.columns(2)
            with col[0]:
                a = st.text_input("Option A")
                c = st.text_input("Option C")
            with col[1]:
                b = st.text_input("Option B")
                d = st.text_input("Option D")
            ans = st.selectbox("Correct Option", ["A", "B", "C", "D"])
            if st.form_submit_button("Save Question") and subject and question and a and b and c and d:
                with get_conn() as conn:
                    conn.execute(
                        """
                        INSERT INTO questions (subject, question, option_a, option_b, option_c, option_d, correct_option, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            subject.strip(),
                            question.strip(),
                            a.strip(),
                            b.strip(),
                            c.strip(),
                            d.strip(),
                            ans,
                            datetime.utcnow().isoformat(),
                        ),
                    )
                    conn.commit()
                st.success("Question saved ✍️")

        st.divider()
        st.markdown("### All Questions")
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, subject, question, option_a, option_b, option_c, option_d, correct_option, created_at FROM questions ORDER BY id DESC"
            ).fetchall()
        if rows:
            for r in rows:
                qid, subject, q, a, b, c, d, ans, created = r
                with st.container(border=True):
                    st.markdown(f"**{subject}** — {q}")
                    st.caption(f"A) {a}  |  B) {b}  |  C) {c}  |  D) {d}")
                    co1, co2 = st.columns(2)
                    co1.write(f"Answer: {ans}")
                    if co2.button("Delete", key=f"del_q_{qid}"):
                        with get_conn() as conn:
                            conn.execute("DELETE FROM questions WHERE id=?", (qid,))
                            conn.commit()
                        st.toast("Deleted question")
                        st.rerun()
        else:
            st.info("No questions yet.")

    with tab3:
        with get_conn() as conn:
            rows = conn.execute("SELECT subject, total, correct, taken_at FROM quiz_attempts ORDER BY id DESC").fetchall()
        if rows:
            df = to_df(rows, ["Subject", "Total", "Correct", "When"])
            df["Score %"] = (df["Correct"] / df["Total"]) * 100
            st.dataframe(df, use_container_width=True)
            # Simple Subject-wise summary
            st.markdown("#### Average Score by Subject")
            avg = df.groupby("Subject")["Score %"].mean().reset_index().sort_values("Score %", ascending=False)
            st.bar_chart(avg, x="Subject", y="Score %")
        else:
            st.info("No quiz attempts yet.")


def run_quiz(subject: str, num: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, question, option_a, option_b, option_c, option_d, correct_option FROM questions WHERE subject=? ORDER BY RANDOM() LIMIT ?",
            (subject, num),
        ).fetchall()
    if not rows:
        st.warning("No questions in this subject.")
        return

    st.session_state.setdefault("quiz_answers", {})
    st.session_state.setdefault("quiz_correct", {})

    st.markdown(f"### {subject} Quiz")
    for idx, r in enumerate(rows, start=1):
        qid, q, a, b, c, d, correct = r
        st.write(f"**Q{idx}.** {q}")
        choice = st.radio(
            f"Choose an option for Q{idx}", ["A", "B", "C", "D"],
            format_func=lambda x: {"A": a, "B": b, "C": c, "D": d}[x],
            key=f"quiz_choice_{qid}",
        )
        st.session_state["quiz_answers"][qid] = choice
        st.session_state["quiz_correct"][qid] = correct
        st.divider()

    if st.button("Submit Quiz"):
        answers = st.session_state["quiz_answers"]
        correct_map = st.session_state["quiz_correct"]
        total = len(answers)
        correct_count = sum(1 for qid, ans in answers.items() if ans == correct_map.get(qid))
        score = int((correct_count / total) * 100)
        st.success(f"You scored {correct_count}/{total} — {score}%")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO quiz_attempts (subject, total, correct, taken_at) VALUES (?, ?, ?, ?)",
                (subject, total, correct_count, datetime.utcnow().isoformat()),
            )
            conn.commit()


############################
# Settings / Backup
############################

def export_data() -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    with get_conn() as conn:
        data["social_links"] = [
            dict(zip(["id", "platform", "username", "url", "added_at"], r))
            for r in conn.execute("SELECT id, platform, username, url, added_at FROM social_links").fetchall()
        ]
        data["tasks"] = [
            dict(
                zip(
                    [
                        "id",
                        "title",
                        "description",
                        "subject",
                        "due_date",
                        "due_time",
                        "priority",
                        "status",
                        "created_at",
                    ],
                    r,
                )
            )
            for r in conn.execute(
                "SELECT id, title, description, subject, due_date, due_time, priority, status, created_at FROM tasks"
            ).fetchall()
        ]
        data["questions"] = [
            dict(
                zip(
                    [
                        "id",
                        "subject",
                        "question",
                        "option_a",
                        "option_b",
                        "option_c",
                        "option_d",
                        "correct_option",
                        "created_at",
                    ],
                    r,
                )
            )
            for r in conn.execute(
                "SELECT id, subject, question, option_a, option_b, option_c, option_d, correct_option, created_at FROM questions"
            ).fetchall()
        ]
        data["quiz_attempts"] = [
            dict(zip(["id", "subject", "total", "correct", "taken_at"], r))
            for r in conn.execute("SELECT id, subject, total, correct, taken_at FROM quiz_attempts").fetchall()
        ]
    return data


def ui_settings():
    st.subheader("Settings & Backup")
    st.caption("Export or import your data.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Data to JSON"):
            data = export_data()
            st.download_button(
                label="Download teens_app_backup.json",
                data=json.dumps(data, indent=2).encode("utf-8"),
                file_name="teens_app_backup.json",
                mime="application/json",
            )
    with col2:
        up = st.file_uploader("Import JSON backup", type=["json"])
        if up is not None:
            try:
                data = json.load(up)
                with get_conn() as conn:
                    # Wipe & restore
                    conn.execute("DELETE FROM social_links")
                    conn.execute("DELETE FROM tasks")
                    conn.execute("DELETE FROM questions")
                    conn.execute("DELETE FROM quiz_attempts")
                    # Social
                    for r in data.get("social_links", []):
                        conn.execute(
                            "INSERT INTO social_links (id, platform, username, url, added_at) VALUES (?, ?, ?, ?, ?)",
                            (r.get("id"), r.get("platform"), r.get("username"), r.get("url"), r.get("added_at")),
                        )
                    # Tasks
                    for r in data.get("tasks", []):
                        conn.execute(
                            """
                            INSERT INTO tasks (id, title, description, subject, due_date, due_time, priority, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                r.get("id"),
                                r.get("title"),
                                r.get("description"),
                                r.get("subject"),
                                r.get("due_date"),
                                r.get("due_time"),
                                r.get("priority"),
                                r.get("status"),
                                r.get("created_at"),
                            ),
                        )
                    # Questions
                    for r in data.get("questions", []):
                        conn.execute(
                            """
                            INSERT INTO questions (id, subject, question, option_a, option_b, option_c, option_d, correct_option, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                r.get("id"),
                                r.get("subject"),
                                r.get("question"),
                                r.get("option_a"),
                                r.get("option_b"),
                                r.get("option_c"),
                                r.get("option_d"),
                                r.get("correct_option"),
                                r.get("created_at"),
                            ),
                        )
                    # Attempts
                    for r in data.get("quiz_attempts", []):
                        conn.execute(
                            "INSERT INTO quiz_attempts (id, subject, total, correct, taken_at) VALUES (?, ?, ?, ?, ?)",
                            (r.get("id"), r.get("subject"), r.get("total"), r.get("correct"), r.get("taken_at")),
                        )
                    conn.commit()
                st.success("Import complete ✅")
            except Exception as e:
                st.error(f"Import failed: {e}")


############################
# App Layout
############################

def main():
    st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")
    st.title(APP_NAME)
    st.caption("Social links • Scheduler • Exam prep — all in one.")

    init_db()
    seed_questions_if_empty()

    # Sidebar Navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Social Hub", "Scheduler", "Exam Prep", "Settings"],
            index=0,
        )
        st.markdown("---")
        st.markdown("**Tips**")
        st.caption("Use Settings to backup or move your data.")

    if page == "Social Hub":
        ui_social_hub()
    elif page == "Scheduler":
        ui_scheduler()
    elif page == "Exam Prep":
        ui_exam_prep()
    else:
        ui_settings()


if __name__ == "__main__":
    main()
