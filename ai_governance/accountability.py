"""
Accountability — tamper-evident audit trail / 責任の所在(監査証跡)

When an AI system contributes to a clinical decision, who decided what, and
when? Accountability requires an immutable record: each entry chains a hash of
the previous one, so any later alteration breaks the chain and is detectable.
Each record also captures whether a human reviewed the AI's recommendation
(human-in-the-loop). Standard library only.
"""

import hashlib
from dataclasses import dataclass, field


@dataclass
class AuditRecord:
    timestamp: str
    actor: str            # clinician or system component responsible
    action: str
    model_version: str
    recommendation: str
    human_reviewed: bool
    prev_hash: str
    entry_hash: str = field(default="")

    def compute_hash(self) -> str:
        payload = "|".join([
            self.timestamp, self.actor, self.action, self.model_version,
            self.recommendation, str(self.human_reviewed), self.prev_hash,
        ])
        return hashlib.sha256(payload.encode()).hexdigest()


class AuditLog:
    GENESIS = "0" * 64

    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def append(
        self, timestamp: str, actor: str, action: str,
        model_version: str, recommendation: str, human_reviewed: bool,
    ) -> AuditRecord:
        prev_hash = self.records[-1].entry_hash if self.records else self.GENESIS
        record = AuditRecord(
            timestamp, actor, action, model_version,
            recommendation, human_reviewed, prev_hash,
        )
        record.entry_hash = record.compute_hash()
        self.records.append(record)
        return record

    def verify(self) -> bool:
        """Re-derive the chain; return False if any record was altered."""
        prev_hash = self.GENESIS
        for record in self.records:
            if record.prev_hash != prev_hash:
                return False
            if record.entry_hash != record.compute_hash():
                return False
            prev_hash = record.entry_hash
        return True

    def unreviewed(self) -> list[AuditRecord]:
        """AI recommendations that were never checked by a human."""
        return [r for r in self.records if not r.human_reviewed]


if __name__ == "__main__":
    log = AuditLog()
    log.append("2026-06-04T09:00", "model:sepsis-risk", "score_patient",
               "v1.2.0", "high risk: escalate", human_reviewed=False)
    log.append("2026-06-04T09:05", "dr_tanaka", "review_recommendation",
               "v1.2.0", "agree: start protocol", human_reviewed=True)
    log.append("2026-06-04T09:10", "dr_tanaka", "order_treatment",
               "v1.2.0", "broad-spectrum antibiotics", human_reviewed=True)

    print(f"Chain valid: {log.verify()}")
    print(f"Unreviewed AI actions: {[r.action for r in log.unreviewed()]}")

    # Someone tampers with a past record after the fact.
    log.records[1].recommendation = "disagree: no action"
    print(f"Chain valid after tampering: {log.verify()}")
