from django.http import JsonResponse
from django.urls import resolve
from django.shortcuts import redirect

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
EXEMPT_URLS = ['index','login_auth','logout_aut', 'admin']

def process_view(request, view_func, view_args, view_kwargs):
    # Jalankan hanya untuk path yang terkait dengan 'product'
    if not request.path.startswith('/product'):
        return None
    
    path = resolve(request.path_info).url_name

    print(f"Middleware triggered for path: {request.path}, resolved name: {path}")

    if not request.user.is_authenticated and path not in EXEMPT_URLS:
        return redirect('product:index')

    user = request.user

    if user.is_superuser:
        return None  # Superuser punya akses penuh
    
    print(user.get_all_permissions())
    
    # Mapping method -> permission
    if request.method in SAFE_METHODS:
        perm_code = 'product.view_module_product'
    elif request.method == 'POST':
        perm_code = 'product.add_module_product'
    elif request.method in ['PUT', 'PATCH']:
        perm_code = 'product.change_module_product'
    elif request.method == 'DELETE':
        perm_code = 'product.delete_module_product'
    else:
        perm_code = None

    print(f"Checking permission for user: {user.username}, method: {request.method}, required perm: {perm_code}")

    if perm_code and not user.has_perm(perm_code) and path not in EXEMPT_URLS:
        return JsonResponse({
            'error': f'Access denied: Missing {perm_code}'
        }, status=403)

    return None