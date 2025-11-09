import json
from django.shortcuts import render
from django.http import JsonResponse

from engine.module_loader import get_available_modules, load_active_modules, settings_app_add_module, settings_app_remove_module, upgrade_module_loader
from engine.models import Module
from pathlib import Path 

def reload_modules(request):
    if not request.user.is_superuser:
        return JsonResponse({"status":"error", "message": "Not authorized"}, status=403)
    load_active_modules()
    return JsonResponse({"status":"success", "message": "Modules reloaded successfully"})

def view_all_modules(request):
    if not request.user.is_superuser:
        return JsonResponse({"status":"error", "message": "Not authorized"}, status=403)    

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
    except Module.DoesNotExist:
        return JsonResponse({"status":"error", "message": "Module not found"}, status=404)
    
    return JsonResponse({"status":"success", "message": f"Module {module_slug} installed successfully"})

def uninstall_module(request, module_slug):
    if not request.user.is_superuser:
        return JsonResponse({"status":"error", "message": "Not authorized"}, status=403)
    try:
        module = Module.objects.get(slug=module_slug)
        module.is_active = False
        module.save()
        settings_app_remove_module(module_slug)
    except Module.DoesNotExist:
        return JsonResponse({"status":"error", "message": "Module not found"}, status=404)
    
    return JsonResponse({"status":"success", "message": f"Module {module_slug} uninstalled successfully"})

def upgrade_module(request, module_slug):
    if not request.user.is_superuser:
        return JsonResponse({"status":"error", "message": "Not authorized"}, status=403)
    try:
        getNewVersion = upgrade_module_loader(module_slug)

        module = Module.objects.get(slug=module_slug)
        module.version = getNewVersion 
        module.save()

        return JsonResponse({"status":"success","message": f"Module {module_slug} upgraded successfully to version {getNewVersion}"})
    except Module.DoesNotExist:
        return JsonResponse({"status":"error", "message": "Module not found"}, status=404)
