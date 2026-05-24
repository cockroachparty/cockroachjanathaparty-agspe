"""
AGSPE Audit Logger - Logs all algorithmic decisions for
transparency, compliance, and independent verification.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class AuditLogger:
    """
    Audit trail for all algorithmic decisions in AGSPE.

    Every validation, prediction, and bias detection event is logged
    with full context to enable independent verification and
    regulatory compliance.
    """

    def __init__(self, log_dir: str = "/tmp/agspe_audit"):
        self.log_dir = log_dir
        self.entries: List[Dict] = []
        os.makedirs(log_dir, exist_ok=True)

    def log(
        self,
        action: str,
        details: Dict,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Log an algorithmic decision.

        Args:
            action: The action type (e.g., "validation", "prediction", "bias_detection")
            details: Detailed information about the decision
            user_id: Optional user identifier
            session_id: Optional session identifier

        Returns:
            The logged entry dictionary
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details,
            "user_id": user_id or "system",
            "session_id": session_id or "default",
            "entry_id": f"audit-{len(self.entries) + 1:06d}",
        }

        self.entries.append(entry)
        return entry

    def log_validation(
        self,
        claim: str,
        sources: List[Dict],
        result: Dict,
    ) -> Dict:
        """Log a validation event with full context."""
        return self.log("validation", {
            "claim": claim,
            "source_count": len(sources),
            "source_tiers": [s.get("tier", 3) for s in sources],
            "source_names": [s.get("name", "Unknown") for s in sources],
            "validation_score": result.get("validation_score"),
            "bias_risk_level": result.get("bias_risk_level"),
            "flags": result.get("flags", []),
            "cross_verification_status": result.get("cross_verification_status"),
        })

    def log_prediction(
        self,
        prediction: Dict,
        input_data_summary: Dict,
    ) -> Dict:
        """Log a prediction generation event."""
        return self.log("prediction", {
            "prediction_id": prediction.get("id"),
            "likely_action": prediction.get("likely_action"),
            "confidence_score": prediction.get("confidence_score"),
            "category": prediction.get("category"),
            "input_summary": input_data_summary,
        })

    def log_bias_detection(
        self,
        text: str,
        detection_result: Dict,
    ) -> Dict:
        """Log a bias detection event."""
        return self.log("bias_detection", {
            "text_snippet": text[:200],
            "pro_group_indicators": detection_result.get("pro_group_indicators"),
            "negative_indicators": detection_result.get("negative_indicators"),
            "bias_score": detection_result.get("bias_score"),
            "is_likely_promotional": detection_result.get("is_likely_promotional"),
        })

    def export_to_json(self, filepath: Optional[str] = None) -> str:
        """Export the audit trail to a JSON file."""
        if filepath is None:
            filepath = os.path.join(
                self.log_dir,
                f"audit_trail_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )

        with open(filepath, "w") as f:
            json.dump(self.entries, f, indent=2, default=str)

        return filepath

    def get_entries(
        self,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:
        """Retrieve audit entries with optional filtering."""
        entries = self.entries
        if action:
            entries = [e for e in entries if e["action"] == action]
        return entries[offset:offset + limit]

    def get_summary(self) -> Dict:
        """Get a summary of all audit activity."""
        action_counts = {}
        for entry in self.entries:
            action = entry["action"]
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total_entries": len(self.entries),
            "action_counts": action_counts,
            "first_entry": self.entries[0]["timestamp"] if self.entries else None,
            "last_entry": self.entries[-1]["timestamp"] if self.entries else None,
        }

    def clear(self) -> None:
        """Clear all in-memory audit entries."""
        self.entries = []


# Global audit logger instance
audit_logger = AuditLogger()
