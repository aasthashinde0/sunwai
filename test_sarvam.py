import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for emojis and Indic scripts
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load SARVAM_API_KEY from .env
load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")

if not api_key:
    print("Error: SARVAM_API_KEY is not set in your .env file.")
    print("Please paste your key into .env and try again.")
    sys.exit(1)

try:
    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=api_key)

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {
                "role": "system",
                "content": "You are Sunwai, an empathetic AI maths tutor for Indian school students."
            },
            {
                "role": "user",
                "content": "Hello! Can you help me understand subtraction with borrowing in 2 sentences?"
            }
        ]
    )

    content = response.choices[0].message.content
    print("\n--- Sarvam AI Response ---")
    print(content)
    print("--------------------------\n")

except Exception as e:
    print(f"Error calling Sarvam AI: {e}")
    sys.exit(1)
