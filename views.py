# cryptocurrency/views.py

from flask import Blueprint, jsonify, request, render_template
import requests
import uuid

# 'api' é o nome do blueprint. Usado para organizar as rotas.
api_blueprint = Blueprint('api', __name__)

# Esta variável global será preenchida pela instância criada em main.py
blockchain = None

def set_blockchain(blockchain_instance):
    """
    Função para injetar a instância do blockchain a partir do main.py.
    """
    global blockchain
    blockchain = blockchain_instance

# --- Funções Auxiliares ---

def search_recursively(data, term_to_find):
    """
    Função auxiliar que busca recursivamente por um termo em um dicionário ou lista.
    """
    term_to_find = str(term_to_find).lower()

    # Se 'data' for um dicionário (objeto JSON)
    if isinstance(data, dict):
        for key, value in data.items():
            # Compara o valor do dicionário com o termo de busca
            if str(value).lower() == term_to_find:
                return True
            # Se o valor for outro dicionário ou uma lista, chama a função recursivamente
            if isinstance(value, (dict, list)):
                if search_recursively(value, term_to_find):
                    return True
    
    # Se 'data' for uma lista
    elif isinstance(data, list):
        for item in data:
            # Compara o item da lista com o termo de busca
            if str(item).lower() == term_to_find:
                return True
            # Se o item for outro dicionário ou uma lista, chama a função recursivamente
            if isinstance(item, (dict, list)):
                if search_recursively(item, term_to_find):
                    return True
    
    # Se não encontrar, retorna False
    return False


# --- Rotas da API ---

@api_blueprint.route('/', methods=['GET'])
def home():
    """
    Rota para a página inicial com a interface de teste da API.
    """
    return render_template('index.html') 

# ==================================================================
# ROTA DE PESQUISA ATUALIZADA (BUSCA UNIVERSAL)
# ==================================================================
@api_blueprint.route('/search', methods=['GET'])
def search_transactions():
    """
    Busca por um termo em qualquer lugar dentro das transações na blockchain.
    Exemplo de uso: /search?q=termo_a_buscar
    """
    # Pega o parâmetro de busca 'q' da URL
    query_term = request.args.get('q')

    if not query_term:
        return jsonify({'error': 'Parâmetro de busca "q" é obrigatório.'}), 400

    found_transactions = []

    # Percorre toda a cadeia de blocos
    for block in blockchain.chain:
        # Percorre todas as transações dentro de um bloco
        for transaction in block['transactions']:
            # Usa a nova função de busca recursiva
            if search_recursively(transaction, query_term):
                # Se encontrar, adiciona a transação e o índice do bloco aos resultados
                found_transactions.append({
                    'block_index': block['index'],
                    'transaction': transaction
                })

    if not found_transactions:
        return jsonify({
            'message': 'Nenhuma transação encontrada contendo o termo fornecido.',
            'search_term': query_term
        }), 404

    return jsonify({
        'message': f'{len(found_transactions)} transação(ões) encontrada(s).',
        'results': found_transactions
    }), 200
# ==================================================================

@api_blueprint.route('/mine_block', methods=['GET'])
def mine_block():
    """
    Minera um novo bloco, adiciona à cadeia e retorna seus detalhes.
    """
    # ==================================================================
    # PASSO ZERO: CONSENSO AUTOMÁTICO ANTES DE MINERAR
    # Garante que estamos na cadeia mais longa e válida antes de fazer o trabalho.
    print("Iniciando mineração: Verificando consenso com a rede...")
    replaced = blockchain.resolve_conflicts()
    if replaced:
        print("CONSENSO: Cadeia atualizada. A mineração continuará na nova cadeia.")
    else:
        print("CONSENSO: Cadeia local já é a correta. Prosseguindo.")
    # ==================================================================

    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Recompensa por mineração
    node_address = str(uuid.uuid4()).replace('-', '')
    blockchain.add_transaction({
        'sender': 'reward',
        'receiver': node_address,
        'amount': 1
    })

    block = blockchain.create_block(proof, previous_hash)
    
    response = {
        'message': 'Parabéns, você minerou um bloco!',
        'block': block
    }
    return jsonify(response), 200

