from rest_framework.decorators import action, permission_classes
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .permissions import *
from .models import *
from .serilaizers import *

# Create your views here.
class AssetViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Asset.objects.all()
    permission_classes = [IsAuthenticated, ReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'partial_update':
            return UpdateAssetSerializer
        return AssetSerializer
    
    def get(self, request):
        asset, created = Asset.objects.get_or_create(user=request.user)  # Use square brackets
        if request.method == 'GET':
            serializer = AssetSerializer(asset)
            return Response(serializer.data)
        
class LevelViewSet(ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    ordering_fields = ['name', 'profit_rate', 'min_refferral', 'min_deposit']


    def get_permissions(self):
        return [IsAdminOrReadOnly()]
    
class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [IsUserOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransactionSerializer
        return TransactionSerializer
    
    def get_queryset(self):
        user = self.request.user

        return Transaction.objects.filter(user=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        asset = Asset.objects.get(user=user)
        serializer.save(asset=asset, user=user)