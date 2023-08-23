# from djoser.views import UserViewSet
# from rest_framework import status
# from rest_framework.response import Response
# from .models import CustomUser
# from .serializers import CustomUserCreateSerializer
from django.shortcuts import render, redirect
from .models import Chat
from .forms import ChatMessageForm

def chat_detail_view(request, chat_id):
    chat = Chat.objects.get(pk=chat_id)
    return render(request, 'admin_chat_page.html', {'chat': chat})


def add_chat_message(request, chat_id):
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.user = request.user
            chat_message.chat_id = chat_id
            chat_message.save()
    return redirect('admin:core_chat_change', chat_id)

# class CustomUserViewSet(UserViewSet):
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return CustomUserCreateSerializer
#         return super().get_serializer_class()