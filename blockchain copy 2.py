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
        self.create_block(proof=1, previous_hash='0')

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
        encoded_block = json.dumps(block, sort_keys=True).encode()
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

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
    <head>
        <title>Criptomoeda API</title>
        <style>
            body { font-family: Arial; background: #f9f9f9; padding: 20px; }
            h1 { color: #333; }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                margin: 5px;
                border: none;
                cursor: pointer;
                font-size: 16px;
                border-radius: 5px;
            }
            button:hover {
                background-color: #45a049;
            }
            .btn-link {
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <h1>Bem-vindo à API da Criptomoeda!</h1>
        <p>Clique nos botões para executar ações:</p>
        <a href="/get_chain" class="btn-link"><button>🔗 Ver Blockchain</button></a>
        <a href="/mine_block" class="btn-link"><button>⛏️ Minerar Bloco</button></a>
        <a href="/is_valid" class="btn-link"><button>✅ Verificar Blockchain</button></a>
        <p>Para adicionar transações, use um cliente como o Postman para enviar uma requisição <b>POST</b> para <code>/add_transaction</code>.</p>
    </body>
    </html>
    """

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(transaction={'from': 'network', 'to': node_address, 'reward': 1})
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

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Tudo certo. A Blockchain é válida.'}
    else:
        response = {'message': 'Houston, temos um problema. A Blockchain não é válida.'}
    return jsonify(response), 200
