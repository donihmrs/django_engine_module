# engine/middleware.py
import importlib, os

class ModularMiddlewareRouter:
    def __init__(self, get_response):
        self.get_response = get_response
        self.module_middlewares = []
        self.load_module_middlewares()

    def load_module_middlewares(self):
        base_dir = os.path.join(os.getcwd(), "modules")
        
        for module in os.listdir(base_dir):
            mw_path = f"modules.{module}.middleware"
            try:
                mod = importlib.import_module(mw_path)
                if hasattr(mod, "process_view"):
                    self.module_middlewares.append(mod)
                    print(f"Loaded module middleware: {mw_path}")
            except ModuleNotFoundError:
                continue

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        for mod in self.module_middlewares:
            if hasattr(mod, "process_view"):
                result = mod.process_view(request, view_func, view_args, view_kwargs)
                if result:
                    return result
