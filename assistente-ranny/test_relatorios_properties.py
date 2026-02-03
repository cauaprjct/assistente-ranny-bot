"""
Property-Based Tests para Sistema de Relatórios

Feature: assistente-ranny-v3
Property 12: Token tem TTL de 24h

Validates: Requirements 5.1, 5.2

Testes de propriedade usando hypothesis para validar o sistema de relatórios.
"""
import os
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid
from dotenv import load_dotenv

# Carrega variáveis de ambiente ANTES de importar database
load_dotenv()

# Verifica se as variáveis estão configuradas
if not os.getenv('SUPABASE_URL'):
    pytest.skip("SUPABASE_URL não configurado", allow_module_level=True)

# Garante que SUPABASE_KEY está disponível (usa ANON_KEY se SERVICE_KEY não estiver)
if not os.getenv('SUPABASE_SERVICE_KEY') and not os.getenv('SUPABASE_ANON_KEY'):
    pytest.skip("Nenhuma chave Supabase configurada", allow_module_level=True)


# ============ ESTRATÉGIAS DE GERAÇÃO ============

# Estratégia para gerar tipos de relatório
tipo_relatorio_strategy = st.sampled_from([
    'grafico', 'resumo', 'semanal', 'mensal', 'fechamentos', 'vencimentos'
])

# Estratégia para gerar períodos
periodo_strategy = st.sampled_from([
    '7dias', '15dias', '30dias', 'semana', 'mes', 'Últimos 7 dias', 'Últimos 30 dias'
])

# Estratégia para gerar valores de fechamento
valor_fechamento_strategy = st.floats(
    min_value=100.0, 
    max_value=50000.0, 
    allow_nan=False, 
    allow_infinity=False
)

# Estratégia para gerar lista de fechamentos
fechamentos_strategy = st.lists(
    st.fixed_dictionaries({
        'data': st.dates(
            min_value=datetime(2024, 1, 1).date(),
            max_value=datetime(2026, 12, 31).date()
        ).map(lambda d: d.strftime('%Y-%m-%d')),
        'valor': valor_fechamento_strategy
    }),
    min_size=1,
    max_size=30
)

# Estratégia para gerar dados de relatório completos
dados_relatorio_strategy = st.fixed_dictionaries({
    'periodo': periodo_strategy,
    'fechamentos': fechamentos_strategy
})


def calcular_ttl_horas(created_at: str, expires_at: str) -> float:
    """
    Calcula o TTL em horas entre created_at e expires_at.
    
    Args:
        created_at: Timestamp de criação (ISO format)
        expires_at: Timestamp de expiração (ISO format)
    
    Returns:
        Diferença em horas
    """
    # Remove timezone info para parsing simples
    created_str = created_at.replace('Z', '').replace('+00:00', '').split('.')[0]
    expires_str = expires_at.replace('Z', '').replace('+00:00', '').split('.')[0]
    
    created = datetime.fromisoformat(created_str)
    expires = datetime.fromisoformat(expires_str)
    
    diff = expires - created
    return diff.total_seconds() / 3600


# ============ PROPERTY 12: Token tem TTL de 24h ============

