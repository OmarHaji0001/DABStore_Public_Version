from mainapp.models import Theme, Category, Product


def storeTheme(request):
    theme = Theme.objects.get(id=1)
    return {'theme': theme}

def getTopSales(request):
    topProducts = Product.objects.order_by('-number_of_sales')[:9]
    return {'top_selling_products': topProducts}

def getCategory(request):
    categories = Category.objects.exclude(name='Default')
    return {'categories': categories}
