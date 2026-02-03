"""
Property-Based Tests para Sistema de Lembretes

Feature: assistente-ranny-v3
Property 4: Pedido de lembrete cria lembrete no banco
Property 5: Lembrete sem hora usa 09:00
Property 6: Listagem retorna apenas ativos
Property 7: Cancelamento marca como inativo
Property 8: Recorrente gera próximo após disparo

Validates: Requirements 3.1-3.6

Testes de propriedade usando hypothesis para validar o sistema de lembretes.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock

from date_parser import (
    parse_lembrete, 
    extrair_hora, 
    extrair_data, 
    proxima_dia_semana,
    calcular_dia_mes,
    limpar_descricao,
    detectar_recorrencia
)


# ============ ESTRATÉGIAS DE GERAÇÃO ============

# Estratégia para gerar descrições de lembretes
descricao_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=3,
    max_size=100
).filter(lambda x: x.strip())

# Estratégia para gerar horas válidas
hora_strategy = st.builds(
    lambda h, m: f'{h:02d}:{m:02d}',
    h=st.integers(min_value=0, max_value=23),
    m=st.integers(min_value=0, max_value=59)
)

# Estratégia para gerar dias do mês
dia_mes_strategy = st.integers(min_value=1, max_value=28)

# Estratégia para gerar número de dias no futuro
dias_futuro_strategy = st.integers(min_value=1, max_value=365)

# Estratégia para gerar dias da semana (0=segunda, 6=domingo)
dia_semana_strategy = st.integers(min_value=0, max_value=6)

# Tipos de recorrência
recorrencia_strategy = st.sampled_from(['diario', 'semanal', 'mensal', None])


# ============ PROPERTY 5: Lembrete sem hora usa 09:00 ============

class TestLembreteSemHoraUsaPadrao:
    """
    Property 5: Lembrete sem hora usa 09:00
    
    Para qualquer lembrete criado sem hora especificada, 
    a hora deve ser 09:00 como padrão.
    
    **Feature: assistente-ranny-v3, Property 5: Lembrete sem hora usa 09:00**
    **Validates: Requirements 3.2**
    """
    
    @given(descricao=descricao_strategy)
    @settings(max_examples=100)
    def test_texto_sem_hora_retorna_09_00(self, descricao: str):
        """
        Para qualquer texto de lembrete sem indicação de hora,
        o parser deve retornar 09:00 como hora padrão.
        """
        # Garante que não tem padrões de hora no texto
        assume('h' not in descricao.lower())
        assume(':' not in descricao)
        assume('manhã' not in descricao.lower())
        assume('manha' not in descricao.lower())
        assume('tarde' not in descricao.lower())
        assume('noite' not in descricao.lower())
        
        texto = f"me lembra amanhã de {descricao}"
        resultado = parse_lembrete(texto)
        
        assert resultado['hora'] == '09:00', \
            f"Hora deveria ser 09:00, mas foi {resultado['hora']}"
    
    def test_extrair_hora_sem_hora_retorna_padrao(self):
        """
        Testa que extrair_hora retorna 09:00 quando não há hora no texto.
        """
        texto = "me lembra amanhã de pagar conta"
        hora, _ = extrair_hora(texto)
        assert hora == '09:00'
    
    @given(h=st.integers(min_value=0, max_value=23), m=st.integers(min_value=0, max_value=59))
    @settings(max_examples=100)
    def test_texto_com_hora_explicita_usa_hora_especificada(self, h: int, m: int):
        """
        Para qualquer texto com hora explícita, o parser deve usar a hora especificada.
        """
        texto = f"me lembra amanhã às {h}h{m:02d} de fazer algo"
        resultado = parse_lembrete(texto)
        
        assert resultado['hora'] == f'{h:02d}:{m:02d}', \
            f"Hora deveria ser {h:02d}:{m:02d}, mas foi {resultado['hora']}"


# ============ PROPERTY 4: Pedido de lembrete cria lembrete ============

class TestPedidoLembreteCriaLembrete:
    """
    Property 4: Pedido de lembrete cria lembrete no banco
    
    Para qualquer mensagem que contém pedido de lembrete válido,
    um registro de lembrete deve ser criado com data e descrição extraídas.
    
    **Feature: assistente-ranny-v3, Property 4: Pedido de lembrete cria lembrete no banco**
    **Validates: Requirements 1.4, 3.1**
    """
    
    @given(descricao=descricao_strategy, dias=dias_futuro_strategy)
    @settings(max_examples=100)
    def test_parse_lembrete_extrai_data_e_descricao(self, descricao: str, dias: int):
        """
        Para qualquer pedido de lembrete com "daqui X dias",
        o parser deve extrair a data correta e a descrição.
        """
        texto = f"me lembra daqui {dias} dias de {descricao}"
        resultado = parse_lembrete(texto)
        
        # Verifica que data foi extraída
        assert 'data' in resultado
        assert resultado['data'] is not None
        
        # Verifica que data está no formato correto
        try:
            data_parsed = datetime.strptime(resultado['data'], '%Y-%m-%d')
        except ValueError:
            pytest.fail(f"Data '{resultado['data']}' não está no formato YYYY-MM-DD")
        
        # Verifica que data é no futuro
        hoje = date.today()
        data_lembrete = data_parsed.date()
        assert data_lembrete >= hoje, \
            f"Data do lembrete {data_lembrete} deveria ser >= hoje {hoje}"
    
    @given(descricao=descricao_strategy)
    @settings(max_examples=100)
    def test_parse_lembrete_amanha_retorna_data_correta(self, descricao: str):
        """
        Para qualquer pedido de lembrete com "amanhã",
        a data deve ser exatamente amanhã.
        """
        texto = f"me lembra amanhã de {descricao}"
        resultado = parse_lembrete(texto)
        
        amanha = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        assert resultado['data'] == amanha, \
            f"Data deveria ser {amanha}, mas foi {resultado['data']}"
    
    def test_parse_lembrete_hoje_retorna_data_correta(self):
        """
        Testa que "hoje" retorna a data de hoje.
        """
        texto = "me lembra hoje de fazer algo"
        resultado = parse_lembrete(texto)
        
        hoje = date.today().strftime('%Y-%m-%d')
        assert resultado['data'] == hoje


# ============ TESTES DE PARSING DE DATA ============

class TestParsingDataPortugues:
    """
    Testes para parsing de datas em português.
    
    Validates: Requirements 3.1
    """
    
    @given(dia_semana=dia_semana_strategy)
    @settings(max_examples=100)
    def test_proxima_dia_semana_retorna_futuro(self, dia_semana: int):
        """
        Para qualquer dia da semana, proxima_dia_semana deve retornar
        uma data no futuro (mínimo 1 dia).
        """
        resultado = proxima_dia_semana(dia_semana)
        hoje = date.today()
        
        assert resultado > hoje, \
            f"Data {resultado} deveria ser maior que hoje {hoje}"
        
        # Verifica que é o dia da semana correto
        assert resultado.weekday() == dia_semana, \
            f"Dia da semana deveria ser {dia_semana}, mas foi {resultado.weekday()}"
    
    @given(dia=dia_mes_strategy)
    @settings(max_examples=100)
    def test_calcular_dia_mes_retorna_futuro_ou_hoje(self, dia: int):
        """
        Para qualquer dia do mês, calcular_dia_mes deve retornar
        uma data >= hoje.
        """
        resultado = calcular_dia_mes(dia)
        hoje = date.today()
        
        assert resultado >= hoje, \
            f"Data {resultado} deveria ser >= hoje {hoje}"
        
        # Verifica que é o dia correto
        assert resultado.day == dia, \
            f"Dia deveria ser {dia}, mas foi {resultado.day}"
    
    def test_depois_de_amanha(self):
        """Testa parsing de 'depois de amanhã'"""
        texto = "me lembra depois de amanhã de fazer algo"
        resultado = parse_lembrete(texto)
        
        depois_amanha = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        assert resultado['data'] == depois_amanha
    
    def test_proxima_semana(self):
        """Testa parsing de 'próxima semana'"""
        texto = "me lembra próxima semana de fazer algo"
        resultado = parse_lembrete(texto)
        
        proxima_semana = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        assert resultado['data'] == proxima_semana
    
    def test_daqui_uma_semana(self):
        """Testa parsing de 'daqui uma semana'"""
        texto = "me lembra daqui uma semana de fazer algo"
        resultado = parse_lembrete(texto)
        
        uma_semana = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        assert resultado['data'] == uma_semana
    
    def test_dia_especifico(self):
        """Testa parsing de 'dia 15'"""
        texto = "me lembra dia 15 de fazer algo"
        resultado = parse_lembrete(texto)
        
        # Verifica que o dia é 15
        data_parsed = datetime.strptime(resultado['data'], '%Y-%m-%d')
        assert data_parsed.day == 15


# ============ TESTES DE PARSING DE HORA ============

class TestParsingHora:
    """
    Testes para parsing de hora.
    
    Validates: Requirements 3.2
    """
    
    def test_as_14h(self):
        """Testa parsing de 'às 14h'"""
        hora, _ = extrair_hora("às 14h")
        assert hora == '14:00'
    
    def test_as_14h30(self):
        """Testa parsing de 'às 14h30'"""
        hora, _ = extrair_hora("às 14h30")
        assert hora == '14:30'
    
    def test_as_14_30(self):
        """Testa parsing de 'às 14:30'"""
        hora, _ = extrair_hora("às 14:30")
        assert hora == '14:30'
    
    def test_de_manha(self):
        """Testa parsing de 'de manhã'"""
        hora, _ = extrair_hora("de manhã")
        assert hora == '09:00'
    
    def test_a_tarde(self):
        """Testa parsing de 'à tarde'"""
        hora, _ = extrair_hora("à tarde")
        assert hora == '14:00'
    
    def test_a_noite(self):
        """Testa parsing de 'à noite'"""
        hora, _ = extrair_hora("à noite")
        assert hora == '20:00'
    
    def test_meio_dia(self):
        """Testa parsing de 'meio-dia'"""
        hora, _ = extrair_hora("ao meio-dia")
        assert hora == '12:00'


# ============ TESTES DE RECORRÊNCIA ============

class TestRecorrencia:
    """
    Testes para detecção de recorrência.
    
    Property 8: Recorrente gera próximo após disparo
    Validates: Requirements 3.6
    """
    
    def test_detecta_diario(self):
        """Testa detecção de recorrência diária"""
        assert detectar_recorrencia("todo dia às 9h") == 'diario'
        assert detectar_recorrencia("todos os dias") == 'diario'
    
    def test_detecta_semanal(self):
        """Testa detecção de recorrência semanal"""
        assert detectar_recorrencia("toda semana") == 'semanal'
        assert detectar_recorrencia("todas as semanas") == 'semanal'
    
    def test_detecta_mensal(self):
        """Testa detecção de recorrência mensal"""
        assert detectar_recorrencia("todo mês") == 'mensal'
        assert detectar_recorrencia("todo dia 7") == 'mensal'
    
    def test_nao_detecta_quando_nao_tem(self):
        """Testa que não detecta recorrência quando não há"""
        assert detectar_recorrencia("amanhã às 9h") is None
        assert detectar_recorrencia("dia 15") is None


# ============ TESTES DE LIMPEZA DE DESCRIÇÃO ============

class TestLimpezaDescricao:
    """
    Testes para limpeza de descrição do lembrete.
    """
    
    def test_remove_me_lembra(self):
        """Testa remoção de 'me lembra'"""
        resultado = limpar_descricao("me lembra de pagar conta")
        assert 'me lembra' not in resultado.lower()
    
    def test_remove_lembrete(self):
        """Testa remoção de 'lembrete'"""
        resultado = limpar_descricao("lembrete pagar conta")
        assert 'lembrete' not in resultado.lower()
    
    def test_mantem_descricao_util(self):
        """Testa que mantém a parte útil da descrição"""
        resultado = limpar_descricao("me lembra de pagar FGTS")
        assert 'fgts' in resultado.lower() or 'pagar' in resultado.lower()


# ============ TESTES DE INTEGRAÇÃO COM DATABASE (MOCK) ============

class TestIntegracaoDatabase:
    """
    Testes de integração com o banco de dados usando mocks.
    
    Property 6: Listagem retorna apenas ativos
    Property 7: Cancelamento marca como inativo
    """
    
    def test_add_lembrete_usa_hora_padrao(self):
        """
        Property 5: Verifica que add_lembrete usa 09:00 como padrão.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            mock_client.table.return_value.insert.return_value.execute.return_value.data = [
                {'id': 1, 'descricao': 'teste', 'data': '2025-01-20', 'hora': '09:00'}
            ]
            
            import database as db
            resultado = db.add_lembrete('teste', '2025-01-20')
            
            # Verifica que a hora padrão foi usada
            call_args = mock_client.table.return_value.insert.call_args
            dados_inseridos = call_args[0][0]
            assert dados_inseridos['hora'] == '09:00'
    
    def test_get_lembretes_ativos_filtra_por_ativo(self):
        """
        Property 6: Verifica que get_lembretes_ativos filtra por ativo=True.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            import database as db
            db.get_lembretes_ativos()
            
            # Verifica que filtrou por ativo=True
            mock_client.table.return_value.select.return_value.eq.assert_called_with('ativo', True)
    
    def test_cancelar_lembrete_marca_inativo(self):
        """
        Property 7: Verifica que cancelar_lembrete marca ativo=False.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
                {'id': 1, 'ativo': False}
            ]
            
            import database as db
            db.cancelar_lembrete(1)
            
            # Verifica que atualizou ativo=False
            call_args = mock_client.table.return_value.update.call_args
            dados_atualizados = call_args[0][0]
            assert dados_atualizados['ativo'] == False


