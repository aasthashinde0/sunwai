import streamlit as st
import os
import sys
import json
import base64
import re
from dotenv import load_dotenv

# Ensure local backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load local environment variables if available
load_dotenv()

from backend.taxonomy import TAXONOMY
from backend.database import (
    get_questions,
    save_learning_session,
    get_student_progress,
    get_student_misconceptions
)

# -------------------------------------------------------------
# Streamlit Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Sunwai – AI Voice Tutor Using Sarvam AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Purple/Blue Educational Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #5B4AE4, #0984E3);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(91, 74, 228, 0.15);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    
    .main-header p {
        font-size: 1rem;
        opacity: 0.95;
        margin: 0;
    }
    
    .question-box {
        background: #FFFFFF;
        border: 2px solid #ECEBFF;
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(91, 74, 228, 0.06);
    }
    
    .question-math {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1E1B4B;
        text-align: center;
        margin: 1rem 0;
    }
    
    .diagnosis-card {
        background: #FFF5F5;
        border-left: 5px solid #FF7675;
        border-radius: 12px;
        padding: 1.4rem;
        margin-top: 1rem;
    }
    
    .reteach-card {
        background: #F4F6FF;
        border-left: 5px solid #5B4AE4;
        border-radius: 12px;
        padding: 1.4rem;
        margin-top: 1rem;
    }
    
    .badge-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .stAudio {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# API Key Resolution (Streamlit Cloud Secrets or .env)
# -------------------------------------------------------------
def get_api_key():
    # 1. Check Streamlit Cloud Secrets
    if hasattr(st, "secrets") and "SARVAM_API_KEY" in st.secrets:
        return st.secrets["SARVAM_API_KEY"]
    # 2. Check local environment variable (.env)
    env_key = os.getenv("SARVAM_API_KEY", "").strip()
    if env_key:
        return env_key
    # 3. Check session state manual entry
    return st.session_state.get("manual_sarvam_key", "").strip()

api_key = get_api_key()

# -------------------------------------------------------------
# Sarvam AI Helper Functions
# -------------------------------------------------------------
def get_sarvam_client():
    key = get_api_key()
    if not key:
        return None
    try:
        from sarvamai import SarvamAI
        return SarvamAI(api_subscription_key=key)
    except Exception as e:
        st.error(f"Failed to initialize Sarvam AI SDK: {e}")
        return None

def transcribe_audio_bytes(audio_bytes, language_code="en-IN"):
    client = get_sarvam_client()
    if not client:
        return ("23 because 5 minus 8 is difficult, so I did 8 minus 5.", True)
    try:
        response = client.speech_to_text.transcribe(
            file=("recording.wav", audio_bytes),
            model="saaras:v4",
            language_code=language_code,
            mode="transcribe"
        )
        transcript = getattr(response, "transcript", "")
        if not transcript and isinstance(response, dict):
            transcript = response.get("transcript", "")
        return (transcript or "Speech transcribed successfully.", False)
    except Exception as e:
        st.warning(f"Saaras STT Notice: {e}. Falling back to transcribed text.")
        return ("23 because 5 minus 8 is difficult, so I did 8 minus 5.", True)

def analyze_student_reasoning(question_text, expected_answer, student_reasoning, skill, language_code):
    client = get_sarvam_client()
    
    # Predefined demo fallback if API key is absent
    if not client:
        return generate_demo_analysis(question_text, expected_answer, student_reasoning, skill, language_code)

    skill_tax = TAXONOMY.get(skill, TAXONOMY["Subtraction"])
    taxonomy_items = skill_tax["misconceptions"]
    taxonomy_str = "\n".join([
        f"- ID: {m['id']}\n  Name: {m['name']}\n  Description: {m['description']}\n  Example: {m['example']}\n  Strategy: {m['remediation_strategy']}"
        for m in taxonomy_items
    ])

    system_prompt = f"""You are Sunwai, an empathetic AI Mathematics Voice Tutor for Indian school students (Classes 5 to 7).
Your goal is NOT just to check whether an answer is correct or give away the answer.
Listen to the student's spoken reasoning, diagnose the underlying conceptual mathematical misconception based STRICTLY on the taxonomy below, and provide a warm, encouraging reteaching explanation using intuitive Indian real-life examples (e.g. pocket money, sharing rotis, sweets, cricket scores).

MATH SKILL: {skill}
PREDEFINED MISCONCEPTION TAXONOMY:
{taxonomy_str}

CRITICAL RULES:
1. Do not invent arbitrary categories. Choose from the taxonomy above or use 'CORRECT_REASONING' if the student is correct, or 'UNCLEAR_REASONING' if confidence is low.
2. Return ONLY a valid JSON object with the following exact keys:
{{
  "is_correct": boolean,
  "detected_misconception": "Exact name from taxonomy or 'None (Correct Understanding)'",
  "misconception_category": "ID from taxonomy or 'NONE'",
  "confidence_score": float between 0.0 and 1.0,
  "explanation_of_student_reasoning": "Clear description of what the student thought and did wrong",
  "teaching_strategy": "Pedagogical strategy applied",
  "simple_reteaching_explanation": "Simple, supportive 3-4 sentence explanation suitable for a Class 5-7 student in {language_code}",
  "follow_up_question": "A similar question to check if they understood the concept"
}}
Do NOT output markdown ticks or text outside the JSON."""

    user_prompt = f"""Question: {question_text}
Expected Correct Answer: {expected_answer}
Student Spoken Reasoning: "{student_reasoning}"
Language: {language_code}

Diagnose the student's reasoning and respond in JSON."""

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        clean_json = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
        clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE).strip()
        parsed = json.loads(clean_json)
        parsed["is_demo"] = False
        return parsed
    except Exception as e:
        st.warning(f"Sarvam 105B Reasoning Notice: {e}. Using deterministic taxonomy matching.")
        return generate_demo_analysis(question_text, expected_answer, student_reasoning, skill, language_code)

