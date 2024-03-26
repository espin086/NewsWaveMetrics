from twilio.rest import Client
from dotenv import load_dotenv
import os

import config


# Load environment variables from .env file
load_dotenv()

# Get account SID and auth token from environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Create Twilio client
client = Client(account_sid, auth_token)


def send_sms(message, to_number=config.ALERT_PHONE_NUMBER):
    """
    Send SMS to a phone number using Twilio API
    """
    message = client.messages.create(
        body=message, from_=config.TWILIO_PHONE_NUMBER, to=to_number
    )
    print(f"Message sent to {to_number} with SID: {message.sid}")


if __name__ == "__main__":
    # Send SMS to a phone number
    send_sms(message="Have a good day Jackie! This is Python saying hello!")