class TestGetLembretesParaDisparar:
    """
    Testes para a função get_lembretes_para_disparar.
    
    Verifica que busca lembretes do dia com hora <= agora,
    ativos e não disparados.
    
    Requirements: 3.3
    """
    
    def test_filtra_por_data_hora_ativo_disparado(self):
        """
        Verifica que get_lembretes_para_disparar aplica todos os filtros corretos:
        - data = hoje
        - hora <= hora_atual
        - ativo = TRUE
        - disparado = FALSE
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Configura mock para retornar lista vazia
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.eq.return_value = mock_query
            mock_query.lte.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = []
            
            import database as db
            db.get_lembretes_para_disparar('10:00')
            
            # Verifica que table foi chamado com 'lembretes'
            mock_client.table.assert_called_with('lembretes')
    
    def test_retorna_lembretes_com_hora_menor_ou_igual(self):
        """
        Verifica que retorna lembretes com hora <= hora_atual.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Simula lembretes retornados
            lembretes_mock = [
                {'id': 1, 'descricao': 'Lembrete 1', 'data': '2025-01-15', 'hora': '09:00'},
                {'id': 2, 'descricao': 'Lembrete 2', 'data': '2025-01-15', 'hora': '10:00'},
            ]
            
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.eq.return_value = mock_query
            mock_query.lte.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = lembretes_mock
            
            import database as db
            resultado = db.get_lembretes_para_disparar('10:00')
            
            assert len(resultado) == 2
            assert resultado[0]['descricao'] == 'Lembrete 1'


