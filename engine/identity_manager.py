
import uuid
from datetime import datetime

class IdentityManager:
    def __init__(self, storage_path="data/identities"):
        self.storage_path = storage_path

    def create_user(self, email, role="student"):
        return {
            "id": str(uuid.uuid4()),
            "email": email,
            "role": role,
            "created": datetime.utcnow().isoformat(),
            "status": "active"
        }
