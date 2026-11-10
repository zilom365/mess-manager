import streamlit as st
import pandas as pd
from datetime import date
from extractor import extract

st.set_page_config(page_title="Mess Manager", page_icon="🗓️")
st.title("🗓️ Mess Manager")
st.caption("Add a note by text, screenshot or voice. The app extracts tasks and dates, and you confirm them.")

today = st.date_input("Today's date", value=date(2026, 10, 18))


def text_from_image(image_file):
    """WEEK 2: replace with OCR or a vision model. Return the text found in the image."""
    return ""


def text_from_audio(audio_file):
    """WEEK 2: replace with speech-to-text (for example Whisper). Return the spoken text."""
    return ""


tab_text, tab_img, tab_voice = st.tabs(["✍️ Text", "📷 Screenshot / photo", "🎤 Voice note"])

with tab_text:
    typed = st.text_area(
        "Your note",
        value="Amr kalle meeting ache, 20 October quiz, ar electricity bill porer shoptaho due",
        height=100,
    )

with tab_img:
    img = st.file_uploader("Choose a screenshot or photo", type=["png", "jpg", "jpeg"])
    if img is not None:
        st.image(img, caption="Uploaded")

with tab_voice:
    recorded = st.audio_input("Record a voice note")
    uploaded_audio = st.file_uploader("...or upload an audio file", type=["wav", "mp3", "m4a"])

if st.button("Extract"):
    parts = [typed]
    notes = []

    if img is not None:
        t = text_from_image(img)
        if t:
            parts.append(t)
        else:
            notes.append("Screenshot received. Reading text from images is not built yet (Week 2).")

    audio = recorded if recorded is not None else uploaded_audio
    if audio is not None:
        t = text_from_audio(audio)
        if t:
            parts.append(t)
        else:
            notes.append("Voice note received. Speech-to-text is not built yet (Week 2).")

    for n in notes:
        st.info(n)

    text = ", ".join(p for p in parts if p.strip())
    df = extract(text, today)
    if df.empty:
        st.warning("No tasks found. Try adding a task word like meeting, quiz, exam or bill.")
        st.session_state.pop("tasks", None)
    else:
        df["due"] = pd.to_datetime(df["due"])
        df["confirmed"] = False
        st.session_state["tasks"] = df

if "tasks" in st.session_state:
    st.subheader("Review and confirm")
    st.write("Rows marked 'needs_confirmation' have an unclear date. Fix the date if needed, then tick Confirmed.")
    edited = st.data_editor(
        st.session_state["tasks"],
        column_config={
            "due": st.column_config.DateColumn("due"),
            "confirmed": st.column_config.CheckboxColumn("Confirmed"),
        },
        disabled=["task", "needs_confirmation", "source"],
        hide_index=True,
        key="editor",
    )

    st.subheader("Your timeline")
    done = edited[edited["confirmed"]].sort_values("due")
    if done.empty:
        st.info("Nothing confirmed yet.")
    else:
        for _, r in done.iterrows():
            day = r["due"].strftime("%d %b %Y") if pd.notna(r["due"]) else "no date"
            st.write(f"📌 **{day}**: {r['task'].title()}")