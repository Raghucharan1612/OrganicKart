import os

os.environ.setdefault("NOTIFICATION_DATABASE_URL", "sqlite:///./test_notification.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("INTERNAL_SERVICE_KEY", "test-internal-key")
