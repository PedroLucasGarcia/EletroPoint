// Render the PayPal button into #paypal-button-container
var form = document.getElementById('form');

paypal.Buttons({

    style: {
        color: 'blue',
        shape: 'rect'
    },

    createOrder: function(data, actions) {

        var morada = document.querySelector('input[name="morada"]') ? document.querySelector('input[name="morada"]').value : '';
        var cidade = document.querySelector('input[name="cidade"]') ? document.querySelector('input[name="cidade"]').value : '';
        var codigoPostal = document.querySelector('input[name="código postal"]') ? document.querySelector('input[name="código postal"]').value : '';
        var pais = document.querySelector('input[name="país"]') ? document.querySelector('input[name="país"]').value : '';

        return actions.order.create({
            purchase_units: [{
                amount: {
                    value: parseFloat(total).toFixed(2)
                },
                shipping: {
                    address: {
                        address_line_1: morada,
                        admin_area_2: cidade,
                        postal_code: codigoPostal,
                        country_code: 'PT'
                    }
                }
            }]
        });
    },

    onApprove: function(data, actions) {
        return actions.order.capture().then(function(details) {
            submitFormData();
        });
    }

}).render('#paypal-button-container');


if (shipping == 'False') {
    var shippingEl = document.getElementById('shipping-info');
    if (shippingEl) shippingEl.innerHTML = '';
}

if (user != 'AnonymousUser') {
    var userEl = document.getElementById('user-info');
    if (userEl) userEl.innerHTML = '';
}

if (shipping == 'False' && user != 'AnonymousUser') {
    document.getElementById('shipping-info').classList.add('hidden');
    document.getElementById('payment-info').classList.remove('hidden');
}

form.addEventListener('submit', function(e) {
    e.preventDefault();
    console.log('Form submitted');
    document.getElementById('form-button').classList.add('hidden');
    document.getElementById('payment-info').classList.remove('hidden');
});

function submitFormData() {
    console.log('Payment button clicked');

    var userFormData = {
        'nome': null,
        'email': null,
        'telemóvel': null,
        'total': total
    };

    var shippingInfo = {
        'morada': null,
        'código postal': null,
        'cidade': null,
        'país': null
    };

    if (shipping != 'False') {
        shippingInfo['morada'] = form['morada'].value;
        shippingInfo['código postal'] = form['código postal'].value;
        shippingInfo['cidade'] = form['cidade'].value;
        shippingInfo['país'] = form['país'].value;
    }

    if (user == 'AnonymousUser') {
        userFormData['nome'] = form['nome'].value;
        userFormData['email'] = form['email'].value;
        userFormData['telemóvel'] = form['telemóvel'].value;
    }

    fetch(processOrderUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'form': userFormData,
            'shipping': shippingInfo
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Success:', data);
        alert('Transação realizada com sucesso!');
        cart = {};
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";
        window.location.href = homepageUrl;
    });
}

// Botão X — usa delegação de eventos para garantir que funciona sempre
document.addEventListener('click', function(e) {
    var btn = e.target.closest('.resume-delete-btn');
    if (!btn) return;

    var productId = btn.dataset.product;
    var color = btn.dataset.color || '';
    var storage = btn.dataset.storage || '';

    if (user == 'AnonymousUser') {
        var itemKey = productId + '_' + color + '_' + storage;
        delete cart[itemKey];
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";
        location.reload();
    } else {
        fetch('/update-item/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'productId': productId,
                'action': 'delete',
                'color': color,
                'storage': storage
            })
        })
        .then(response => response.json())
        .then(data => {
            location.reload();
        });
    }
});