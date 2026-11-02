// Sunwai – AI Voice Tutor Application Client

let currentLanguage = "en-IN";
let currentSkill = "Subtraction";
let allQuestions = [];
let currentQuestionIndex = 0;
let currentQuestion = null;
let currentAnalysisResult = null;
let currentAudioElement = null;

// Audio Recording state
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let audioContext = null;
let analyser = null;
let animFrameId = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", async () => {
  await checkSystemStatus();
  await loadQuestions();
  await loadStudentData();
  await loadTaxonomy();
});

// -------------------------------------------------------------
// System Status & Setup
// -------------------------------------------------------------
async function checkSystemStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    const badge = document.getElementById("apiStatusBadge");
    const text = document.getElementById("apiStatusText");
    const banner = document.getElementById("demoBanner");

    if (data.is_configured) {
      badge.classList.add("live");
      text.innerText = "🟢 Sarvam AI Connected";
      banner.style.display = "none";
    } else {
      badge.classList.remove("live");
      text.innerText = "🟡 Demo Mode (Sarvam AI Ready)";
      banner.style.display = "flex";
    }
  } catch (err) {
    console.warn("Could not check status:", err);
  }
}

function dismissBanner() {
  document.getElementById("demoBanner").style.display = "none";
}

function changeLanguage(lang) {
  currentLanguage = lang;
  console.log("Language changed to:", lang);
}

// -------------------------------------------------------------
// View Switching Navigation
// -------------------------------------------------------------
function switchView(viewName) {
  // Update nav buttons
  const navIds = ["landing", "dashboard", "tutor", "progress", "taxonomy"];
  navIds.forEach(id => {
    const btn = document.getElementById(`nav-${id}`);
    if (btn) btn.classList.toggle("active", id === viewName);
  });

  // Update view visibility
  document.querySelectorAll(".page-view").forEach(el => el.classList.remove("active"));
  const activeView = document.getElementById(`view-${viewName}`);
  if (activeView) activeView.classList.add("active");

  if (viewName === "dashboard" || viewName === "progress") {
    loadStudentData();
  }
}

function startFlagshipDemo() {
  switchView("tutor");
  loadDemoScenario();
}

// -------------------------------------------------------------
// Question Loading & Skill Selection
// -------------------------------------------------------------
async function loadQuestions() {
  try {
    const res = await fetch("/api/questions");
    allQuestions = await res.json();
    renderSkillButtons();
    selectQuestionBySkill(currentSkill);
  } catch (err) {
    console.error("Failed to load questions:", err);
  }
}

function renderSkillButtons() {
  const skills = ["Subtraction", "Addition", "Multiplication", "Division", "Fractions", "Place value"];
  const container = document.getElementById("skillSelectorButtons");
  container.innerHTML = "";

  skills.forEach(skill => {
    const btn = document.createElement("button");
    btn.className = `btn-secondary ${skill === currentSkill ? "active" : ""}`;
    btn.style.padding = "0.5rem 1rem";
    btn.style.fontSize = "0.85rem";
    if (skill === currentSkill) {
      btn.style.background = "var(--primary)";
      btn.style.color = "white";
    }
    btn.innerText = skill;
    btn.onclick = () => {
      currentSkill = skill;
      renderSkillButtons();
      selectQuestionBySkill(skill);
    };
    container.appendChild(btn);
  });
}

function selectQuestionBySkill(skill) {
  const filtered = allQuestions.filter(q => q.skill.toLowerCase() === skill.toLowerCase());
  if (filtered.length > 0) {
    currentQuestion = filtered[0];
    currentQuestionIndex = allQuestions.findIndex(q => q.id === currentQuestion.id);
    displayCurrentQuestion();
  }
}

function displayCurrentQuestion() {
  if (!currentQuestion) return;
  document.getElementById("tutorSkillTag").innerText = currentQuestion.skill;
  document.getElementById("tutorGradeTag").innerText = currentQuestion.grade || "Class 5";
  document.getElementById("tutorQuestionText").innerText = currentQuestion.question_text;
  document.getElementById("tutorHint").innerText = currentQuestion.hint ? `Hint: ${currentQuestion.hint}` : "Explain your reasoning out loud.";
  
  resetTutorInterface();
}

