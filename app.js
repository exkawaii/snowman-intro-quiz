const $ = (selector) => document.querySelector(selector);

const els = {
  audio: $("#audio"),
  headerCount: $("#header-count"),
  catalogCount: $("#catalog-count"),
  loading: $("#loading-state"),
  topbar: $("#game-topbar"),
  questionArea: $("#question-area"),
  resultArea: $("#result-area"),
  roundCount: $("#round-count"),
  questionNumber: $("#question-number"),
  questionTotal: $("#question-total"),
  progressBar: $("#progress-bar"),
  score: $("#score"),
  streak: $("#streak"),
  releasePill: $("#release-pill"),
  trackCredit: $("#track-credit"),
  waveform: $("#waveform"),
  audioStage: $("#audio-stage"),
  audioStatus: $("#audio-status"),
  playButton: $("#play-button"),
  playText: $(".play-text"),
  timeBar: $("#time-bar"),
  timeLimit: $("#time-limit"),
  choices: $("#choices"),
  feedback: $("#feedback"),
  feedbackIcon: $("#feedback-icon"),
  feedbackLabel: $("#feedback-label"),
  feedbackTitle: $("#feedback-title"),
  feedbackNote: $("#feedback-note"),
  appleLink: $("#apple-link"),
  nextButton: $("#next-button"),
  resultScore: $("#result-score"),
  resultTotal: $("#result-total"),
  resultAccuracy: $("#result-accuracy"),
  resultMessage: $("#result-message"),
  bestScore: $("#best-score"),
  retryButton: $("#retry-button"),
};

const PREVIEW_SECONDS = 12;
const state = {
  songs: [],
  remaining: [],
  current: null,
  choices: [],
  questionIndex: 0,
  total: 10,
  score: 0,
  streak: 0,
  answered: false,
};

function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function pad(number) {
  return String(number).padStart(2, "0");
}

function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return "00:00";
  const safeSeconds = Math.max(0, Math.floor(seconds));
  return `${String(Math.floor(safeSeconds / 60)).padStart(2, "0")}:${String(safeSeconds % 60).padStart(2, "0")}`;
}

function displayRelease(release) {
  if (!release) return "STREAMING";
  return release.length > 23 ? `${release.slice(0, 23)}…` : release;
}

function renderWaveform() {
  const bars = Array.from({ length: 72 }, (_, index) => {
    const height = 12 + ((index * 19) % 53);
    const delay = `${((index % 9) * 0.07).toFixed(2)}s`;
    return `<i style="--h:${height}%;--delay:${delay}"></i>`;
  }).join("");
  els.waveform.innerHTML = bars;
}

function updateCatalogCount() {
  const count = state.songs.length;
  els.headerCount.textContent = `${count} TRACKS READY`;
  els.catalogCount.textContent = String(count).padStart(3, "0");
}

function setLoading(loading) {
  els.loading.classList.toggle("hidden", !loading);
  els.topbar.classList.toggle("hidden", loading);
  els.questionArea.classList.toggle("hidden", loading);
}

function setAudioStatus(text) {
  els.audioStatus.textContent = text;
}

function setPlayButton(isPlaying) {
  els.playButton.classList.toggle("is-playing", isPlaying);
  els.playText.textContent = isPlaying ? "PAUSE INTRO" : "PLAY INTRO";
  els.audioStage.classList.toggle("is-playing", isPlaying);
  els.playButton.setAttribute("aria-label", isPlaying ? "イントロを一時停止" : "イントロを再生");
}

function stopAudio(reset = false) {
  els.audio.pause();
  setPlayButton(false);
  if (reset) {
    els.audio.currentTime = 0;
    els.timeBar.style.width = "0%";
  }
}

function getRoundTotal() {
  const selected = els.roundCount.value;
  return selected === "all" ? state.songs.length : Number(selected);
}

