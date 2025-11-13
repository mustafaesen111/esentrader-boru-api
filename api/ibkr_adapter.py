# IBKR adapter (iskelet)
# Sonra ib_insync ile dolduracağız

class IBKRBroker:
    def __init__(self, host="127.0.0.1", port=7497, client_id=1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.connected = False

    def connect(self):
        # sonraki fazlarda ib_insync ile doldurulacak
        self.connected = True
        return True

    def place_order(self, symbol, qty, side, price=None):
        # market/limit emirleri IBKR API üzerinden gönderilecek
        return {
            "status": "pending",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "price": price
        }
