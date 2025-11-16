from flask import Flask
import requests

app = Flask(__name__)

# API aynı makinede çalışıyor
API_BASE = "http://127.0.0.1:5055"


@app.route("/")
def index():
    # Varsayılan boş değerler
    health = {}
    ibkr_status = {}
    account = {}
    positions = []
    errors = []

    # API HEALTH
    try:
        r = requests.get(f"{API_BASE}/api/health", timeout=2)
        health = r.json()
    except Exception as e:
        errors.append(f"API health hata: {e}")

    # IBKR STATUS
    try:
        r = requests.get(f"{API_BASE}/api/ibkr/status", timeout=2)
        ibkr_status = r.json()
    except Exception as e:
        errors.append(f"IBKR status hata: {e}")

    # IBKR ACCOUNT
    try:
        r = requests.get(f"{API_BASE}/api/ibkr/account", timeout=2)
        account = r.json()
    except Exception as e:
        errors.append(f"IBKR account hata: {e}")

    # IBKR POSITIONS
    try:
        r = requests.get(f"{API_BASE}/api/ibkr/positions", timeout=2)
        data = r.json()
        positions = data.get("positions", [])
    except Exception as e:
        errors.append(f"IBKR positions hata: {e}")

    # FLAG: Bağlı mı?
    connected = bool(ibkr_status.get("ibkr_connected"))

    # Pozisyon satırlarını burada hazırla (f-string içinde p.get(...) yazmayalım)
    rows = ""
    for p in positions:
        rows += (
            "<tr>"
            f"<td>{p.get('symbol')}</td>"
            f"<td>{p.get('qty')}</td>"
            f"<td>{p.get('avg_price')}</td>"
            f"<td>{p.get('market_price')}</td>"
            f"<td>{p.get('unrealized_pnl')}</td>"
            "</tr>"
        )

    # Basit HTML panel
    html = f"""
<!doctype html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <title>ESENTRADER — Basit Operasyon Paneli</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #111;
            color: #eee;
            margin: 0;
            padding: 20px;
        }}
        h1, h2, h3 {{
            margin: 0 0 10px 0;
        }}
        .api-base {{
            margin-bottom: 20px;
            color: #aaa;
        }}
        .section {{
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            background: #181818;
        }}
        .ok {{
            color: #4caf50;
            font-weight: bold;
        }}
        .bad {{
            color: #ff5252;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #333;
            padding: 6px 8px;
            text-align: left;
            font-size: 14px;
        }}
        th {{
            background: #222;
        }}
        .errors {{
            margin-top: 10px;
            color: #ff9800;
            font-size: 13px;
        }}
        .small-json {{
            font-size: 12px;
            color: #aaa;
            white-space: pre-wrap;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <h1>ESENTRADER — Basit Operasyon Paneli</h1>
    <div class="api-base">
        <strong>API_BASE:</strong> {API_BASE}
    </div>

    <div class="section">
        <h2>API HEALTH</h2>
        <div class="{ 'ok' if health.get('status') == 'ok' else 'bad' }">
            { 'OK' if health.get('status') == 'ok' else 'HATA' } — {health}
        </div>
    </div>

    <div class="section">
        <h2>IBKR BAĞLANTISI</h2>
        <div class="{ 'ok' if connected else 'bad' }">
            { 'BAĞLI' if connected else 'BAĞLI DEĞİL' }
            — host={ibkr_status.get('host')} , port={ibkr_status.get('port')} , client_id={ibkr_status.get('client_id')}
        </div>
        <div class="small-json">
            Son durum JSON: {ibkr_status}
        </div>
    </div>

    <div class="section">
        <h2>IBKR HESAP ÖZETİ</h2>
        <p>
            <strong>Equity:</strong> {account.get('equity', 0)} {account.get('currency', 'USD')}<br>
            <strong>Cash:</strong> {account.get('cash', 0)} {account.get('currency', 'USD')}<br>
        </p>
        <div class="small-json">
            Raw account JSON: {account}
        </div>
    </div>

    <div class="section">
        <h2>IBKR POZİSYONLAR</h2>
        {"<p>Hiç pozisyon yok.</p>" if not positions else
         "<table><tr><th>Sembol</th><th>Adet</th><th>Ortalama Fiyat</th><th>Piyasa Fiyatı</th><th>K/Z</th></tr>" +
         rows +
         "</table>"
        }
    </div>

    {"<div class='section errors'><h3>Hatalar</h3><ul>" +
     "".join(f"<li>{e}</li>" for e in errors) +
     "</ul></div>" if errors else ""}

</body>
</html>
"""
    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