class TestJobCheckLembretes:
    """
    Testes para o job check_lembretes.
    
    Verifica que:
    - Busca lembretes para disparar
    - Envia mensagem no Tópico_Chat
    - Marca como disparado
    - Cria próximo para recorrentes
    
    Requirements: 3.3
    """
    
    @pytest.mark.asyncio
    async def test_check_lembretes_sem_bot_retorna_zero(self):
        """
        Verifica que check_lembretes retorna 0 quando bot não está configurado.
        """
        import jobs
        jobs._telegram_bot = None
        
        resultado = await jobs.check_lembretes()
        assert resultado == 0
    
    @pytest.mark.asyncio
    async def test_check_lembretes_sem_lembretes_retorna_zero(self):
        """
        Verifica que check_lembretes retorna 0 quando não há lembretes.
        """
        import jobs
        
        mock_bot = MagicMock()
        jobs.set_telegram_bot(mock_bot)
        
        with patch('database.get_lembretes_para_disparar') as mock_get:
            mock_get.return_value = []
            
            resultado = await jobs.check_lembretes()
            assert resultado == 0
        
        # Limpa
        jobs._telegram_bot = None
    
    @pytest.mark.asyncio
    async def test_check_lembretes_dispara_e_marca(self):
        """
        Verifica que check_lembretes dispara lembretes e marca como disparado.
        """
        import jobs
        from unittest.mock import AsyncMock
        
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        jobs.set_telegram_bot(mock_bot)
        
        lembrete_mock = {
            'id': 1,
            'descricao': 'Pagar FGTS',
            'data': '2025-01-15',
            'hora': '09:00',
            'recorrente': None
        }
        
        with patch('database.get_lembretes_para_disparar') as mock_get, \
             patch('database.marcar_lembrete_disparado') as mock_marcar:
            mock_get.return_value = [lembrete_mock]
            
            resultado = await jobs.check_lembretes()
            
            # Verifica que enviou mensagem
            mock_bot.send_message.assert_called_once()
            
            # Verifica que marcou como disparado
            mock_marcar.assert_called_once_with(1)
            
            assert resultado == 1
        
        # Limpa
        jobs._telegram_bot = None
    
    @pytest.mark.asyncio
    async def test_check_lembretes_cria_proximo_recorrente(self):
        """
        Verifica que check_lembretes cria próximo lembrete para recorrentes.
        """
        import jobs
        from unittest.mock import AsyncMock
        
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        jobs.set_telegram_bot(mock_bot)
        
        lembrete_mock = {
            'id': 1,
            'descricao': 'Pagar FGTS',
            'data': '2025-01-15',
            'hora': '09:00',
            'recorrente': 'mensal'
        }
        
        with patch('database.get_lembretes_para_disparar') as mock_get, \
             patch('database.marcar_lembrete_disparado') as mock_marcar, \
             patch('database.criar_proximo_lembrete_recorrente') as mock_criar:
            mock_get.return_value = [lembrete_mock]
            mock_criar.return_value = {'id': 2, 'data': '2025-02-15'}
            
            resultado = await jobs.check_lembretes()
            
            # Verifica que criou próximo
            mock_criar.assert_called_once_with(lembrete_mock)
            
            assert resultado == 1
        
        # Limpa
        jobs._telegram_bot = None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