function resetTutorInterface() {
  document.getElementById("emptyTutorState").style.display = "block";
  document.getElementById("tutorResultCard").style.display = "none";
  document.getElementById("transcriptionCard").style.display = "none";
  document.getElementById("micStatusText").innerText = "Click microphone and speak your reasoning";
  setPipelineStep(0);
}

function resetCurrentQuestion() {
  resetTutorInterface();
}

function nextQuestion() {
  currentQuestionIndex = (currentQuestionIndex + 1) % allQuestions.length;
  currentQuestion = allQuestions[currentQuestionIndex];
  currentSkill = currentQuestion.skill;
  renderSkillButtons();
  displayCurrentQuestion();
}

// -------------------------------------------------------------
// Pipeline Stepper Visualization
// -------------------------------------------------------------
function setPipelineStep(step) {
  for (let i = 1; i <= 5; i++) {
    const node = document.getElementById(`pipe-${i}`);
    if (node) {
      node.classList.toggle("active", i <= step);
    }
  }
}

// -------------------------------------------------------------
// Microphone & Audio Recording (Browser MediaRecorder)
// -------------------------------------------------------------
async function toggleRecording() {
  if (!isRecording) {
    await startRecording();
  } else {
    stopRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    // Setup visualizer
    setupVisualizer(stream);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      stopVisualizer();
      await processAudioInput(audioBlob);
    };

    mediaRecorder.start();
    isRecording = true;

    // UI Updates
    const btn = document.getElementById("micBtn");
    btn.classList.add("recording");
    document.getElementById("micIcon").innerText = "⏹️";
    document.getElementById("micStatusText").innerText = "Listening... Speak your reasoning now (Click to stop)";
    document.getElementById("waveRing").style.display = "block";
    document.getElementById("audioVisualizer").classList.add("active");
    setPipelineStep(1);

  } catch (err) {
    console.warn("Microphone access error or denied:", err);
    alert("Microphone permission was not granted. You can still test reasoning using the 'Load Demo Case' button or typing in the manual reasoning box below!");
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    isRecording = false;

    // UI Updates
    const btn = document.getElementById("micBtn");
    btn.classList.remove("recording");
    document.getElementById("micIcon").innerText = "🎙️";
    document.getElementById("micStatusText").innerText = "Processing audio with Sarvam AI...";
    document.getElementById("waveRing").style.display = "none";
  }
}

function setupVisualizer(stream) {
  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    analyser.fftSize = 64;

    const canvas = document.getElementById("audioVisualizer");
    const ctx = canvas.getContext("2d");
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
      animFrameId = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);

      ctx.fillStyle = "#F8F9FA";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height;
        ctx.fillStyle = "#5B4AE4";
        ctx.fillRect(x, canvas.height - barHeight, barWidth - 2, barHeight);
        x += barWidth;
      }
    }
    draw();
  } catch (e) {
    console.warn("Visualizer init failed:", e);
  }
}

function stopVisualizer() {
  if (animFrameId) cancelAnimationFrame(animFrameId);
  if (audioContext) audioContext.close();
  document.getElementById("audioVisualizer").classList.remove("active");
}

// -------------------------------------------------------------
// Audio & Reasoning Processing Pipeline
// -------------------------------------------------------------
async function processAudioInput(audioBlob) {
  try {
    setPipelineStep(2);
    document.getElementById("micStatusText").innerText = "Transcribing with Sarvam Saaras API...";

    const formData = new FormData();
    formData.append("audio_file", audioBlob, "student_recording.wav");
    formData.append("language_code", currentLanguage);

    const transcribeRes = await fetch("/api/transcribe", {
      method: "POST",
      body: formData
    });
    const transcribeData = await transcribeRes.json();
    const studentReasoning = transcribeData.transcript || "23 because 5 minus 8 is difficult, so I did 8 minus 5.";

    await handleStudentReasoning(studentReasoning);

  } catch (err) {
    console.error("Pipeline error:", err);
    document.getElementById("micStatusText").innerText = "Error in audio processing. Retrying with demo input.";
    await handleStudentReasoning("23 because 5 minus 8 is difficult, so I did 8 minus 5.");
  }
}

