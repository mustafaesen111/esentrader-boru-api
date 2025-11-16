from __future__ import annotations
from typing import Dict, Any, Optional, List


class IBKRBroker:
    """
    FAZ A DEMO ADAPTER
    ------------------
    - Gerçek IBKR / ib_insync bağlantısı YOK.
    - connect() çağrıldığında sadece kendini "bağlı" sayar.
    - account_info / positions / place_order sahte (dummy) veri döner.
    - Ama API ÇÖKMEZ, her zaman /api/health ve /api/ibkr/status cevap verir.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 4001, client_id: int = 1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.connected: bool = False
        self.last_error: Optional[str] = None

    # ---- Bağlantı (DEMO) ----
    def connect(self) -> Dict[str, Any]:
        """
        Gerçek bağlantı yok. Sadece "bağlı" bayrağını True yapar.
        """
        self.connected = True
        self.last_error = None
        return self.status()

    # ---- Durum ----
    def status(self) -> Dict[str, Any]:
        return {
            "ibkr_connected": self.connected,
            "host": self.host,
            "port": self.port,
            "client_id": self.client_id,
            "last_error": self.last_error,
        }

    # ---- Hesap Özeti (DEMO) ----
    def account_info(self) -> Dict[str, Any]:
        if not self.connected:
            return {
                "cash": 0.0,
                "equity": 0.0,
                "currency": "USD",
                "notes": "IBKR not connected (DEMO)",
                "last_error": self.last_error or "Not connected",
            }

        # Burayı istersen sonra gerçek IBKR verisiyle dolduracağız.
        return {
            "cash": 3200.0,
            "equity": 5380.0,
            "currency": "USD",
            "notes": "DEMO account_info (FAZ A stub)",
            "last_error": None,
        }

    # ---- Pozisyonlar (DEMO) ----
    def positions(self) -> List[Dict[str, Any]]:
        if not self.connected:
            return []

        # Örnek dummy pozisyonlar
        return [
            {
                "symbol": "GLDM",
                "qty": 10,
                "avg_price": 210.5,
                "market_price": 212.0,
                "unrealized_pnl": 15.0,
            },
            {
                "symbol": "SMH",
                "qty": 5,
                "avg_price": 240.0,
                "market_price": 238.5,
                "unrealized_pnl": -7.5,
            },
        ]

    # ---- Emir Gönderme (DEMO) ----
    def place_order(self, symbol: str, qty: float, side: str) -> Dict[str, Any]:
        """
        Gerçek emir YOK. Sadece log/response döner.
        """
        if not self.connected:
            return {
                "ok": False,
                "error": "IBKR not connected (DEMO)",
                "details": self.status(),
            }

        return {
            "ok": True,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "note": "DEMO order – Faz A stub (gerçek IBKR yok).",
        }
