"""
OTP Generator and Validation

Simulates OTP generation and validation for care context linking.
In production, this would integrate with SMS/email services.
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict


class OTPManager:
    """
    Manages OTP generation and validation.

    In development mode, stores OTPs in memory.
    In production, would use Redis or similar.
    """

    def __init__(self):
        self._otps: Dict[str, Dict] = {}  # link_reference -> {otp, expires_at, attempts}

    def generate_otp(self, link_reference: str, patient_identifier: str) -> str:
        """
        Generate a 6-digit OTP for care context linking.

        Args:
            link_reference: Unique link reference ID
            patient_identifier: Patient identifier (phone/ABHA)

        Returns:
            6-digit OTP
        """
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store with expiry (5 minutes)
        self._otps[link_reference] = {
            "otp": otp,
            "otp_hash": self._hash_otp(otp),
            "patient_identifier": patient_identifier,
            "expires_at": datetime.now() + timedelta(minutes=5),
            "attempts": 0,
            "verified": False
        }

        return otp

    def verify_otp(self, link_reference: str, otp: str) -> bool:
        """
        Verify OTP for a link reference.

        Args:
            link_reference: Link reference ID
            otp: OTP to verify

        Returns:
            True if OTP is valid and not expired
        """
        if link_reference not in self._otps:
            return False

        otp_data = self._otps[link_reference]

        # Check if already verified
        if otp_data["verified"]:
            return False

        # Check if expired
        if datetime.now() > otp_data["expires_at"]:
            return False

        # Check attempts (max 3)
        otp_data["attempts"] += 1
        if otp_data["attempts"] > 3:
            return False

        # Verify OTP
        if self._hash_otp(otp) == otp_data["otp_hash"]:
            otp_data["verified"] = True
            return True

        return False

    def get_otp_status(self, link_reference: str) -> Optional[Dict]:
        """
        Get OTP status for a link reference.

        Args:
            link_reference: Link reference ID

        Returns:
            OTP status dict or None
        """
        if link_reference not in self._otps:
            return None

        otp_data = self._otps[link_reference]
        return {
            "verified": otp_data["verified"],
            "expired": datetime.now() > otp_data["expires_at"],
            "attempts": otp_data["attempts"],
            "remaining_attempts": max(0, 3 - otp_data["attempts"])
        }

    def cleanup_expired(self):
        """Remove expired OTPs from memory."""
        now = datetime.now()
        expired_refs = [
            ref for ref, data in self._otps.items()
            if now > data["expires_at"]
        ]

        for ref in expired_refs:
            del self._otps[ref]

    def _hash_otp(self, otp: str) -> str:
        """Hash OTP for secure storage."""
        return hashlib.sha256(otp.encode()).hexdigest()

    def get_otp_for_dev(self, link_reference: str) -> Optional[str]:
        """
        DEV ONLY: Get OTP for testing.

        In production, OTPs would be sent via SMS/email.

        Args:
            link_reference: Link reference ID

        Returns:
            OTP or None
        """
        if link_reference in self._otps:
            return self._otps[link_reference]["otp"]
        return None


# Global OTP manager instance
otp_manager = OTPManager()
