const $ = (selector) => document.querySelector(selector);

const els = {
  audio: $("#audio"),
  headerCount: $("#header-count"),
  loading: $("#loading-state"),
  startGate: $("#start-gate"),
  beginGame: $("#begin-game"),
  topbar: $("#game-topbar"),
  questionArea: $("#question-area"),
  resultArea: $("#result-area"),
  roundCount: $("#round-count"),
  customRoundWrap: $("#custom-round-wrap"),
  customRoundCount: $("#custom-round-count"),
  questionNumber: $("#question-number"),
  questionTotal: $("#question-total"),
  progressBar: $("#progress-bar"),
  score: $("#score"),
  streak: $("#streak"),
  waveform: $("#waveform"),
  audioStage: $("#audio-stage"),
  audioCaptionLabel: $("#audio-caption-label"),
  audioStatus: $("#audio-status"),
  playButton: $("#play-button"),
  playText: $(".play-text"),
  timeBar: $("#time-bar"),
  timeLimit: $("#time-limit"),
  choices: $("#choices"),
  answerReveal: $("#answer-reveal"),
  answerArtwork: $("#answer-artwork"),
  answerArtFallback: $("#answer-art-fallback"),
  answerRelease: $("#answer-release"),
  answerSongTitle: $("#answer-song-title"),
  answerSongCredit: $("#answer-song-credit"),
  answerRevealLabel: $("#answer-reveal-label"),
  revealStatus: $("#reveal-status"),
  youtubePlayerShell: $("#youtube-player-shell"),
  youtubeSourceLink: $("#youtube-source-link"),
  feedback: $("#feedback"),
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

const INTRO_SECONDS = 12;
const DEFAULT_HIGHLIGHT_START = 0;
const HIGHLIGHT_SECONDS = 30;
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
  started: false,
  audioMode: "intro",
  highlightStart: DEFAULT_HIGHLIGHT_START,
  highlightEnd: DEFAULT_HIGHLIGHT_START + HIGHLIGHT_SECONDS,
};
let youtubePlayer = null;
let youtubeApiPromise = null;

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
  els.headerCount.textContent = `${state.songs.length} TRACKS READY`;
  els.customRoundCount.max = String(state.songs.length);
}

function setLoading(loading) {
  els.loading.classList.toggle("hidden", !loading);
  if (loading) {
    els.startGate.classList.add("hidden");
    els.topbar.classList.add("hidden");
    els.questionArea.classList.add("hidden");
    els.resultArea.classList.add("hidden");
  }
}

function syncCustomControls() {
  const isCustom = els.roundCount.value === "custom";
  els.customRoundWrap.classList.toggle("hidden", !isCustom);
  if (state.songs.length) {
    els.customRoundCount.max = String(state.songs.length);
  }
}

function setAudioStatus(text) {
  els.audioStatus.textContent = text;
}

function setPlayButton(isPlaying) {
  const isHighlight = state.audioMode === "highlight";
  els.playButton.classList.toggle("is-playing", isPlaying);
  els.playText.textContent = isPlaying ? (isHighlight ? "PAUSE HIGHLIGHT" : "PAUSE INTRO") : (isHighlight ? "PLAY HIGHLIGHT" : "PLAY INTRO");
  els.audioStage.classList.toggle("is-playing", isPlaying);
  els.playButton.setAttribute("aria-label", isPlaying ? "再生を一時停止" : (isHighlight ? "ハイライトを再生" : "イントロを再生"));
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
  if (els.roundCount.value === "all") return state.songs.length;
  if (els.roundCount.value === "custom") {
    const requested = Number.parseInt(els.customRoundCount.value, 10);
    const safe = Number.isFinite(requested) ? requested : 1;
    const total = Math.min(Math.max(safe, 1), state.songs.length);
    els.customRoundCount.value = String(total);
    return total;
  }
  return Math.min(Number(els.roundCount.value), state.songs.length);
}

