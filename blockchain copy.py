# Module 2 - Create a Cryptocurrency

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]
    
    # ## <-- ALTERAÇÃO 1: Método agora aceita um dicionário de transação
    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

# Part 2 - Mining our Blockchain
app = Flask(__name__)
node_address = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/', methods = ['GET'])
def home():
    return """
    <h1>Bem-vindo à API da Criptomoeda!</h1>
    <p>Endpoints disponíveis:</p>
    <ul>
        <li><b>[GET]</b> <a href="/get_chain">/get_chain</a>: Retorna a blockchain completa.</li>
        <li><b>[GET]</b> <a href="/mine_block">/mine_block</a>: Minera um novo bloco.</li>
        <li><b>[GET]</b> <a href="/is_valid">/is_valid</a>: Verifica se a blockchain é válida.</li>
        <li><b>[POST]</b> /add_transaction: Adiciona uma nova transação. (Use o Postman)</li>
    </ul>
    """

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(transaction = {'from': 'network', 'to': node_address, 'reward': 1})
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Parabéns, você minerou um bloco!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Tudo certo. A Blockchain é válida.'}
    else:
        response = {'message': 'Houston, temos um problema. A Blockchain não é válida.'}
    return jsonify(response), 200

# ## <-- ALTERAÇÃO 2: Endpoint modificado para extrair dados do seu JSON
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    received_json = request.get_json()
    
    if not received_json or 'id' not in received_json or 'converter' not in received_json:
        return 'JSON inválido ou faltando chaves essenciais como "id" ou "converter"', 400

    converter_data = received_json.get('converter', {})
    
    transaction_data = {
        'task_id': received_json.get('id'),
        'task_name': received_json.get('name'),
        'task_engine': received_json.get('engine'),
        'converter_id': converter_data.get('id'),
        'converter_code': converter_data.get('code'),
        'converter_name': converter_data.get('name'),
    }
    
    index = blockchain.add_transaction(transaction_data)
    response = {'message': f'Os dados extraídos da tarefa serão adicionados ao Bloco {index}'}
    return jsonify(response), 201

# Running the app
app.run(host = '0.0.0.0', port = 5000)
