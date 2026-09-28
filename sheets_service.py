import os
import json
import uuid
import datetime
import logging
import requests

logger = logging.getLogger(__name__)

class SheetsService:
    """
    Google Sheets API and Submission Persistence Service.
    Supports:
    1. Google Apps Script Webhook URL (instant Google Sheet append).
    2. Google Sheets API v4 endpoint (Service Account or API key).
    3. Transparent Local File Store (data/submissions.json) with audit timestamps.
    """

    def __init__(self, data_dir: str = None):
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "").strip()
        self.webhook_url = os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "").strip()
        self.api_key = os.getenv("GOOGLE_SHEETS_API_KEY", "").strip()
        self.service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "").strip()

        # Local storage setup
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.storage_file = os.path.join(self.data_dir, "submissions.json")
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        if not os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
            except Exception as e:
                logger.error(f"Failed to initialize storage file: {e}")

    def save_submission(self, data: dict) -> dict:
        """
        Record a loan submission, save to persistent local store, and sync to Google Sheets.
        """
        submission_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        record = {
            "id": submission_id,
            "timestamp": timestamp,
            "applicant_name": data.get("applicant_name", "Anonymous Applicant"),
            "applicant_email": data.get("applicant_email", "applicant@example.com"),
            "monthly_income": float(data.get("monthly_income", 0)),
            "existing_debt": float(data.get("existing_debt", 0)),
            "requested_amount": float(data.get("requested_amount", 0)),
            "employment_status": data.get("employment_status", "Salaried"),
            "loan_purpose": data.get("loan_purpose", "Personal"),
            "tenure_years": float(data.get("tenure_years", 5)),
            "credit_score": int(data.get("credit_score", 700)),
            "dti_ratio": float(data.get("dti_ratio", 0)),
            "calculated_emi": float(data.get("calculated_emi", 0)),
            "max_eligible_loan": float(data.get("max_eligible_loan", 0)),
            "eligibility_score": int(data.get("eligibility_score", 0)),
            "approval_verdict": data.get("approval_verdict", "Under Review"),
            "synced_to_sheets": False,
            "sync_details": "Saved to local persistent ledger"
        }

        # Attempt Google Sheets sync
        sync_result = self._sync_to_google_sheets(record)
        record["synced_to_sheets"] = sync_result.get("success", False)
        record["sync_details"] = sync_result.get("message", "Pending sync")

        # Save to local file store
        self._persist_to_local_store(record)

        return record

    def get_submissions(self, limit: int = 50) -> list:
        """
        Retrieve recent submissions from the persistent ledger.
        """
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    records.reverse()  # Latest first
                    return records[:limit]
        except Exception as e:
            logger.error(f"Error reading submissions file: {e}")
        return []

    def _persist_to_local_store(self, record: dict):
        try:
            records = []
            if os.path.exists(self.storage_file):
                try:
                    with open(self.storage_file, "r", encoding="utf-8") as f:
                        records = json.load(f)
                except Exception:
                    records = []
            records.append(record)
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            logger.error(f"Error appending record to local storage: {e}")

    def _sync_to_google_sheets(self, record: dict) -> dict:
        """
        Push record row to Google Sheets via configured integration path.
        """
        # Strategy 1: Google Apps Script Webhook (Zero GCP overhead, recommended)
        if self.webhook_url and not self.webhook_url.startswith("https://script.google.com/macros/s/your_"):
            try:
                resp = requests.post(
                    self.webhook_url,
                    json=record,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if resp.status_code in [200, 201, 302]:
                    return {"success": True, "message": "Synced via Google Apps Script Webhook"}
                else:
                    logger.warning(f"Google Apps Script Webhook returned HTTP {resp.status_code}")
                    return {"success": False, "message": f"Webhook returned HTTP {resp.status_code}"}
            except Exception as e:
                logger.error(f"Google Apps Script Webhook sync failed: {e}")
                return {"success": False, "message": f"Webhook sync error: {str(e)}"}

        # Strategy 2: Direct Google Sheets API v4 using API Key & Spreadsheet ID
        if self.spreadsheet_id and self.api_key:
            try:
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/A1:append?valueInputOption=USER_ENTERED&key={self.api_key}"
                row_values = [
                    record["id"],
                    record["timestamp"],
                    record["applicant_name"],
                    record["applicant_email"],
                    record["monthly_income"],
                    record["existing_debt"],
                    record["requested_amount"],
                    record["employment_status"],
                    record["loan_purpose"],
                    record["tenure_years"],
                    record["credit_score"],
                    record["dti_ratio"],
                    record["calculated_emi"],
                    record["max_eligible_loan"],
                    record["eligibility_score"],
                    record["approval_verdict"]
                ]
                resp = requests.post(
                    url,
                    json={"values": [row_values]},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if resp.status_code == 200:
                    return {"success": True, "message": "Synced via Google Sheets API v4"}
                else:
                    return {"success": False, "message": f"Google Sheets API HTTP {resp.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Google Sheets API error: {str(e)}"}

        # Fallback explanation
        return {
            "success": False,
            "message": "Saved to local persistent ledger. Google Sheets API credentials not yet configured."
        }
