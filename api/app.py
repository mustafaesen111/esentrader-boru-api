from flask import Flask, request, jsonify

app = Flask(__name__)


# ------- Healthcheck -------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "esentrader-boru-api"})


# ------- Manual Test Endpoint -------
@app.route("/api/test", methods=["POST"])
def test_order():
    data = request.json
    return jsonify({"received": data})


# ------- TradingView Signal Processor (şimdilik iskelet) -------
def process_tradingview_signal(payload: dict) -> dict:
    """
    Burada gelen TradingView webhook datasını normalize ediyoruz.
    İleride buradan copy_engine / IBKR / Binance adapter'ına göndereceğiz.
    Şimdilik sadece log + parse.
    """

    # TradingView'den gelebilecek olası alan isimleri:
    symbol = (
        payload.get("symbol")
        or payload.get("ticker")
        or payload.get("SYMBOL")
    )
    side = (
        payload.get("side")
        or payload.get("action")
        or payload.get("SIDE")
        or payload.get("direction")
    )
    note = payload.get("note") or payload.get("comment") or payload.get("NOTE")
    mode = payload.get("mode") or payload.get("MODE") or "usd"

    qty = payload.get("qty") or payload.get("quantity")
    usd = payload.get("usd") or payload.get("amount_usd") or payload.get("AMOUNT_USD")

    # Şimdilik sadece loglayalım (ileride burada order-router'a paslayacağız)
    print("[TV SIGNAL RAW] ", payload, flush=True)
    print("[TV SIGNAL PARSED] symbol=", symbol, "side=", side, "mode=", mode, "qty=", qty, "usd=", usd, flush=True)

    return {
        "symbol": symbol,
        "side": side,
        "mode": mode,
        "qty": qty,
        "usd": usd,
        "note": note,
    }


# ------- /alert (ana TradingView webhook endpoint'i) -------
@app.route("/alert", methods=["POST"])
def alert():
    payload = request.get_json(force=True, silent=True) or {}

    parsed = process_tradingview_signal(payload)

    # Şimdilik sadece geri dönüyoruz.
    # Bir sonraki adımda burada copy_engine'e / broker adapter'ına çağrı ekleyeceğiz.
    return jsonify({
        "status": "ok",
        "source": "tradingview",
        "received": payload,
        "parsed": parsed,
    })


# ------- /signal (TradingView'deki eski URL için alias) -------
@app.route("/signal", methods=["POST"])
def signal_alias():
    """
    TradingView tarafında webhook URL'in /signal ise,
    burası /alert ile aynı işlevi görür.
    """
    return alert()


if __name__ == "__main__":
    # Port'u şimdilik 5055'te bırakıyoruz.
    # Dışarıdan erişirken: http://SUNUCU_IP:5055/alert veya /signal
    app.run(host="0.0.0.0", port=5055, debug=True)
