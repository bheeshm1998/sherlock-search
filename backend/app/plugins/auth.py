from fastapi import HTTPException, Header
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase
cred = credentials.Certificate("path-to-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

# Function to verify users
def verify_user(authorization: str = Header(...)):
    try:
        token = authorization.split("Bearer ")[1]  # Extract token
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email")

        if not email.endswith("@payoda.com"):
            raise HTTPException(status_code=403, detail="Access restricted to payoda.com users")

        return email
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