class TestTokenTTL24Horas:
    """
    Property 12: Token tem TTL de 24h
    
    Para qualquer relatório gerado, o token deve ter 
    expires_at = created_at + 24 horas.
    
    **Feature: assistente-ranny-v3, Property 12: Token tem TTL de 24h**
    **Validates: Requirements 5.1, 5.2**
    """
    
    @given(
        tipo=tipo_relatorio_strategy,
        dados=dados_relatorio_strategy
    )
    @settings(max_examples=20, deadline=timedelta(seconds=10))
    def test_token_expira_em_24_horas(self, tipo: str, dados: Dict[str, Any]):
        """
        Para qualquer relatório gerado, o TTL deve ser de 24 horas.
        
        Property 12: Token tem TTL de 24h
        """
        from database import criar_relatorio_temp, get_relatorio_temp, get_supabase
        
        # Cria relatório
        token = criar_relatorio_temp(tipo=tipo, dados=dados)
        
        try:
            assert token is not None, "Token não deveria ser None"
            
            # Busca relatório criado
            relatorio = get_relatorio_temp(token)
            assert relatorio is not None, "Relatório deveria existir"
            
            # Verifica campos obrigatórios
            assert 'created_at' in relatorio, "Relatório deve ter created_at"
            assert 'expires_at' in relatorio, "Relatório deve ter expires_at"
            
            # Calcula TTL
            ttl_horas = calcular_ttl_horas(
                relatorio['created_at'], 
                relatorio['expires_at']
            )
            
            # Verifica que TTL é aproximadamente 24 horas (tolerância de 1 hora)
            assert 23.0 <= ttl_horas <= 25.0, \
                f"TTL deveria ser ~24h, mas foi {ttl_horas:.2f}h"
            
        finally:
            # Cleanup
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()
    
    @given(
        tipo=tipo_relatorio_strategy,
        periodo=periodo_strategy
    )
    @settings(max_examples=20, deadline=timedelta(seconds=10))
    def test_token_formato_uuid_valido(self, tipo: str, periodo: str):
        """
        Para qualquer relatório gerado, o token deve ser um UUID válido.
        """
        from database import criar_relatorio_temp, get_supabase
        
        dados = {'periodo': periodo, 'fechamentos': []}
        token = criar_relatorio_temp(tipo=tipo, dados=dados)
        
        try:
            assert token is not None, "Token não deveria ser None"
            
            # Verifica formato UUID
            try:
                uuid_obj = uuid.UUID(token)
                assert str(uuid_obj) == token.lower(), \
                    "Token deveria ser um UUID válido"
            except ValueError:
                pytest.fail(f"Token '{token}' não é um UUID válido")
            
        finally:
            # Cleanup
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()
    
    @given(
        tipo=tipo_relatorio_strategy,
        dados=dados_relatorio_strategy
    )
    @settings(max_examples=20, deadline=timedelta(seconds=10))
    def test_token_unico_por_relatorio(self, tipo: str, dados: Dict[str, Any]):
        """
        Para qualquer dois relatórios gerados, os tokens devem ser diferentes.
        """
        from database import criar_relatorio_temp, get_supabase
        
        # Cria dois relatórios com mesmos dados
        token1 = criar_relatorio_temp(tipo=tipo, dados=dados)
        token2 = criar_relatorio_temp(tipo=tipo, dados=dados)
        
        try:
            assert token1 is not None, "Token 1 não deveria ser None"
            assert token2 is not None, "Token 2 não deveria ser None"
            
            # Tokens devem ser diferentes
            assert token1 != token2, \
                "Cada relatório deve ter um token único"
            
        finally:
            # Cleanup
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token1).execute()
            supabase.table('relatorios_temp').delete().eq('token', token2).execute()
    
    @given(
        tipo=tipo_relatorio_strategy,
        dados=dados_relatorio_strategy
    )
    @settings(max_examples=20, deadline=timedelta(seconds=10))
    def test_relatorio_preserva_dados(self, tipo: str, dados: Dict[str, Any]):
        """
        Para qualquer relatório gerado, os dados devem ser preservados.
        """
        from database import criar_relatorio_temp, get_relatorio_temp, get_supabase
        
        token = criar_relatorio_temp(tipo=tipo, dados=dados)
        
        try:
            assert token is not None, "Token não deveria ser None"
            
            # Busca relatório
            relatorio = get_relatorio_temp(token)
            assert relatorio is not None, "Relatório deveria existir"
            
            # Verifica que tipo foi preservado
            assert relatorio['tipo'] == tipo, \
                f"Tipo deveria ser '{tipo}', mas foi '{relatorio['tipo']}'"
            
            # Verifica que dados foram preservados
            assert relatorio['dados'] == dados, \
                "Dados do relatório deveriam ser preservados"
            
        finally:
            # Cleanup
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()


