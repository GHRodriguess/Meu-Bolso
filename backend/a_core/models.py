from django.db import models
from djmoney.models.fields import MoneyField
from datetime import date
from django.conf import settings
from dateutil.relativedelta import relativedelta 


class Conta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contas', null=True, blank=True)
    nome = models.CharField(max_length=100)
    saldo_atual = MoneyField(max_digits=12, decimal_places=2, default_currency='BRL', default=0)
    saldo = MoneyField(max_digits=12, decimal_places=2, default_currency='BRL', default=0)
    
    def __str__(self):
        return self.nome
    
class Categoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categorias', null=True, blank=True)
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    
class Transacao(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transacoes', null=True, blank=True)
    conta = models.ForeignKey('Conta', on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = MoneyField(max_digits=12, decimal_places=2, default_currency='BRL')
    descricao = models.CharField(max_length=255, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes')
    data = models.DateTimeField(auto_now_add=True)
    realizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.descricao}"

    def save(self, *args, **kwargs):
        if self.pk:
            antiga = Transacao.objects.get(pk=self.pk)

            if antiga.tipo == 'entrada':
                antiga.conta.saldo -= antiga.valor
            else:
                antiga.conta.saldo += antiga.valor

            if antiga.realizado:
                if antiga.tipo == 'entrada':
                    antiga.conta.saldo_atual -= antiga.valor
                else:
                    antiga.conta.saldo_atual += antiga.valor

            antiga.conta.save()

        super().save(*args, **kwargs)

        if self.tipo == 'entrada':
            self.conta.saldo += self.valor
            if self.realizado:
                self.conta.saldo_atual += self.valor
        else:
            self.conta.saldo -= self.valor
            if self.realizado:
                self.conta.saldo_atual -= self.valor

        self.conta.save()
        

class Recorrente(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    CATEGORIA_TIPO_CHOICES = [
        ('assinatura', 'Assinatura'),
        ('parcela', 'Parcela'),
        ('conta', 'Conta'),
        ('financiamento', 'Financiamento'),
    ]

    PERIODICIDADE_CHOICES = [
        ('diario', 'Diário'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recorrentes', null=True, blank=True)
    conta = models.ForeignKey('Conta', on_delete=models.CASCADE, related_name='recorrentes')
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorrentes')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = MoneyField(max_digits=12, decimal_places=2, default_currency='BRL')
    periodicidade = models.CharField(max_length=10, choices=PERIODICIDADE_CHOICES, default='mensal')
    proxima_execucao = models.DateField(default=date.today)
    recorrente_tipo = models.CharField(max_length=20, choices=CATEGORIA_TIPO_CHOICES, default='assinatura')
    parcela_total = models.PositiveIntegerField(null=True, blank=True)
    parcela_atual = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()}) - {self.valor}"

    def deve_executar(self):
        return self.ativo and self.proxima_execucao <= date.today()

    def gerar_transacao(self):
        if not self.deve_executar():
            return None

        from .models import Transacao 

        if self.recorrente_tipo == 'parcela':
            self.parcela_atual += 1
            descricao = f"{self.nome} {self.parcela_atual}/{self.parcela_total}"
        else:
            descricao = self.nome 

        transacao = Transacao.objects.create(
            conta=self.conta,
            tipo=self.tipo,
            valor=self.valor,
            descricao=descricao,
            categoria=self.categoria,
            realizado=True
        )

        if self.periodicidade == 'diario':
            self.proxima_execucao += relativedelta(days=1)
        elif self.periodicidade == 'semanal':
            self.proxima_execucao += relativedelta(weeks=1)
        elif self.periodicidade == 'mensal':
            self.proxima_execucao += relativedelta(months=1)
        elif self.periodicidade == 'anual':
            self.proxima_execucao += relativedelta(years=1)

        if self.recorrente_tipo == 'parcela' and self.parcela_total and self.parcela_atual >= self.parcela_total:
            self.ativo = False

        self.save()
        return transacao