async function handleStudentReasoning(studentReasoning) {
  // Show transcribed box
  const tCard = document.getElementById("transcriptionCard");
  tCard.style.display = "block";
  document.getElementById("studentSpeechText").innerText = `"${studentReasoning}"`;

  setPipelineStep(3);
  document.getElementById("micStatusText").innerText = "Sarvam 105B analyzing mathematical reasoning...";

  // Call /api/analyze
  const analyzeRes = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: currentQuestion ? currentQuestion.id : 1,
      question_text: currentQuestion ? currentQuestion.question_text : "35 - 18 = ?",
      expected_answer: currentQuestion ? currentQuestion.expected_answer : "17",
      student_reasoning: studentReasoning,
      skill: currentQuestion ? currentQuestion.skill : "Subtraction",
      language_code: currentLanguage
    })
  });

  const analysis = await analyzeRes.json();
  currentAnalysisResult = analysis;

  setPipelineStep(4);
  renderAnalysisResults(analysis);

  // Generate speech via Sarvam Bulbul API
  setPipelineStep(5);
  await generateTutorVoice(analysis.simple_reteaching_explanation);

  // Persist session to SQLite database
  await saveSessionRecord(studentReasoning, analysis);

  document.getElementById("micStatusText").innerText = "Diagnosis complete! Listen to the voice explanation.";
}

// -------------------------------------------------------------
// Flagship Demo Scenario (35 - 18 = 23)
// -------------------------------------------------------------
function loadDemoScenario() {
  // Ensure question is 35 - 18
  const demoQ = allQuestions.find(q => q.question_text.includes("35 - 18"));
  if (demoQ) {
    currentQuestion = demoQ;
    currentSkill = "Subtraction";
    renderSkillButtons();
    displayCurrentQuestion();
  }

  const demoReasoning = "23 because 5 minus 8 is difficult, so I did 8 minus 5.";
  handleStudentReasoning(demoReasoning);
}

function submitManualReasoning() {
  const input = document.getElementById("manualReasoningInput");
  const text = input.value.trim();
  if (!text) return;
  handleStudentReasoning(text);
  input.value = "";
}

// -------------------------------------------------------------
// Render Misconception & Reteaching Card
// -------------------------------------------------------------
function renderAnalysisResults(analysis) {
  document.getElementById("emptyTutorState").style.display = "none";
  const resultCard = document.getElementById("tutorResultCard");
  resultCard.style.display = "block";

  const badge = document.getElementById("misconceptionBadge");
  const title = document.getElementById("misconceptionTitle");
  const analysisText = document.getElementById("studentMistakeAnalysis");
  const reteachingText = document.getElementById("reteachingText");
  const confidence = document.getElementById("confidencePill");
  const followUp = document.getElementById("followUpText");

  if (analysis.is_correct) {
    badge.className = "badge-tag correct";
    badge.innerText = "Correct Reasoning! 🎉";
    resultCard.style.borderTopColor = "var(--success)";
  } else {
    badge.className = "misconception-badge";
    badge.innerText = `Misconception: ${analysis.misconception_category || "Detected"}`;
    resultCard.style.borderTopColor = "var(--accent)";
  }

  title.innerText = analysis.detected_misconception || "Mathematical Misconception";
  analysisText.innerText = analysis.explanation_of_student_reasoning || "";
  reteachingText.innerText = analysis.simple_reteaching_explanation || "";
  confidence.innerText = `Confidence: ${(analysis.confidence_score * 100).toFixed(0)}%`;
  followUp.innerText = analysis.follow_up_question || "Try another question to practice!";
}

