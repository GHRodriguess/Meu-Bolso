from rest_framework import serializers
from .models import Conta, Categoria, Transacao, Recorrente

class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = '__all__'


class RecorrenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recorrente
        fields = '__all__'