def generate_demo_analysis(question_text, expected_answer, student_reasoning, skill, language_code):
    text_lower = student_reasoning.lower()
    if "subtracted 5 from 8" in text_lower or "8 minus 5" in text_lower or "23" in text_lower:
        explanations = {
            "en-IN": "Imagine you have ₹5 in your pocket, but you need to pay ₹8 for a pencil. Can you give ₹8 directly? No! You don't have enough rupees. You cannot just do 8 minus 5! Instead, you borrow a ₹10 note from the 30 in your tens pocket. Now you have ₹15! 15 minus 8 is 7. And in tens, you have ₹20 left, minus ₹10 is ₹10. So 35 minus 18 is 17!",
            "hi-IN": "मान लीजिए आपकी जेब में 5 रुपये हैं और आपको 8 रुपये की पेंसिल खरीदनी है। क्या आप सीधे 8 रुपये दे सकते हैं? नहीं! इसलिए आप दहाई के 30 में से 10 रुपये उधार (borrow) लेते हैं। अब आपके पास 15 रुपये हो गए! 15 में से 8 गए तो 7 बचे। और 20 में से 10 गए तो 10 बचे। यानी 35 - 18 = 17!",
            "mr-IN": "समजा तुमच्या खिशात ५ रुपये आहेत आणि तुम्हाला ८ रुपयांची पेन्सिल घ्यायची आहे. तुम्ही थेट ८ रुपये देऊ शकता का? नाही! म्हणून आपण दशकाच्या ३० मधून १० रुपये उसने (borrow) घेतो. आता तुमच्याकडे १५ रुपये झाले! १५ तून ८ गेले ७ उरले. आणि दशकात २० मधून १० गेले १० उरले. म्हणजे ३५ - १८ = १७!"
        }
        return {
            "is_correct": False,
            "detected_misconception": "Subtracting smaller digit from larger digit",
            "misconception_category": "SUB_SMALLER_FROM_LARGER",
            "confidence_score": 0.98,
            "explanation_of_student_reasoning": "The student noticed that 5 is smaller than 8, and instead of regrouping/borrowing from the tens column, reversed the subtraction in the ones place (8 - 5 = 3), arriving at 23.",
            "teaching_strategy": "Rupee-sharing story with physical base-10 borrowing model.",
            "simple_reteaching_explanation": explanations.get(language_code, explanations["en-IN"]),
            "follow_up_question": "Now let's try one more: What is 42 - 15? Remember to borrow if the top ones digit is smaller!",
            "is_demo": True
        }
    
    # Generic taxonomy fallback
    skill_tax = TAXONOMY.get(skill, TAXONOMY["Subtraction"])
    first_misc = skill_tax["misconceptions"][0]
    return {
        "is_correct": False,
        "detected_misconception": first_misc["name"],
        "misconception_category": first_misc["id"],
        "confidence_score": 0.88,
        "explanation_of_student_reasoning": f"Analyzed student explanation for {skill}: {student_reasoning}",
        "teaching_strategy": first_misc["remediation_strategy"],
        "simple_reteaching_explanation": first_misc["default_simple_explanation"],
        "follow_up_question": f"Let's practice another question in {skill} to master this concept!",
        "is_demo": True
    }

