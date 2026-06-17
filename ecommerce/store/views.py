from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.shortcuts import get_object_or_404


# ==========================================================
# FUNÇÃO AUXILIAR DO CARRINHO
# ==========================================================
# Esta função verifica se o utilizador está autenticado.
# Caso esteja autenticado, obtém o carrinho (Order) ativo
# e devolve a quantidade total de itens presentes.
# Caso contrário, devolve 0 para utilizadores anónimos.
# ==========================================================
def get_cart_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    return cartItems


# ==========================================================
# PÁGINA INICIAL (HOME)
# ==========================================================
# Carrega todos os produtos da loja e envia para o template.
# Também envia a quantidade de itens do carrinho para ser
# exibida no cabeçalho da aplicação.
# ==========================================================
def homepage(request):
    cartItems = get_cart_data(request)

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()

    context = {
        'products': products,
        'cartItems': cartItems
    }

    return render(request, 'store/index.html', context)


# ==========================================================
# PÁGINA DE LOGIN
# ==========================================================
# Exibe o formulário de autenticação do utilizador.
# ==========================================================
def loginPage(request):
    cartItems = get_cart_data(request)

    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                return render(request, 'store/loginPage.html', {'error': 'Credenciais inválidas', 'cartItems': cartItems})
        except User.DoesNotExist:
            return render(request, 'store/loginPage.html', {'error': 'Email não encontrado', 'cartItems': cartItems})

    return render(request, 'store/loginPage.html', {'cartItems': cartItems})


# ==========================================================
# PÁGINA DE REGISTO
# ==========================================================
# Exibe o formulário para criação de uma nova conta.
# ==========================================================
def registerPage(request):
    cartItems = get_cart_data(request)

    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'store/registerPage.html', {'error': 'As senhas não coincidem', 'cartItems': cartItems})
        if User.objects.filter(email=email).exists():
            return render(request, 'store/registerPage.html', {'error': 'Email já registado', 'cartItems': cartItems})

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        Customer.objects.create(user=user, name=name, email=email)
        login(request, user)
        return redirect('homepage')

    return render(request, 'store/registerPage.html', {'cartItems': cartItems})


# ==========================================================
# PÁGINA DE LOGOUT
# ==========================================================
def logoutUser(request):
    logout(request)
    return redirect('homepage')


# ==========================================================
# PÁGINA DE RESET PASSWORD
# ==========================================================
def resetPassword(request):
    cartItems = get_cart_data(request)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'store/resetPassword.html', {
                'error': 'Email não encontrado.',
                'cartItems': cartItems
            })

        if password != password2:
            return render(request, 'store/resetPassword.html', {
                'error': 'As passwords não coincidem.',
                'cartItems': cartItems
            })

        if len(password) < 8:
            return render(request, 'store/resetPassword.html', {
                'error': 'A password deve ter no mínimo 8 caracteres.',
                'cartItems': cartItems
            })

        user.set_password(password)
        user.save()
        return render(request, 'store/resetPassword.html', {
            'success': 'Password alterada com sucesso! Podes fazer login.',
            'cartItems': cartItems
        })

    return render(request, 'store/resetPassword.html', {'cartItems': cartItems})

# ==========================================================
# PÁGINA DO CARRINHO
# ==========================================================
# Obtém todos os produtos adicionados ao carrinho pelo
# utilizador autenticado e envia os dados para o template.
# ==========================================================
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
 
    return render(request, 'store/cart.html', context)


# ==========================================================
# PÁGINA DE CHECKOUT
# ==========================================================
# Exibe o resumo final da encomenda antes do pagamento.
# ==========================================================
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }

    return render(request, 'store/checkout.html', context)


# ==========================================================
# ATUALIZAÇÃO DOS ITENS DO CARRINHO (AJAX)
# ==========================================================
# Recebe pedidos enviados por JavaScript para:
# - Adicionar uma unidade ao produto
# - Remover uma unidade do produto
# - Eliminar completamente o produto do carrinho
#
# Se a quantidade chegar a 0, o item é removido da encomenda.
# ==========================================================
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    quantity = data.get('quantity', 1)
    color = data.get('color', '')
    storage = data.get('storage', '')
    custom_price = data.get('custom_price', None)
    color_image = data.get('color_image', '')

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Procura um OrderItem que corresponda exatamente ao produto + cor + memória
    orderItem = OrderItem.objects.filter(
        order=order,
        product=product,
        color=color,
        storage=storage
    ).first()

    if action == 'add':
        if orderItem is None:
            # Combinação nova — cria um item novo
            orderItem = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=0,
                color=color,
                storage=storage,
                custom_price=float(custom_price) if custom_price else None,
                color_image=color_image
            )
        orderItem.quantity += quantity
        orderItem.save()

    elif action == 'remove':
        if orderItem:
            orderItem.quantity -= 1
            orderItem.save()
            if orderItem.quantity <= 0:
                orderItem.delete()

    elif action == 'delete':
        if orderItem:
            orderItem.delete()

    return JsonResponse('Item was updated', safe=False)

