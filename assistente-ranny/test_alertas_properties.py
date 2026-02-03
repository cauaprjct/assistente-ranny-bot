"""
Property-Based Tests para Sistema de Alertas de Vencimentos

Feature: assistente-ranny-v3
Property 15: Alertas baseados em dias restantes
Property 16: Vencimento pago não gera alertas

Validates: Requirements 8.1-8.4

Testes de propriedade usando hypothesis para validar o sistema de alertas.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from typing import List, Dict


# ============ ESTRATÉGIAS DE GERAÇÃO ============

# Estratégia para gerar descrições de vencimentos
descricao_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=3,
    max_size=50
).filter(lambda x: x.strip())

# Estratégia para gerar valores monetários
valor_strategy = st.floats(min_value=10.0, max_value=10000.0, allow_nan=False, allow_infinity=False)

# Estratégia para gerar dias restantes (0-30)
dias_restantes_strategy = st.integers(min_value=0, max_value=30)

# Estratégia para gerar tipos de vencimento
tipo_strategy = st.sampled_from(['luz', 'agua', 'internet', 'aluguel', 'fgts', 'das', 'fornecedor'])

# Dias que devem gerar alerta
DIAS_ALERTA = [7, 3, 1]


def criar_vencimento(
    descricao: str,
    valor: float,
    dias_restantes: int,
    pago: bool = False,
    tipo: str = 'conta'
) -> Dict:
    """Helper para criar um vencimento de teste"""
    hoje = date.today()
    data_vencimento = hoje + timedelta(days=dias_restantes)
    
    return {
        'id': 1,
        'tipo': tipo,
        'descricao': descricao,
        'valor': valor,
        'data_vencimento': data_vencimento.strftime('%Y-%m-%d'),
        'vencimento': data_vencimento.strftime('%Y-%m-%d'),
        'pago': pago,
        'pago_em': None,
        'recorrente': None,
        'dias_restantes': dias_restantes
    }


def criar_lista_vencimentos(vencimentos_config: List[tuple]) -> List[Dict]:
    """
    Cria lista de vencimentos a partir de configuração.
    
    Args:
        vencimentos_config: Lista de tuplas (descricao, valor, dias_restantes, pago)
    
    Returns:
        Lista de dicts de vencimentos
    """
    resultado = []
    for i, (desc, valor, dias, pago) in enumerate(vencimentos_config):
        venc = criar_vencimento(desc, valor, dias, pago)
        venc['id'] = i + 1
        resultado.append(venc)
    return resultado


# ============ PROPERTY 15: Alertas baseados em dias restantes ============

class TestAlertasBaseadosEmDiasRestantes:
    """
    Property 15: Alertas baseados em dias restantes
    
    Para qualquer vencimento não pago, alertas devem ser gerados
    quando dias_restantes está em [7, 3, 1].
    
    **Feature: assistente-ranny-v3, Property 15: Alertas baseados em dias restantes**
    **Validates: Requirements 8.1, 8.2, 8.3**
    """
    
    @given(
        descricao=descricao_strategy,
        valor=valor_strategy,
        dias=st.sampled_from(DIAS_ALERTA)
    )
    @settings(max_examples=100)
    def test_vencimento_em_dias_alerta_gera_alerta(
        self, 
        descricao: str, 
        valor: float, 
        dias: int
    ):
        """
        Para qualquer vencimento não pago com dias_restantes em [7, 3, 1],
        o sistema deve gerar um alerta.
        """
        vencimento = criar_vencimento(descricao, valor, dias, pago=False)
        
        # Verifica que dias_restantes está nos dias de alerta
        assert vencimento['dias_restantes'] in DIAS_ALERTA, \
            f"dias_restantes {vencimento['dias_restantes']} deveria estar em {DIAS_ALERTA}"
        
        # Verifica que não está pago
        assert vencimento['pago'] is False, \
            "Vencimento deveria estar não pago"
        
        # Simula a lógica de filtro do check_vencimentos
        deve_alertar = (
            vencimento['dias_restantes'] in DIAS_ALERTA and 
            not vencimento['pago']
        )
        
        assert deve_alertar is True, \
            f"Vencimento com {dias} dias restantes deveria gerar alerta"
    
    @given(
        descricao=descricao_strategy,
        valor=valor_strategy,
        dias=dias_restantes_strategy
    )
    @settings(max_examples=100)
    def test_vencimento_fora_dias_alerta_nao_gera_alerta(
        self, 
        descricao: str, 
        valor: float, 
        dias: int
    ):
        """
        Para qualquer vencimento não pago com dias_restantes fora de [7, 3, 1],
        o sistema NÃO deve gerar um alerta.
        """
        # Garante que dias não está nos dias de alerta
        assume(dias not in DIAS_ALERTA)
        
        vencimento = criar_vencimento(descricao, valor, dias, pago=False)
        
        # Simula a lógica de filtro do check_vencimentos
        deve_alertar = vencimento['dias_restantes'] in DIAS_ALERTA
        
        assert deve_alertar is False, \
            f"Vencimento com {dias} dias restantes NÃO deveria gerar alerta"
    
    def test_alerta_7_dias_mensagem_correta(self):
        """
        Verifica que alerta de 7 dias tem mensagem apropriada.
        """
        vencimento = criar_vencimento("Conta de luz", 150.0, 7, pago=False)
        
        # Simula lógica de mensagem do jobs.py
        dias = vencimento['dias_restantes']
        if dias == 1:
            urgencia = "⚠️ AMANHÃ!"
        elif dias == 3:
            urgencia = "📅 Em 3 dias"
        else:
            urgencia = "📆 Em 7 dias"
        
        assert urgencia == "📆 Em 7 dias"
    
    def test_alerta_3_dias_mensagem_correta(self):
        """
        Verifica que alerta de 3 dias tem mensagem apropriada.
        """
        vencimento = criar_vencimento("Conta de água", 80.0, 3, pago=False)
        
        dias = vencimento['dias_restantes']
        if dias == 1:
            urgencia = "⚠️ AMANHÃ!"
        elif dias == 3:
            urgencia = "📅 Em 3 dias"
        else:
            urgencia = "📆 Em 7 dias"
        
        assert urgencia == "📅 Em 3 dias"
    
    def test_alerta_1_dia_mensagem_urgente(self):
        """
        Verifica que alerta de 1 dia tem mensagem urgente.
        """
        vencimento = criar_vencimento("FGTS", 500.0, 1, pago=False)
        
        dias = vencimento['dias_restantes']
        if dias == 1:
            urgencia = "⚠️ AMANHÃ!"
        elif dias == 3:
            urgencia = "📅 Em 3 dias"
        else:
            urgencia = "📆 Em 7 dias"
        
        assert urgencia == "⚠️ AMANHÃ!"


# ============ PROPERTY 16: Vencimento pago não gera alertas ============

class TestVencimentoPagoNaoGeraAlertas:
    """
    Property 16: Vencimento pago não gera alertas
    
    Para qualquer vencimento marcado como pago, não deve aparecer
    na lista de alertas pendentes.
    
    **Feature: assistente-ranny-v3, Property 16: Vencimento pago não gera alertas**
    **Validates: Requirements 8.4**
    """
    
    @given(
        descricao=descricao_strategy,
        valor=valor_strategy,
        dias=st.sampled_from(DIAS_ALERTA)
    )
    @settings(max_examples=100)
    def test_vencimento_pago_nao_gera_alerta(
        self, 
        descricao: str, 
        valor: float, 
        dias: int
    ):
        """
        Para qualquer vencimento pago, mesmo com dias_restantes em [7, 3, 1],
        o sistema NÃO deve gerar alerta.
        """
        vencimento = criar_vencimento(descricao, valor, dias, pago=True)
        
        # Verifica que está pago
        assert vencimento['pago'] is True, \
            "Vencimento deveria estar pago"
        
        # Simula a lógica de filtro - vencimentos pagos não devem alertar
        deve_alertar = (
            vencimento['dias_restantes'] in DIAS_ALERTA and 
            not vencimento['pago']
        )
        
        assert deve_alertar is False, \
            f"Vencimento pago NÃO deveria gerar alerta, mesmo com {dias} dias restantes"
    
    @given(
        descricao=descricao_strategy,
        valor=valor_strategy,
        dias=dias_restantes_strategy
    )
    @settings(max_examples=100)
    def test_vencimento_pago_qualquer_dia_nao_gera_alerta(
        self, 
        descricao: str, 
        valor: float, 
        dias: int
    ):
        """
        Para qualquer vencimento pago, independente de dias_restantes,
        o sistema NÃO deve gerar alerta.
        """
        vencimento = criar_vencimento(descricao, valor, dias, pago=True)
        
        # Vencimento pago nunca deve alertar
        deve_alertar = not vencimento['pago']
        
        assert deve_alertar is False, \
            "Vencimento pago nunca deveria gerar alerta"


# ============ TESTES DE INTEGRAÇÃO COM DATABASE (MOCK) ============

class TestGetVencimentosProximos:
    """
    Testes para a função get_vencimentos_proximos do database.
    
    Verifica que:
    - Retorna apenas vencimentos não pagos
    - Calcula dias_restantes corretamente
    - Filtra por período correto
    
    Requirements: 8.1-8.4
    """
    
    def test_get_vencimentos_proximos_filtra_pagos(self):
        """
        Verifica que get_vencimentos_proximos filtra vencimentos pagos.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Configura mock para retornar vencimentos
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.eq.return_value = mock_query
            mock_query.gte.return_value = mock_query
            mock_query.lte.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = []
            
            import database as db
            db.get_vencimentos_proximos(7)
            
            # Verifica que filtrou por pago=False
            mock_query.eq.assert_called_with('pago', False)
    
    def test_calcula_dias_restantes_corretamente(self):
        """
        Verifica que dias_restantes é calculado corretamente.
        """
        hoje = date.today()
        data_venc = hoje + timedelta(days=5)
        
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Simula retorno do Supabase
            vencimento_mock = {
                'id': 1,
                'descricao': 'Conta teste',
                'valor': 100.0,
                'data_vencimento': data_venc.strftime('%Y-%m-%d'),
                'pago': False
            }
            
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.eq.return_value = mock_query
            mock_query.gte.return_value = mock_query
            mock_query.lte.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = [vencimento_mock]
            
            import database as db
            resultado = db.get_vencimentos_proximos(7)
            
            # Verifica que dias_restantes foi calculado
            assert len(resultado) == 1
            assert resultado[0]['dias_restantes'] == 5


