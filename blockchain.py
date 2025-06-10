# Module 2 - Create a Cryptocurrency

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request # ## <-- ALTERAÇÃO: Importar 'request'
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = [] ## <-- ALTERAÇÃO: Lista para guardar transações pendentes
        self.create_block(proof = 1, previous_hash = '0')

    # ## <-- ALTERAÇÃO: O método agora aceita 'transactions' como argumento
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions ## <-- ALTERAÇÃO: Adiciona as transações ao bloco
                 }
        self.transactions = [] ## <-- ALTERAÇÃO: Limpa a lista de transações pendentes
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]
    
    # ## <-- ALTERAÇÃO: Novo método para adicionar transações
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
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

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# Creating a welcome route for the homepage
@app.route('/', methods = ['GET'])
def home():
    welcome_message = """
    <h1>Bem-vindo à API da Criptomoeda!</h1>
    <p>Endpoints disponíveis:</p>
    <ul>
        <li><b>[GET]</b> <a href="/get_chain">/get_chain</a>: Retorna a blockchain completa.</li>
        <li><b>[GET]</b> <a href="/mine_block">/mine_block</a>: Minera um novo bloco.</li>
        <li><b>[GET]</b> <a href="/is_valid">/is_valid</a>: Verifica se a blockchain é válida.</li>
        <li><b>[POST]</b> /add_transaction: Adiciona uma nova transação. (Use o Postman)</li>
    </ul>
    """
    return welcome_message, 200

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    # ## <-- ALTERAÇÃO: Adiciona uma transação de "recompensa" pela mineração
    blockchain.add_transaction(sender = node_address, receiver = 'Minerador', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Parabéns, você minerou um bloco!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']} ## <-- ALTERAÇÃO: Mostra as transações no response
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Tudo certo. A Blockchain é válida.'}
    else:
        response = {'message': 'Houston, temos um problema. A Blockchain não é válida.'}
    return jsonify(response), 200

# ## <-- ALTERAÇÃO: Endpoint inteiramente novo para adicionar transações
# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Alguns elementos da transação estão faltando', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'Esta transação será adicionada ao Bloco {index}'}
    return jsonify(response), 201

# Running the app
app.run(host = '0.0.0.0', port = 5000)
