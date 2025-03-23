from django.urls import path
from .views import chat_api, chat_page

urlpatterns = [
    path('', chat_page, name='chat_page'),
    path('api/chat/', chat_api, name='chat_api'),
]
