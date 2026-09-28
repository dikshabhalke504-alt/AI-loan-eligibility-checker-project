import os
import math
import logging
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.claude_service import ClaudeService
from services.sheets_service import SheetsService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "bfsi-loan-checker-secret-key-change-in-prod")

# Initialize services
claude_service = ClaudeService()
sheets_service = SheetsService()

# -------------------------------------------------------------
# Static SPA Hosting Routes
# -------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

# -------------------------------------------------------------
# Health & Configuration Status API
# -------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "AI Loan Eligibility Checker API",
        "claude_integration": {
            "configured": claude_service.has_active_key,
            "model": claude_service.model,
            "mode": "Live Anthropic API" if claude_service.has_active_key else "Intelligent Heuristic Fallback"
        },
        "google_sheets_integration": {
            "configured": bool(sheets_service.webhook_url or (sheets_service.spreadsheet_id and sheets_service.api_key)),
            "target": "Google Sheets" if (sheets_service.webhook_url or sheets_service.spreadsheet_id) else "Local File Persistence"
        }
    })

# -------------------------------------------------------------
# Module 1: Dynamic Loan Eligibility Engine
# -------------------------------------------------------------
@app.route("/api/calculate-eligibility", methods=["POST"])
def calculate_eligibility():
    try:
        data = request.get_json() or {}
        income = float(data.get("monthly_income", 0))
        debt = float(data.get("existing_debt", 0))
        requested = float(data.get("requested_amount", 0))
        credit_score = int(data.get("credit_score", 700))
        employment = str(data.get("employment_status", "Salaried"))
        purpose = str(data.get("loan_purpose", "Personal"))
        tenure_years = float(data.get("tenure_years", 5))

        if income <= 0:
            return jsonify({"error": "Monthly income must be greater than zero."}), 400

        # 1. Debt-to-Income (DTI) Ratio
        dti_ratio = round((debt / income) * 100, 2)

        # 2. Benchmark FOIR (Fixed Obligation to Income Ratio)
        foir_map = {
            "Salaried": 0.55,
            "Self-Employed": 0.50,
            "Business Owner": 0.50,
            "Freelancer": 0.45
        }
        foir_ceiling = foir_map.get(employment, 0.50)

        # 3. Maximum allowable monthly EMI
        max_allowable_emi = max(0.0, (income * foir_ceiling) - debt)

        # 4. Estimated Benchmark Interest Rate by Credit Score
        if credit_score >= 780:
            est_annual_rate = 6.99
        elif credit_score >= 740:
            est_annual_rate = 7.75
        elif credit_score >= 700:
            est_annual_rate = 8.99
        elif credit_score >= 650:
            est_annual_rate = 11.50
        elif credit_score >= 600:
            est_annual_rate = 14.50
        else:
            est_annual_rate = 18.00

        # Adjust slightly for loan purpose
        purpose_adjustment = {
            "Home": -1.25,
            "Vehicle": -0.50,
            "Personal": 0.0,
            "Business": 0.75,
            "Education": -0.75
        }
        est_annual_rate = max(4.5, est_annual_rate + purpose_adjustment.get(purpose, 0.0))

        # 5. Calculate Max Eligible Loan Amount using Present Value of Annuity
        monthly_rate = (est_annual_rate / 100.0) / 12.0
        tenure_months = int(tenure_years * 12)

        if monthly_rate > 0 and tenure_months > 0:
            factor = (1 + monthly_rate) ** tenure_months
            max_eligible_loan = max_allowable_emi * ((factor - 1) / (monthly_rate * factor))
        else:
            max_eligible_loan = max_allowable_emi * tenure_months

        max_eligible_loan = max(0.0, round(max_eligible_loan, 2))

        # 6. Calculate Requested Loan's Estimated Monthly EMI
        if requested > 0 and monthly_rate > 0 and tenure_months > 0:
            factor = (1 + monthly_rate) ** tenure_months
            requested_emi = round(requested * (monthly_rate * factor) / (factor - 1), 2)
        else:
            requested_emi = 0.0

        # 7. Multi-Factor Eligibility Scoring (0 - 100)
        # Factor A: DTI Score (0 to 35 pts)
        if dti_ratio <= 20:
            dti_score = 35
        elif dti_ratio <= 35:
            dti_score = 30
        elif dti_ratio <= 45:
            dti_score = 22
        elif dti_ratio <= 55:
            dti_score = 12
        else:
            dti_score = 4

        # Factor B: Credit Score (0 to 35 pts)
        if credit_score >= 780:
            credit_score_pts = 35
        elif credit_score >= 720:
            credit_score_pts = 30
        elif credit_score >= 660:
            credit_score_pts = 22
        elif credit_score >= 600:
            credit_score_pts = 12
        else:
            credit_score_pts = 5

        # Factor C: Coverage / Loan Capacity (0 to 20 pts)
        if max_eligible_loan >= requested and requested > 0:
            capacity_ratio = requested / max_eligible_loan
            if capacity_ratio <= 0.7:
                capacity_pts = 20
            elif capacity_ratio <= 0.9:
                capacity_pts = 16
            else:
                capacity_pts = 12
        elif max_eligible_loan > 0 and requested > 0:
            capacity_pts = max(2, int(10 * (max_eligible_loan / requested)))
        else:
            capacity_pts = 5

        # Factor D: Employment Stability (0 to 10 pts)
        emp_pts = {"Salaried": 10, "Business Owner": 9, "Self-Employed": 8, "Freelancer": 6}.get(employment, 7)

        total_score = min(100, dti_score + credit_score_pts + capacity_pts + emp_pts)

        # Verdict and Risk Classification
        if total_score >= 75 and requested_emi <= max_allowable_emi:
            verdict = "Approved (Prime Tier)"
            verdict_badge = "success"
            status_desc = "Your financial profile meets all prime underwriting criteria for automated clearance."
        elif total_score >= 60 and requested_emi <= (max_allowable_emi * 1.10):
            verdict = "Conditional Approval"
            verdict_badge = "warning"
            status_desc = "Eligible with standard verification. Minor adjustments or lower borrowing recommended."
        elif total_score >= 45:
            verdict = "Manual Review Required"
            verdict_badge = "review"
            status_desc = "Underwriting review needed due to debt-to-income or capacity thresholds."
        else:
            verdict = "High Risk / Ineligible"
            verdict_badge = "danger"
            status_desc = "Requested amount exceeds safe capacity or debt-to-income ratio exceeds risk limits."

        return jsonify({
            "dti_ratio": dti_ratio,
            "max_allowable_emi": round(max_allowable_emi, 2),
            "max_eligible_loan": max_eligible_loan,
            "estimated_interest_rate": est_annual_rate,
            "requested_loan_amount": requested,
            "requested_monthly_emi": requested_emi,
            "eligibility_score": total_score,
            "approval_verdict": verdict,
            "verdict_badge": verdict_badge,
            "status_description": status_desc,
            "tenure_years": tenure_years,
            "credit_score": credit_score
        })
    except Exception as e:
        logger.error(f"Error calculating eligibility: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------
# Module 4: AI Financial Tips (Claude AI Powered)
# -------------------------------------------------------------
@app.route("/api/ai/financial-tips", methods=["POST"])
def get_ai_financial_tips():
    try:
        telemetry = request.get_json() or {}
        tips = claude_service.generate_financial_tips(telemetry)
        return jsonify(tips)
    except Exception as e:
        logger.error(f"Error generating AI tips: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/ask", methods=["POST"])
def ask_ai():
    try:
        data = request.get_json() or {}
        telemetry = data.get("telemetry", {})
        question = data.get("question", "")
        response = claude_service.answer_custom_question(telemetry, question)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error answering question: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------
# Database & Persistence (Google Sheets & Persistent Store)
# -------------------------------------------------------------
@app.route("/api/submissions/save", methods=["POST"])
def save_submission():
    try:
        data = request.get_json() or {}
        saved_record = sheets_service.save_submission(data)
        return jsonify({
            "success": True,
            "message": "Submission recorded successfully.",
            "record": saved_record
        })
    except Exception as e:
        logger.error(f"Error saving submission: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/submissions/list", methods=["GET"])
def list_submissions():
    try:
        records = sheets_service.get_submissions(limit=30)
        return jsonify({"submissions": records})
    except Exception as e:
        logger.error(f"Error listing submissions: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() in ["true", "1", "yes"]
    logger.info(f"Starting AI Loan Eligibility Checker on port {port} (debug={debug})...")
    app.run(host="0.0.0.0", port=port, debug=debug)