# ============ TESTES DE EXPIRAÇÃO ============

class TestRelatorioExpiracao:
    """
    Testes para verificar comportamento de expiração de relatórios.
    
    Validates: Requirements 5.2
    """
    
    def test_relatorio_expirado_nao_retorna(self):
        """
        Verifica que relatório expirado não é retornado por get_relatorio_temp.
        
        Nota: Este teste verifica a lógica de filtro por expires_at.
        """
        from database import get_supabase
        
        supabase = get_supabase()
        
        # Cria relatório já expirado diretamente no banco
        data = {
            'tipo': 'teste_expirado',
            'dados': {'teste': True},
            'expires_at': (datetime.now() - timedelta(hours=1)).isoformat()
        }
        
        result = supabase.table('relatorios_temp').insert(data).execute()
        token = result.data[0]['token'] if result.data else None
        
        try:
            assert token is not None, "Token não deveria ser None"
            
            # Busca relatório - deve retornar None pois expirou
            from database import get_relatorio_temp
            relatorio = get_relatorio_temp(token)
            
            assert relatorio is None, \
                "Relatório expirado não deveria ser retornado"
            
        finally:
            # Cleanup
            if token:
                supabase.table('relatorios_temp').delete().eq('token', token).execute()
    
    def test_relatorio_nao_expirado_retorna(self):
        """
        Verifica que relatório não expirado é retornado normalmente.
        """
        from database import criar_relatorio_temp, get_relatorio_temp, get_supabase
        
        dados = {'teste': 'nao_expirado'}
        token = criar_relatorio_temp(tipo='teste', dados=dados)
        
        try:
            assert token is not None, "Token não deveria ser None"
            
            # Busca relatório - deve retornar pois não expirou
            relatorio = get_relatorio_temp(token)
            
            assert relatorio is not None, \
                "Relatório não expirado deveria ser retornado"
            assert relatorio['dados'] == dados, \
                "Dados deveriam ser preservados"
            
        finally:
            # Cleanup
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()


# ============ TESTES DE INTEGRAÇÃO COM WEB ============

class TestWebRelatorioEndpoint:
    """
    Testes para o endpoint /relatorio/{token} do FastAPI.
    
    Validates: Requirements 5.1, 5.3
    """
    
    def test_token_invalido_retorna_400(self):
        """
        Verifica que token inválido retorna erro 400.
        """
        from fastapi.testclient import TestClient
        from web import app
        
        client = TestClient(app)
        
        # Token com formato inválido
        response = client.get("/relatorio/token-invalido")
        assert response.status_code == 400
    
    def test_token_inexistente_retorna_404(self):
        """
        Verifica que token inexistente retorna erro 404.
        """
        from fastapi.testclient import TestClient
        from web import app
        
        client = TestClient(app)
        
        # Token UUID válido mas inexistente
        token_fake = str(uuid.uuid4())
        response = client.get(f"/relatorio/{token_fake}")
        assert response.status_code == 404
    
    def test_token_valido_retorna_html(self):
        """
        Verifica que token válido retorna página HTML.
        """
        from fastapi.testclient import TestClient
        from web import app
        from database import criar_relatorio_temp, get_supabase
        
        client = TestClient(app)
        
        # Cria relatório válido
        dados = {
            'periodo': 'Últimos 7 dias',
            'fechamentos': [
                {'data': '2025-01-10', 'valor': 1500.0},
                {'data': '2025-01-11', 'valor': 1800.0}
            ]
        }
        token = criar_relatorio_temp(tipo='grafico', dados=dados)
        
        try:
            response = client.get(f"/relatorio/{token}")
            
            assert response.status_code == 200
            assert 'text/html' in response.headers['content-type']
            assert 'GRN Pizzas' in response.text
            
        finally:
            # Cleanup
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
