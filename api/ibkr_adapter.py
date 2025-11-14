from typing import Optional, Dict, Any, List

from ib_insync import IB, Stock, MarketOrder


class IBKRBroker:
    """
    Basit, senkron IBKR adapter'i.
    - IB Gateway / TWS host:port üzerinde çalışıyorsa bağlanır.
    - Bağlantı kurulamazsa connected=False kalır; last_error içine hata yazılır.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 4001, client_id: int = 1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib: Optional[IB] = None
        self.connected: bool = False
        self.last_error: Optional[str] = None

    # ---- Dahili yardımcı ----
    def _ensure_ib(self) -> IB:
        if self.ib is None:
            self.ib = IB()
        return self.ib

    # ---- Bağlantı ----
    def connect(self) -> Dict[str, Any]:
        """
        Senkron bağlantı. Timeout kısa tutuldu (2 sn).
        Başarısız olursa exception fırlatmaz, sadece last_error'a yazar.
        """
        ib = self._ensure_ib()
        try:
            if not ib.isConnected():
                # Olası yarım bağlantıyı temizle
                ib.disconnect()
                ib.connect(self.host, self.port, clientId=self.client_id, timeout=2)

            self.connected = ib.isConnected()
            self.last_error = None
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            print(f"[IBKR] Connect error: {e}", flush=True)

        return self.status()

    # ---- Durum ----
    def status(self) -> Dict[str, Any]:
        """
        IBKR bağlantı durumunu döner.
        """
        ib = self._ensure_ib()
        self.connected = ib.isConnected()
        return {
            "ibkr_connected": self.connected,
            "host": self.host,
            "port": self.port,
            "client_id": self.client_id,
            "last_error": self.last_error,
        }

    # ---- Hesap Özeti ----
    def account_info(self) -> Dict[str, Any]:
        """
        IBKR hesap özetini döner.
        NetLiquidation, AvailableFunds, BuyingPower, CashBalance gibi alanları toplar.
        """
        ib = self._ensure_ib()

        if not ib.isConnected():
            self.connect()

        if not ib.isConnected():
            return {
                "ok": False,
                "error": "IBKR not connected",
                "details": self.status(),
            }

        try:
            accounts = ib.managedAccounts() or []
            account = accounts[0] if accounts else ""

            summary = ib.accountSummary(account)
            summary_map = {item.tag: item.value for item in summary}

            def _to_float(val: Optional[str]) -> float:
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return 0.0

            data = {
                "ok": True,
                "account": account,
                "currency": summary_map.get("Currency", "USD"),
                "net_liquidation": _to_float(summary_map.get("NetLiquidation")),
                "cash": _to_float(
                    summary_map.get("AvailableFunds")
                    or summary_map.get("CashBalance")
                ),
                "buying_power": _to_float(summary_map.get("BuyingPower")),
                "raw": summary_map,
            }
            return data

        except Exception as e:
            self.last_error = str(e)
            print(f"[IBKR] account_info error: {e}", flush=True)
            return {
                "ok": False,
                "error": str(e),
                "details": self.status(),
            }

    # ---- Pozisyonlar ----
    def positions(self) -> List[Dict[str, Any]]:
        """
        IBKR açık pozisyon listesini döner.
        Şimdilik: account, symbol, position, avgCost
        (ileride marketPrice & unrealizedPnL eklenebilir)
        """
        ib = self._ensure_ib()

        if not ib.isConnected():
            self.connect()

        if not ib.isConnected():
            # API endpoint'inde boş liste görürüz
            return []

        try:
            pos_list = []
            for p in ib.positions():
                contract = p.contract
                symbol = contract.localSymbol or contract.symbol

                pos_list.append({
                    "account": p.account,
                    "symbol": symbol,
                    "position": float(p.position),
                    "avgCost": float(p.avgCost),
                })

            return pos_list

        except Exception as e:
            self.last_error = str(e)
            print(f"[IBKR] positions error: {e}", flush=True)
            return []

    # ---- Emir gönderme (çok basit iskelet) ----
    def place_order(self, symbol: str, qty: float, side: str) -> Dict[str, Any]:
        """
        Çok basit market order iskeleti.
        - Bağlı değilse hata döner.
        - Canlı sistemde risk/limit kontrolleri ayrıca eklenecek.
        """
        ib = self._ensure_ib()

        if not ib.isConnected():
            self.connect()

        if not ib.isConnected():
            return {
                "ok": False,
                "error": "IBKR not connected",
                "details": self.status(),
            }

        try:
            contract = Stock(symbol, "SMART", "USD")
            ib.qualifyContracts(contract)

            action = side.upper()
            order = MarketOrder(action, qty)

            trade = ib.placeOrder(contract, order)
            return {
                "ok": True,
                "symbol": symbol,
                "side": action,
                "qty": qty,
                "orderId": trade.order.orderId,
            }
        except Exception as e:
            self.last_error = str(e)
            print(f"[IBKR] place_order error: {e}", flush=True)
            return {
                "ok": False,
                "error": str(e),
                "details": self.status(),
            }