@api_blueprint.route('/get_chain', methods=['GET'])
def get_chain():
    """
    Retorna a blockchain completa.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# No seu arquivo cryptocurrency/views.py
# Adicione esta nova rota ao final do arquivo

@api_blueprint.route('/network/chain', methods=['GET'])
def get_authoritative_chain():
    authoritative_node = None
    """
    Esta é a rota do "Cliente Inteligente" para o usuário final.
    Ela executa o seguinte processo:
    1. Identifica todos os nós na rede, incluindo a si mesmo.
    2. Pede a cadeia de cada um deles usando a rota /get_chain.
    3. Compara todas as cadeias recebidas.
    4. Retorna a cadeia que for a mais longa e válida.
    """
    print("Iniciando busca pela cadeia autoritativa em toda a rede...")
    
    # 1. Monta a lista de todos os nós que precisamos verificar.
    # Começamos com uma cópia dos nós registrados.
    nodes_to_check = blockchain.nodes.copy()
    # Adicionamos o endereço do próprio nó à lista, para que ele também seja uma fonte.
    # `request.host` é uma forma prática do Flask obter o endereço do servidor atual.
    nodes_to_check.add(request.host)

    best_chain = None
    max_length = len(blockchain.chain) # O tamanho da nossa cadeia local é o recorde a ser batido

    # 2. Faz um loop por cada nó para "entrevistá-lo".
    for node in nodes_to_check:
        try:
            # Pede a cadeia usando a rota simples /get_chain
            response = requests.get(f'http://{node}/get_chain')

            if response.status_code == 200:
                data = response.json()
                length = data['length']
                chain = data['chain']

                # 3. A VERIFICAÇÃO DUPLA: É mais longa E é válida?
                # Usamos a lógica de validação do nosso próprio nó para auditar a cadeia recebida.
                if length > max_length and blockchain.is_chain_valid(chain):
                    authoritative_node = f"Encontrada uma cadeia melhor no nó {node} (Tamanho: {length})"
                    max_length = length
                    best_chain = chain

        except requests.exceptions.RequestException:
            print(f"AVISO: Nó {node} está offline ou não respondeu.")
            continue

    # 4. Determina a resposta final.
    # Se encontramos uma cadeia melhor na rede, 'best_chain' terá essa cadeia.
    # Se não, 'best_chain' ainda será None.
    if best_chain:
        
        final_response_data = {
            'message': f'{authoritative_node}',
            'chain': best_chain
        }
        return jsonify(final_response_data), 200
    else:
        # Se nenhuma cadeia melhor foi encontrada, a nossa já era a correta.
        final_response_data = {
            'message': 'A cadeia local já é a autoritativa.',
            'chain': blockchain.chain
        }
        return jsonify(final_response_data), 200

@api_blueprint.route('/is_valid', methods=['GET'])
def is_valid():
    """
    Verifica se a blockchain é válida.
    """
    valid = blockchain.is_chain_valid(blockchain.chain)
    if valid:
        response = {'message': 'A blockchain é válida.'}
    else:
        response = {'message': 'A blockchain NÃO é válida.'}
    return jsonify(response), 200

@api_blueprint.route('/add_transaction', methods=['POST'])
def add_transaction_route():
    """
    Adiciona uma nova transação, filtrando e validando para salvar
    apenas os campos essenciais na blockchain.
    """
    # ==================================================================
    # PASSO ZERO: CONSENSO AUTOMÁTICO ANTES DE ADICIONAR TRANSAÇÃO
    # Garante que o nó está sincronizado com a rede.
    blockchain.resolve_conflicts()
    # ==================================================================

    json_data = request.get_json()
    
    # 1. Validação inicial: Verifica se o campo 'transactions' existe e é uma lista
    transactions_input = json_data.get('transactions')
    if not transactions_input or not isinstance(transactions_input, list) or not transactions_input:
        error_response = {'error': 'Requisição inválida. O campo "transactions" é obrigatório e deve ser uma lista não vazia.'}
        return jsonify(error_response), 400
    
    # ... O resto da sua função continua exatamente igual ...
    # Lista para armazenar as transações já filtradas e prontas para o blockchain
    filtered_transactions_to_add = []

    # 2. Itera sobre cada transação enviada para validar e filtrar
    for t in transactions_input:
        # --- Validação dos campos obrigatórios ---
        required_keys = ['id', 'name', 'engine', 'converter']
        if not all(key in t for key in required_keys):
            error_msg = f'Transação inválida. Os campos "id", "name", "engine", e "converter" são obrigatórios. Transação problemática: {t}'
            return jsonify({'error': error_msg}), 400

        converter_data = t.get('converter')
        if not isinstance(converter_data, dict):
            error_msg = f'O campo "converter" deve ser um objeto (dicionário). Transação problemática: {t}'
            return jsonify({'error': error_msg}), 400
            
        required_converter_keys = ['code', 'id', 'name']
        if not all(key in converter_data for key in required_converter_keys):
            error_msg = f'Objeto "converter" inválido. Os campos "code", "id", e "name" são obrigatórios. Transação problemática: {t}'
            return jsonify({'error': error_msg}), 400
            
        # --- Criação do novo objeto JSON filtrado ---
        # Apenas os campos que você quer serão incluídos aqui.
        new_clean_transaction = {
            'id': t.get('id'),
            'name': t.get('name'),
            'engine': t.get('engine'),
            'converter': {
                'id': converter_data.get('id'),
                'code': converter_data.get('code'),
                'name': converter_data.get('name')
            }
        }
        
        filtered_transactions_to_add.append(new_clean_transaction)

    # 3. Se todas as transações no lote forem válidas, adiciona-as à blockchain
    if not filtered_transactions_to_add:
        return jsonify({'error': 'Nenhuma transação válida foi fornecida.'}), 400

    for clean_t in filtered_transactions_to_add:
        blockchain.add_transaction(clean_t)
        
    # 4. Retorna uma resposta de sucesso
    previous_block = blockchain.get_previous_block()
    index = previous_block['index'] + 1
    response = {
        'message': f'{len(filtered_transactions_to_add)} transações foram validadas, filtradas e serão adicionadas ao Bloco {index}'
    }
    return jsonify(response), 201

# Adicione esta rota ao final do seu arquivo views.py

@api_blueprint.route('/edit_block_test', methods=['POST'])
def edit_block_test():
    """
    ===================================================================
    == ATENÇÃO: ESTA FUNÇÃO É APENAS PARA FINS DE TESTE EDUCACIONAL ==
    == ELA QUEBRA PROPOSITALMENTE A INTEGRIDADE DA BLOCKCHAIN.       ==
    ===================================================================
    """
    json_data = request.get_json()
    
    # Pega os parâmetros da requisição
    block_index = json_data.get('block_index')
    new_transaction = json_data.get('new_transaction')
    
    # Validação simples da requisição
    if block_index is None or new_transaction is None:
        return jsonify({'error': 'Os campos "block_index" e "new_transaction" são obrigatórios.'}), 400
        
    # Verifica se o índice do bloco é válido
    if not isinstance(block_index, int) or block_index >= len(blockchain.chain) or block_index < 0:
        return jsonify({'error': f'Índice de bloco inválido. A blockchain tem {len(blockchain.chain)} blocos (índices de 0 a {len(blockchain.chain) - 1}).'}), 400
        
    # --- O ATO DA "SABOTAGEM" ---
    # Altera diretamente a lista de transações de um bloco já existente.
    # Isso é algo que NUNCA se deve fazer.
    print(f"--- INICIANDO TESTE DE SABOTAGEM NO BLOCO {block_index} ---")
    original_block = blockchain.chain[block_index].copy()
    blockchain.chain[block_index]['transactions'] = [new_transaction]
    edited_block = blockchain.chain[block_index]
    print(f"Bloco Original: {original_block}")
    print(f"Bloco Editado: {edited_block}")
    
    # --- A CONSEQUÊNCIA ---
    # Imediatamente após a edição, verificamos a validade da cadeia
    is_now_valid = blockchain.is_chain_valid(blockchain.chain)
    
    message = "A blockchain foi SABOTADA com sucesso!"
    if is_now_valid:
        # Este caso é teoricamente impossível de acontecer se a lógica estiver correta.
        conclusion = "Incrivelmente, a cadeia ainda se reporta como válida. Verifique a lógica de is_chain_valid."
    else:
        conclusion = "Como esperado, a função is_chain_valid AGORA REPORTA a cadeia como INVÁLIDA."

    response = {
        'message': message,
        'conclusion': conclusion,
        'block_edited_index': block_index,
        'block_content_after_edit': edited_block,
        'is_chain_still_valid': is_now_valid
    }
    
    return jsonify(response), 200

@api_blueprint.route('/connect_node', methods=['POST'])
def connect_node():
    """
    Conecta este nó a outros nós da rede.
    """
    json_data = request.get_json()
    nodes = json_data.get('nodes')
    if nodes is None:
        return "Erro: Forneça uma lista de nós válida no corpo da requisição.", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Todos os nós foram conectados. A blockchain agora contém os seguintes nós:',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@api_blueprint.route('/consensus', methods=['GET'])
def consensus():
    """
    Executa o algoritmo de consenso para garantir que o nó tem a cadeia correta.
    """
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'A cadeia foi substituída pela cadeia autoritativa (mais longa).',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'A cadeia atual já é a autoritativa.',
            'current_chain': blockchain.chain
        }
    return jsonify(response), 200
