import bcrypt
import hmac
import hashlib
import base64
import json
import time
from backend.app.config import JWT_SECRET_KEY

# Password hashing helpers using bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

# Self-contained signed token helper (mimicking JWT)
def create_access_token(data: dict, expires_in: int = 86400) -> str:
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in
    
    # Base64 encode header and payload
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    # Sign token
    signature_input = f"{header_b64}.{payload_b64}".encode()
    sig = hmac.new(JWT_SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify signature
        signature_input = f"{header_b64}.{payload_b64}".encode()
        sig = hmac.new(JWT_SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        recalculated_sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        
        if not hmac.compare_digest(sig_b64, recalculated_sig_b64):
            return None
            
        # Decode payload
        # Pad base64 representation
        payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (4 - len(payload_b64) % 4)).decode()
        payload = json.loads(payload_json)
        
        # Check expiration
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None
