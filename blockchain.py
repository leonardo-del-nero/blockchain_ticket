# cryptocurrency/blockchain.py

import datetime
import hashlib
import json

class Blockchain:
    """
    Classe que representa a estrutura e as operações do Blockchain.
    """
    def __init__(self):
        """
        Inicializa o blockchain com uma lista vazia para a cadeia e transações,
        e cria o bloco gênesis.
        """
        self.chain = []
        self.transactions = []
        # Cria o Bloco Gênesis
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        """
        Cria um novo bloco e o adiciona à cadeia.

        Args:
            proof (int): A prova de trabalho do novo bloco.
            previous_hash (str): O hash do bloco anterior.

        Returns:
            dict: O novo bloco criado.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now(datetime.timezone.utc)),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        # Limpa a lista de transações, pois elas já foram incluídas no bloco
        self.transactions = []
        self.chain.append(block)
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
            if hash_operation[:7] == '0000000':
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
            if hash_operation[:7] != '0000000':
                return False
            
            previous_block = block
            block_index += 1
            
        return True
