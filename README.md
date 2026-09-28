# AI Loan Eligibility Checker — BFSI Financial Intelligence Platform

An institutional-grade Banking, Financial Services, and Insurance (BFSI) web platform titled **AI Loan Eligibility Checker**. The application pairs a dark glassmorphic design system with real-time financial telemetry, an annuity-based EMI engine, a credit score simulator, Claude AI integration for credit underwriting reasoning, and Google Sheets synchronization for session persistence.

---

## 1. Platform Architecture & Modules

```
                           AI Loan Eligibility Checker (SPA)
  ┌─────────────────────────┬───────────────────────────┬───────────────────────────┐
  │  1. Eligibility Engine  │  2. Credit Score Analyzer │     3. EMI Calculator     │
  │  - DTI & FOIR metrics   │  - 300-850 SVG gauge      │  - Annuity formula        │
  │  - Max borrowing limit  │  - 5-factor impact cards  │  - Interactive SVG donut  │
  │  - Underwriting verdict │  - Real-time score sim    │  - Full amortization      │
  └────────────┬────────────┴─────────────┬─────────────┴─────────────┬─────────────┘
               │                          │                           │
               ▼                          ▼                           ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │                 4. Claude AI Financial Intelligence               │
        │      - Underwriting risk analysis & approval probability          │
        │      - Actionable tips (credit, debt consolidation, rate disc)    │
        │      - Interactive "Ask Financial AI" conversational advisory     │
        └─────────────────────────────────┬─────────────────────────────────┘
                                          │
                                          ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │           5. Database & Google Sheets Ledger Persistence          │
        │      - Live synchronization via Apps Script Webhook / Sheets API  │
        │      - File-backed persistent audit ledger (data/submissions.json)│
        └───────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Functional Modules

### 1. Loan Eligibility Checker
* **Inputs**: Gross monthly income, existing debt obligations, employment status (*Salaried, Self-Employed, Freelancer, Business Owner*), requested loan amount, tenure (years), and loan purpose.
* **Underwriting Metrics**:
  * **Debt-to-Income (DTI)** ratio calculated dynamically with visual prime threshold indicators.
  * **Fixed Obligation to Income Ratio (FOIR)** safety limits tailored to applicant employment classification.
  * **Max Allowable Monthly EMI** and **Max Eligible Loan Amount** calculated via the present value annuity formula.
  * **Multi-Factor Score (0-100)** with automated underwriting clearance status (*Approved Prime Tier, Conditional Approval, Manual Review Required, High Risk*).

### 2. Credit Score Analyzer
* **Dynamic SVG Gauge**: Real-time rotating needle visualizing credit health across all rating bands: Poor (<580), Fair (580-669), Good (670-739), Very Good (740-799), Exceptional (800+).
* **FICO/VantageScore Factor Breakdown**: Detailed cards covering Payment History (35%), Credit Utilization (30%), Credit History Length (15%), Credit Mix (10%), and New Inquiries (10%).
* **Real-Time Score Simulator**: Interactive scenario toggles (*pay down 35% revolving debt (+35 pts)*, *erase late payment (+50 pts)*, *request credit line increase (+20 pts)*, *missed payment penalty (-65 pts)*) that dynamically adjust the score and allow instant transfer into the loan profile.

### 3. Interactive EMI Calculator
* **Dual Controls**: Synchronized range sliders and numeric input fields for Principal ($5,000 - $1,000,000), Annual Interest Rate (3.5% - 22%), and Tenure (Years/Months switchable).
* **Annuity Computation**:
  $$\text{EMI} = P \times r \times \frac{(1+r)^n}{(1+r)^n - 1}$$
* **Interactive SVG Donut Chart**: Dynamic SVG arc rendering showing exact Principal vs. Interest percentage distribution with glowing neon indicators.
* **Comprehensive Amortization**: Annual summary table and full monthly amortization schedule tracking opening balance, EMI, principal portion, interest paid, and remaining balance.
* **Prepayment Acceleration Simulator**: Live simulator calculating interest savings and months shaved off loan term when paying extra principal monthly.

### 4. AI Financial Tips (Powered by Anthropic Claude)
* **Real-time Telemetry Synthesis**: Sends complete applicant profile (income, debt, DTI, credit score, tenure, requested vs. eligible loan) to Anthropic Claude 3.5 Sonnet.
* **Underwriter Synthesis**:
  * Prime approval probability rating (0% - 100%).
  * Executive underwriting verdict and risk tier.
  * Contextual debt consolidation recommendations.
  * Concrete rate negotiation leverage tips for discussions with loan officers.
* **Interactive "Ask Financial AI" Chat**: Real-time conversational advisory enabling applicants to ask custom follow-up questions regarding their terms, tenure trade-offs, and rate discounts.
* **High-Fidelity Heuristic Fallback**: Intelligent built-in BFSI underwriting engine that provides mathematically rigorous advice even if the external API key is unconfigured or temporarily unreachable.

### 5. Google Sheets Database & Session Persistence
* **Google Sheets Sync**: Automatically transmits approved loan submissions, applicant contact details, and financial telemetry to a designated Google Sheet.
* **Audit Ledger UI**: Dedicated in-app tab displaying all saved applications, timestamped in UTC, with instant search, sync badges, and verification IDs.
* **Dual-Layer Persistence**: Transparent file-backed storage (`data/submissions.json`) guarantees zero data loss if Google credentials are not yet configured.

---

## 3. Technology Stack & Design System

* **Frontend**: Native HTML5, modern CSS3, and modular ES6+ JavaScript.
* **Aesthetic**: Premium dark glassmorphism:
  * Multi-layer `backdrop-filter: blur(16px)` panels on midnight palette (`#070a13`, `#0d1322`).
  * Neon accents: Electric Cyan (`#00f2fe`), Emerald (`#00e676`), Royal Violet (`#7928ca`), and Amber (`#f59e0b`).
  * Typography: `Plus Jakarta Sans` for typography and `JetBrains Mono` for financial metrics.
