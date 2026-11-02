# 🎙️ Sunwai – AI Voice Tutor Using Sarvam AI Only

> **"Learn by Understanding, Not Memorising."**  
> An empathetic AI voice tutor for Indian school students (Classes 5–7) that listens to spoken mathematical reasoning, detects conceptual misconceptions, and teaches foundational principles through conversational voice explanations.

---

## 🌟 Key Features

1. **Exclusively Powered by Sarvam AI**:
   - **Speech-to-Text (STT)**: Sarvam **Saaras** (`saaras:v4`) transcribes spoken reasoning across English (`en-IN`), Hindi (`hi-IN`), and Marathi (`mr-IN`).
   - **Reasoning & Misconception Classification**: Sarvam **105B Conversations** (`sarvam-105b-conversations`) diagnoses root conceptual misconceptions against a curated taxonomy.
   - **Text-to-Speech (TTS)**: Sarvam **Bulbul** (`bulbul:v3`) generates encouraging, natural voice explanations using Indian real-life analogies (rupees, sharing sweets, rotis).

2. **6-Skill Curated Misconception Taxonomy**:
   - **Subtraction**: Subtracting smaller digit from larger digit, forgetting to decrement after borrowing, borrowing across zero.
   - **Addition**: Forgetting carried-over digits, left-to-right concatenation, place-value column misalignment.
   - **Multiplication**: Confusing with addition, forgetting zero placeholder, times table errors.
   - **Division**: Confusing remainder with decimal, dividing smaller digit by larger, intermediate zero skipping.
   - **Fractions**: Adding denominators directly, numerator/denominator confusion, equivalent fraction rules.
   - **Place Value**: Face value vs place value, reading digits independently, decimal length confusion.

3. **High-Fidelity Student Experience**:
   - **Landing Page**: Project overview, methodology, and direct demo launcher.
   - **Student Dashboard**: Individualized mastery tracking for Aarav Sharma (Class 5), accuracy metrics, common misconceptions.
   - **Voice Learning Interface**: Question cards, animated microphone button, live audio visualizer waveform, pipeline stage tracking, diagnosis badge, conversational reteaching story, Bulbul voice player, and follow-up question.
   - **Progress Dashboard & Analytics**: Skill-wise mastery percentages and historical misconception log.
   - **Taxonomy Viewer**: Interactive catalog of all diagnosed mathematical errors.

4. **Interactive Demo Mode**:
   - Fully testable immediately out of the box!
   - Pre-loaded with the flagship demo question: `35 - 18 = ?` and student reasoning: `"23 because 5 minus 8 is difficult, so I did 8 minus 5."`
   - Switching to live Sarvam AI is as simple as adding `SARVAM_API_KEY` into `.env`.

---

## 📂 Project Structure

```
sunwai/
├── .env                  # Your secret API key (git-ignored)
├── .env.example          # Template for environment variables
├── .gitignore            # Ignores .env, pycache, SQLite database
├── test_sarvam.py        # Minimal script testing Sarvam 105B Chat Completion
├── README.md             # Complete documentation
├── backend/
│   ├── main.py           # FastAPI server & route handlers
│   ├── sarvam_service.py # Sarvam AI API client (Saaras, 105B, Bulbul)
│   ├── database.py       # SQLite database (Students, Sessions, Progress)
│   ├── taxonomy.py       # Curated 6-skill mathematical misconception rules
│   └── models.py         # Pydantic data schemas
└── frontend/
    ├── index.html        # Modern responsive 4-view dashboard
    ├── styles.css        # Purple-blue educational UI theme
    └── app.js            # MediaRecorder mic capture, API calls, audio playback
```

---

## 🚀 Quickstart Guide

### 1. Requirements
- Python 3.10+
- Installed packages: `pip install sarvamai fastapi uvicorn python-dotenv python-multipart httpx`

### 2. Configure Your Sarvam API Key
Open `.env` and paste your Sarvam AI API subscription key:
```env
SARVAM_API_KEY=your_actual_sarvam_key_here
```

### 3. Verify Single Sarvam API Call (Test Script)
Run the dedicated Sarvam API test script:
```powershell
python test_sarvam.py
```
This initializes the `SarvamAI` client and makes a completion call to `sarvam-105b-conversations`.

### 4. Run the Sunwai Web Application
Start the FastAPI backend with static frontend hosting:
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser at:
👉 **`http://localhost:8000`**

---

## 🧪 Testing the Flagship Demo Case

1. Navigate to the **Voice Learning** tab (or click **"Try Flagship Demo"** on the home page).
2. The active question will be: **`35 - 18 = ?`**
3. Click **"Load Demo Case"** (or click the microphone and speak: *"23 because 5 minus 8 is difficult, so I did 8 minus 5"*).
4. Watch the 5-step pipeline:
   - **Step 1**: Audio Captured
   - **Step 2**: Transcribed with Sarvam Saaras
   - **Step 3**: Reasoning evaluated by Sarvam 105B
   - **Step 4**: Misconception flagged: *"Subtracting the smaller digit from the larger digit"*
   - **Step 5**: Conversational rupee-sharing explanation synthesized by Sarvam Bulbul voice!
5. Listen to the voice explanation and click **"Try Follow-Up Question"** to solve `42 - 15 = ?`!
6. Visit **Student Dashboard** to see the session recorded in SQLite and the updated mastery score.

---

## 🔒 Security & Privacy
- API keys are **strictly server-side** in `.env` and never exposed to client browsers.
- No other LLM providers (OpenAI, Gemini, Groq, Claude) are used.
- All student sessions and diagnosed misconceptions are saved privately in local SQLite (`sunwai.db`).
