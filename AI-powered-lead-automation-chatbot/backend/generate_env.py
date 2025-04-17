# generate_env.py

env_content = """
# Email credentials
SENDER_EMAIL="Your_Email"
SENDER_PASSWORD="Your_Email_password"
RECEIVER_EMAIL="Receiver_Email"

# HubSpot API key
HUBSPOT_API_KEY="API_Key_From HUBSPOT"
""".strip()

with open(".env", "w") as f:
    f.write(env_content)

print("✅ .env file created successfully!")
