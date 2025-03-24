# from fastapi import HTTPException, Header
# from firebase_admin import auth, credentials
# import firebase_admin
#
# # Initialize Firebase
# cred = credentials.Certificate("path-to-firebase-adminsdk.json")
# firebase_admin.initialize_app(cred)
#
# def verify_user(authorization: str = Header(...)):
#     """
#     Verifies Firebase ID token and restricts access to @payoda.com users.
#     """
#     try:
#         token = authorization.split("Bearer ")[1]  # Extract token
#         decoded_token = auth.verify_id_token(token)
#         email = decoded_token.get("email")
#
#         if not email.endswith("@payoda.com"):
#             raise HTTPException(status_code=403, detail="Access restricted to payoda.com users")
#
#         return email
#     except Exception:
#         raise HTTPException(status_code=401, detail="Unauthorized")
