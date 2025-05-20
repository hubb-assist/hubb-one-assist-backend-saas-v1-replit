"""
Aplicação Flask simples para health checks
Esta aplicação é apenas para passar no health check do deploy do Replit
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health():
    """Endpoint para health check"""
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)