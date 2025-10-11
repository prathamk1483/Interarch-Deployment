from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.loginView,name="login"),
    path('home/',views.index,name= 'home'),
    path('userCreationPage/', views.userCreationPage, name='createUserPage'),
    path('createClient/', views.createClient, name='createClient'),
    path('userSearchingPage/', views.userSearchingPage, name='userSearchPage'),
    path('searchClient/', views.searchClient, name='searchClient'),
    path('getInvoice/', views.getInvoice, name='getInvoice'),
    path('userUpdationPage/', views.userUpdationPage, name='userUpdatePage'),
    path('updateClient/', views.updateClient, name='updateClient'),
    path('updateClientInfo/<str:client_id>', views.updateClientInfo, name='updateClientInfo'),
    path('userDeletionPage/', views.userDeletionPage, name='userDeletePage'),
    path('deleteClient/', views.deleteClient, name='deleteClient'),
    path('logout/',views.logoutView,name = 'logout'),
    path('uploads/<str:folder_name>/', views.list_uploads, name='list_uploads'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
