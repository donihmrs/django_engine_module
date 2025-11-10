from django.http import JsonResponse

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

def process_view(request, view_func, view_args, view_kwargs):
    # Jalankan hanya untuk path yang terkait dengan 'product'
    if not request.path.startswith('/product'):
        return None

    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # Mapping method -> permission
    if request.method in SAFE_METHODS:
        perm_code = 'modules.product.view_module_product'
    elif request.method == 'POST':
        perm_code = 'modules.product.add_module_product'
    elif request.method in ['PUT', 'PATCH']:
        perm_code = 'modules.product.change_module_product'
    elif request.method == 'DELETE':
        perm_code = 'modules.product.delete_module_product'
    else:
        perm_code = None

    print(f"Checking permission for user: {user.username}, method: {request.method}, required perm: {perm_code}")

    if perm_code and not user.has_perm(perm_code):
        return JsonResponse({
            'error': f'Access denied: Missing {perm_code}'
        }, status=403)

    return None