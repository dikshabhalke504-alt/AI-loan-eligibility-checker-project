/**
 * AI Loan Eligibility Checker - Core Application Controller
 * Manages SPA tab switching, global telemetry state synchronization,
 * health status polling, and toast notifications.
 */
document.addEventListener("DOMContentLoaded", () => {
  window.App = {
    telemetry: {},

    init() {
      this.cacheDOM();
      this.bindEvents();
      this.checkSystemHealth();

      // Initialize all functional modules
      if (window.EligibilityModule) window.EligibilityModule.init();
      if (window.CreditModule) window.CreditModule.init();
      if (window.EmiModule) window.EmiModule.init();
      if (window.AiModule) window.AiModule.init();
      if (window.SheetsModule) window.SheetsModule.init();
    },

    cacheDOM() {
      this.navTabs = document.querySelectorAll(".nav-tab");
      this.tabPanels = document.querySelectorAll(".tab-panel");
      this.systemStatusText = document.getElementById("system-status-text");
      this.systemStatusPill = document.getElementById("system-status-pill");
      this.toastContainer = document.getElementById("toast-container");

      // Ribbon DOM
      this.ribbonIncome = document.getElementById("ribbon-income");
      this.ribbonDebt = document.getElementById("ribbon-debt");
      this.ribbonDti = document.getElementById("ribbon-dti");
      this.ribbonCredit = document.getElementById("ribbon-credit");
      this.ribbonRequested = document.getElementById("ribbon-requested");
      this.ribbonStatus = document.getElementById("ribbon-status");
    },

    bindEvents() {
      // Tab switching
      this.navTabs.forEach(tab => {
        tab.addEventListener("click", () => {
          const targetTabId = tab.getAttribute("data-tab");
          this.switchTab(targetTabId);
        });
      });
    },

    switchTab(tabId) {
      this.navTabs.forEach(tab => {
        if (tab.getAttribute("data-tab") === tabId) {
          tab.classList.add("active");
        } else {
          tab.classList.remove("active");
        }
      });

      this.tabPanels.forEach(panel => {
        if (panel.id === tabId) {
          panel.classList.add("active");
        } else {
          panel.classList.remove("active");
        }
      });

      // Module-specific hooks on tab activation
      if (tabId === "tab-emi" && window.EmiModule) {
        if (this.telemetry.requested_amount) {
          window.EmiModule.setValues(
            this.telemetry.requested_amount,
            this.telemetry.estimated_interest_rate,
            this.telemetry.tenure_years
          );
        }
      } else if (tabId === "tab-ai" && window.AiModule) {
        window.AiModule.handleTelemetryUpdate(this.telemetry);
      } else if (tabId === "tab-ledger" && window.SheetsModule) {
        window.SheetsModule.loadSubmissions();
      }

      window.scrollTo({ top: 0, behavior: "smooth" });
    },

    updateTelemetry(newTelemetry) {
      this.telemetry = { ...this.telemetry, ...newTelemetry };

      // Update Ribbon Elements
      if (this.ribbonIncome) this.ribbonIncome.textContent = `₹${(this.telemetry.monthly_income || 0).toLocaleString('en-IN')}`;
      if (this.ribbonDebt) this.ribbonDebt.textContent = `₹${(this.telemetry.existing_debt || 0).toLocaleString('en-IN')}`;

      if (this.ribbonDti) {
        this.ribbonDti.textContent = `${this.telemetry.dti_ratio || 0}%`;
        this.ribbonDti.className = `ribbon-val ${(this.telemetry.dti_ratio <= 36) ? 'text-success' : (this.telemetry.dti_ratio <= 45 ? 'text-cyan' : 'text-purple')}`;
      }

      if (this.ribbonCredit) {
        let band = "Good";
        const score = this.telemetry.credit_score || 740;
        if (score >= 800) band = "Exceptional";
        else if (score >= 740) band = "Very Good";
        else if (score >= 670) band = "Good";
        else if (score >= 580) band = "Fair";
        else band = "Poor";
        this.ribbonCredit.textContent = `${score} (${band})`;
      }

      if (this.ribbonRequested) {
        this.ribbonRequested.textContent = `₹${(this.telemetry.requested_amount || 0).toLocaleString('en-IN')}`;
      }

      if (this.ribbonStatus) {
        this.ribbonStatus.textContent = this.telemetry.approval_verdict || "Approved (Prime)";
        this.ribbonStatus.className = `badge-status badge-${this.telemetry.verdict_badge || 'success'}`;
      }

      // Propagate telemetry to AI Module
      if (window.AiModule && typeof window.AiModule.handleTelemetryUpdate === "function") {
        window.AiModule.activeTelemetry = this.telemetry;
      }
    },

    async checkSystemHealth() {
      try {
        const resp = await fetch("/api/health");
        if (resp.ok) {
          const health = await resp.json();
          if (health.claude_integration?.configured) {
            this.systemStatusText.textContent = "Claude AI Live";
            this.systemStatusPill.style.borderColor = "rgba(0, 230, 118, 0.4)";
            this.systemStatusPill.style.color = "var(--accent-emerald)";
          } else {
            this.systemStatusText.textContent = "Claude AI Engine Ready";
            this.systemStatusPill.style.borderColor = "rgba(0, 242, 254, 0.4)";
            this.systemStatusPill.style.color = "var(--accent-cyan)";
          }
        }
      } catch (e) {
        this.systemStatusText.textContent = "Offline Mode";
        this.systemStatusPill.style.borderColor = "rgba(245, 158, 11, 0.4)";
        this.systemStatusPill.style.color = "var(--accent-amber)";
      }
    },

    showToast(message, type = "info") {
      if (!this.toastContainer) return;

      const toast = document.createElement("div");
      toast.className = `toast toast-${type}`;

      const iconSvg = type === "success"
        ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`
        : type === "error"
        ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`
        : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00f2fe" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;

      toast.innerHTML = `
        ${iconSvg}
        <span>${message}</span>
      `;

      this.toastContainer.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(20px)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
      }, 4000);
    }
  };

  window.App.init();
});
