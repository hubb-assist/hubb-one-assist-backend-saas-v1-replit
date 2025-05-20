"""
Aplicação simples para health checks
Esta aplicação Flask é usada apenas para verificação de saúde.
A API real FastAPI continua disponível em porta diferente.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health_check():
    """
    Endpoint de health check simples para o deploy
    """
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)