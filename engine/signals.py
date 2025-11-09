from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()
@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == 'adminapi':
        if not User.objects.filter(role='admin').exists():
            User.objects.create_superuser(
                username='admin',
                first_name='Admin',
                last_name='TokoCoding',
                email='admin@tokocoding.com',
                password='password123',
                is_staff=True,
            )
            print("Default admin user created: admin / password123")

        # Create user role manager dan staff

        if not User.objects.filter(role='manager').exists():
            User.objects.create_user(
                username='manager',
                first_name='Manager',
                last_name='TokoCoding',
                email='manager@tokocoding.com',
                password='password123',
                is_staff=True,
            )  

            print("Default manager user created: manager / password123")

        if not User.objects.filter(role='staff').exists():
            User.objects.create_user(
                username='staff',
                first_name='Staff',
                last_name='TokoCoding',
                email='staff@tokocoding.com',
                password='password123',
                is_staff=True,
            )

            print("Default staff user created: staff / password123")
