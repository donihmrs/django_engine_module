import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from engine.module_loader import render_module_template
from engine.views import load_permissions
from .models import Product

def index(request):
    get_permissions = json.loads(load_permissions(request).content)

    return render(request, 'product/templates/page/index.html', {'user_permissions': get_permissions})

def list_product_backup(request):
    # Cara render module template ini akan memperlambat sedikit prosesnya
    product = Product.objects.all().values('name', 'barcode', 'price', 'stock')
    html = render_module_template('product', 'page/list.html', {'products': product})
    
    return HttpResponse(html)

def list_product(request):
    get_permissions = json.loads(load_permissions(request).content)

    if not get_permissions.get('can_view', False):
        return JsonResponse({"status":"error", "message": "Not authorized"}, status=403)
    
    product = Product.objects.all().values('name', 'barcode', 'price', 'stock')
    return render(request, 'product/templates/page/list.html', {'products': product})

def detail(request, id):
    try:
        if request.method == 'GET':
            product = Product.objects.get(id=id)
            data = {
                "name": product.name,
                "barcode": product.barcode,
                "price": str(product.price),
                "stock": product.stock,
            }
            return JsonResponse(data)
        
        return JsonResponse({"status":"error", "message": "Invalid request method"}, status=400)

    except Product.DoesNotExist:
        return JsonResponse({"status":"error", "message": "Product not found"}, status=404)
    
def create_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        barcode = request.POST.get('barcode')
        price = request.POST.get('price')
        stock = request.POST.get('stock')

        product = Product.objects.create(
            name=name,
            barcode=barcode,
            price=price,
            stock=stock
        )
        return JsonResponse({"status":"success", "message": "Product created", "product_id": product.id})
    return JsonResponse({"status":"error", "message": "Invalid request method"}, status=400)

#Update Product method PUT

def update_product(request, id):
    if request.method == 'PUT':
        try:
            product = Product.objects.get(id=id)
            name = request.PUT.get('name')
            barcode = request.PUT.get('barcode')
            price = request.PUT.get('price')
            stock = request.PUT.get('stock')

            product.name = name
            product.barcode = barcode
            product.price = price
            product.stock = stock
            product.save()

            return JsonResponse({"status":"success", "message": "Product updated"})
        except Product.DoesNotExist:
            return JsonResponse({"status":"error", "message": "Product not found"}, status=404)
    return JsonResponse({"status":"error", "message": "Invalid request method"}, status=400)

def delete_product(request, id):
    if request.method == 'DELETE':
        try:
            product = Product.objects.get(id=id)
            product.delete()
            return JsonResponse({"status":"success", "message": "Product deleted"})
        except Product.DoesNotExist:
            return JsonResponse({"status":"error", "message": "Product not found"}, status=404)
    return JsonResponse({"status":"error", "message": "Invalid request method"}, status=400)

