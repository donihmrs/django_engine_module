from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='product_index'),
    path('create/', views.create_product, name='create_product'),
    path('update/<int:id>/', views.update_product, name='update_product'),
    path('delete/<int:id>/', views.delete_product, name='delete_product'),
    path('detail/<int:id>/', views.detail, name='product_detail'),
]