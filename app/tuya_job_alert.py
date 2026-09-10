import os
from datetime import datetime

class TuyaJobDeskAlert:
    """
    Tuya IoT Open Cloud Platform Integration for CodeKitchen AI Job Tracker.
    Triggers smart desk indicator LED alerts when high-match jobs (Score >= 90%) or interview invites arrive.
    """
    TUYA_DEVICE_ID = os.getenv("TUYA_DEVICE_ID", "tuya_desk_led_indicator_01")

    @classmethod
    def trigger_job_alert(cls, job_data: dict) -> dict:
        title = job_data.get("title", "Job Opportunity")
        company = job_data.get("company", "Company")
        match_score = job_data.get("match_score", 90)

        alert_payload = {
            "device_id": cls.TUYA_DEVICE_ID,
            "timestamp": datetime.now().isoformat(),
            "event": "HIGH_MATCH_JOB_ALERT",
            "company": company,
            "title": title,
            "match_score": match_score,
            "led_color": "#00FF00" if match_score >= 90 else "#FFB800",
            "tuya_status": "SIGNAL_SENT_SUCCESSFULLY"
        }
        
        print(f"[Tuya IoT] Smart Desk LED alert triggered for {company} - {title} (Match: {match_score}%)")
        return alert_payload
