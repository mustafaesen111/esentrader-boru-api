from flask import Flask, jsonify, request
from ibkr_adapter import IBKRBroker

app = Flask(__name__)

# Tek boru: Şimdilik sadece IBKR DEMO adapter
ibkr_broker = IBKRBroker()


# ------- Healthcheck -------
@app.route("/api/health", methods=["GET"])
def health():
    """
    API'nin ayakta olup olmadığını döner.
    """
    return jsonify({
        "status": "ok",
        "service": "esentrader-boru-api"
    })


# ------- IBKR Status (DEMO) -------
@app.route("/api/ibkr/status", methods=["GET"])
def ibkr_status():
    """
    IBKR DEMO adapter durumunu döner.
    connect() sadece self.connected=True yapar.
    """
    status = ibkr_broker.connect()
    return jsonify(status)


# ------- IBKR Account (DEMO) -------
@app.route("/api/ibkr/account", methods=["GET"])
def ibkr_account():
    """
    IBKR DEMO hesap özeti.
    """
    ibkr_broker.connect()
    data = ibkr_broker.account_info()
    return jsonify(data)


# ------- IBKR Positions (DEMO) -------
@app.route("/api/ibkr/positions", methods=["GET"])
def ibkr_positions():
    """
    IBKR DEMO pozisyon listesi.
    """
    ibkr_broker.connect()
    positions = ibkr_broker.positions()
    return jsonify({"positions": positions})


# ------- Basit Test Endpoint -------
@app.route("/api/test", methods=["POST"])
def api_test():
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify({
        "status": "ok",
        "echo": payload,
    })


if __name__ == "__main__":
    # Debug kapalı, tek process, port çakışma derdi yok.
    app.run(host="0.0.0.0", port=5055, debug=False)
