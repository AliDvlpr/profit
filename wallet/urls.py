from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('asset', views.AssetViewSet, basename="asset")
router.register('level', views.LevelViewSet, basename='level')
router.register('transaction',views.TransactionViewSet, basename='transaction')
router.register('dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = router.urls