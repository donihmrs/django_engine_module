from django.http import JsonResponse
from django.shortcuts import render
from .models import Product

def handle_request(request):
    return JsonResponse({"status":"success", "message": "Product module active!"})

def list_product(request):
    product = Product.objects.all().values('name', 'barcode', 'price', 'stock')
    return render(request, 'page/list.html', {'products': product})
    
def index(request):
    return JsonResponse({"status":"success", "message": "Welcome to the Product Module"})  

def detail(request, id):
    try:
        product = Product.objects.get(id=id)
        data = {
            "name": product.name,
            "barcode": product.barcode,
            "price": str(product.price),
            "stock": product.stock,
        }
        return JsonResponse(data)
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

