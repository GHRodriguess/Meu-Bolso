from django.contrib import admin
from .models import Conta, Categoria, Transacao, Recorrente

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'saldo', 'saldo_atual')
    search_fields = ('nome',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'conta', 'tipo', 'valor', 'categoria', 'realizado', 'data')
    list_filter = ('tipo', 'realizado', 'categoria', 'conta')
    search_fields = ('descricao',)
    date_hierarchy = 'data'


@admin.register(Recorrente)
class RecorrenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'valor', 'conta', 'recorrente_tipo', 'parcela_atual', 'parcela_total', 'ativo', 'proxima_execucao')
    list_filter = ('tipo', 'recorrente_tipo', 'ativo', 'periodicidade')
    search_fields = ('nome',)
    readonly_fields = ('parcela_atual',)
