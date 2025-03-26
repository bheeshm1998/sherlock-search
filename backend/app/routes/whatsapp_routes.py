# from fastapi import APIRouter, Request, HTTPException
# import requests
# import os
#
# router = APIRouter()
#
# # Load environment variables
# WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
# WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
# WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
#
#
# @router.post("/whatsapp/webhook/")
# async def whatsapp_webhook(request: Request):
#     """
#     Receives incoming WhatsApp messages and responds accordingly.
#     """
#     data = await request.json()
#
#     try:
#         # Check if this is a valid WhatsApp event
#         if "entry" in data:
#             for entry in data["entry"]:
#                 for change in entry["changes"]:
#                     if "messages" in change["value"]:
#                         for message in change["value"]["messages"]:
#                             sender_id = message["from"]  # Sender's phone number
#                             text = message.get("text", {}).get("body", "")
#
#                             # Reply to the user
#                             send_whatsapp_message(sender_id, f"Hello! You said: {text}")
#
#         return {"status": "ok"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# def send_whatsapp_message(to: str, message: str):
#     """
#     Sends a message via WhatsApp Cloud API.
#     """
#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "text": {"body": message}
#     }
#
#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     return response.json()
