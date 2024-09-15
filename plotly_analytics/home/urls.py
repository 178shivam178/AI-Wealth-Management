from django.urls import path,include
from . import views
from home.dash_apps.finished_apps import home_page


urlpatterns = [
    path('', views.home, name = 'home'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('search/', views.search_view, name='search_view'),
    # path('HomePage', home_page, name="home_page")
]
