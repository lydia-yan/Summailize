from typing import Optional, Dict, List

class UserToken:
    def __init__(self, access_token: str, refresh_token: str, token_expiry: datetime):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry

    def to_dict(self):
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expiry": self.token_expiry.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return UserToken(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_expiry=datetime.fromisoformat(data["token_expiry"])
        )
    

class UserSettings:
    def __init__(self, summary_time: str = "08:00"):
        self.summary_time = summary_time

    def to_dict(self) -> Dict:
        return {
            "summary_time": self.summary_time
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            summary_time=data.get("summary_time", "08:00")
        )


class PerEmailSummary:
    def __init__(
        self,
        email_id: str,
        sender_name: str,
        subject: str,
        summary: str,
        receiveAt: str,  # e.g., "2024-04-17 11:40:00 UTC"
        category: str,
        attachment_names: Optional[List[str]] = None
    ):
        self.email_id = email_id
        self.sender_name = sender_name
        self.subject = subject
        self.summary = summary
        self.receiveAt = receiveAt
        self.category = category
        self.attachment_names = attachment_names or []

    def to_dict(self) -> Dict:
        return {
            "sender_name": self.sender_name,
            "subject": self.subject,
            "summary": self.summary,
            "receiveAt": self.receiveAt,
            "category": self.category,
            "attachment_names": self.attachment_names
        }

    @classmethod
    def from_dict(cls, email_id: str, data: Dict):
        return cls(
            email_id=email_id,
            sender_name=data.get("sender_name", ""),
            subject=data.get("subject", ""),
            summary=data.get("summary", ""),
            receiveAt=data.get("receiveAt", ""),
            category=data.get("category", ""),
            attachment_names=data.get("attachment_names", [])
        )


class CategorySummary:
    def __init__(
        self,
        category: str,
        email_count: int,
        summary_bullets: List[str],
        attachments: Optional[List[str]] = None
    ):
        self.category = category
        self.email_count = email_count
        self.summary_bullets = summary_bullets
        self.attachments = attachments or []

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "email_count": self.email_count,
            "summary_bullets": self.summary_bullets,
            "attachments": self.attachments
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            category=data.get("category", ""),
            email_count=data.get("email_count", 0),
            summary_bullets=data.get("summary_bullets", []),
            attachments=data.get("attachments", [])
        )


class OverallSummary:
    def __init__(
        self,
        overall_summary: List[CategorySummary],
        last_email_timestamp: str  # e.g., "2024-04-17 11:40:00 UTC"
    ):
        self.overall_summary = overall_summary
        self.last_email_timestamp = last_email_timestamp

    def to_dict(self) -> Dict:
        return {
            "overall_summary": [c.to_dict() for c in self.overall_summary],
            "last_email_timestamp": self.last_email_timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict):
        categories = [CategorySummary.from_dict(c) for c in data.get("overall_summary", [])]
        return cls(
            overall_summary=categories,
            last_email_timestamp=data.get("last_email_timestamp", "")
        )
    

