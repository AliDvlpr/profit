from rest_framework.decorators import action, permission_classes
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .permissions import FullDjangoModelPermissions, IsAdminOrReadOnly
from .models import *
from .serilaizers import *

# Create your views here.
class AssetViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset =Asset.objects.all()
    serializer_class = AssetSerializer
    
    @action(detail=False, methods=['GET'])
    def me(self, request):
        (asset, created) = Asset.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = AssetSerializer(asset)  # Make sure you're passing an instance, not a string
            return Response(serializer.data)
        
class LevelViewSet(ModelViewSet):
    queryset = Level.objects.prefetch_related('images', 'attributes').all()
    serializer_class = LevelSerializer
    ordering_fields = ['name', 'profit_rate', 'min_refferral', 'min_deposit']


    def get_permissions(self):
        return [IsAdminOrReadOnly()]