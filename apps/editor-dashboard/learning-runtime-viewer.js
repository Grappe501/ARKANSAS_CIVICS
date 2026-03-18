(() => {
  "use strict";

  const state = {
    activeSeconds: 0,
    idleSeconds: 0,
    running: false,
    blackout: false,
    lastInteractionAt: Date.now(),
    idleThresholdMs: 15000,
    timer: null,
  };

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function formatSeconds(total) {
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const seconds = total % 60;
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  }

  function render() {
    const clock = document.getElementById("learningClock");
    const status = document.getElementById("learningClockStatus");
    const idle = document.getElementById("learningIdleClock");
    const overlay = document.getElementById("learningBlackoutOverlay");
    if (!clock || !status || !idle || !overlay) return;

    clock.textContent = formatSeconds(state.activeSeconds);
    idle.textContent = formatSeconds(state.idleSeconds);
    status.textContent = state.blackout ? "Paused for inactivity" : state.running ? "Active learning mode" : "Stopped";
    overlay.style.display = state.blackout ? "flex" : "none";
  }

  function markInteraction() {
    state.lastInteractionAt = Date.now();
    if (state.blackout) {
      state.blackout = false;
      state.running = true;
    }
    render();
  }

  function tick() {
    if (!state.running) return;

    const idleMs = Date.now() - state.lastInteractionAt;
    if (idleMs >= state.idleThresholdMs) {
      state.blackout = true;
      state.idleSeconds += 1;
    } else {
      state.activeSeconds += 1;
      state.blackout = false;
    }
    render();
  }

  function start() {
    if (state.running) return;
    state.running = true;
    if (!state.timer) state.timer = window.setInterval(tick, 1000);
    render();
  }

  function stop() {
    state.running = false;
    render();
  }

  function reset() {
    state.activeSeconds = 0;
    state.idleSeconds = 0;
    state.blackout = false;
    state.lastInteractionAt = Date.now();
    render();
  }

  function init() {
    document.getElementById("startLearningClock")?.addEventListener("click", start);
    document.getElementById("stopLearningClock")?.addEventListener("click", stop);
    document.getElementById("resetLearningClock")?.addEventListener("click", reset);
    ["mousemove", "click", "scroll", "keydown", "touchstart"].forEach((eventName) => {
      window.addEventListener(eventName, markInteraction, { passive: true });
    });
    render();
  }

  window.StandUpArkansasLearningRuntime = { start, stop, reset, state };
  window.addEventListener("load", init);
})();