# ==========================================================
# PROCESSAMENTO DA ENCOMENDA
# ==========================================================
# Finaliza a encomenda após o pagamento:
# 1. Gera um ID único para a transação.
# 2. Valida o valor total recebido.
# 3. Marca a encomenda como concluída.
# 4. Guarda a morada de entrega quando necessário.
# ==========================================================
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()

    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer

        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])

    order.transaction_id = transaction_id

    # Validação do valor total recebido
    if total == float(order.get_cart_total):
        order.complete = True

    order.save()

    # Guarda a morada caso a encomenda necessite de envio
    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['morada'],
            zipcode=data['shipping']['código postal'],
            city=data['shipping']['cidade'],
            country=data['shipping']['país'],
        )

    return JsonResponse('Payment complete!', safe=False)


# -------------------- TODOS OS PRODUTOS --------------------#
def todos(request):
    cartItems = get_cart_data(request)
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/todos/todos.html', context)

def product_detail(request, slug):
    cartItems = get_cart_data(request)
    product = get_object_or_404(Product, slug=slug)
    template = f'store/{product.link_product}'
    return render(request, template, {'product': product, 'cartItems': cartItems})


# -------------------- SMARTPHONES --------------------#
def smartphones(request):
    cartItems = get_cart_data(request)
    categoria = Category.objects.get(slug='smartphones')
    products = Product.objects.filter(category=categoria)
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/smartphones/smartphones.html', context)

# Apple --------------------
def smartphoneApple(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='smartphones')
    brand = get_object_or_404(Brand, slug='apple')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/smartphones/smartphone-apple.html', {'products': products, 'cartItems': cartItems})

