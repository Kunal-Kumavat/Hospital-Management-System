import os
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
	return password_hash.hash(password)


def verify_password(password: str, encoded_password: str) -> bool:
	return password_hash.verify(password, encoded_password)


def create_access_token(profile_id: int, role: str) -> str:
	now = datetime.now(UTC)
	payload = {
		"sub": str(profile_id),
		"role": role,
		"iat": now,
		"exp": now + timedelta(minutes=60),
	}
	secret = os.getenv("JWT_SECRET", "local-development-secret-change-me")
	return jwt.encode(payload, secret, algorithm="HS256")