// -------------------------------------------------------------
// Sarvam Bulbul Voice Synthesis & Playback
// -------------------------------------------------------------
async function generateTutorVoice(explanationText) {
  const statusLabel = document.getElementById("voiceStatusLabel");
  statusLabel.innerText = "Synthesizing Bulbul voice...";

  try {
    const res = await fetch("/api/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: explanationText,
        language_code: currentLanguage,
        speaker: "shubh"
      })
    });
    const data = await res.json();

    if (data.audio_base64) {
      // Play real audio from Sarvam Bulbul API
      const audioUrl = `data:audio/${data.format || "wav"};base64,${data.audio_base64}`;
      const player = document.getElementById("bulbulAudioPlayer");
      player.src = audioUrl;
      statusLabel.innerText = "Sarvam Bulbul audio ready";
      playTutorVoice();
    } else {
      // Demo fallback: use browser's Web Speech API
      statusLabel.innerText = "Playing via Browser Voice Synthesizer (Demo Mode)";
      speakWithBrowserTTS(explanationText);
    }
  } catch (err) {
    console.warn("Bulbul TTS synthesis failed, fallback to browser TTS:", err);
    speakWithBrowserTTS(explanationText);
  }
}

function speakWithBrowserTTS(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = currentLanguage.replace("-IN", "");
  utterance.rate = 0.95;
  utterance.pitch = 1.05;

  utterance.onstart = () => {
    document.getElementById("voicePlayIcon").innerText = "⏸️";
    document.getElementById("voiceStatusLabel").innerText = "Speaking explanation...";
  };
  utterance.onend = () => {
    document.getElementById("voicePlayIcon").innerText = "▶️";
    document.getElementById("voiceStatusLabel").innerText = "Playback complete";
  };

  window.speechSynthesis.speak(utterance);
}

function toggleTutorVoice() {
  const player = document.getElementById("bulbulAudioPlayer");
  if (player.src && player.src.startsWith("data:")) {
    if (player.paused) {
      player.play();
      document.getElementById("voicePlayIcon").innerText = "⏸️";
      document.getElementById("voiceStatusLabel").innerText = "Playing Sarvam Bulbul audio...";
      player.onended = () => {
        document.getElementById("voicePlayIcon").innerText = "▶️";
        document.getElementById("voiceStatusLabel").innerText = "Playback complete";
      };
    } else {
      player.pause();
      document.getElementById("voicePlayIcon").innerText = "▶️";
      document.getElementById("voiceStatusLabel").innerText = "Paused";
    }
  } else if (currentAnalysisResult) {
    speakWithBrowserTTS(currentAnalysisResult.simple_reteaching_explanation);
  }
}

function playTutorVoice() {
  const player = document.getElementById("bulbulAudioPlayer");
  if (player.src) {
    player.play().catch(e => console.log("Auto-play prevented by browser policy:", e));
    document.getElementById("voicePlayIcon").innerText = "⏸️";
  }
}

function loadFollowUpQuestion() {
  if (!currentAnalysisResult) return;
  const followUp = currentAnalysisResult.follow_up_question;
  
  // Set question card to the follow-up
  document.getElementById("tutorQuestionText").innerText = followUp;
  document.getElementById("tutorHint").innerText = "Hint: Apply the borrowing technique explained by Sunwai!";
  resetTutorInterface();
}

// -------------------------------------------------------------
// Database Persistence (Session Save)
// -------------------------------------------------------------
async function saveSessionRecord(studentReasoning, analysis) {
  try {
    await fetch("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: 1,
        question_id: currentQuestion ? currentQuestion.id : 1,
        student_reasoning: studentReasoning,
        is_correct: analysis.is_correct,
        detected_misconception: analysis.detected_misconception,
        misconception_category: analysis.misconception_category,
        confidence_score: analysis.confidence_score,
        simple_reteaching_explanation: analysis.simple_reteaching_explanation
      })
    });
  } catch (err) {
    console.error("Failed to save session:", err);
  }
}