function totalLabel() {
  return els.roundCount.value === "all" ? "ALL" : pad(state.total);
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
  state.started = true;
  els.score.textContent = "00";
  els.streak.textContent = "00";
  els.questionTotal.textContent = totalLabel();
  els.startGate.classList.add("hidden");
  els.resultArea.classList.add("hidden");
  els.topbar.classList.remove("hidden");
  els.questionArea.classList.remove("hidden");
  nextQuestion();
}

function buildChoices(answer) {
  const distractors = shuffle(state.songs.filter((song) => song.id !== answer.id)).slice(0, 3);
  return shuffle([answer, ...distractors]);
}

function resetAnswerReveal() {
  if (youtubePlayer && typeof youtubePlayer.stopVideo === "function") youtubePlayer.stopVideo();
  els.answerReveal.classList.add("hidden");
  els.youtubePlayerShell.classList.add("hidden");
  els.youtubeSourceLink.href = "#";
  els.answerArtwork.removeAttribute("src");
  els.answerArtwork.classList.add("hidden");
  els.answerArtFallback.classList.remove("hidden");
  els.answerRelease.textContent = "";
  els.answerSongTitle.textContent = "";
  els.answerSongCredit.textContent = "";
  els.answerRevealLabel.textContent = "TRACK HIGHLIGHT / OFFICIAL VIDEO";
  els.revealStatus.textContent = "LOADING OFFICIAL VIDEO";
}

