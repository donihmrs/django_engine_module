from django.urls import path
from django.shortcuts import redirect
from . import views

def redirect_to_home(request):
    return redirect('index/')

app_name = 'product'

urlpatterns = [
    path('', redirect_to_home),
    path('index/', views.index, name='index'),
    path('list/', views.list_product, name='list'),
    path('create/', views.create_product, name='add_product'),
    path('update/<int:id>/', views.update_product, name='update_product'),
    path('delete/<int:id>/', views.delete_product, name='delete_product'),
    path('detail/<int:id>/', views.detail, name='detail_product'),
    path('login/', views.login_auth, name='login_auth'),
    path('logout/', views.logout_auth, name='logout_auth'),
]