def iphoneAir(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/iphone-air.html', {'cartItems': cartItems})

def iphone17Pro(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/iphone17Pro.html', {'cartItems': cartItems})

def iphone17(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/iphone17.html', {'cartItems': cartItems})

def iphone16(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/iphone16.html', {'cartItems': cartItems})

def iphone16e(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/iphone16e.html', {'cartItems': cartItems})

# Google --------------------
def smartphoneGoogle(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='smartphones')
    brand = get_object_or_404(Brand, slug='google')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/smartphones/smartphone-google.html', {'products': products, 'cartItems': cartItems})

def pixel10ProXL(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/pixel10-pro-xl.html', {'cartItems': cartItems})

def pixel10Pro(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/pixel10-pro.html', {'cartItems': cartItems})

def pixel10(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/pixel10.html', {'cartItems': cartItems})

# Samsung --------------------
def smartphoneSamsung(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='smartphones')
    brand = get_object_or_404(Brand, slug='samsung')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/smartphones/smartphone-samsung.html', {'products': products, 'cartItems': cartItems})

def s25Ultra(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/s25-ultra.html', {'cartItems': cartItems})

def s25Edge(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/s25-edge.html', {'cartItems': cartItems})

def s25(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/s25.html', {'cartItems': cartItems})

def zFold7(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/z-fold-7.html', {'cartItems': cartItems})

def zFlip7(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/z-flip-7.html', {'cartItems': cartItems})

# Xiaomi --------------------
def smartphoneXiaomi(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='smartphones')
    brand = get_object_or_404(Brand, slug='xiaomi')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/smartphones/smartphone-xiaomi.html', {'products': products, 'cartItems': cartItems})

def xiaomi15Ultra(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/xiaomi15-ultra.html', {'cartItems': cartItems})

def xiaomi15(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/xiaomi15.html', {'cartItems': cartItems})

def xiaomi15tPro(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/xiaomi15t-pro.html', {'cartItems': cartItems})

def xiaomi15t(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/xiaomi15t.html', {'cartItems': cartItems})

def redmiNote15ProPlus(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/smartphones/redmi-note15-pro-plus.html', {'cartItems': cartItems})


# -------------------- COMPUTADORES --------------------#
def computadores(request):
    cartItems = get_cart_data(request)
    categoria = Category.objects.get(slug='computadores')
    products = Product.objects.filter(category=categoria)
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/computadores/computadores.html', context)

# Amd --------------------
def computadorAmd(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='computadores')
    brand = get_object_or_404(Brand, slug='amd')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/computadores/computador-amd.html', {'products': products, 'cartItems': cartItems})

def ryzen9_5900x(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/computadores/ryzen9-5900x.html', {'cartItems': cartItems})

def ryzen7_8700f(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/computadores/ryzen7-8700f.html', {'cartItems': cartItems})

def ryzen7_5800x(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/computadores/ryzen7-5800x.html', {'cartItems': cartItems})

# Intel --------------------
def computadorIntel(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='computadores')
    brand = get_object_or_404(Brand, slug='intel')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/computadores/computador-intel.html', {'products': products, 'cartItems': cartItems})

def coreI5_14400f(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/computadores/core-i5-14400f.html', {'cartItems': cartItems})

def coreI5_12400f(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/computadores/core-i5-12400f.html', {'cartItems': cartItems})


# -------------------- PORTÁTEIS --------------------#
def portateis(request):
    cartItems = get_cart_data(request)
    categoria = Category.objects.get(slug='portateis')
    products = Product.objects.filter(category=categoria)
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/portateis/portateis.html', context)

# Apple --------------------
def portatilApple(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='portateis')
    brand = get_object_or_404(Brand, slug='apple')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/portateis/portatil-apple.html', {'products': products, 'cartItems': cartItems})

def macbookPro(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/portateis/macbook-pro.html', {'cartItems': cartItems})

def macbookAir(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/portateis/macbook-air.html', {'cartItems': cartItems})

# Lenovo --------------------
def portatilLenovo(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='portateis')
    brand = get_object_or_404(Brand, slug='lenovo')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/portateis/portatil-lenovo.html', {'products': products, 'cartItems': cartItems})

def ideapadSlim5(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/portateis/ideapad-slim5.html', {'cartItems': cartItems})

# Samsung --------------------
def portatilSamsung(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='portateis')
    brand = get_object_or_404(Brand, slug='samsung')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/portateis/portatil-samsung.html', {'products': products, 'cartItems': cartItems})

def book5Pro360(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/portateis/book5Pro-360.html', {'cartItems': cartItems})

def book4(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/portateis/book4.html', {'cartItems': cartItems})

def book3Pro(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/portateis/book3Pro.html', {'cartItems': cartItems})


# -------------------- TABLETS --------------------#
def tablets(request):
    cartItems = get_cart_data(request)
    categoria = Category.objects.get(slug='tablets')
    products = Product.objects.filter(category=categoria)
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/tablets/tablets.html', context)

# Apple --------------------
def tabletApple(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='tablets')
    brand = get_object_or_404(Brand, slug='apple')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/tablets/tablet-apple.html', {'products': products, 'cartItems': cartItems})

def ipadPro(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/tablets/ipad-pro.html', {'cartItems': cartItems})

def ipadAir(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/tablets/ipad-air.html', {'cartItems': cartItems})

def ipad(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/tablets/ipad.html', {'cartItems': cartItems})

# Samsung --------------------
def tabletSamsung(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='tablets')
    brand = get_object_or_404(Brand, slug='samsung')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/tablets/tablet-samsung.html', {'products': products, 'cartItems': cartItems})

def tabS10Plus(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/tablets/tab-s10-plus.html', {'cartItems': cartItems})

def tabS10Fe(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/tablets/tab-s10-fe.html', {'cartItems': cartItems})

# Xiaomi --------------------
def tabletXiaomi(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='tablets')
    brand = get_object_or_404(Brand, slug='xiaomi')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/tablets/tablet-xiaomi.html', {'products': products, 'cartItems': cartItems})

def redmiPad2(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/tablets/redmi-pad2.html', {'cartItems': cartItems})


# -------------------- CONSOLAS --------------------#
def consolas(request):
    cartItems = get_cart_data(request)
    categoria = Category.objects.get(slug='consolas')
    products = Product.objects.filter(category=categoria)
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/consolas/consolas.html', context)

# Nintendo --------------------
def consolaNintendo(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='consolas')
    brand = get_object_or_404(Brand, slug='nintendo')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/consolas/consola-nintendo.html', {'products': products, 'cartItems': cartItems})

def switch2(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/consolas/switch2.html', {'cartItems': cartItems})

def switch(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/consolas/switch.html', {'cartItems': cartItems})

# Sony --------------------
def consolaSony(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='consolas')
    brand = get_object_or_404(Brand, slug='sony')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/consolas/consola-sony.html', {'products': products, 'cartItems': cartItems})

def playstation5pro(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/consolas/playstation5pro.html', {'cartItems': cartItems})

def playstation5(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/consolas/playstation5.html', {'cartItems': cartItems})

# Xbox --------------------
def consolaXbox(request):
    cartItems = get_cart_data(request)
    category = get_object_or_404(Category, slug='consolas')
    brand = get_object_or_404(Brand, slug='xbox')
    products = Product.objects.filter(category=category, brand=brand)
    return render(request, 'store/consolas/consola-xbox.html', {'products': products, 'cartItems': cartItems})

def xboxX(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/consolas/xbox-x.html', {'cartItems': cartItems})

def xboxS(request):
    cartItems = get_cart_data(request)
    return render(request, 'store/consolas/xbox-s.html', {'cartItems': cartItems})
