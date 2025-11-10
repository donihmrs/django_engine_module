from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.utils import OperationalError, ProgrammingError

User = get_user_model()

@receiver(post_migrate)
def create_roles(sender, **kwargs):
    if sender.name == 'modules.product': 
        # Role: manager, user, public
        try:
            # === Pastikan tabel sudah ada ===
            content_type, _ = ContentType.objects.get_or_create(
                app_label='product', 
                model='module_product'  
            )

            # === Buat custom permissions ===
            custom_permissions = [
                ('add_module_product', 'Can add module product'),
                ('change_module_product', 'Can change module product'),
                ('delete_module_product', 'Can delete module product'),
                ('view_module_product', 'Can view module product'),
            ]

            for codename, name in custom_permissions:
                Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    name=name
                )

            # === Buat groups ===
            manager_group, _ = Group.objects.get_or_create(name='manager')
            user_group, _ = Group.objects.get_or_create(name='user')
            public_group, _ = Group.objects.get_or_create(name='public')

            # Ambil semua permissions untuk module_product
            all_perms = Permission.objects.filter(content_type=content_type)

            # Manager → CRUD
            manager_group.permissions.set(all_perms)

            # User → CRU
            user_perms = all_perms.filter(codename__in=[
                'add_module_product',
                'change_module_product',
                'view_module_product',
            ])
            user_group.permissions.set(user_perms)

            # Public → R
            public_perms = all_perms.filter(codename__in=['view_module_product'])
            public_group.permissions.set(public_perms)

            print("Roles dan permission RBAC Product berhasil diperbarui.")

            # === Buat Default Users ===
            default_users = [
                {
                    'username': 'manager',
                    'first_name': 'Manager',
                    'last_name': 'TokoCoding',
                    'email': 'manager@tokocoding.com',
                    'password': 'password123',
                    'group': manager_group,
                },
                {
                    'username': 'staff',
                    'first_name': 'Staff',
                    'last_name': 'TokoCoding',
                    'email': 'staff@tokocoding.com',
                    'password': 'password123',
                    'group': user_group,
                },
                {
                    'username': 'public',
                    'first_name': 'Public',
                    'last_name': 'TokoCoding',
                    'email': 'public@tokocoding.com',
                    'password': 'password123',
                    'group': public_group,
                },
            ]

            for u in default_users:
                if not User.objects.filter(username=u['username']).exists():
                    user = User.objects.create_user(
                        username=u['username'],
                        first_name=u['first_name'],
                        last_name=u['last_name'],
                        email=u['email'],
                        password=u['password'],
                        is_staff=True,
                    )
                    user.groups.add(u['group'])
                    print(f"Default user created: {u['username']} / {u['password']}")

        except (OperationalError, ProgrammingError) as e:
            print(f"Skip create_roles_and_permissions (DB belum siap): {e}")