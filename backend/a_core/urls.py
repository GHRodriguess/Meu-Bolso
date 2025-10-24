from rest_framework import routers
from django.urls import path, include
from .viewsets import ContaViewSet, CategoriaViewSet, TransacaoViewSet, RecorrenteViewSet

router = routers.DefaultRouter()
router.register(r'contas', ContaViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'transacoes', TransacaoViewSet)
router.register(r'recorrentes', RecorrenteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]