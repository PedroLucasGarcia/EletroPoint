/*
=========================================
CONTROLO DO CARRINHO DE COMPRAS
=========================================

Este script é responsável por atualizar a quantidade de produtos
no carrinho através dos botões de aumentar (+), diminuir (-)
e remover.

Funcionamento:

1. Obtém todos os elementos com a classe "update-cart".

2. Adiciona um evento de clique a cada botão encontrado.

3. Quando um botão é clicado:
   - Obtém o ID do produto através do atributo data-product.
   - Obtém a ação através do atributo data-action.
   - As ações possíveis são:
        "add"    -> aumenta a quantidade em 1.
        "remove" -> diminui a quantidade em 1.
        "delete" -> remove completamente o produto do carrinho.

4. Verifica se o utilizador está autenticado.
   - Se não estiver autenticado, apenas mostra uma mensagem na consola.
   - Se estiver autenticado, chama a função updateUserOrder().

5. A função updateUserOrder():
   - Envia um pedido POST para a rota "/update-item/".
   - Envia o ID do produto e a ação em formato JSON.
   - Inclui o token CSRF para segurança do Django.
   - A view Django recebe os dados e atualiza o carrinho na base de dados.

6. Após receber a resposta do servidor:
   - A página é recarregada com location.reload().
   - Isto atualiza os valores apresentados no carrinho
     (quantidades, subtotais e total da encomenda).

Fluxo resumido:

Clique no botão
      ↓
Obtém productId e action
      ↓
Verifica autenticação
      ↓
Envia pedido POST para Django
      ↓
Django atualiza o carrinho
      ↓
Página recarrega
      ↓
Carrinho atualizado no ecrã
*/

var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        var color = this.dataset.color || ''
        var storage = this.dataset.storage || ''
        var context = this.dataset.context || 'cart'  // ← novo

        if (user == 'AnonymousUser') {
            addCookieItem(productId, action, color, storage, null, context)
        } else {
            updateUserOrder(productId, action, color, storage, context)
        }
    })
}

function addCookieItem(productId, action, color, storage, customPrice, context) {
    var itemKey = productId + '_' + (color || '') + '_' + (storage || '')

    if (action == 'add') {
        if (cart[itemKey] == undefined) {
            cart[itemKey] = {
                'quantity': 1,
                'productId': productId,
                'color': color || '',
                'storage': storage || '',
                'custom_price': customPrice || null
            }
        } else {
            cart[itemKey]['quantity'] += 1
        }
    }

    if (action == 'remove') {
        if (cart[itemKey] != undefined) {
            cart[itemKey]['quantity'] -= 1
            if (cart[itemKey]['quantity'] <= 0) {
                delete cart[itemKey]
            }
        }
    }

    if (action == 'delete') {
        delete cart[itemKey]
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()  // reload na página atual (cart ou checkout)
}

function updateUserOrder(productId, action, color, storage, context) {
    fetch('/update-item/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'productId': productId,
            'action': action,
            'color': color,
            'storage': storage
        })
    })
    .then(response => response.json())
    .then(data => {
        if (context === 'checkout') {
            location.reload()   // ← fica no checkout
        } else {
            window.location.href = '/cart/'  // ← vai para o cart
        }
    })
}