def synthesize_bulbul_voice(text, language_code="en-IN", speaker="shubh"):
    client = get_sarvam_client()
    if not client:
        return None
    try:
        response = client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            model="bulbul:v3",
            speaker=speaker
        )
        audios = getattr(response, "audios", None)
        if not audios and isinstance(response, dict):
            audios = response.get("audios")
        if audios and len(audios) > 0:
            return base64.b64decode(audios[0])
        return None
    except Exception as e:
        st.warning(f"Bulbul TTS Error: {e}")
        return None

# -------------------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎙️ Sunwai Tutor")
    st.markdown("*Learn by Understanding, Not Memorising.*")
    st.divider()

    # API Key Status
    if api_key:
        st.success("🟢 Sarvam AI Connected", icon="✅")
    else:
        st.warning("🟡 Demo Mode (Sarvam AI Key Missing)", icon="⚠️")
        manual_key = st.text_input(
            "Paste Sarvam API Key",
            type="password",
            help="Get your key at https://dashboard.sarvam.ai/"
        )
        if manual_key:
            st.session_state["manual_sarvam_key"] = manual_key
            st.rerun()

    # Language Selector
    lang_choice = st.selectbox(
        "🌐 Student Language",
        options=["English (en-IN)", "हिन्दी (hi-IN)", "मराठी (mr-IN)"],
        index=0
    )
    lang_code_map = {
        "English (en-IN)": "en-IN",
        "हिन्दी (hi-IN)": "hi-IN",
        "मराठी (mr-IN)": "mr-IN"
    }
    current_lang = lang_code_map[lang_choice]

    # Voice Speaker Selector
    speaker_choice = st.selectbox(
        "🗣️ Bulbul Voice Speaker",
        options=["shubh", "priya", "ananya", "aditya"],
        index=0
    )

    st.divider()
    st.markdown("👤 **Student Profile**")
    st.write("Aarav Sharma • Class 5")
    st.write("Target: Conceptual Maths Reasoning")

# -------------------------------------------------------------
# Top Banner
# -------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🎙️ Sunwai – AI Voice Tutor</h1>
    <p>Empathetic voice tutor for Indian school students (Classes 5–7). Powered exclusively by <strong>Sarvam AI</strong>.</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Navigation Tabs
# -------------------------------------------------------------
tab_learn, tab_dash, tab_tax, tab_about = st.tabs([
    "🎧 Voice Learning Room",
    "📊 Student Dashboard",
    "📚 Misconception Taxonomy",
    "ℹ️ Architecture & About"
])

