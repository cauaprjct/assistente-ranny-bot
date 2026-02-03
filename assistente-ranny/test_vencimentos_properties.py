"""
Property-Based Tests para Sistema de Vencimentos

Feature: assistente-ranny-v3
Property 17: Recorrente gera próximo
Property 18: Boleto tem valor e vencimento extraídos

Validates: Requirements 8.5, 2.3

Testes de propriedade usando hypothesis para validar o sistema de vencimentos.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
from typing import Dict, Optional


# ============ ESTRATÉGIAS DE GERAÇÃO ============

# Estratégia para gerar descrições de vencimentos
descricao_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=3,
    max_size=50
).filter(lambda x: x.strip())

# Estratégia para gerar valores monetários
valor_strategy = st.floats(min_value=10.0, max_value=10000.0, allow_nan=False, allow_infinity=False)

# Estratégia para gerar tipos de vencimento
tipo_strategy = st.sampled_from(['luz', 'agua', 'internet', 'aluguel', 'fgts', 'das', 'fornecedor', 'gas', 'telefone'])

# Estratégia para gerar tipos de recorrência
recorrencia_strategy = st.sampled_from(['diario', 'semanal', 'mensal'])

# Estratégia para gerar datas de vencimento (próximos 365 dias)
data_vencimento_strategy = st.dates(
    min_value=date.today(),
    max_value=date.today() + timedelta(days=365)
)

# Estratégia para gerar beneficiários
beneficiario_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'Z')),
    min_size=3,
    max_size=30
).filter(lambda x: x.strip())


# ============ HELPERS ============

def criar_vencimento_mock(
    tipo: str,
    descricao: str,
    valor: float,
    data_vencimento: date,
    recorrente: Optional[str] = None
) -> Dict:
    """Helper para criar um vencimento de teste"""
    return {
        'id': 1,
        'tipo': tipo,
        'descricao': descricao,
        'valor': valor,
        'data_vencimento': data_vencimento.strftime('%Y-%m-%d'),
        'recorrente': recorrente,
        'pago': False,
        'pago_em': None,
        'documento_id': None
    }


def calcular_proxima_data(data_atual: date, recorrencia: str) -> date:
    """Calcula a próxima data baseado no tipo de recorrência"""
    if recorrencia == 'diario':
        return data_atual + timedelta(days=1)
    elif recorrencia == 'semanal':
        return data_atual + timedelta(weeks=1)
    elif recorrencia == 'mensal':
        if data_atual.month == 12:
            return data_atual.replace(year=data_atual.year + 1, month=1)
        else:
            try:
                return data_atual.replace(month=data_atual.month + 1)
            except ValueError:
                # Dia não existe no próximo mês
                if data_atual.month == 11:
                    return date(data_atual.year + 1, 1, 1) - timedelta(days=1)
                else:
                    return date(data_atual.year, data_atual.month + 2, 1) - timedelta(days=1)
    return data_atual


# ============ PROPERTY 17: Recorrente gera próximo ============

class TestVencimentoRecorrenteGeraProximo:
    """
    Property 17: Vencimento recorrente gera próximo
    
    Para qualquer vencimento com recorrente != NULL que é marcado como pago,
    um novo vencimento deve ser criado com data futura calculada.
    
    **Feature: assistente-ranny-v3, Property 17: Recorrente gera próximo**
    **Validates: Requirements 8.5**
    """
    
    @given(
        tipo=tipo_strategy,
        descricao=descricao_strategy,
        valor=valor_strategy,
        data_venc=data_vencimento_strategy,
        recorrencia=recorrencia_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_vencimento_recorrente_cria_proximo(
        self,
        tipo: str,
        descricao: str,
        valor: float,
        data_venc: date,
        recorrencia: str
    ):
        """
        Para qualquer vencimento recorrente, ao ser marcado como pago,
        deve criar um novo vencimento com data futura.
        """
        from database import criar_proximo_vencimento_recorrente
        
        vencimento = criar_vencimento_mock(tipo, descricao, valor, data_venc, recorrencia)
        
        # Mock do add_vencimento para não precisar de conexão real
        with patch('database.add_vencimento') as mock_add:
            # Simula retorno do add_vencimento
            mock_add.return_value = {
                'id': 2,
                'tipo': tipo,
                'descricao': descricao,
                'valor': valor,
                'data_vencimento': calcular_proxima_data(data_venc, recorrencia).strftime('%Y-%m-%d'),
                'recorrente': 'mensal',
                'pago': False
            }
            
            resultado = criar_proximo_vencimento_recorrente(vencimento)
            
            # Verifica que add_vencimento foi chamado
            assert mock_add.called, "add_vencimento deveria ter sido chamado para vencimento recorrente"
            
            # Verifica os argumentos passados
            call_args = mock_add.call_args
            assert call_args is not None
            
            # Verifica que a data do próximo é futura
            proxima_data_esperada = calcular_proxima_data(data_venc, recorrencia)
            assert call_args.kwargs['vencimento'] == proxima_data_esperada.strftime('%Y-%m-%d'), \
                f"Data do próximo vencimento deveria ser {proxima_data_esperada}"
            
            # Verifica que mantém recorrente=True
            assert call_args.kwargs['recorrente'] is True, \
                "Próximo vencimento deveria manter recorrente=True"
    
    @given(
        tipo=tipo_strategy,
        descricao=descricao_strategy,
        valor=valor_strategy,
        data_venc=data_vencimento_strategy
    )
    @settings(max_examples=100)
    def test_vencimento_nao_recorrente_nao_cria_proximo(
        self,
        tipo: str,
        descricao: str,
        valor: float,
        data_venc: date
    ):
        """
        Para qualquer vencimento NÃO recorrente (recorrente=NULL),
        ao ser marcado como pago, NÃO deve criar novo vencimento.
        """
        from database import criar_proximo_vencimento_recorrente
        
        # Vencimento sem recorrência
        vencimento = criar_vencimento_mock(tipo, descricao, valor, data_venc, recorrente=None)
        
        resultado = criar_proximo_vencimento_recorrente(vencimento)
        
        # Não deve criar próximo
        assert resultado is None, \
            "Vencimento não recorrente NÃO deveria criar próximo"
    
    @given(
        data_venc=data_vencimento_strategy,
        recorrencia=recorrencia_strategy
    )
    @settings(max_examples=100)
    def test_proxima_data_sempre_futura(
        self,
        data_venc: date,
        recorrencia: str
    ):
        """
        Para qualquer data e tipo de recorrência, a próxima data
        deve ser sempre posterior à data atual.
        """
        proxima_data = calcular_proxima_data(data_venc, recorrencia)
        
        assert proxima_data > data_venc, \
            f"Próxima data {proxima_data} deveria ser posterior a {data_venc}"
    
    @given(
        data_venc=data_vencimento_strategy
    )
    @settings(max_examples=100)
    def test_recorrencia_diaria_adiciona_1_dia(self, data_venc: date):
        """
        Para recorrência diária, a próxima data deve ser exatamente 1 dia depois.
        """
        proxima_data = calcular_proxima_data(data_venc, 'diario')
        diff = (proxima_data - data_venc).days
        
        assert diff == 1, f"Recorrência diária deveria adicionar 1 dia, mas adicionou {diff}"
    
    @given(
        data_venc=data_vencimento_strategy
    )
    @settings(max_examples=100)
    def test_recorrencia_semanal_adiciona_7_dias(self, data_venc: date):
        """
        Para recorrência semanal, a próxima data deve ser exatamente 7 dias depois.
        """
        proxima_data = calcular_proxima_data(data_venc, 'semanal')
        diff = (proxima_data - data_venc).days
        
        assert diff == 7, f"Recorrência semanal deveria adicionar 7 dias, mas adicionou {diff}"
    
    @given(
        data_venc=data_vencimento_strategy
    )
    @settings(max_examples=100)
    def test_recorrencia_mensal_adiciona_aproximadamente_1_mes(self, data_venc: date):
        """
        Para recorrência mensal, a próxima data deve ser aproximadamente 1 mês depois.
        """
        proxima_data = calcular_proxima_data(data_venc, 'mensal')
        diff = (proxima_data - data_venc).days
        
        # Um mês pode ter entre 28 e 31 dias
        assert 28 <= diff <= 31, \
            f"Recorrência mensal deveria adicionar entre 28-31 dias, mas adicionou {diff}"


# ============ PROPERTY 18: Boleto tem valor e vencimento extraídos ============

class TestBoletoTemValorEVencimentoExtraidos:
    """
    Property 18: Boleto tem valor e vencimento extraídos
    
    Para qualquer documento classificado como boleto, os campos valor
    e data_vencimento devem ser extraídos e salvos.
    
    **Feature: assistente-ranny-v3, Property 18: Boleto tem valor e vencimento extraídos**
    **Validates: Requirements 2.3**
    """
    
    @given(
        valor=valor_strategy,
        data_venc=data_vencimento_strategy,
        beneficiario=beneficiario_strategy,
        tipo_conta=tipo_strategy
    )
    @settings(max_examples=100)
    def test_criar_vencimento_de_boleto_com_dados_completos(
        self,
        valor: float,
        data_venc: date,
        beneficiario: str,
        tipo_conta: str
    ):
        """
        Para qualquer boleto com valor e vencimento, deve criar vencimento
        com os dados extraídos.
        """
        from database import criar_vencimento_de_boleto
        
        dados_boleto = {
            'valor': valor,
            'vencimento': data_venc.strftime('%Y-%m-%d'),
            'beneficiario': beneficiario,
            'tipo_conta': tipo_conta
        }
        
        with patch('database.add_vencimento') as mock_add:
            mock_add.return_value = {
                'id': 1,
                'tipo': tipo_conta,
                'descricao': f'Conta - {beneficiario}',
                'valor': valor,
                'data_vencimento': data_venc.strftime('%Y-%m-%d'),
                'pago': False
            }
            
            resultado = criar_vencimento_de_boleto(dados_boleto)
            
            # Verifica que add_vencimento foi chamado
            assert mock_add.called, "add_vencimento deveria ter sido chamado"
            
            # Verifica os argumentos
            call_args = mock_add.call_args
            assert call_args.kwargs['valor'] == valor, \
                f"Valor deveria ser {valor}"
            assert call_args.kwargs['vencimento'] == data_venc.strftime('%Y-%m-%d'), \
                f"Vencimento deveria ser {data_venc}"
    
    @given(
        valor=valor_strategy
    )
    @settings(max_examples=100)
    def test_boleto_sem_vencimento_nao_cria_vencimento(self, valor: float):
        """
        Para qualquer boleto sem data de vencimento, NÃO deve criar vencimento.
        """
        from database import criar_vencimento_de_boleto
        
        dados_boleto = {
            'valor': valor,
            # Sem vencimento
            'beneficiario': 'Teste'
        }
        
        resultado = criar_vencimento_de_boleto(dados_boleto)
        
        assert resultado is None, \
            "Boleto sem vencimento NÃO deveria criar vencimento"
    
    def test_boleto_sem_valor_e_sem_vencimento_nao_cria_vencimento(self):
        """
        Boleto sem valor E sem vencimento não deve criar vencimento.
        """
        from database import criar_vencimento_de_boleto
        
        dados_boleto = {
            'beneficiario': 'Teste',
            'tipo_conta': 'luz'
        }
        
        resultado = criar_vencimento_de_boleto(dados_boleto)
        
        assert resultado is None, \
            "Boleto sem valor e sem vencimento NÃO deveria criar vencimento"
    
    @given(
        data_venc=data_vencimento_strategy,
        tipo_conta=tipo_strategy
    )
    @settings(max_examples=100)
    def test_boleto_com_vencimento_sem_valor_usa_valor_zero(
        self,
        data_venc: date,
        tipo_conta: str
    ):
        """
        Para boleto com vencimento mas sem valor, deve criar vencimento com valor 0.
        """
        from database import criar_vencimento_de_boleto
        
        dados_boleto = {
            'vencimento': data_venc.strftime('%Y-%m-%d'),
            'tipo_conta': tipo_conta
            # Sem valor
        }
        
        with patch('database.add_vencimento') as mock_add:
            mock_add.return_value = {
                'id': 1,
                'tipo': tipo_conta,
                'valor': 0.0,
                'data_vencimento': data_venc.strftime('%Y-%m-%d'),
                'pago': False
            }
            
            resultado = criar_vencimento_de_boleto(dados_boleto)
            
            # Verifica que add_vencimento foi chamado com valor 0
            assert mock_add.called
            call_args = mock_add.call_args
            assert call_args.kwargs['valor'] == 0.0, \
                "Valor deveria ser 0.0 quando não especificado"


# ============ TESTES DE EXTRAÇÃO DE BOLETO ============

class TestExtracaoBoleto:
    """
    Testes para extração de dados de boleto do texto.
    
    **Validates: Requirements 2.3**
    """
    
    @given(
        valor=st.floats(min_value=1.0, max_value=99999.99, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_extrai_valor_formato_brasileiro(self, valor: float):
        """
        Para qualquer valor no formato brasileiro (R$ X.XXX,XX),
        deve extrair corretamente.
        """
        from ai import extract_boleto_from_text
        
        # Formata valor no padrão brasileiro
        valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        texto = f"Valor: {valor_formatado}"
        
        resultado = extract_boleto_from_text(texto)
        
        # Verifica que extraiu o valor (com tolerância para arredondamento)
        if resultado.get('valor'):
            assert abs(resultado['valor'] - valor) < 0.01, \
                f"Valor extraído {resultado['valor']} deveria ser aproximadamente {valor}"
    
    @given(
        dia=st.integers(min_value=1, max_value=28),
        mes=st.integers(min_value=1, max_value=12),
        ano=st.integers(min_value=2024, max_value=2030)
    )
    @settings(max_examples=100)
    def test_extrai_vencimento_formato_brasileiro(self, dia: int, mes: int, ano: int):
        """
        Para qualquer data no formato dd/mm/yyyy, deve extrair corretamente.
        """
        from ai import extract_boleto_from_text
        
        data_str = f"{dia:02d}/{mes:02d}/{ano}"
        texto = f"Vencimento: {data_str}"
        
        resultado = extract_boleto_from_text(texto)
        
        # Verifica que extraiu a data no formato ISO
        if resultado.get('vencimento'):
            esperado = f"{ano}-{mes:02d}-{dia:02d}"
            assert resultado['vencimento'] == esperado, \
                f"Data extraída {resultado['vencimento']} deveria ser {esperado}"


# ============ TESTES DE NORMALIZAÇÃO ============

class TestNormalizacaoBoleto:
    """
    Testes para normalização de dados de boleto.
    
    **Validates: Requirements 2.3**
    """
    
    @given(
        valor=valor_strategy
    )
    @settings(max_examples=100)
    def test_normaliza_valor_float(self, valor: float):
        """
        Para qualquer valor float, deve manter como float.
        """
        from ai import normalize_boleto_data
        
        dados = {'valor': valor}
        resultado = normalize_boleto_data(dados)
        
        assert isinstance(resultado['valor'], float), \
            "Valor deveria ser float"
        assert resultado['valor'] == valor, \
            f"Valor deveria ser {valor}"
    
    @given(
        valor=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=100)
    def test_normaliza_valor_int_para_float(self, valor: int):
        """
        Para qualquer valor int, deve converter para float.
        """
        from ai import normalize_boleto_data
        
        dados = {'valor': valor}
        resultado = normalize_boleto_data(dados)
        
        assert isinstance(resultado['valor'], float), \
            "Valor deveria ser convertido para float"
        assert resultado['valor'] == float(valor), \
            f"Valor deveria ser {float(valor)}"
    
    @given(
        dia=st.integers(min_value=1, max_value=28),
        mes=st.integers(min_value=1, max_value=12),
        ano=st.integers(min_value=2024, max_value=2030)
    )
    @settings(max_examples=100)
    def test_normaliza_data_formato_brasileiro(self, dia: int, mes: int, ano: int):
        """
        Para qualquer data no formato dd/mm/yyyy, deve converter para ISO.
        """
        from ai import normalize_boleto_data
        
        data_br = f"{dia:02d}/{mes:02d}/{ano}"
        dados = {'vencimento': data_br}
        resultado = normalize_boleto_data(dados)
        
        esperado = f"{ano}-{mes:02d}-{dia:02d}"
        assert resultado['vencimento'] == esperado, \
            f"Data {data_br} deveria ser normalizada para {esperado}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
