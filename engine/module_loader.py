import importlib, os, sys
from django.core.management import call_command
from django.conf import settings
from django.apps import apps, AppConfig
from django.db.utils import ProgrammingError, OperationalError
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
        from engine.models.module import Module
        
        active_modules = Module.objects.filter(is_active=True)
        for mod in active_modules:
            try:
                full_module_path = f"modules.{mod.slug}"
                print(f"Adding module to INSTALLED_APPS: {full_module_path}")

                # Tambahkan ke INSTALLED_APPS secara dinamis
                if full_module_path not in settings.INSTALLED_APPS:
                    settings.INSTALLED_APPS.append(full_module_path)
                    print(f"{full_module_path} added to INSTALLED_APPS")

                # Reload modules views, urls, models
                reload_modules(mod.slug)
        
                print(f"Loaded module: {mod.name}")
            except ModuleNotFoundError as e:
                print(f"Module {mod.slug} not found in /modules folder: {e}")
                return False
            
        apps.set_installed_apps(settings.INSTALLED_APPS)
        reload_dynamic_urls()

        reload_templates()
    except (ProgrammingError, OperationalError ) as e:
        print(f"Error Load active balance: {e}")
        return False
    except ImportError as e:
        print(f"Error Load active balance import: {e}")
        return False

    return True

def get_dynamic_urls():    
    if settings.START_APP_ON_LOAD:
        print("Initial app loading, setting up installed apps...")
        
        apps.set_installed_apps(settings.INSTALLED_APPS)
        settings.START_APP_ON_LOAD = False

    urlpatterns = []

    try :
        print("Getting dynamic URLs for active modules...")

        from engine.models.module import Module
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
    except (ProgrammingError, OperationalError ) as e:
        print(f"Error getting dynamic URLs Programming: {e}")
    except ImportError as e:
        print(f"Error getting dynamic URL Import: {e}")

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
        # Reload modules views, urls, models
        reload_modules(module_name)

        if apps.is_installed(full_path):
            print(f"Running makemigrations + migrate for {module_name}")
            call_command('makemigrations', module_name, interactive=False)
            call_command('migrate', module_name, interactive=False)
        else:
            print(f" App '{module_name}' not found in registry.")

        print(f"Reloaded models for {module_name}")
    except ModuleNotFoundError:
        print(f"No models.py for {module_name}, skipping models reload")

def reload_templates():
    try :
        print("Reloading template loaders...")
        from django.template import engines

        for engine in engines.all():
            if hasattr(engine, 'engine') and hasattr(engine.engine, 'template_loaders'):
                for loader in engine.engine.template_loaders:
                    if hasattr(loader, 'reset'):
                        loader.reset()
    except Exception as e:
        print(f"Error resetting template loaders: {e}")

def reload_modules(module_name: str):
    try: 
        module_path_urls = f"modules.{module_name}.urls"
        module_path_models = f"modules.{module_name}.models"
        module_path_views = f"modules.{module_name}.views"

        if module_path_views in sys.modules:
            # reload modul yang sudah di-import
            importlib.reload(sys.modules[module_path_views])
        else:
            # import modul pertama kali
            importlib.import_module(module_path_views)

        if module_path_urls in sys.modules:
            importlib.reload(sys.modules[module_path_urls])
        else:
            importlib.import_module(module_path_urls)

        if module_path_models in sys.modules:
            importlib.reload(sys.modules[module_path_models])
        else:
            importlib.import_module(module_path_models)

        return True
    except ModuleNotFoundError as e:
        print(f"Module {module_name} not found in /modules folder: {e}")
        return False
    

def render_module_template(module_name: str, template_name: str, context: dict):
    from django.template import Engine, Context, TemplateDoesNotExist

    module_templates_dir = Path(settings.BASE_DIR) / "modules" / module_name / "templates"
    
    print(f"Rendering template from: {module_templates_dir} - {template_name}")
    # Buat template engine sementara khusus modul
    engine = Engine(
        loaders=[
            ('django.template.loaders.filesystem.Loader', [str(module_templates_dir)]),
        ],
        debug=settings.DEBUG,
    )
    
    try:
        template = engine.get_template(template_name)
    except TemplateDoesNotExist as e:
        print(f"TemplateDoesNotExist: {e}")
        raise TemplateDoesNotExist(f"Template '{template_name}' not found in {module_templates_dir}")
    
    return template.render(Context(context))