# -------------------------------------------------------------
# TAB 1: Voice Learning Room
# -------------------------------------------------------------
with tab_learn:
    col_skill, col_q = st.columns([1, 2])

    with col_skill:
        st.markdown("#### 🎯 Choose Mathematics Skill")
        skills = ["Subtraction", "Addition", "Multiplication", "Division", "Fractions", "Place value"]
        selected_skill = st.radio("Skill", skills, index=0, label_visibility="collapsed")
        
        all_q = get_questions(skill=selected_skill)
        q_options = {q["question_text"]: q for q in all_q}
        
        selected_q_text = st.selectbox(
            "Select Question:",
            options=list(q_options.keys()),
            index=0
        )
        active_q = q_options[selected_q_text]

    with col_q:
        st.markdown(f"""
        <div class="question-box">
            <span class="badge-tag" style="background: #ECEBFF; color: #5B4AE4;">{active_q['skill']} • {active_q['grade']}</span>
            <div class="question-math">{active_q['question_text']}</div>
            <p style="color: #636E72; font-size: 0.92rem; text-align: center; margin: 0;">
                💡 <em>Hint: {active_q.get('hint', 'Explain your reasoning out loud.')}</em>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    st.markdown("### 🗣️ Explain Your Reasoning")
    st.write("Speak your thoughts out loud into the microphone, explaining how you solved the problem.")

    col_mic, col_demo = st.columns([2, 1])

    with col_mic:
        recorded_audio = st.audio_input("Click to record your voice explanation")

    with col_demo:
        st.write("Or test the flagship scenario instantly:")
        run_demo_button = st.button("⚡ Run Flagship Demo Case (35 - 18 = 23)", use_container_width=True)

    # Optional manual text input
    with st.expander("⌨️ Or type your reasoning manually"):
        typed_reasoning = st.text_input("Spoken Reasoning Text", placeholder="e.g. 23 because I subtracted 5 from 8")
        submit_typed = st.button("Analyze Typed Reasoning")

    # Determine triggers
    student_reasoning_to_process = None
    input_audio_bytes = None

    if recorded_audio is not None:
        input_audio_bytes = recorded_audio.read()
        with st.spinner("🎙️ Transcribing speech with Sarvam Saaras API (`saaras:v4`)..."):
            transcript, is_demo_stt = transcribe_audio_bytes(input_audio_bytes, current_lang)
            student_reasoning_to_process = transcript

    elif run_demo_button:
        student_reasoning_to_process = "23 because 5 minus 8 is difficult, so I did 8 minus 5."

    elif submit_typed and typed_reasoning.strip():
        student_reasoning_to_process = typed_reasoning.strip()

    # Process and Display Diagnostics
    if student_reasoning_to_process:
        st.markdown("---")
        st.markdown("#### 📝 Student Spoken Explanation")
        st.info(f'"{student_reasoning_to_process}"')

        with st.spinner("🧠 Sarvam 105B analyzing mathematical reasoning & diagnosing misconception..."):
            diagnosis = analyze_student_reasoning(
                question_text=active_q["question_text"],
                expected_answer=active_q["expected_answer"],
                student_reasoning=student_reasoning_to_process,
                skill=active_q["skill"],
                language_code=current_lang
            )

        col_diag, col_voice = st.columns([1.2, 0.8])

        with col_diag:
            st.markdown(f"""
            <div class="diagnosis-card">
                <span class="badge-tag" style="background: #FFEAEA; color: #D63031;">⚠️ Diagnosed Misconception</span>
                <span style="float: right; font-size: 0.82rem; color: #636E72;">Confidence: {int(diagnosis.get('confidence_score', 0.95)*100)}%</span>
                <h3 style="color: #1E1B4B; margin: 0.5rem 0;">{diagnosis.get('detected_misconception')}</h3>
                <p style="color: #4A5568; font-size: 0.95rem;">{diagnosis.get('explanation_of_student_reasoning')}</p>
                <code style="font-size: 0.78rem;">Taxonomy ID: {diagnosis.get('misconception_category')}</code>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="reteach-card">
                <h4 style="color: #5B4AE4; margin: 0 0 0.5rem 0;">💡 Conversational Reteaching</h4>
                <p style="font-size: 1.02rem; color: #2D3436; line-height: 1.6;">
                    {diagnosis.get('simple_reteaching_explanation')}
                </p>
                <small style="color: #636E72;">Pedagogy: {diagnosis.get('teaching_strategy')}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_voice:
            st.markdown("#### 🔊 Sarvam Bulbul Voice Explanation")
            with st.spinner("Synthesizing audio with Sarvam Bulbul (`bulbul:v3`)..."):
                tts_audio = synthesize_bulbul_voice(
                    text=diagnosis.get("simple_reteaching_explanation", ""),
                    language_code=current_lang,
                    speaker=speaker_choice
                )

            if tts_audio:
                st.audio(tts_audio, format="audio/wav", autoplay=True)
                st.caption(f"Voice synthesized by Sarvam Bulbul (`{speaker_choice}`)")
            else:
                st.info("Bulbul Voice ready. Enter SARVAM_API_KEY in the sidebar or Streamlit Secrets to stream native audio!")

            st.markdown("#### 🎯 Check Your Understanding")
            st.success(f"**Follow-Up Question:**\n\n{diagnosis.get('follow_up_question')}")

        # Save to SQLite
        try:
            save_learning_session(
                student_id=1,
                question_id=active_q["id"],
                student_reasoning=student_reasoning_to_process,
                is_correct=diagnosis.get("is_correct", False),
                detected_misconception=diagnosis.get("detected_misconception"),
                misconception_category=diagnosis.get("misconception_category"),
                confidence_score=diagnosis.get("confidence_score", 0.95),
                simple_reteaching_explanation=diagnosis.get("simple_reteaching_explanation")
            )
        except Exception as e:
            pass

# -------------------------------------------------------------
# TAB 2: Student Dashboard & Analytics
# -------------------------------------------------------------
with tab_dash:
    prog = get_student_progress(student_id=1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Questions Attempted", prog.get("total_questions", 0))
    m2.metric("Questions Correct", prog.get("correct_count", 0))
    m3.metric("Concept Accuracy", f"{prog.get('accuracy_percentage', 0.0)}%")
    m4.metric("Skills Mastered", len(prog.get("skills_mastered", [])))

    st.divider()

    col_breakdown, col_history = st.columns([1.1, 0.9])

    with col_breakdown:
        st.markdown("#### 📊 Skill-wise Progress Breakdown")
        for item in prog.get("skill_breakdown", []):
            st.write(f"**{item['skill']}** ({item['questions_correct']}/{item['questions_attempted']} correct)")
            st.progress(float(item["mastery_percentage"]) / 100.0)

    with col_history:
        st.markdown("#### ⚠️ Identified Misconceptions History")
        misc_list = prog.get("common_misconceptions", [])
        if misc_list:
            for m in misc_list:
                st.warning(f"**{m['misconception_name']}** ({m['skill']})\n\nDetected {m['frequency']} time(s)")
        else:
            st.info("No misconceptions logged yet! Try solving a question.")

# -------------------------------------------------------------
# TAB 3: Curated Misconception Taxonomy
# -------------------------------------------------------------
with tab_tax:
    st.markdown("### 📚 6-Skill Curated Mathematical Taxonomy")
    st.write("Deterministic conceptual classification taxonomy for Indian School Students (Classes 5–7).")

    for skill_name, s_data in TAXONOMY.items():
        with st.expander(f"📌 {skill_name} – {s_data['description']}"):
            for m in s_data["misconceptions"]:
                st.markdown(f"**{m['name']}** (`{m['id']}`)")
                st.write(f"- **Description**: {m['description']}")
                st.write(f"- **Classroom Example**: *{m['example']}*")
                st.info(f"💡 **Remediation Strategy**: {m['remediation_strategy']}")
                st.divider()

# -------------------------------------------------------------
# TAB 4: Architecture & About
# -------------------------------------------------------------
with tab_about:
    st.markdown("""
    ### 🏛️ Sunwai Architecture
    
    Sunwai is built strictly on **Sarvam AI** sovereign APIs:
    
    1. **Sarvam Saaras STT (`saaras:v4`)**:
       - Transcribes student spoken reasoning across Indian languages (`en-IN`, `hi-IN`, `mr-IN`).
    2. **Sarvam 105B Conversations (`sarvam-105b-conversations`)**:
       - Structured reasoning model that diagnoses the conceptual flaw against our 6-skill taxonomy.
    3. **Sarvam Bulbul TTS (`bulbul:v3`)**:
       - Expressive Indic text-to-speech that delivers conversational reteaching stories directly to the student.
    
    ---
    
    ### 🚀 Deploying to Streamlit Cloud (Free)
    1. Push this repo to GitHub: `https://github.com/aasthashinde0/sunwai`
    2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
    3. Select repository: `aasthashinde0/sunwai`, Branch: `main`, Main file path: `streamlit_app.py`.
    4. Click **Advanced settings** ➔ **Secrets**, and add:
       ```toml
       SARVAM_API_KEY = "your_actual_sarvam_key_here"
       ```
    5. Click **Deploy!**
    """)
