# from djoser.views import UserViewSet
# from rest_framework import status
# from rest_framework.response import Response
# from .models import CustomUser
# from .serializers import CustomUserCreateSerializer

# class CustomUserViewSet(UserViewSet):
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return CustomUserCreateSerializer
#         return super().get_serializer_class()