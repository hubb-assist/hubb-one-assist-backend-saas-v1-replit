"""
Script simples para resolver o problema de deploy com o Replit
Fornece uma resposta para o health check da rota raiz ("/")
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    """Endpoint raiz para health checks."""
    return jsonify({
        "status": "online",
        "version": "0.1.0",
        "app": "HUBB ONE Assist API"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)