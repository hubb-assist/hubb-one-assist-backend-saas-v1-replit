"""
Arquivo principal Flask para resolver problemas de deploy com o Replit
"""
from flask import Flask, jsonify, redirect

app = Flask(__name__)

@app.route('/')
def home():
    """Endpoint raiz para health checks."""
    return jsonify({
        "status": "online",
        "version": "0.1.0",
        "app": "HUBB ONE Assist API"
    })

@app.route('/api/<path:path>')
def api_proxy(path):
    """
    Redireciona todas as chamadas da API para a aplicação principal.
    """
    return jsonify({"message": "API em manutenção", "path": path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)