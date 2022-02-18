from django.urls import path
from . import views

app_name='product'

urlpatterns = [
        path('search/', views.search, name='search'),
        path('select/<category_name>', views.select_category, name ='select'),
        path('search_name/<search_key>', views.search_name, name='search_name'),         # search inside a product/ brand/ category page
        path('sort/<search_key>/<sort_type>', views.sort, name='sort'),         # search inside a product/ brand/ category page
        path('filter/<search_key>/<filter_type>', views.filter, name='filter'),         # search inside a product/ brand/ category page
]