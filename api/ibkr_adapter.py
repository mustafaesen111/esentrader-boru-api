# api/ibkr_adapter.py

from ib_insync import IB, Stock, MarketOrder


class IBKRBroker:
    """
    IBKR tarafı için tek boru adapter'i.
    - connect()  : TWS / Gateway'e bağlanır
    - account_info(): hesap özeti (NetLiquidation, Cash vs.)
    - positions(): açık pozisyonlar
    - place_order(): market BUY/SELL emri gönderir (REAL hesapta da geçerlidir)
    """

    def __init__(self, host="127.0.0.1", port=7496, client_id=1, master_account=None):
        """
        host          : TWS / IB Gateway IP
        port          : REAL TWS genelde 7496 (paper 7497)
        client_id     : Aynı makinede her uygulama için farklı olmalı
        master_account: Varsa ana hesap ID'si (Uxxxxxx). Yoksa managedAccounts()[0] kullanılır.
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.master_account = master_account  # birden fazla hesabın varsa bunu sonra set edebiliriz

    # ------------- Bağlantı -------------
    def connect(self) -> bool:
        """
        Bağlı değilse IBKR'a bağlanır, True/False döner.
        İlk bağlantıda managedAccounts() listesinden master_account seçer.
        """
        if not self.ib.isConnected():
            try:
                self.ib.connect(self.host, self.port, clientId=self.client_id)
                print(f"[IBKR] Bağlandı: {self.host}:{self.port} clientId={self.client_id}")

                # Eğer master_account set edilmemişse, ilk hesabı ana hesap olarak al
                if not self.master_account:
                    accounts = self.ib.managedAccounts()
                    if accounts:
                        self.master_account = accounts[0]
                        print(f"[IBKR] master_account = {self.master_account}")
            except Exception as e:
                print("[IBKR] Bağlanamadı:", e)
        return self.ib.isConnected()

    # ------------- Hesap Özeti -------------
    def account_info(self):
        """
        Hesap özetini (equity, cash vs.) döndürür.
        """
        if not self.connect():
            return {"error": "IBKR bağlantısı yok"}

        summary = self.ib.accountSummary()
        data = {}
        for item in summary:
            # Örnek: NetLiquidation_USD: 5380.00
            key = f"{item.tag}_{item.currency}" if item.currency else item.tag
            data[key] = item.value
        return data

    # ------------- Pozisyonlar -------------
    def positions(self):
        """
        Açık pozisyonları döndürür.
        """
        if not self.connect():
            return {"error": "IBKR bağlantısı yok"}

        positions = self.ib.positions()
        out = []
        for p in positions:
            c = p.contract
            out.append({
                "account": p.account,
                "symbol": c.symbol,
                "secType": c.secType,
                "currency": c.currency,
                "exchange": getattr(c, "exchange", ""),
                "position": float(p.position),
                "avgCost": float(p.avgCost),
            })
        return out

    # ------------- Emir Gönderme -------------
    def place_order(self, symbol: str, qty: float, side: str, account: str = None):
        """
        REAL hesapta çalışan market BUY/SELL emri.
        - symbol: "AAPL", "GLD", "NVDA" vb.
        - qty   : adet (pozitif sayı)
        - side  : "BUY" veya "SELL"
        - account: İsteğe bağlı; boşsa master_account veya IB default hesabı kullanılır.
        """
        if not self.connect():
            return {"ok": False, "error": "IBKR bağlantısı yok"}

        if not symbol:
            return {"ok": False, "error": "symbol boş"}
        try:
            qty = float(qty)
        except Exception:
            return {"ok": False, "error": f"qty sayıya çevrilemedi: {qty}"}
        if qty <= 0:
            return {"ok": False, "error": f"qty pozitif olmalı: {qty}"}

        action = "BUY" if str(side).upper() == "BUY" else "SELL"

        # Sadece hisse senedi için temel Stock kontratı.
        # İleride future/opsiyon ekleriz.
        contract = Stock(symbol, "SMART", "USD")

        order = MarketOrder(action, qty)

        # Birden fazla hesabın varsa ve master_account doluysa,
        # IBKR emrini o hesaba yaz.
        final_account = account or self.master_account
        if final_account:
            order.account = final_account

        print(f"[IBKR] EMIR: {action} {qty} x {symbol} account={getattr(order, 'account', None)}", flush=True)

        try:
            trade = self.ib.placeOrder(contract, order)
            # OrderID ve status'in dolması için çok kısa bekletiyoruz
            self.ib.sleep(1.0)

            order_id = getattr(trade.order, "orderId", None)
            status = getattr(trade.orderStatus, "status", None)

            print(f"[IBKR] EMIR GÖNDERİLDİ: orderId={order_id}, status={status}", flush=True)

            return {
                "ok": True,
                "orderId": order_id,
                "status": status,
                "symbol": symbol,
                "side": action,
                "qty": qty,
                "account": getattr(order, "account", None),
            }
        except Exception as e:
            print("[IBKR] EMIR HATASI:", e, flush=True)
            return {"ok": False, "error": str(e)}