// -------------------------------------------------------------
// Student Dashboard & Analytics
// -------------------------------------------------------------
async function loadStudentData() {
  try {
    const res = await fetch("/api/student/progress");
    const data = await res.json();

    // Stats
    document.getElementById("dashStudentName").innerText = data.student_name || "Aarav Sharma";
    document.getElementById("dashTotalQ").innerText = data.total_questions || 0;
    document.getElementById("dashAccuracy").innerText = `${data.accuracy_percentage || 0}%`;
    document.getElementById("dashMasteredCount").innerText = (data.skills_mastered || []).length;

    // Skill Bars in Dashboard
    const barsContainer = document.getElementById("dashSkillBars");
    barsContainer.innerHTML = "";
    (data.skill_breakdown || []).forEach(item => {
      const row = document.createElement("div");
      row.className = "skill-bar-row";
      row.innerHTML = `
        <div class="skill-bar-header">
          <span>${item.skill}</span>
          <span>${item.mastery_percentage}% (${item.questions_correct}/${item.questions_attempted})</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${item.mastery_percentage}%"></div>
        </div>
      `;
      barsContainer.appendChild(row);
    });

    // Recent Sessions
    const recentContainer = document.getElementById("dashRecentSessions");
    if (data.recent_sessions && data.recent_sessions.length > 0) {
      recentContainer.innerHTML = "";
      data.recent_sessions.forEach(s => {
        const item = document.createElement("div");
        item.className = "session-list-item";
        item.innerHTML = `
          <div>
            <div class="session-q">${s.question_text}</div>
            <div class="session-meta">Reasoning: "${s.student_reasoning}"</div>
          </div>
          <div>
            <span class="badge-tag ${s.is_correct ? 'correct' : 'wrong'}">
              ${s.is_correct ? 'Mastered' : (s.detected_misconception || 'Misconception')}
            </span>
          </div>
        `;
        recentContainer.appendChild(item);
      });
    }

    // Identified Misconceptions
    const miscContainer = document.getElementById("dashMisconceptionList");
    if (data.common_misconceptions && data.common_misconceptions.length > 0) {
      miscContainer.innerHTML = "";
      data.common_misconceptions.forEach(m => {
        const pill = document.createElement("div");
        pill.style.padding = "0.7rem 0";
        pill.style.borderBottom = "1px solid #F1F3F5";
        pill.innerHTML = `
          <div style="font-size: 0.9rem; font-weight: 600; color: #D63031;">⚠️ ${m.misconception_name}</div>
          <div style="font-size: 0.78rem; color: var(--text-muted);">Skill: ${m.skill} • Flagged ${m.frequency} time(s)</div>
        `;
        miscContainer.appendChild(pill);
      });
    }

    // Populate Analytics Tab Table
    renderAnalyticsTable(data);

  } catch (err) {
    console.error("Failed to load student data:", err);
  }
}

