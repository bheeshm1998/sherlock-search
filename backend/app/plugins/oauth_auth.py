# from fastapi import FastAPI, HTTPException
# from fastapi.security import OAuth2AuthorizationCodeBearer
# from fastapi.responses import RedirectResponse
# import os
#
# app = FastAPI()
#
# # OAuth2 configuration
# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     tokenUrl="https://accounts.google.com/o/oauth2/auth",
#     authorizationUrl="https://your-api-url.com/auth"
# )
#
# @app.get("/auth/")
# async def auth_redirect():
#     """Redirects user to Google OAuth2 for authentication."""
#     return RedirectResponse("https://accounts.google.com/o/oauth2/auth")
#
# @app.get("/verify/")
# async def verify_google_token(token: str):
#     """
#     Verifies Google OAuth2 token and restricts access to @payoda.com users.
#     """
#     idinfo = auth.verify_id_token(token)
#     email = idinfo.get("email")
#
#     if not email.endswith("@payoda.com"):
#         raise HTTPException(status_code=403, detail="Access denied")
#
#     return {"message": "Access granted", "email": email}