function renderQuestion() {
  const song = state.current;
  state.audioMode = "intro";
  state.highlightStart = DEFAULT_HIGHLIGHT_START;
  state.highlightEnd = state.highlightStart + HIGHLIGHT_SECONDS;
  els.questionNumber.textContent = pad(state.questionIndex + 1);
  els.questionTotal.textContent = totalLabel();
  els.progressBar.style.width = `${(state.questionIndex / state.total) * 100}%`;
  els.feedback.classList.add("hidden");
  els.feedback.classList.remove("is-wrong");
  resetAnswerReveal();
  els.audioCaptionLabel.textContent = "INTRO PREVIEW";
  els.timeBar.style.width = "0%";
  els.timeLimit.textContent = formatTime(INTRO_SECONDS);
  setAudioStatus("LOADING INTRO");
  setPlayButton(false);

  els.choices.innerHTML = state.choices.map((choice, index) => `
    <button class="choice" type="button" data-id="${choice.id}" data-index="${index}" aria-label="${index + 1} ${choice.title}">
      <span class="choice-number">${index + 1}</span>
      <span><strong class="choice-title">${choice.title}</strong></span>
    </button>
  `).join("");

  els.choices.querySelectorAll(".choice").forEach((button) => {
    button.addEventListener("click", () => answerQuestion(button.dataset.id));
  });

  stopAudio(true);
  els.audio.src = song.previewUrl || "";
  if (song.previewUrl) {
    els.audio.load();
    // The start button and the next-question button are user gestures, so autoplay is allowed in normal browsers.
    window.setTimeout(() => playIntro(), 0);
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

function showAnswerReveal(song) {
  els.answerReveal.classList.remove("hidden");
  els.answerRelease.textContent = song.release || "配信中の作品";
  els.answerSongTitle.textContent = song.title;
  els.answerSongCredit.textContent = song.credit ? `UNIT / ${song.credit}` : "Snow Man";
  if (song.artworkUrl) {
    els.answerArtwork.src = song.artworkUrl;
    els.answerArtwork.classList.remove("hidden");
    els.answerArtFallback.classList.add("hidden");
  }
}

function loadYouTubeApi() {
  if (window.YT && window.YT.Player) return Promise.resolve();
  if (youtubeApiPromise) return youtubeApiPromise;
  youtubeApiPromise = new Promise((resolve, reject) => {
    const previousCallback = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      if (typeof previousCallback === "function") previousCallback();
      resolve();
    };
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.async = true;
    script.onerror = () => reject(new Error("YouTube IFrame API failed to load"));
    document.head.appendChild(script);
  });
  return youtubeApiPromise;
}

function youtubeWindow(song) {
  const start = Number.isFinite(Number(song.youtubeStart)) ? Number(song.youtubeStart) : 0;
  const explicitEnd = Number.isFinite(Number(song.youtubeEnd)) ? Number(song.youtubeEnd) : null;
  return { start, end: explicitEnd && explicitEnd > start ? explicitEnd : null };
}

async function playOfficialYouTube(song) {
  if (!song.youtubeVideoId) return false;
  stopAudio(true);
  state.audioMode = "youtube";
  els.youtubePlayerShell.classList.remove("hidden");
  els.youtubeSourceLink.href = song.youtubeUrl || `https://www.youtube.com/watch?v=${song.youtubeVideoId}`;
  els.answerRevealLabel.textContent = "TRACK HIGHLIGHT / OFFICIAL VIDEO";
  els.revealStatus.textContent = "LOADING OFFICIAL VIDEO";
  const range = youtubeWindow(song);
  await loadYouTubeApi();
  const loadVideo = (player) => {
    const video = { videoId: song.youtubeVideoId, startSeconds: range.start };
    if (range.end) video.endSeconds = range.end;
    player.loadVideoById(video);
  };
  if (!youtubePlayer) {
    youtubePlayer = new window.YT.Player("youtube-player", {
      width: "100%",
      height: "220",
      videoId: song.youtubeVideoId,
      host: "https://www.youtube-nocookie.com",
      playerVars: {
        autoplay: 0,
        controls: 1,
        playsinline: 1,
        rel: 0,
        origin: window.location.origin,
      },
      events: {
        onReady: (event) => loadVideo(event.target),
        onStateChange: (event) => {
          if (event.data === window.YT.PlayerState.PLAYING) els.revealStatus.textContent = "PLAYING OFFICIAL VIDEO";
          if (event.data === window.YT.PlayerState.ENDED) els.revealStatus.textContent = "OFFICIAL CLIP ENDED";
        },
        onAutoplayBlocked: () => { els.revealStatus.textContent = "PRESS PLAY IN VIDEO"; },
        onError: () => {
          els.revealStatus.textContent = "YOUTUBE UNAVAILABLE / USING PREVIEW";
          els.youtubePlayerShell.classList.add("hidden");
          playHighlight();
        },
      },
    });
  } else {
    loadVideo(youtubePlayer);
  }
  return true;
}

async function playAnswerMedia(song) {
  if (song.youtubeVideoId) {
    try {
      const loaded = await playOfficialYouTube(song);
      if (loaded) return;
    } catch (error) {
      els.revealStatus.textContent = "YOUTUBE UNAVAILABLE / USING PREVIEW";
    }
  }
  playHighlight();
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

  if (isCorrect) {
    showAnswerReveal(state.current);
    playAnswerMedia(state.current);
  }

  state.questionIndex += 1;
  els.progressBar.style.width = `${(state.questionIndex / state.total) * 100}%`;
  els.nextButton.textContent = state.questionIndex >= state.total ? "結果を見る  →" : "次の問題  →";
  (isCorrect ? els.answerReveal : els.feedback).scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function finishGame() {
  stopAudio(true);
  resetAnswerReveal();
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

async function playIntro() {
  if (!state.current || !state.current.previewUrl || state.answered) return;
  state.audioMode = "intro";
  els.audioCaptionLabel.textContent = "INTRO PREVIEW";
  els.timeLimit.textContent = formatTime(INTRO_SECONDS);
  els.audio.currentTime = 0;
  try {
    await els.audio.play();
    setAudioStatus("PLAYING INTRO");
  } catch (error) {
    setAudioStatus("TAP TO PLAY");
  }
}

async function playHighlight() {
  if (!state.current || !state.current.previewUrl) return;
  state.audioMode = "highlight";
  els.youtubePlayerShell.classList.add("hidden");
  els.answerRevealLabel.textContent = "TRACK HIGHLIGHT / 30 SEC PREVIEW";
  els.audioCaptionLabel.textContent = "HIGHLIGHT / 30 SEC";
  els.revealStatus.textContent = "PLAYING HIGHLIGHT";
  const startPlayback = async () => {
    const duration = Number.isFinite(els.audio.duration) ? els.audio.duration : state.highlightStart + HIGHLIGHT_SECONDS;
    state.highlightEnd = Math.min(duration, state.highlightStart + HIGHLIGHT_SECONDS);
    if (state.highlightEnd <= state.highlightStart) state.highlightStart = 0;
    els.audio.currentTime = Math.min(state.highlightStart, Math.max(0, duration - 1));
    els.timeLimit.textContent = formatTime(Math.max(1, state.highlightEnd - state.highlightStart));
    try {
      await els.audio.play();
      setAudioStatus("PLAYING HIGHLIGHT");
      els.revealStatus.textContent = "PLAYING HIGHLIGHT";
    } catch (error) {
      setAudioStatus("TAP TO PLAY HIGHLIGHT");
      els.revealStatus.textContent = "TAP TO PLAY HIGHLIGHT";
    }
  };
  if (els.audio.readyState >= 1) {
    await startPlayback();
  } else {
    els.audio.addEventListener("loadedmetadata", startPlayback, { once: true });
  }
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
  if (state.audioMode === "highlight") {
    await playHighlight();
  } else {
    await playIntro();
  }
}

function wireEvents() {
  els.beginGame.addEventListener("click", startGame);
  els.playButton.addEventListener("click", toggleAudio);
  els.nextButton.addEventListener("click", nextQuestion);
  els.retryButton.addEventListener("click", startGame);
  els.roundCount.addEventListener("change", syncCustomControls);

  els.answerArtwork.addEventListener("error", () => {
    els.answerArtwork.classList.add("hidden");
    els.answerArtFallback.classList.remove("hidden");
  });
  els.audio.addEventListener("play", () => setPlayButton(true));
  els.audio.addEventListener("pause", () => {
    setPlayButton(false);
    if (state.answered && state.audioMode === "highlight") els.revealStatus.textContent = "HIGHLIGHT PAUSED";
    if (els.audio.currentTime > 0) setAudioStatus(state.audioMode === "highlight" ? "HIGHLIGHT PAUSED" : "PAUSED");
  });
  els.audio.addEventListener("ended", () => {
    setPlayButton(false);
    setAudioStatus(state.audioMode === "highlight" ? "HIGHLIGHT ENDED" : "PREVIEW ENDED");
    if (state.audioMode === "highlight") els.revealStatus.textContent = "HIGHLIGHT ENDED";
    els.timeBar.style.width = "100%";
  });
  els.audio.addEventListener("error", () => {
    setPlayButton(false);
    setAudioStatus("PREVIEW UNAVAILABLE");
    if (state.audioMode === "highlight") els.revealStatus.textContent = "PREVIEW UNAVAILABLE";
  });
  els.audio.addEventListener("timeupdate", () => {
    const start = state.audioMode === "highlight" ? state.highlightStart : 0;
    const end = state.audioMode === "highlight" ? state.highlightEnd : INTRO_SECONDS;
    const currentTime = Math.min(els.audio.currentTime, end);
    const progress = end > start ? Math.max(0, Math.min(100, ((currentTime - start) / (end - start)) * 100)) : 0;
    els.timeBar.style.width = `${progress}%`;
    if (currentTime >= end - 0.05 && !els.audio.paused) {
      els.audio.pause();
      els.audio.currentTime = end;
      setAudioStatus(state.audioMode === "highlight" ? "HIGHLIGHT ENDED" : "12 SEC PREVIEW ENDED");
      if (state.audioMode === "highlight") els.revealStatus.textContent = "HIGHLIGHT ENDED";
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
  syncCustomControls();
  try {
    const response = await fetch("songs.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`songs.json returned ${response.status}`);
    const data = await response.json();
    state.songs = Array.isArray(data.songs) ? data.songs.filter((song) => song.title && song.previewUrl) : [];
    if (state.songs.length < 4) throw new Error("Not enough songs with previews");
    updateCatalogCount();
    setLoading(false);
    els.startGate.classList.remove("hidden");
  } catch (error) {
    els.loading.innerHTML = `<p>曲データを読み込めませんでした。<br />GitHub Pagesまたはローカルサーバー経由で開いてください。</p>`;
    els.headerCount.textContent = "LOAD ERROR";
  }
}

init();
