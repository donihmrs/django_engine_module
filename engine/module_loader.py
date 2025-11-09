import importlib, os
from django.core.management import call_command
from django.conf import settings
from django.apps import apps, AppConfig
from django.urls import include, path, clear_url_caches
from pathlib import Path 
import json

MODULES_DIR = os.path.abspath(os.path.join(os.getcwd(), "modules"))

def get_available_modules():
    base_path = Path(f"modules")
    modules = []

    if not base_path.exists():
        return []

    for module_dir in base_path.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith("__"):
            info = {
                "name": module_dir.name,
                "slug": module_dir.name,
                "path": str(module_dir),
                "version": "unknown",
                "description": "",
                "is_active": False,
            }

            json_file = module_dir / "module.json"
            if json_file.exists():
                try:
                    data = json.loads(json_file.read_text())
                    info.update({
                        "name": data.get("name", module_dir.name),
                        "slug": data.get("slug", module_dir.name),
                        "author": data.get("author", "-"),
                        "version": data.get("version", "0.0.0"),
                        "description": data.get("description", ""),
                    })
                except Exception as e:
                    info["description"] = f"⚠️ Error reading module.json: {e}"

            modules.append(info)

    return modules

def load_active_modules():
    try :
        print("Loading all modules...")
        from engine.models import Module

        active_modules = Module.objects.filter(is_active=True)
        for mod in active_modules:
            try:
                print(f"Loading module: {mod.slug}")
                importlib.import_module(f"modules.{mod.slug}.views")
                importlib.import_module(f"modules.{mod.slug}.urls")

                full_module_path = f"modules.{mod.slug}"
                print(f"Adding module to INSTALLED_APPS: {full_module_path}")
                # 1 Tambahkan ke INSTALLED_APPS secara dinamis
                if full_module_path not in settings.INSTALLED_APPS:
                    settings.INSTALLED_APPS.append(full_module_path)
                    print(f"{full_module_path} added to INSTALLED_APPS")
                
                print(f"Loaded module: {mod.name}")
            except ModuleNotFoundError as e:
                print(f"Module {mod.slug} not found in /modules folder: {e}")
                return False
            
        reload_dynamic_urls()
    except Exception as e:
        print(f"Error loading modules: {e}")
        return False

    return True

def get_dynamic_urls():
    urlpatterns = []

    try :
        print("Getting dynamic URLs for active modules...")

        from engine.models import Module
        active_modules = Module.objects.filter(is_active=True)

        for mod in active_modules:
            try:
                # Coba import urls.py dari module tersebut
                urls_module = importlib.import_module(f"modules.{mod.slug}.urls")

                urlpatterns.append(
                    path(f"{mod.slug}/", include((urls_module.urlpatterns, mod.slug)))
                )
                print(f"URL loaded for module: {mod.slug}")
            except ModuleNotFoundError:
                print(f"No urls.py found for module: {mod.slug}")
            except Exception as e:
                print(f"Error loading {mod.slug}: {e}")
    except Exception as e:
        print(f"Error getting dynamic URLs: {e}")
        urlpatterns = []    

    return urlpatterns

def settings_app_add_module(module_name: str):
    full_path = f"modules.{module_name}"
    print(f"Adding module to INSTALLED_APPS: {full_path}")
    
    if full_path not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append(full_path)
        print(f"{full_path} added to INSTALLED_APPS")
    
    try:
        try :
            print(f"Loading dynamic app: {full_path}")
            
            # Reload dynamic apps
            reload_dynamic_apps(full_path, module_name)
        except Exception as e:
            print(f"Error loading dynamic app {module_name}: {e}")
            
        return True
    except ModuleNotFoundError:
        print(f"Module {module_name} not found")
        return False

def settings_app_remove_module(module_name: str):
    full_module_path = f"modules.{module_name}"
    if full_module_path in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.remove(full_module_path)
        print(f"{full_module_path} removed from INSTALLED_APPS")

    load_active_modules()

    return True

def upgrade_module_loader(module_name: str):
    try:
        importlib.import_module(f"modules.{module_name}")
        print(f"Upgrading module: {module_name}...")

        base_path = Path(f"modules/{module_name}")
        module_json = base_path / "module.json"
        if not module_json.exists():
            raise FileNotFoundError(f"module.json not found for {module_name}")
        
        with open(module_json, "r") as f:
            meta = json.load(f)

        version = meta.get("version", "0.0.0")

        full_path = f"modules.{module_name}"

        # Reload dynamic apps
        reload_dynamic_apps(full_path, module_name)

        print(f"Module '{module_name}' upgraded successfully.")

        load_active_modules()

        return version
    except Exception as e:
        print(f"Upgrade failed for module '{module_name}': {e}")
        return "0.0.0"

def reload_dynamic_urls():
    from enginemoduledoni import urls

    clear_url_caches()
    importlib.reload(urls)
    print("Dynamic URLs reloaded.")

    return True


def reload_dynamic_apps(full_path: str, module_name: str):
    module = importlib.import_module(full_path)

    # Cari apps.py dan ambil Config class
    try:
        app_module = importlib.import_module(f"{full_path}.apps")
        importlib.reload(app_module)

        app_config_class = None
        for name in dir(app_module):
            attr = getattr(app_module, name)
            if isinstance(attr, type) and issubclass(attr, AppConfig) and attr is not AppConfig:
                app_config_class = attr
                break

        print(f"Found AppConfig class: {app_config_class}")
    except ModuleNotFoundError:
        print(f"No apps.py found for module: {module_name}, using default AppConfig")
        app_config_class = AppConfig  # fallback

    app_config = app_config_class(full_path, module)

    print(f"Created AppConfig instance: {app_config}")

    # Registrasi manual
    print(f"Registering app: {app_config.label}")
    apps.app_configs[app_config.label] = app_config

    if full_path not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append(full_path)

    apps.set_installed_apps(settings.INSTALLED_APPS)

    try:
        models_module = importlib.import_module(f"{full_path}.models")
        importlib.reload(models_module)

        if apps.is_installed(full_path):
            print(f"Running makemigrations + migrate for {module_name}")
            call_command('makemigrations', module_name, interactive=False)
            call_command('migrate', module_name, interactive=False)
        else:
            print(f" App '{module_name}' not found in registry.")

        print(f"Reloaded models for {module_name}")
    except ModuleNotFoundError:
        print(f"No models.py for {module_name}, skipping models reload")