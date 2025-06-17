# cryptocurrency/blockchain.py

import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse

class Blockchain:
    """
    Classe que representa a estrutura e as operações do Blockchain.
    """
    
    # 1. SUBSTITUA SEU __init__ POR ESTE
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        # Tenta carregar a cadeia do disco
        self.load_chain_from_disk()

    # 2. ADICIONE ESTES DOIS NOVOS MÉTODOS À SUA CLASSE
    def load_chain_from_disk(self):
        """Carrega a blockchain de um arquivo JSON, se existir."""
        try:
            with open('blockchain_data.json', 'r') as f:
                self.chain = json.load(f)
            # Se o arquivo estava vazio ou corrompido
            if not self.chain:
                print("Arquivo encontrado, mas vazio. Criando Bloco Gênesis.")
                self.create_block(proof=1, previous_hash='0')
        except (FileNotFoundError, json.JSONDecodeError):
            print("Nenhum arquivo de blockchain encontrado. Criando Bloco Gênesis.")
            self.create_block(proof=1, previous_hash='0')

    def save_chain_to_disk(self):
        """Salva a blockchain atual em um arquivo JSON."""
        with open('blockchain_data.json', 'w') as f:
            json.dump(self.chain, f, indent=4)

    # 3. MODIFIQUE SEU create_block PARA CHAMAR O MÉTODO DE SALVAR
    def create_block(self, proof, previous_hash):
        # ... (toda a lógica que você já tem para criar o 'block') ...
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        
        # A LINHA MÁGICA:
        self.save_chain_to_disk() # Salva toda vez que um bloco é criado

        return block

    def get_previous_block(self):
        """
        Retorna o último bloco da cadeia.

        Returns:
            dict: O bloco mais recente da cadeia.
        """
        return self.chain[-1]

    def add_transaction(self, transaction):
        """
        Adiciona uma nova transação à lista de transações pendentes.

        Args:
            transaction (dict): A transação a ser adicionada.

        Returns:
            int: O índice do bloco que irá conter esta transação.
        """
        self.transactions.append(transaction)
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def proof_of_work(self, previous_proof):
        """
        Encontra um número (prova) que, quando combinado com a prova anterior,
        produz um hash com 4 zeros à esquerda.

        Args:
            previous_proof (int): A prova de trabalho do bloco anterior.

        Returns:
            int: A nova prova de trabalho encontrada.
        """
        new_proof = 1
        check_proof = False
        while not check_proof:
            # Operação de hash para o algoritmo de consenso
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()
            ).hexdigest()
            
            # Verifica se o hash atende à condição de dificuldade
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        """
        Calcula o hash SHA-256 de um bloco.

        Args:
            block (dict): O bloco para o qual o hash será calculado.

        Returns:
            str: O hash do bloco em formato hexadecimal.
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        """
        Verifica a integridade de toda a cadeia de blocos.

        Args:
            chain (list): A cadeia de blocos a ser validada.

        Returns:
            bool: True se a cadeia for válida, False caso contrário.
        """
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            
            # 1. Verifica se o hash do bloco anterior está correto
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            # 2. Verifica se a prova de trabalho é válida
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()
            ).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
            
        return True
    
    def register_node(self, address):
        """
        Adiciona um novo nó à lista de nós.

        Args:
            address (str): Endereço do nó. Ex: 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Aceita endereços como '192.168.0.5:5000'
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('URL inválido')

    def resolve_conflicts(self):
        """
        Este é o nosso Algoritmo de Consenso. Ele resolve conflitos
        substituindo nossa cadeia pela mais longa da rede.

        Returns:
            bool: True se nossa cadeia foi substituída, False se não.
        """
        neighbours = self.nodes
        new_chain = None

        # Estamos apenas procurando por cadeias mais longas que a nossa
        max_length = len(self.chain)

        # Pega e verifica as cadeias de todos os nós na nossa rede
        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/get_chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    # Verifica se o tamanho é maior e se a cadeia é válida
                    if length > max_length and self.is_chain_valid(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.RequestException as e:
                print(f"Não foi possível conectar ao nó {node}: {e}")
                continue


        # Substitui nossa cadeia se descobrirmos uma nova cadeia válida e mais longa
        if new_chain:
            self.chain = new_chain
            self.save_chain_to_disk() # Salva a nova cadeia no disco
            return True

        return False
