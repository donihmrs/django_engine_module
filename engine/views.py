import json
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse

from engine.module_loader import get_available_modules, load_active_modules, settings_app_add_module, settings_app_remove_module, upgrade_module_loader
from engine.models.module import Module
from pathlib import Path 

def home(request):
    if not request.user.is_superuser:
        return redirect('admin:login')
    
    return redirect('view_all_modules')
def load_permissions(request, module_name="none"):
    user = request.user

    if user.is_superuser:
        return JsonResponse({'can_view': True, 'can_add': True, 'can_change': True, 'can_delete': True})
    
    # Cek permission user
    can_view = user.has_perm(f"{module_name}.view_module_{module_name}")
    can_add = user.has_perm(f"{module_name}.add_module_{module_name}")
    can_change = user.has_perm(f"{module_name}.change_module_{module_name}")
    can_delete = user.has_perm(f"{module_name}.delete_module_{module_name}")

    return JsonResponse({'can_view': can_view, 'can_add': can_add, 'can_change': can_change, 'can_delete': can_delete})

def reload_modules(request):
    if not request.user.is_superuser:
        return redirect('admin:login')
    
    try:
        load_active_modules()
        messages.success(request, "Modules reloaded successfully.")
    except Exception as e:
        messages.error(request, f"Error reloading modules: {str(e)}")

    return redirect('view_all_modules')

def view_all_modules(request):
    if not request.user.is_superuser:
        return redirect('admin:login')
    
    modules_dir = get_available_modules()
    modules_db = Module.objects.all().values('name', 'slug','author', 'is_active')
    modules = []

    # Check modules_db have a data
    if modules_db:
        print("Modules found in database.")
        for mod in modules_dir:
            mod_info = mod.copy()
            db_entry = next((item for item in modules_db if item["slug"] == mod["slug"]), None)
            if db_entry:
                mod_info.update({
                    "name": db_entry["name"],
                    "author": db_entry["author"],
                    "is_active": db_entry["is_active"],
                })
            modules.append(mod_info)

    else:
        print("No modules found in database. Using filesystem data.")
        modules = modules_dir
    
    # Return render to a templates admin
    return render(request, 'engine/module_list.html', {'modules': modules})

def install_module(request, module_slug):
    if not request.user.is_superuser:
        return JsonResponse({"status":"error", "message": "Not authorized"}, status=403)
    try:
        module, created = Module.objects.get_or_create(slug=module_slug)

        if created:
            base_path = Path(f"modules/{module_slug}")
            module_json = base_path / "module.json"
            if not module_json.exists():
                raise FileNotFoundError(f"module.json not found for {module_slug}")
            
            with open(module_json, "r") as f:
                meta = json.load(f)

                module.name = meta.get("name", module_slug)
                module.slug = meta.get("slug", module_slug)
                module.author = meta.get("author", "-")
                module.version = meta.get("version", "0.0.0")
                module.is_active = True
                module.save()
        else:
            module.is_active = True
            module.save()

        settings_app_add_module(module_slug)
        load_active_modules()

        messages.success(request, f"Module {module_slug} installed successfully")
    except Module.DoesNotExist:
        messages.warning(request, f"Module {module_slug} Module not found")
    
    return redirect('view_all_modules')

def uninstall_module(request, module_slug):
    if not request.user.is_superuser:
        return redirect('admin:login')
    try:
        module = Module.objects.get(slug=module_slug)
        module.is_active = False
        module.save()
        settings_app_remove_module(module_slug)

        messages.success(request, f"Module {module_slug} uninstalled successfully")
    except Module.DoesNotExist:
        messages.warning(request, f"Module {module_slug} Module not found")
    
    return redirect('view_all_modules')

def upgrade_module(request, module_slug):
    if not request.user.is_superuser:
        return redirect('admin:login')
    try:
        getNewVersion = upgrade_module_loader(module_slug)

        module = Module.objects.get(slug=module_slug)
        module.version = getNewVersion 
        module.save()

        messages.success(request, f"Module {module_slug} upgraded successfully to version {getNewVersion}")
    except Module.DoesNotExist:
        messages.warning(request, f"Module {module_slug} Module not found")

    return redirect('view_all_modules')
