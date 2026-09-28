/**
 * Module 2: Credit Score Analyzer & Dynamic Simulator
 * Visualizes credit rating bands, factor weights, and simulates scenario point impacts.
 */
(function() {
  const CreditModule = {
    baseScore: 740,
    simulatedScore: 740,

    init() {
      this.cacheDOM();
      this.bindEvents();
      this.render();
    },

    cacheDOM() {
      this.needle = document.getElementById("gauge-needle");
      this.scoreReadout = document.getElementById("sim-score-readout");
      this.bandReadout = document.getElementById("sim-band-readout");
      this.deltaBadge = document.getElementById("sim-delta-badge");

      this.checkboxes = document.querySelectorAll(".sim-checkbox");
      this.btnReset = document.getElementById("btn-reset-sim");
      this.btnApply = document.getElementById("btn-apply-sim-to-profile");
    },

    bindEvents() {
      this.checkboxes.forEach(cb => {
        cb.addEventListener("change", () => this.calculateSimulatedScore());
      });

      this.btnReset.addEventListener("click", () => {
        this.checkboxes.forEach(cb => cb.checked = false);
        this.calculateSimulatedScore();
        window.App?.showToast("Simulator reset to base credit score", "info");
      });

      this.btnApply.addEventListener("click", () => {
        if (window.EligibilityModule && typeof window.EligibilityModule.setCreditScore === "function") {
          window.EligibilityModule.setCreditScore(this.simulatedScore);
          window.App?.showToast(`Applied simulated score (${this.simulatedScore}) to loan profile!`, "success");
          window.App?.switchTab("tab-eligibility");
        }
      });
    },

    setBaseScore(score) {
      this.baseScore = score;
      this.calculateSimulatedScore();
    },

    calculateSimulatedScore() {
      let delta = 0;
      this.checkboxes.forEach(cb => {
        if (cb.checked) {
          const impact = parseInt(cb.getAttribute("data-impact"), 10) || 0;
          delta += impact;
        }
      });

      let calculated = this.baseScore + delta;
      // Clamp between 300 and 850
      this.simulatedScore = Math.max(300, Math.min(850, calculated));
      this.render(delta);
    },

    render(delta = 0) {
      const score = this.simulatedScore;
      this.scoreReadout.textContent = score;

      // Calculate needle rotation angle (-90deg at 300 to +90deg at 850)
      const ratio = (score - 300) / 550;
      const angle = -90 + (ratio * 180);
      if (this.needle) {
        this.needle.style.transform = `rotate(${angle}deg)`;
      }

      // Band name & color
      let bandText = "Good (670 - 739)";
      let bandColor = "#10b981";

      if (score >= 800) {
        bandText = "Exceptional (800 - 850)";
        bandColor = "#c084fc";
      } else if (score >= 740) {
        bandText = "Very Good (740 - 799)";
        bandColor = "#0ea5e9";
      } else if (score >= 670) {
        bandText = "Good (670 - 739)";
        bandColor = "#10b981";
      } else if (score >= 580) {
        bandText = "Fair (580 - 669)";
        bandColor = "#f59e0b";
      } else {
        bandText = "Poor (300 - 579)";
        bandColor = "#ef4444";
      }

      this.bandReadout.textContent = bandText;
      this.bandReadout.style.color = bandColor;

      // Delta Badge
      if (delta > 0) {
        this.deltaBadge.className = "sim-delta positive";
        this.deltaBadge.textContent = `+${delta} pts Simulated Net Gain`;
      } else if (delta < 0) {
        this.deltaBadge.className = "sim-delta negative";
        this.deltaBadge.textContent = `${delta} pts Simulated Penalty`;
      } else {
        this.deltaBadge.className = "sim-delta";
        this.deltaBadge.textContent = "Base Credit Score";
      }
    }
  };

  window.CreditModule = CreditModule;
})();
