import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Custom CSS for background
page_bg_img = f'''
<style>
.stApp {{
    background-image: url("https://i.imgur.com/mTqfIzb.jpeg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

# Database connection
def get_conn():
    conn = sqlite3.connect("teens_app.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS chapters (id INTEGER PRIMARY KEY, subject TEXT, chapter TEXT, created_at TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, content TEXT, created_at TEXT)")
    return conn

# Study Materials UI
def ui_study_materials():
    st.subheader("📚 Study Materials")
    st.caption("Organize subjects and chapters for revision.")

    # Add new chapter
    with st.form("add_chapter", clear_on_submit=True):
        subject = st.text_input("Subject", placeholder="Mathematics")
        chapter = st.text_input("Chapter", placeholder="Trigonometry - Ratios")
        if st.form_submit_button("Add Chapter") and subject and chapter:
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO chapters (subject, chapter, created_at) VALUES (?, ?, ?)",
                    (subject.strip(), chapter.strip(), datetime.utcnow().isoformat())
                )
                conn.commit()
            st.success("Chapter added 📖")

    st.divider()
    search_term = st.text_input("🔍 Search Chapters", placeholder="Type to search...")

    with get_conn() as conn:
        if search_term:
            rows = conn.execute(
                "SELECT id, subject, chapter, created_at FROM chapters WHERE subject LIKE ? OR chapter LIKE ? ORDER BY subject, id DESC",
                (f"%{search_term}%", f"%{search_term}%")
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, subject, chapter, created_at FROM chapters ORDER BY subject, id DESC"
            ).fetchall()

    if rows:
        subjects = {}
        for r in rows:
            sid, subj, chap, created = r
            subjects.setdefault(subj, []).append((sid, chap, created))
        
        for subj, chapters in subjects.items():
            with st.expander(subj, expanded=False):
                for sid, chap, created in chapters:
                    st.markdown(f"- {chap} _(added {created[:10]})_")
                    if st.button("Delete", key=f"del_chap_{sid}"):
                        with get_conn() as conn:
                            conn.execute("DELETE FROM chapters WHERE id=?", (sid,))
                            conn.commit()
                        st.toast("Deleted chapter")
                        st.rerun()
    else:
        st.info("No chapters yet. Add some above ✍️")

# Notepad UI
def ui_notepad():
    st.subheader("📝 Notepad")
    st.caption("Write and save personal notes.")

    # Add new note
    with st.form("add_note", clear_on_submit=True):
        title = st.text_input("Title", placeholder="e.g., Reminder on Physics")
        content = st.text_area("Content", placeholder="Type your note here...")
        if st.form_submit_button("Save Note") and title and content:
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
                    (title.strip(), content.strip(), datetime.utcnow().isoformat())
                )
                conn.commit()
            st.success("Note saved ✍️")

    st.divider()
    search_term = st.text_input("🔍 Search Notes", placeholder="Type to search...")

    with get_conn() as conn:
        if search_term:
            rows = conn.execute(
                "SELECT id, title, content, created_at FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC",
                (f"%{search_term}%", f"%{search_term}%")
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, title, content, created_at FROM notes ORDER BY id DESC"
            ).fetchall()

    if rows:
        for nid, title, content, created in rows:
            with st.container(border=True):
                st.markdown(f"### {title}")
                st.caption(f"Created {created[:10]}")
                st.write(content)
                c1, c2, c3 = st.columns(3)
                if c1.button("Delete", key=f"del_note_{nid}"):
                    with get_conn() as conn:
                        conn.execute("DELETE FROM notes WHERE id=?", (nid,))
                        conn.commit()
                    st.toast("Deleted note 🗑️")
                    st.rerun()
                if c2.button("Edit", key=f"edit_note_{nid}"):
                    with st.form(f"edit_form_{nid}", clear_on_submit=True):
                        new_title = st.text_input("Edit Title", value=title)
                        new_content = st.text_area("Edit Content", value=content)
                        if st.form_submit_button("Save Changes"):
                            with get_conn() as conn:
                                conn.execute(
                                    "UPDATE notes SET title=?, content=? WHERE id=?",
                                    (new_title.strip(), new_content.strip(), nid)
                                )
                                conn.commit()
                            st.success("Note updated ✅")
                            st.rerun()
    else:
        st.info("No notes yet. Add one above ✍️")

# Sidebar Navigation
PAGES = {
    "Study Materials": ui_study_materials,
    "Notepad": ui_notepad,
}

choice = st.sidebar.radio("📌 Navigate", list(PAGES.keys()))
PAGES[choice]()
