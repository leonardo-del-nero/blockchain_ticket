# cryptocurrency/main.py

from flask import Flask
from blockchain import Blockchain  # <-- ALTERAÇÃO AQUI
from views import api_blueprint, set_blockchain

# 1. Cria a instância da aplicação Flask
app = Flask(__name__)

# 2. Cria a instância do Blockchain
blockchain_instance = Blockchain()

# 3. Injeta a instância do blockchain no blueprint das rotas
#    Isso permite que as rotas em 'views.py' acessem o mesmo objeto blockchain.
set_blockchain(blockchain_instance)

# 4. Registra o blueprint na aplicação Flask
#    Todas as rotas definidas em 'api_blueprint' agora fazem parte da aplicação.
app.register_blueprint(api_blueprint)

# 5. Executa a aplicação
if __name__ == '__main__':
    # O host '0.0.0.0' torna a aplicação acessível na sua rede local.
    app.run(host='0.0.0.0', port=5000, debug=True)
    