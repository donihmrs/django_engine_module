from django.apps import AppConfig
from django.core.management import call_command
from django.db import connection
from django.apps import apps

class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.product'
    label = 'product'

    def ready(self):
        try:
            print("[Product] Checking and applying migrations...")

            # if not apps.is_installed('modules.product'):
            #     print("[Product] App not installed in INSTALLED_APPS yet.")
            
            # with connection.cursor() as cursor:
            #     cursor.execute("SHOW TABLES LIKE 'product_product';")
            #     table_exists = cursor.fetchone()

            # print(table_exists)
            
            # if not table_exists:
            #     print("DEBUG: Migration check complete.")

            #     call_command('makemigrations', 'product', interactive=False)
            #     print("OK1")
            #     call_command('migrate', 'product', interactive=False)
            #     print("[Product] Migration complete.")
            # else:
            #     print("[Product] Already migrated.")

            return
        except Exception as e:
            print(f"[Product] Migration skipped: {e}")
