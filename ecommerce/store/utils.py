import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    order = {
        'get_cart_total': 0,
        'get_cart_items': 0,
        'shipping': False
    }
    cartItems = order['get_cart_items']

    for key in cart:
        try:
            item_data = cart[key]
            # Suporta chave antiga (só productId) e nova (productId_cor_memoria)
            product_id = item_data.get('productId', key)
            quantity = item_data.get('quantity', 1)

            product = Product.objects.get(id=product_id)

            custom_price = item_data.get('custom_price', None)
            price = float(custom_price) if custom_price else float(product.price)
            total = price * quantity

            order['get_cart_total'] += total
            order['get_cart_items'] += quantity
            cartItems += quantity

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': price,
                    'imageURL': product.imageURL,
                    'slug': product.slug,           # ← para links clicáveis
                },
                'quantity': quantity,
                'get_total': total,
                'color': item_data.get('color', ''),
                'storage': item_data.get('storage', ''),
                'custom_price': custom_price,
                'color_image': item_data.get('color_image', '')
            }
            items.append(item)

            if product.image:
                order['shipping'] = True
        except:
            pass

    return {
        'cartItems': cartItems,
        'order': order,
        'items': items
    }


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    print('User is not authenticated')
    print('COOKIES:', request.COOKIES)

    name = data['form']['nome']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
            color=item.get('color', ''),
            storage=item.get('storage', ''),
            custom_price=item.get('custom_price', None),
            color_image=item.get('color_image', '')
        )

    return customer, order