function startGame() {
  if (!state.songs.length) return;
  stopAudio(true);
  state.total = getRoundTotal();
  state.remaining = shuffle(state.songs);
  state.current = null;
  state.choices = [];
  state.questionIndex = 0;
  state.score = 0;
  state.streak = 0;
  els.score.textContent = "00";
  els.streak.textContent = "00";
  els.questionTotal.textContent = state.total === state.songs.length && els.roundCount.value === "all" ? "ALL" : pad(state.total);
  els.resultArea.classList.add("hidden");
  els.topbar.classList.remove("hidden");
  els.questionArea.classList.remove("hidden");
  nextQuestion();
}

function buildChoices(answer) {
  const distractors = shuffle(state.songs.filter((song) => song.id !== answer.id)).slice(0, 3);
  return shuffle([answer, ...distractors]);
}

function renderQuestion() {
  const song = state.current;
  els.questionNumber.textContent = pad(state.questionIndex + 1);
  els.questionTotal.textContent = state.total === state.songs.length && els.roundCount.value === "all" ? "ALL" : pad(state.total);
  els.progressBar.style.width = `${(state.questionIndex / state.total) * 100}%`;
  els.releasePill.textContent = displayRelease(song.release);
  els.trackCredit.textContent = song.credit ? `UNIT / ${song.credit}` : "SNOW MAN";
  els.feedback.classList.add("hidden");
  els.feedback.classList.remove("is-wrong");
  els.timeBar.style.width = "0%";
  els.timeLimit.textContent = `00:${String(PREVIEW_SECONDS).padStart(2, "0")}`;
  setAudioStatus("READY TO PLAY");
  setPlayButton(false);

  els.choices.innerHTML = state.choices.map((choice, index) => `
    <button class="choice" type="button" data-id="${choice.id}" data-index="${index}" aria-label="${index + 1} ${choice.title}">
      <span class="choice-number">${index + 1}</span>
      <span><strong class="choice-title">${choice.title}</strong>${choice.credit ? `<small class="choice-credit">${choice.credit}</small>` : ""}</span>
    </button>
  `).join("");

  els.choices.querySelectorAll(".choice").forEach((button) => {
    button.addEventListener("click", () => answerQuestion(button.dataset.id));
  });

  stopAudio(true);
  els.audio.src = song.previewUrl || "";
  if (song.previewUrl) {
    els.audio.load();
  } else {
    setAudioStatus("PREVIEW UNAVAILABLE");
  }
}

function nextQuestion() {
  stopAudio(true);
  if (state.questionIndex >= state.total || !state.remaining.length) {
    finishGame();
    return;
  }
  state.current = state.remaining.pop();
  state.choices = buildChoices(state.current);
  state.answered = false;
  renderQuestion();
}

