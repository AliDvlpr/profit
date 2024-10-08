from rest_framework.decorators import action, permission_classes
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from .permissions import *
from .models import *
from .serilaizers import *
from core.models import *
from .filters import *
from core.serializers import *

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
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = TransactionFilter

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransactionSerializer
        return TransactionSerializer
    
    def get_queryset(self):
        user = self.request.user
        asset = Asset.objects.get(user=user)
        return Transaction.objects.filter(asset=asset)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        asset = Asset.objects.get(user=user)

        #Validate action type
        action = request.data.get('action')
        if action == Transaction.ACTION_DEPOSIT:
            transaction_id = request.data.get('transaction_id')
            if not transaction_id:
                return Response({'error': 'transaction id cannot be blank for deposit action.'}, status=status.HTTP_400_BAD_REQUEST)
        elif action == Transaction.ACTION_WITHDRAW:
            wallet_address = request.data.get('wallet_address')
            if not wallet_address:
                return Response({'error': 'wallet address cannot be blank for withdraw action.'}, status=status.HTTP_400_BAD_REQUEST)
            
            amount = Decimal(request.data.get('amount', 0))
            if amount > (Decimal(asset.amount) + Decimal(user.credit)):
                return Response({'error': 'The requested withdrawal amount exceeds your available assets and credited profit.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(asset=asset, user=user, created_at=timezone.now())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DashboardViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated] 
    serializer_class = UserDashboardSerializer

    def get_queryset(self):
        user = self.request.user
        return CustomUser.objects.filter(pk=user.pk)
    
class ChatViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated] 
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        user = self.request.user
        chat, created = Chat.objects.get_or_create(user=user)
        return ChatMessage.objects.filter(chat=chat)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        chat, created = Chat.objects.get_or_create(user=user)
        serializer = CreateMessageSerializer(data={
            'content': request.data['content'],
            'chat': chat.pk,
            'user': user.pk
        })
        if serializer.is_valid():
            serializer.save()
            chat.status = 'P'
            chat.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SettingViewSet(ListModelMixin, GenericViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    