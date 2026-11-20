from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.models import AuditEvent

def log_audit_event(db: Session, actor_id: str, action_type: str, outcome: str):
    """Safely records an audit event without PII, passwords, or raw prompts."""
    try:
        event = AuditEvent(
            actor_id=actor_id,
            action_type=action_type,
            timestamp=datetime.now(timezone.utc),
            outcome=outcome
        )
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()
