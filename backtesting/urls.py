from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),


    path('start/', views.start, name='start'),
    path('process_data_source/', views.process_data_source, name='process_data_source'), 
    
    path('analytical_page/', views.analytical_page, name='analytical_page'), 
    path('search/', views.search, name='search'),  
    path('handle/', views.handle, name='handle'),

    path('backtest/', views.backtest, name='backtest'),
    path('backtest_run/', views.backtest_run, name='backtest_run'),
    path('update_current_tickers/', views.update_current_tickers, name='update_current_tickers')

]