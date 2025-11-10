from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_migrate)
def create_default_superadmin(sender, **kwargs):
    if sender.name == 'engine':
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                    username='admin',
                    first_name='Admin',
                    last_name='TokoCoding',
                    email='admin@tokocoding.com',
                    password='password123',
                    is_staff=True,
                    is_active=True,
                    is_superuser=True
                )
            print("Default admin user created: admin / password123")