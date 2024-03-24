import os
from twilio.rest import Client
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Get account SID and auth token from environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Create Twilio client
client = Client(account_sid, auth_token)

message = client.messages.create(
    body="This is the ship that made the Kessel Run in fourteen parsecs?",
    from_="+13238798975",
    to="+13233330336",
)
print(message)