* **Backend**: Python 3.14 + Flask REST API with `requests` and `python-dotenv`.
* **Testing**: Python `unittest` test suite covering mathematical models and API response mappings.

---

## 4. Environment Variables & API Setup

Configuration is managed via the `.env` file in the project root. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### Environment Variable Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `ANTHROPIC_API_KEY` | Your Anthropic Claude API Key | `sk-ant-api03-...` |
| `ANTHROPIC_MODEL` | Preferred Claude model | `claude-3-5-sonnet-20241022` |
| `GOOGLE_SHEETS_WEBHOOK_URL` | Google Apps Script Webhook URL (Method A) | `https://script.google.com/macros/s/.../exec` |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Google Spreadsheet ID (Method B) | `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms` |
| `GOOGLE_SHEETS_API_KEY` | Google Sheets API v4 Key (Method B) | `AIzaSy...` |
| `GOOGLE_SERVICE_ACCOUNT_PATH` | Path to Google Service Account JSON | `./credentials/service_account.json` |
| `PORT` | Flask application server port | `5000` |
| `DEBUG` | Flask debug mode flag | `True` |

---

### Step-by-Step API Configuration Guides

#### A. Setting up Anthropic Claude AI
1. Visit the [Anthropic Console](https://console.anthropic.com/) and generate an API key.
2. Open `.env` and set:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ```
3. Restart the server. The header badge will update to **"Claude AI Live"**.
*(Note: If left empty, the application seamlessly runs on its built-in BFSI underwriting intelligence engine).*

---

#### B. Setting up Google Sheets Integration

##### Option 1: Google Apps Script Webhook (Recommended — No GCP Overhead)
1. Open [Google Sheets](https://sheets.new) and create a new sheet titled **"AI Loan Applications"**.
2. Add header columns in Row 1:
   ```
   ID | Timestamp | Applicant Name | Email | Monthly Income | Debt | Requested Amount | Employment | Purpose | Tenure | Credit Score | DTI | EMI | Max Eligible | Score | Verdict
   ```
3. In the top menu, go to **Extensions > Apps Script**.
4. Replace existing code with:
   ```javascript
   function doPost(e) {
     var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
     var data = JSON.parse(e.postData.contents);
     sheet.appendRow([
       data.id,
       data.timestamp,
       data.applicant_name,
       data.applicant_email,
       data.monthly_income,
       data.existing_debt,
       data.requested_amount,
       data.employment_status,
       data.loan_purpose,
       data.tenure_years,
       data.credit_score,
       data.dti_ratio,
       data.calculated_emi,
       data.max_eligible_loan,
       data.eligibility_score,
       data.approval_verdict
     ]);
     return ContentService.createTextOutput(JSON.stringify({ status: "success" }))
       .setMimeType(ContentService.MimeType.JSON);
   }
   ```
5. Click **Deploy > New deployment**. Select type **Web app**.
   * Execute as: **Me**
   * Who has access: **Anyone**
6. Copy the **Web App URL** and paste it into `.env`:
   ```env
   GOOGLE_SHEETS_WEBHOOK_URL=https://script.google.com/macros/s/AKfycbx.../exec
   ```

##### Option 2: Google Cloud Service Account
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API**.
3. Create a Service Account, generate a JSON Key, and share your Google Sheet with the service account email.
4. Set in `.env`:
   ```env
   GOOGLE_SHEETS_SPREADSHEET_ID=your_sheet_id_here
   GOOGLE_SERVICE_ACCOUNT_PATH=./credentials/service_account.json
   ```

---

## 5. Runtime Deployment Instructions

### Prerequisites
* Python 3.10+ (Tested on Python 3.14)
* `pip` package manager

### Step 1: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 2: Run Automated Unit Tests
Verify all financial formulas, DTI logic, and API endpoints:
```bash
python test_app.py
```
*Expected output: `Ran 8 tests ... OK`.*

### Step 3: Launch Web Platform
```bash
python app.py
```

### Step 4: Access Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 6. REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | Health check and integration status for Claude & Google Sheets |
| `/api/calculate-eligibility` | `POST` | Processes applicant telemetry, computes DTI, FOIR, max loan, and verdict |
| `/api/ai/financial-tips` | `POST` | Synthesizes underwriting reasoning and advice via Claude AI |
| `/api/ai/ask` | `POST` | Conversational financial advisory responding to user queries |
| `/api/submissions/save` | `POST` | Persists applicant submission to ledger and syncs to Google Sheets |
| `/api/submissions/list` | `GET` | Retrieves recent submissions from the persistent ledger |

---

## 7. License & Compliance
Designed for institutional and enterprise BFSI demonstration. Built strictly with standard financial annuity formulas and responsive web standards.
