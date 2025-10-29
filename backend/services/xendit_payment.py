"""
Xendit Payment Gateway Service
Miluv.app - Untuk Consultation Payment
"""

import os
import requests
import hashlib
import hmac
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class XenditPaymentService:
    """Service untuk Xendit Payment Gateway"""
    
    def __init__(self):
        self.secret_key = os.getenv('XENDIT_SECRET_KEY')
        self.public_key = os.getenv('XENDIT_PUBLIC_KEY')
        self.webhook_token = os.getenv('XENDIT_WEBHOOK_TOKEN')
        self.base_url = "https://api.xendit.co"
        
    def create_invoice(
        self,
        external_id: str,
        amount: float,
        payer_email: str,
        description: str,
        success_redirect_url: Optional[str] = None,
        failure_redirect_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Buat invoice untuk pembayaran consultation
        
        Args:
            external_id: Unique ID dari sistem Anda (consultation_id)
            amount: Jumlah pembayaran dalam Rupiah
            payer_email: Email user yang bayar
            description: Deskripsi pembayaran
            success_redirect_url: URL redirect jika berhasil
            failure_redirect_url: URL redirect jika gagal
            
        Returns:
            {
                "invoice_id": str,
                "invoice_url": str,
                "status": str,
                "expiry_date": str
            }
        """
        try:
            url = f"{self.base_url}/v2/invoices"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "external_id": external_id,
                "amount": amount,
                "payer_email": payer_email,
                "description": description,
                "invoice_duration": 86400,  # 24 jam
                "success_redirect_url": success_redirect_url or f"miluv://payment/success?invoice_id={external_id}",
                "failure_redirect_url": failure_redirect_url or f"miluv://payment/failed?invoice_id={external_id}",
                "currency": "IDR",
                "items": [
                    {
                        "name": description,
                        "quantity": 1,
                        "price": amount
                    }
                ]
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                auth=(self.secret_key, '')
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "invoice_id": data['id'],
                    "invoice_url": data['invoice_url'],
                    "external_id": data['external_id'],
                    "status": data['status'],
                    "amount": data['amount'],
                    "expiry_date": data['expiry_date'],
                    "payment_methods": data.get('available_banks', [])
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get('message', 'Failed to create invoice'),
                    "error_code": response.json().get('error_code')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating invoice: {str(e)}"
            }
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Cek status invoice
        
        Args:
            invoice_id: Xendit invoice ID
            
        Returns:
            Invoice details dengan status terbaru
        """
        try:
            url = f"{self.base_url}/v2/invoices/{invoice_id}"
            
            response = requests.get(
                url,
                auth=(self.secret_key, '')
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "invoice_id": data['id'],
                    "external_id": data['external_id'],
                    "status": data['status'],  # PENDING, PAID, EXPIRED, SETTLED
                    "amount": data['amount'],
                    "paid_amount": data.get('paid_amount', 0),
                    "payment_method": data.get('payment_method'),
                    "payment_channel": data.get('payment_channel'),
                    "paid_at": data.get('paid_at')
                }
            else:
                return {
                    "success": False,
                    "error": "Invoice not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook_signature(
        self,
        callback_token: str,
        webhook_data: Dict[str, Any]
    ) -> bool:
        """
        Verifikasi webhook dari Xendit
        
        Args:
            callback_token: Token dari header X-CALLBACK-TOKEN
            webhook_data: Data webhook dari Xendit
            
        Returns:
            True jika valid, False jika tidak
        """
        # Xendit menggunakan callback token untuk verifikasi
        return callback_token == self.webhook_token
    
    def create_payment_link(
        self,
        amount: float,
        description: str,
        reference_id: str
    ) -> Dict[str, Any]:
        """
        Buat payment link untuk metode alternatif
        
        Args:
            amount: Jumlah pembayaran
            description: Deskripsi
            reference_id: Reference ID unik
            
        Returns:
            Payment link details
        """
        try:
            url = f"{self.base_url}/payment_links"
            
            payload = {
                "amount": amount,
                "description": description,
                "reference_id": reference_id,
                "currency": "IDR"
            }
            
            response = requests.post(
                url,
                json=payload,
                auth=(self.secret_key, '')
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "payment_link_id": data['id'],
                    "payment_link_url": data['payment_link_url'],
                    "reference_id": data['reference_id'],
                    "status": data['status']
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get('message', 'Failed to create payment link')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
xendit_service = XenditPaymentService()


# Mock function untuk testing
def mock_create_invoice(
    external_id: str,
    amount: float,
    payer_email: str,
    description: str
) -> Dict[str, Any]:
    """
    Mock function untuk testing tanpa Xendit credentials
    """
    import uuid
    
    mock_invoice_id = f"mock-inv-{uuid.uuid4().hex[:8]}"
    
    return {
        "success": True,
        "invoice_id": mock_invoice_id,
        "invoice_url": f"https://checkout.xendit.co/web/{mock_invoice_id}",
        "external_id": external_id,
        "status": "PENDING",
        "amount": amount,
        "expiry_date": datetime.now().isoformat(),
        "payment_methods": ["BCA", "MANDIRI", "BNI", "BRI", "GOPAY", "OVO"],
        "mock": True
    }


def mock_get_invoice_status(invoice_id: str) -> Dict[str, Any]:
    """
    Mock function untuk cek status pembayaran
    """
    return {
        "success": True,
        "invoice_id": invoice_id,
        "status": "PAID",  # Simulate payment success
        "amount": 150000,
        "paid_amount": 150000,
        "payment_method": "EWALLET",
        "payment_channel": "GOPAY",
        "paid_at": datetime.now().isoformat(),
        "mock": True
    }
