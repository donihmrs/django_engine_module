from django.urls import path
from engine.views import install_module, uninstall_module, uninstall_module, upgrade_module, reload_modules, view_all_modules

urlpatterns = [
    path('reload-modules', reload_modules, name='reload_modules'),
    path('module', view_all_modules, name='view_all_modules'),
    path('install-module/<slug:module_slug>', install_module, name='install_module'),
    path('uninstall-module/<slug:module_slug>', uninstall_module, name='uninstall_module'),
    path('upgrade-module/<slug:module_slug>', upgrade_module, name='upgrade_module'),
]