function answerQuestion(id) {
  if (state.answered || !state.current) return;
  state.answered = true;
  stopAudio();
  const isCorrect = id === state.current.id;
  if (isCorrect) {
    state.score += 1;
    state.streak += 1;
  } else {
    state.streak = 0;
  }
  els.score.textContent = pad(state.score);
  els.streak.textContent = pad(state.streak);

  els.choices.querySelectorAll(".choice").forEach((button) => {
    button.disabled = true;
    if (button.dataset.id === state.current.id) button.classList.add("correct");
    if (button.dataset.id === id && !isCorrect) button.classList.add("wrong");
  });

  els.feedback.classList.remove("hidden");
  els.feedback.classList.toggle("is-wrong", !isCorrect);
  els.feedbackLabel.textContent = isCorrect ? "CORRECT / NICE ONE" : "NOT THIS TIME";
  els.feedbackTitle.textContent = state.current.title;
  const noteParts = [state.current.release || "配信曲"];
  if (state.current.credit) noteParts.push(state.current.credit);
  els.feedbackNote.textContent = noteParts.join("  •  ");
  els.appleLink.href = state.current.trackViewUrl || "https://music.apple.com/jp/artist/snow-man/1772019148";

  state.questionIndex += 1;
  els.progressBar.style.width = `${(state.questionIndex / state.total) * 100}%`;
  els.nextButton.textContent = state.questionIndex >= state.total ? "結果を見る  →" : "次の問題  →";
  els.feedback.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function finishGame() {
  stopAudio(true);
  els.questionArea.classList.add("hidden");
  els.resultArea.classList.remove("hidden");
  els.progressBar.style.width = "100%";
  els.resultScore.textContent = pad(state.score);
  els.resultTotal.textContent = state.total;
  const accuracy = state.total ? Math.round((state.score / state.total) * 100) : 0;
  els.resultAccuracy.textContent = `${accuracy}%`;
  const bestKey = `snowman-intro-quiz-best-${state.total}`;
  const oldBest = Number(localStorage.getItem(bestKey) || 0);
  const best = Math.max(oldBest, state.score);
  localStorage.setItem(bestKey, String(best));
  els.bestScore.textContent = pad(best);
  els.resultMessage.textContent = accuracy >= 90
    ? "すごい。イントロだけでSnow Manの世界を見抜いています。"
    : accuracy >= 60
      ? "いい感じ。もう一周すれば、さらに深く聴き分けられそうです。"
      : "ここからが本番。もう一度聴いて、耳をSnow Manモードに。";
}

async function toggleAudio() {
  if (!state.current || !state.current.previewUrl) {
    setAudioStatus("PREVIEW UNAVAILABLE");
    return;
  }
  if (!els.audio.paused) {
    els.audio.pause();
    return;
  }
  if (els.audio.currentTime >= PREVIEW_SECONDS - 0.05 || els.audio.currentTime === 0) {
    els.audio.currentTime = 0;
  }
  try {
    await els.audio.play();
    setAudioStatus("PLAYING INTRO");
  } catch (error) {
    setAudioStatus("TAP TO PLAY");
  }
}

function wireEvents() {
  els.playButton.addEventListener("click", toggleAudio);
  els.nextButton.addEventListener("click", nextQuestion);
  els.retryButton.addEventListener("click", startGame);
  els.roundCount.addEventListener("change", startGame);

  els.audio.addEventListener("play", () => setPlayButton(true));
  els.audio.addEventListener("pause", () => {
    setPlayButton(false);
    if (els.audio.currentTime > 0 && els.audio.currentTime < PREVIEW_SECONDS) setAudioStatus("PAUSED");
  });
  els.audio.addEventListener("ended", () => {
    setPlayButton(false);
    setAudioStatus("PREVIEW ENDED");
    els.timeBar.style.width = "100%";
  });
  els.audio.addEventListener("error", () => {
    setPlayButton(false);
    setAudioStatus("PREVIEW UNAVAILABLE");
  });
  els.audio.addEventListener("timeupdate", () => {
    const currentTime = Math.min(els.audio.currentTime, PREVIEW_SECONDS);
    els.timeBar.style.width = `${(currentTime / PREVIEW_SECONDS) * 100}%`;
    if (currentTime >= PREVIEW_SECONDS - 0.05 && !els.audio.paused) {
      els.audio.pause();
      els.audio.currentTime = PREVIEW_SECONDS;
      setAudioStatus("12 SEC PREVIEW ENDED");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, select, textarea")) return;
    if (!els.questionArea.classList.contains("hidden") && !state.answered && /^[1-4]$/.test(event.key)) {
      const button = els.choices.querySelector(`[data-index="${Number(event.key) - 1}"]`);
      if (button) button.click();
    }
    if (!els.questionArea.classList.contains("hidden") && event.code === "Space") {
      event.preventDefault();
      toggleAudio();
    }
  });
}

async function init() {
  renderWaveform();
  wireEvents();
  try {
    const response = await fetch("songs.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`songs.json returned ${response.status}`);
    const data = await response.json();
    state.songs = Array.isArray(data.songs) ? data.songs.filter((song) => song.title && song.previewUrl) : [];
    if (state.songs.length < 4) throw new Error("Not enough songs with previews");
    updateCatalogCount();
    setLoading(false);
    startGame();
  } catch (error) {
    els.loading.innerHTML = `<p>曲データを読み込めませんでした。<br />GitHub Pagesまたはローカルサーバー経由で開いてください。</p>`;
    els.headerCount.textContent = "LOAD ERROR";
  }
}

init();
