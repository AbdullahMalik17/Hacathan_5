import sys
from pathlib import Path
import json
import asyncio
from uuid import uuid4
from datetime import datetime
import argparse

# Add project root to python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from backend.src.services.kafka_producer import kafka_producer
from backend.src.models import MessageChannel


async def send_email_test():
    """Send test email message to Kafka."""
    message_id = str(uuid4())
    customer_email = "test.user@example.com"

    payload = {
        "channel_message_id": message_id,
        "channel": "email",
        "direction": "inbound",
        "customer_identifier": customer_email,
        "content": "I cannot login to my account. It says invalid password.",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"subject": "Login Issue"},
    }

    print(f"📧 Sending test EMAIL message: {message_id}")

    await kafka_producer.publish(
        topic="fte.tickets.incoming", message=payload, key=customer_email
    )
    print("✅ Email message sent successfully!")
    print("Check your worker terminal for processing logs.")


async def send_whatsapp_test():
    """Send test WhatsApp message to Kafka."""
    message_id = f"SM{uuid4().hex[:32]}"  # Twilio SID format
    customer_phone = "+14155551234"

    payload = {
        "channel": "whatsapp",
        "channel_message_id": message_id,
        "sender": {
            "phone": customer_phone,
            "name": "Test User",
            "wa_id": customer_phone.replace("+", ""),
        },
        "content": "What are your business hours?",
        "metadata": {"num_media": 0, "to": "whatsapp:+14155238886"},
    }

    print(f"💬 Sending test WHATSAPP message: {message_id}")

    await kafka_producer.publish(
        topic="fte.channels.whatsapp.inbound", message=payload, key=customer_phone
    )
    print("✅ WhatsApp message sent successfully!")
    print("Check your worker terminal for processing logs.")


async def main():
    parser = argparse.ArgumentParser(description="Send test messages to Kafka")
    parser.add_argument(
        "--channel",
        choices=["email", "whatsapp", "both"],
        default="both",
        help="Channel to test (default: both)",
    )
    args = parser.parse_args()

    print("Initializing Kafka producer...")
    kafka_producer.connect()

    try:
        if args.channel in ["email", "both"]:
            await send_email_test()
            print()

        if args.channel in ["whatsapp", "both"]:
            await send_whatsapp_test()
            print()

    except Exception as e:
        print(f"❌ Failed to send message: {e}")
    finally:
        kafka_producer.disconnect()
        print("✅ Kafka producer closed")


if __name__ == "__main__":
    asyncio.run(main())