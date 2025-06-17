# cryptocurrency/main.py

from flask import Flask
from argparse import ArgumentParser # <-- 1. IMPORTE ArgumentParser
from blockchain import Blockchain
from views import api_blueprint, set_blockchain

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Cria a instância do Blockchain
blockchain_instance = Blockchain()

# Injeta a instância do blockchain no blueprint das rotas
set_blockchain(blockchain_instance)

# Registra o blueprint na aplicação Flask
app.register_blueprint(api_blueprint)

# 2. MODIFIQUE O BLOCO DE EXECUÇÃO
if __name__ == '__main__':
    # Configura o parser para aceitar argumentos de linha de comando
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='Porta para escutar')
    args = parser.parse_args()
    port = args.port

    # O host '0.0.0.0' torna a aplicação acessível na sua rede local.
    app.run(host='0.0.0.0', port=port, debug=True)
    