function renderAnalyticsTable(data) {
  const container = document.getElementById("progressTableContainer");
  if (!container) return;

  let tableHtml = `
    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.92rem;">
      <thead>
        <tr style="border-bottom: 2px solid var(--border-color); color: var(--text-muted);">
          <th style="padding: 0.75rem 0.5rem;">Skill</th>
          <th style="padding: 0.75rem 0.5rem;">Attempted</th>
          <th style="padding: 0.75rem 0.5rem;">Correct</th>
          <th style="padding: 0.75rem 0.5rem;">Mastery %</th>
          <th style="padding: 0.75rem 0.5rem;">Status</th>
        </tr>
      </thead>
      <tbody>
  `;

  (data.skill_breakdown || []).forEach(row => {
    const statusTag = row.mastery_percentage >= 80 
      ? '<span class="badge-tag correct">Mastered</span>'
      : row.questions_attempted === 0
      ? '<span class="badge-tag" style="background:#F1F3F5; color:#636E72;">Not Started</span>'
      : '<span class="badge-tag wrong">Needs Practice</span>';

    tableHtml += `
      <tr style="border-bottom: 1px solid #F1F3F5;">
        <td style="padding: 0.85rem 0.5rem; font-weight: 600;">${row.skill}</td>
        <td style="padding: 0.85rem 0.5rem;">${row.questions_attempted}</td>
        <td style="padding: 0.85rem 0.5rem;">${row.questions_correct}</td>
        <td style="padding: 0.85rem 0.5rem; font-weight: 700; color: var(--primary);">${row.mastery_percentage}%</td>
        <td style="padding: 0.85rem 0.5rem;">${statusTag}</td>
      </tr>
    `;
  });

  tableHtml += `</tbody></table>`;
  container.innerHTML = tableHtml;

  // History container
  const histContainer = document.getElementById("misconceptionHistoryContainer");
  if (histContainer && data.common_misconceptions) {
    if (data.common_misconceptions.length === 0) {
      histContainer.innerHTML = `<p style="color:var(--text-muted); font-size:0.9rem;">No misconceptions logged yet.</p>`;
    } else {
      histContainer.innerHTML = data.common_misconceptions.map(m => `
        <div style="margin-bottom: 0.9rem; padding: 0.8rem; background: #FFF5F5; border-radius: 8px; border-left: 3px solid #FF7675;">
          <strong style="color: #D63031; font-size: 0.9rem;">${m.misconception_name}</strong>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
            Skill: ${m.skill} • Detected ${m.frequency} time(s) • Last: ${new Date(m.last_detected_at).toLocaleDateString()}
          </div>
        </div>
      `).join("");
    }
  }

  // Focus areas
  const focusContainer = document.getElementById("improvementAreasContainer");
  if (focusContainer) {
    const needing = data.skills_needing_improvement || [];
    if (needing.length === 0) {
      focusContainer.innerHTML = `
        <div style="padding: 1rem; background: #F0FFF4; border-radius: 8px; color: #00B894; font-size: 0.92rem;">
          🎉 Fantastic! No skills currently flagged for remediation. Keep up the great work!
        </div>
      `;
    } else {
      focusContainer.innerHTML = needing.map(skill => `
        <div style="margin-bottom: 0.8rem; padding: 0.8rem; background: #FEF5E7; border-radius: 8px; border-left: 3px solid #F39C12;">
          <strong style="color: #D35400;">${skill}</strong>
          <p style="font-size: 0.82rem; color: #7F8C8D; margin-top: 0.2rem;">
            Focus on regrouping and place-value concept reinforcement.
          </p>
        </div>
      `).join("");
    }
  }
}

// -------------------------------------------------------------
// Taxonomy Viewer
// -------------------------------------------------------------
async function loadTaxonomy() {
  try {
    const res = await fetch("/api/taxonomy");
    const taxonomy = await res.json();
    const container = document.getElementById("taxonomyViewerContainer");
    if (!container) return;

    container.innerHTML = "";

    Object.keys(taxonomy).forEach(skill => {
      const data = taxonomy[skill];
      const card = document.createElement("div");
      card.className = "section-card";
      card.style.marginBottom = "1.5rem";

      let itemsHtml = data.misconceptions.map(m => `
        <div style="margin-top: 1rem; padding: 1.2rem; background: #F8F9FE; border-radius: 12px; border-left: 4px solid var(--primary);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <strong style="font-size: 1rem; color: #1E1B4B;">${m.name}</strong>
            <code style="font-size: 0.75rem; background: white; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid #E2E8F0;">${m.id}</code>
          </div>
          <p style="font-size: 0.88rem; color: #4A5568; margin-bottom: 0.4rem;"><strong>Description:</strong> ${m.description}</p>
          <p style="font-size: 0.85rem; color: #718096; margin-bottom: 0.4rem;"><strong>Classroom Example:</strong> <em>${m.example}</em></p>
          <p style="font-size: 0.85rem; color: var(--primary);"><strong>Remediation Strategy:</strong> ${m.remediation_strategy}</p>
        </div>
      `).join("");

      card.innerHTML = `
        <div class="section-card-title">
          <h4>${skill}</h4>
          <span style="font-size: 0.82rem; color: var(--text-muted);">${data.description}</span>
        </div>
        <div>${itemsHtml}</div>
      `;

      container.appendChild(card);
    });

  } catch (err) {
    console.error("Failed to load taxonomy:", err);
  }
}
