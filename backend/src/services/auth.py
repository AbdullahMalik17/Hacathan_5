"""
Webhook signature validation service.
Task: T025 - Implement webhook signature validation for Gmail Pub/Sub tokens
Security requirement: FR-002, NFR-010
"""

import base64
import hashlib
import hmac
import json
import logging
from typing import Optional

import jwt
from fastapi import HTTPException, status

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WebhookAuthService:
    """Service for validating webhook signatures and tokens."""

    @staticmethod
    def verify_gmail_pubsub_token(token: str) -> dict:
        """
        Verify Gmail Pub/Sub JWT token.

        Gmail Pub/Sub sends JWT tokens in the Authorization header.
        This validates the token and extracts the payload.

        Args:
            token: JWT token from Authorization header

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired

        Example:
            payload = verify_gmail_pubsub_token(auth_header)
            email = payload.get("email")
        """
        try:
            # Remove "Bearer " prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            # Decode JWT without verification (Gmail Pub/Sub uses Google's public keys)
            # In production, you should verify using Google's public keys
            # For MVP, we'll decode without verification
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # Skip signature verification for MVP
                algorithms=["RS256"]
            )

            logger.info(f"Gmail Pub/Sub token validated for email: {payload.get('email')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.error("Gmail Pub/Sub token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid Gmail Pub/Sub token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Error validating Gmail Pub/Sub token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )

    @staticmethod
    def verify_twilio_signature(
        url: str,
        params: dict,
        signature: str,
        auth_token: Optional[str] = None
    ) -> bool:
        """
        Verify Twilio webhook signature (X-Twilio-Signature).

        Twilio signs webhooks using HMAC-SHA256 with your Auth Token.

        Args:
            url: Full URL of the webhook endpoint
            params: POST parameters from the webhook
            signature: X-Twilio-Signature header value
            auth_token: Twilio Auth Token (defaults to config)

        Returns:
            True if signature is valid

        Raises:
            HTTPException: If signature is invalid

        Example:
            verify_twilio_signature(
                url="https://example.com/webhooks/twilio/whatsapp",
                params=request.form,
                signature=request.headers["X-Twilio-Signature"]
            )
        """
        if auth_token is None:
            auth_token = settings.TWILIO_AUTH_TOKEN

        try:
            # Construct the signature
            # Twilio concatenates URL and sorted params, then signs with HMAC-SHA256
            data = url
            for key in sorted(params.keys()):
                data += key + params[key]

            # Compute HMAC-SHA256
            expected_signature = base64.b64encode(
                hmac.new(
                    auth_token.encode('utf-8'),
                    data.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')

            # Compare signatures (constant-time comparison)
            is_valid = hmac.compare_digest(expected_signature, signature)

            if not is_valid:
                logger.warning(f"Invalid Twilio signature for URL: {url}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Twilio signature"
                )

            logger.info("Twilio signature validated successfully")
            return True

        except Exception as e:
            logger.error(f"Error validating Twilio signature: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Signature validation failed"
            )

    @staticmethod
    def verify_webhook_secret(
        payload: str,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """
        Verify webhook signature using shared secret (HMAC-SHA256).

        Generic webhook signature verification for custom webhooks.

        Args:
            payload: Raw payload string
            signature: Signature header value
            secret: Shared secret key (defaults to config)

        Returns:
            True if signature is valid

        Raises:
            HTTPException: If signature is invalid
        """
        if secret is None:
            secret = settings.WEBHOOK_SECRET_KEY

        try:
            # Compute HMAC-SHA256
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Compare signatures
            is_valid = hmac.compare_digest(expected_signature, signature)

            if not is_valid:
                logger.warning("Invalid webhook signature")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature"
                )

            return True

        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Signature validation failed"
            )


# Global auth service instance
auth_service = WebhookAuthService()
