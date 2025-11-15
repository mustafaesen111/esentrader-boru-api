from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# API, aynı VPS üzerinde 5055 portunda
API_BASE = "http://127.0.0.1:5055"


def fetch_json(path: str, timeout: float = 2.0):
    """
    Küçük yardımcı:
    - GET isteği atar
    - JSON dönerse (dict) onu döndürür, hata yoksa error=None
    - Hata varsa data=None, error=str(e)
    """
    try:
        resp = requests.get(f"{API_BASE}{path}", timeout=timeout)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)


TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <title>ESENTRADER — Basit Operasyon Paneli</title>
    <style>
        body {
            background: #020617;
            color: #e5e7eb;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 24px;
        }
        .shell {
            max-width: 900px;
            margin: 0 auto;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 8px;
        }
        .subtitle {
            font-size: 13px;
            color: #9ca3af;
            margin-bottom: 24px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }
        .card {
            background: #020617;
            border-radius: 12px;
            border: 1px solid #1f2937;
            padding: 16px 18px;
        }
        .tag {
            font-size: 11px;
            text-transform: uppercase;
            color: #9ca3af;
            letter-spacing: 0.12em;
            margin-bottom: 6px;
        }
        .title {
            font-size: 16px;
            margin-bottom: 8px;
        }
        .status {
            font-size: 14px;
            margin-bottom: 4px;
        }
        .ok {
            color: #4ade80;
            font-weight: 600;
        }
        .bad {
            color: #f97373;
            font-weight: 600;
        }
        .small {
            font-size: 12px;
            color: #9ca3af;
            margin-top: 4px;
            word-break: break-all;
        }
        footer {
            margin-top: 24px;
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.16em;
        }
        @media (max-width: 800px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
<div class="shell">
    <h1>ESENTRADER — Operasyon Paneli (Basit Versiyon)</h1>
    <div class="subtitle">
        Bu sayfa doğrudan aynı VPS üzerindeki Tek Boru API'den veri çekiyor:
        <b>{{ api_base }}</b>
    </div>

    <div class="grid">
        <!-- API HEALTH KARTI -->
        <div class="card">
            <div class="tag">Durum</div>
            <div class="title">API Health</div>

            {% if api_health %}
                <div class="status">
                    <span class="ok">YEŞİL</span> — API cevap veriyor.
                </div>
                <div class="small">
                    JSON: {{ api_health }}
                </div>
            {% else %}
                <div class="status">
                    <span class="bad">KIRMIZI</span> — API'ye ulaşılamıyor.
                </div>
                {% if api_error %}
                    <div class="small">
                        Hata: {{ api_error }}
                    </div>
                {% endif %}
            {% endif %}
        </div>

        <!-- IBKR STATUS KARTI -->
        <div class="card">
            <div class="tag">IBKR</div>
            <div class="title">IBKR Bağlantısı</div>

            {% if ibkr_status and ibkr_status.ibkr_connected %}
                <div class="status">
                    <span class="ok">YEŞİL</span> — IBKR adapter bağlı görünüyor.
                </div>
                <div class="small">
                    JSON: {{ ibkr_status }}
                </div>
            {% elif ibkr_status %}
                <div class="status">
                    <span class="bad">KIRMIZI</span> — IBKR adapter bağlı değil.
                </div>
                <div class="small">
                    JSON: {{ ibkr_status }}
                </div>
            {% else %}
                <div class="status">
                    <span class="bad">KIRMIZI</span> — /api/ibkr/status erişilemedi.
                </div>
                {% if ibkr_error %}
                    <div class="small">
                        Hata: {{ ibkr_error }}
                    </div>
                {% endif %}
            {% endif %}
        </div>
    </div>

    <footer>
        Sayfayı F5 ile yenileyerek değerleri tekrar çekebilirsin.
    </footer>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    # /api/health
    api_health, api_error = fetch_json("/api/health")

    # /api/ibkr/status
    ibkr_status, ibkr_error = fetch_json("/api/ibkr/status")

    # ibkr_status dict ise Jinja'da .ibkr_connected diye erişebilmek için
    # SimpleNamespace'e çevirelim
    from types import SimpleNamespace
    if isinstance(ibkr_status, dict):
        ibkr_status = SimpleNamespace(**ibkr_status)

    return render_template_string(
        TEMPLATE,
        api_base=API_BASE,
        api_health=api_health,
        api_error=api_error,
        ibkr_status=ibkr_status,
        ibkr_error=ibkr_error,
    )


if __name__ == "__main__":
    # 8000 portunda web arayüzü
    app.run(host="0.0.0.0", port=8000, debug=True)
