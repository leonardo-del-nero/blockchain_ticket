/**
* Função genérica para fazer requisições à API.
*/

async function fetchAPI(endpoint, method, body = null) {
    const responseContainer = document.getElementById('api-response');
    responseContainer.textContent = 'Carregando...';

    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(endpoint, options);
        const data = await response.json();

        responseContainer.textContent = JSON.stringify(data, null, 4);

    } catch (error) {
        console.error('Erro ao fazer a requisição:', error);
        responseContainer.textContent = `Erro na requisição: ${error.message}`;
    }
}

/**
 * Função específica para adicionar uma nova transação.
 */
function addTransaction() {
    const jsonInput = document.getElementById('json-input').value;
    const responseContainer = document.getElementById('api-response');

    if (!jsonInput.trim()) {
        responseContainer.textContent = 'Erro: O campo de payload JSON não pode estar vazio.';
        return;
    }

    try {
        const transactionData = JSON.parse(jsonInput);
        // O backend espera um objeto com a chave "transactions" contendo uma lista
        fetchAPI('/add_transaction', 'POST', { transactions: [transactionData] });
    } catch (error) {
        console.error('Erro ao parsear JSON:', error);
        responseContainer.textContent = `Erro: JSON inválido. Verifique a sintaxe.\n\nDetalhes: ${error.message}`;
    }
}

/**
 * NOVO: Função para conectar um nó à rede.
 */
function connectNode() {
    const nodeAddressInput = document.getElementById('node-address-input');
    const responseContainer = document.getElementById('api-response');
    const nodeAddress = nodeAddressInput.value.trim();

    if (!nodeAddress) {
        responseContainer.textContent = 'Erro: O endereço do nó não pode estar vazio.';
        return;
    }

    // O backend espera um objeto com a chave "nodes" contendo uma lista de endereços
    const body = {
        nodes: [nodeAddress]
    };

    fetchAPI('/connect_node', 'POST', body);
    nodeAddressInput.value = ''; // Limpa o campo após o envio
}