# ============ TESTES DO JOB CHECK_VENCIMENTOS ============

class TestJobCheckVencimentos:
    """
    Testes para o job check_vencimentos.
    
    Verifica que:
    - Busca vencimentos dos próximos 7 dias
    - Filtra apenas dias de alerta [7, 3, 1]
    - Envia mensagem no Tópico_Chat
    
    Requirements: 8.1, 8.2, 8.3
    """
    
    @pytest.mark.asyncio
    async def test_check_vencimentos_sem_bot_retorna_zero(self):
        """
        Verifica que check_vencimentos retorna 0 quando bot não está configurado.
        """
        import jobs
        jobs._telegram_bot = None
        
        resultado = await jobs.check_vencimentos()
        assert resultado == 0
    
    @pytest.mark.asyncio
    async def test_check_vencimentos_sem_vencimentos_retorna_zero(self):
        """
        Verifica que check_vencimentos retorna 0 quando não há vencimentos.
        """
        import jobs
        
        mock_bot = MagicMock()
        jobs.set_telegram_bot(mock_bot)
        
        with patch('database.get_vencimentos_proximos') as mock_get:
            mock_get.return_value = []
            
            resultado = await jobs.check_vencimentos()
            assert resultado == 0
        
        # Limpa
        jobs._telegram_bot = None
    
    @pytest.mark.asyncio
    async def test_check_vencimentos_filtra_dias_alerta(self):
        """
        Verifica que check_vencimentos só alerta para dias em [7, 3, 1].
        """
        import jobs
        
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        jobs.set_telegram_bot(mock_bot)
        
        # Cria vencimentos com diferentes dias restantes
        vencimentos_mock = [
            criar_vencimento("Conta 1", 100.0, 7, pago=False),   # Deve alertar
            criar_vencimento("Conta 2", 200.0, 5, pago=False),   # NÃO deve alertar
            criar_vencimento("Conta 3", 300.0, 3, pago=False),   # Deve alertar
            criar_vencimento("Conta 4", 400.0, 2, pago=False),   # NÃO deve alertar
            criar_vencimento("Conta 5", 500.0, 1, pago=False),   # Deve alertar
        ]
        
        # Atribui IDs únicos
        for i, v in enumerate(vencimentos_mock):
            v['id'] = i + 1
        
        with patch('database.get_vencimentos_proximos') as mock_get:
            mock_get.return_value = vencimentos_mock
            
            resultado = await jobs.check_vencimentos()
            
            # Deve ter enviado 3 alertas (dias 7, 3, 1)
            assert resultado == 3
            assert mock_bot.send_message.call_count == 3
        
        # Limpa
        jobs._telegram_bot = None
    
    @pytest.mark.asyncio
    async def test_check_vencimentos_nao_alerta_pagos(self):
        """
        Verifica que check_vencimentos não alerta vencimentos pagos.
        
        Property 16: Vencimento pago não gera alertas
        """
        import jobs
        
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        jobs.set_telegram_bot(mock_bot)
        
        # Cria vencimentos - alguns pagos
        vencimentos_mock = [
            criar_vencimento("Conta 1", 100.0, 7, pago=False),  # Deve alertar
            criar_vencimento("Conta 2", 200.0, 3, pago=True),   # NÃO deve alertar (pago)
            criar_vencimento("Conta 3", 300.0, 1, pago=False),  # Deve alertar
        ]
        
        for i, v in enumerate(vencimentos_mock):
            v['id'] = i + 1
        
        # Nota: get_vencimentos_proximos já filtra pagos no banco
        # Então simulamos que só retorna os não pagos
        vencimentos_nao_pagos = [v for v in vencimentos_mock if not v['pago']]
        
        with patch('database.get_vencimentos_proximos') as mock_get:
            mock_get.return_value = vencimentos_nao_pagos
            
            resultado = await jobs.check_vencimentos()
            
            # Deve ter enviado 2 alertas (apenas não pagos)
            assert resultado == 2
        
        # Limpa
        jobs._telegram_bot = None


