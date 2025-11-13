# Binance adapter (iskelet)
# İleride gerçek trade fonksiyonlarını ekleyeceğiz

class BinanceBroker:
    def __init__(self, api_key="", api_secret=""):
        self.api_key = api_key
        self.api_secret = api_secret

    def place_order(self, symbol, qty, side, price=None):
        return {
            "status": "pending",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "price": price
        }
