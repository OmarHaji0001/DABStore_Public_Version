from datetime import datetime, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Q, Value, Sum
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.db.models.functions import Concat
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


def mainPage(request):
    products = Product.objects.exclude(quantity=0)

    search_query = request.GET.get('q', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    selected_category = request.GET.get('category', 'all')
    selected_gender = request.GET.get('gender', 'all')
    selected_price = request.GET.get('price', 'all')

    if selected_category != 'all':
        products = products.filter(category__id=selected_category)

    if selected_gender != 'all':
        products = products.filter(Q(gender=selected_gender) | Q(gender='Both'))
        # print(type(products),'asdasdas')
        # products += Product.objects.filter(gender='Both')

    if selected_price == 'low-high':
        products = products.order_by('price')
    elif selected_price == 'high-low':
        products = products.order_by('-price')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_gender': selected_gender,
        'selected_price': selected_price,
        'categories': Category.objects.exclude(name='Default'),
    }
    return render(request, 'pages/productPages.html', context)


def aboutPage(request):
    return render(request, 'pages/about.html')


def adminAddProduct(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    form = ProductForm(request.POST or None, request.FILES or None)
    images=request.FILES.getlist('Multi Images')

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            for img in images:
                MultiImage.objects.create(product=form.instance, image=img)
            return redirect('adminProducts')
    return render(request, 'pages/addProductAdminPage.html', {'form': form})

def adminMultiImageProduct(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    if request.method == 'POST':
        images = request.FILES.getlist('Multi Images')
        for img in images:
            MultiImage.objects.create(product=Product.objects.get(id=id), image=img)
        return redirect('editProductMultiImgae',id=id)
    product = Product.objects.get(id=id)
    images = MultiImage.objects.filter(product=product)
    context={
        'product':product,
        'images':images,
    }
    return render(request, 'pages/editProductsMultiImages.html',context)

def adminDeleteMultiImageProduct(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    image = MultiImage.objects.get(id=id)
    image.delete()
    return redirect('editProductMultiImgae',id=image.product.id)


def adminEditProduct(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    product = Product.objects.get(id=id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST':
        if form.is_valid():

            form.save()

            return redirect('adminProducts')
    return render(request, 'pages/editProductAdminPage.html', {'form': form, 'product': product})


def adminDeleteProduct(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('adminProducts')


def deleteCity(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    city = City.objects.get(id=id)
    city.delete()
    return redirect('cities')


def editCity(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    city = City.objects.get(id=id)
    form = CityForm(request.POST or None, instance=city)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('cities')
    return render(request, 'pages/editCity.html', {'form': form, 'city': city})


def addCity(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    form = CityForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('cities')
    return render(request, 'pages/addCity.html', {'form': form})


def citiesPage(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    cities = City.objects.all()
    return render(request, 'pages/citiesPage.html', {'cities': cities})


def categoriesPage(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    categories = Category.objects.all()
    return render(request, 'pages/categories.html', {'categories': categories})


def deleteCategory(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('categories')


def editCategory(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    category = Category.objects.get(id=id)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('categories')
    return render(request, 'pages/editCategory.html', {'form': form, 'category': category})


def addCategory(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    form = CategoryForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('categories')
    return render(request, 'pages/addCategory.html', {'form': form})


def adminPage(request):
    if (not request.user.is_authenticated) or (request.user.is_superuser == False):
        return redirect('mainPage')
    cities_sales = Orders.objects.values('city__name').annotate(total_sales=Sum('total_price'))
    current_year = datetime.now().year
    sales_this_year = Orders.objects.filter(order_date__year=current_year).aggregate(total_sales=Sum('total_price'))[
        'total_sales']

    categories = Category.objects.exclude(name='Default')

    pending_count = Orders.objects.filter(status='بانتظار التأكيد').count()
    confirmed_count = Orders.objects.filter(status='تم التأكيد').count()
    delivered_count = Orders.objects.filter(status='تم التسليم').count()

    last_month = datetime.now() - timedelta(days=30)
    active_users = CustomUser.objects.filter(is_superuser=False).count()
    context = {
        'cities_sales': cities_sales,
        'sales_this_year': sales_this_year,
        'categories': categories,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'delivered_count': delivered_count,
        'active_users': active_users,
    }
    return render(request, 'pages/adminPanel.html', context)


def adminOrdersUpdate(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')

    order = Orders.objects.get(id=id)

    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.save()
    return redirect('adminOrders')


def adminOrders(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')

    orders = Orders.objects.all()

    search_query = request.GET.get('q', '')

    if search_query != '':
        selected_city = 'all'
        selected_status = 'all'
        orders = orders.filter(id=int(search_query))

    else:
        selected_city = request.GET.get('city', 'all')
        selected_status = request.GET.get('status', 'all')

        if selected_status != 'all':
            orders = orders.filter(status=selected_status)

        if selected_city != 'all':
            orders = orders.filter(city__id=selected_city)
    orders = orders.order_by('-order_date')
    paginator = Paginator(orders, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    cities = City.objects.all()
    context = {
        'page_obj': page_obj,
        'selected_status': selected_status,
        'selected_city': selected_city,
        'cities': cities,
    }

    return render(request, 'pages/orderAdminPage.html', context)


def adminProducts(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')

    products = Product.objects.all()
    products = products.order_by('-id')

    search_query = request.GET.get('q', '')

    if search_query != '':
        products = products.filter(name__icontains=search_query)
        selected_category = 'all'
        selected_gender = 'all'
        selected_price = 'all'
        selected_quantity = 'all'
        selected_discount = 'all'
    else:
        selected_category = request.GET.get('category', 'all')
        selected_gender = request.GET.get('gender', 'all')
        selected_price = request.GET.get('price', 'all')
        selected_quantity = request.GET.get('quantity', 'all')
        selected_discount = request.GET.get('discount', 'all')
        # print(selected_discount,selected_quantity,selected_price,'saasas')
        if selected_category != 'all':
            products = products.filter(category__id=selected_category)

        if selected_gender != 'all':
            products = products.filter(gender=selected_gender)

        if selected_price == 'low-high':
            products = products.order_by('price')
        elif selected_price == 'high-low':
            products = products.order_by('-price')

        if selected_quantity == 'low-high':
            products = products.order_by('quantity')
        elif selected_quantity == 'high-low':
            products = products.order_by('-quantity')

        if selected_discount == 'with-discount':
            products = products.exclude(discount=0)
        elif selected_discount == 'without-discount':
            products = products.filter(discount=0)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_gender': selected_gender,
        'selected_price': selected_price,
        'selected_quantity': selected_quantity,
        'selected_discount': selected_discount,
        'categories': Category.objects.exclude(name='Default'),
    }

    return render(request, 'pages/productsAdmin.html', context)


def productDetail(request, id):
    product = Product.objects.get(id=id)

    if request.method == 'POST' and request.user.is_authenticated:
        quantity = int(request.POST.get('quantity', 1))

        UserProductOrder.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
        )

        messages.success(request, "تم الطلب! تحقق من سلة التسوق الخاصة بك.")

        return redirect('product', id=id)
    elif request.method == 'POST' and not request.user.is_authenticated:
        return redirect('signIn')
    multiImages = MultiImage.objects.filter(product=product)
    context = {
        'product': product,
        'multiImages': multiImages,

    }
    return render(request, 'pages/product.html', context)


def usersPage(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')

    query = request.GET.get('q', '').strip()

    if query:
        users = CustomUser.objects.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(full_name__icontains=query),
            is_staff=False,
            is_superuser=False
        )
    else:
        users = CustomUser.objects.filter(is_staff=False, is_superuser=False)

    paginator = Paginator(users, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pages/users.html', {'page_obj': page_obj, 'query': query})


def signIn(request):
    if request.user.is_authenticated:
        return redirect('mainPage')

    form = CustomAuthenticationForm(request, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            return redirect('mainPage')
    return render(request, 'pages/signIn.html', {'form': form})


def signUp(request):
    if request.user.is_authenticated:
        return redirect('mainPage')

    form = CustomUserCreationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            login(request, form.instance)
            return redirect('mainPage')
    return render(request, 'pages/signup.html', {'form': form})


def signOut(request):
    logout(request)
    return redirect('mainPage')


def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('mainPage')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            login(request, request.user)
            return redirect('settings')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'pages/changePassword.html', {'form': form})


def deleteFromCart(request, id):
    if not request.user.is_authenticated:
        return redirect('mainPage')
    product = UserProductOrder.objects.get(id=id)
    if product.status != 'pending':
        return redirect('mainPage')
    if product.user != request.user and not request.user.is_superuser:
        return redirect('mainPage')
    product.delete()
    return redirect('cart')


def settings(request):
    if not request.user.is_authenticated:
        return redirect('mainPage')
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('settings')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'pages/settings.html', {'form': form})


def cart(request):
    if not request.user.is_authenticated:
        return redirect('mainPage')
    products = UserProductOrder.objects.filter(user=request.user)
    products = products.filter(status='pending')
    total = 0
    for product in products:
        total += product.total_price
    if request.method == 'POST':

        if len(products) > 0:
            for item in products:
                if item.product.quantity >= item.quantity:
                    item.product.quantity -= item.quantity
                else:
                    messages.error(request, f"الكمية المتاحة لـ {item.product.name} غير كافية.")
                    return redirect('cart')
            OrderObject = Orders.objects.create(user=request.user,
                                                order_date=datetime.now(),
                                                status='بانتظار التأكيد',
                                                total_price=total,
                                                city=City.objects.get(id=int(request.POST.get('city'))),
                                                address=request.POST.get('address'))

            for item in products:
                item.product.number_of_sales += item.quantity
                item.status = 'ordered'
                item.order_id = OrderObject.id
                item.product.save()
                item.save()

            OrderObject.save()
            messages.success(request, "تم الطلب! تحقق من طلباتك.")
            return redirect('cart')
        else:
            messages.error(request, "سلة التسوق فارغة.")
            return redirect('cart')
    city = City.objects.all()
    context = {
        'products': products,
        'total': total,
        'city': city,
    }
    return render(request, 'pages/cartPage.html', context)


def orders(request):
    if not request.user.is_authenticated:
        return redirect('mainPage')
    orders = Orders.objects.filter(user=request.user)
    for order in orders:
        products = UserProductOrder.objects.filter(order_id=order.id)

    search_query = request.GET.get('q', '')
    if search_query != '':
        selected_status = 'all'
        orders = orders.filter(id=int(search_query))

    else:
        selected_status = request.GET.get('status', 'all')

        if selected_status != 'all':
            orders = orders.filter(status=selected_status)

    orders = orders.order_by('-order_date')
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'selected_status': selected_status,
    }
    return render(request, 'pages/orders.html', context)


def deleteOrder(request, id):
    if not request.user.is_authenticated:
        return redirect('mainPage')
    order = Orders.objects.get(id=id)
    products = UserProductOrder.objects.filter(order_id=order.id)
    for item in products:
        item.product.quantity += item.quantity
        item.product.number_of_sales -= item.quantity
        item.product.save()

    if order.user != request.user:
        return redirect('mainPage')
    order.delete()
    return redirect('orders')


def orderDetail(request, id):
    if not request.user.is_authenticated:
        return redirect('mainPage')
    order = Orders.objects.get(id=id)
    if order.user != request.user:
        return redirect('mainPage')
    products = UserProductOrder.objects.filter(order_id=order.id)
    context = {
        'order': order,
        'products': products,

    }
    return render(request, 'pages/orderDetail.html', context)


def userInfo(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')

    user1 = CustomUser.objects.get(id=id)

    pending_orders = Orders.objects.filter(user=user1, status='بانتظار التأكيد')
    confirmed_orders = Orders.objects.filter(user=user1, status='تم التأكيد')
    delivered_orders = Orders.objects.filter(user=user1, status='تم التسليم')

    total_paid = delivered_orders.aggregate(total=models.Sum('total_price'))['total'] or 0

    context = {
        'user1': user1,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'delivered_orders': delivered_orders,
        'total_paid': total_paid,
    }

    return render(request, 'pages/userInfo.html', context)


def salesPage(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('mainPage')
    return render(request, 'pages/sales.html')


def generate_sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)

        delivered_orders = Orders.objects.filter(
            status='تم التسليم',
            delivered_time__range=(start_date, end_date)
        )
    else:
        delivered_orders = Orders.objects.none()

    total_sales = sum(order.total_price for order in delivered_orders)

    context = {
        'delivered_orders': delivered_orders,
        'total_sales': total_sales,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'report_date': datetime.now().strftime('%Y-%m-%d')
    }

    template = get_template('pages/sales_report_template.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="sales_report.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
        return HttpResponse(f'Error generating PDF: {pisa_status.err}', status=400)

    return response