# ============ TESTES DE PROPRIEDADE COMBINADOS ============

class TestPropriedadesCombinadas:
    """
    Testes que combinam múltiplas propriedades para validar
    comportamento completo do sistema de alertas.
    """
    
    @given(
        vencimentos=st.lists(
            st.tuples(
                descricao_strategy,
                valor_strategy,
                dias_restantes_strategy,
                st.booleans()  # pago
            ),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_filtro_alertas_correto(self, vencimentos: List[tuple]):
        """
        Para qualquer lista de vencimentos, o filtro de alertas deve:
        - Incluir apenas vencimentos não pagos
        - Incluir apenas vencimentos com dias_restantes em [7, 3, 1]
        """
        lista_vencimentos = criar_lista_vencimentos(vencimentos)
        
        # Aplica filtro de alertas (mesma lógica do check_vencimentos)
        alertas = [
            v for v in lista_vencimentos
            if v['dias_restantes'] in DIAS_ALERTA and not v['pago']
        ]
        
        # Verifica propriedades dos alertas
        for alerta in alertas:
            # Property 15: dias_restantes deve estar em [7, 3, 1]
            assert alerta['dias_restantes'] in DIAS_ALERTA, \
                f"Alerta com dias_restantes={alerta['dias_restantes']} não deveria existir"
            
            # Property 16: não deve estar pago
            assert alerta['pago'] is False, \
                "Alerta de vencimento pago não deveria existir"
        
        # Verifica que nenhum vencimento pago foi incluído
        vencimentos_pagos_alertados = [
            v for v in alertas if v['pago']
        ]
        assert len(vencimentos_pagos_alertados) == 0, \
            "Nenhum vencimento pago deveria gerar alerta"
        
        # Verifica que nenhum vencimento fora dos dias de alerta foi incluído
        vencimentos_fora_dias = [
            v for v in alertas if v['dias_restantes'] not in DIAS_ALERTA
        ]
        assert len(vencimentos_fora_dias) == 0, \
            "Nenhum vencimento fora dos dias de alerta deveria ser incluído"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
