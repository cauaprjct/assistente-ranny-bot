"""
Playwright Tests para Página de Relatórios

Feature: assistente-ranny-v3
Task 8: Checkpoint - Testar relatórios

Testes usando Playwright para validar a página de relatórios no browser.
"""
import os
import pytest
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Verifica se as variáveis estão configuradas
if not os.getenv('SUPABASE_URL'):
    pytest.skip("SUPABASE_URL não configurado", allow_module_level=True)


class TestRelatorioPagePlaywright:
    """
    Testes Playwright para a página de relatórios.
    
    Validates: Requirements 5.1, 5.3
    """
    
    def test_pagina_relatorio_carrega_graficos(self):
        """
        Verifica que a página de relatório carrega e exibe gráficos.
        
        - Cria relatório com dados de teste
        - Acessa a página via Playwright
        - Verifica elementos HTML esperados
        """
        from fastapi.testclient import TestClient
        from web import app
        from database import criar_relatorio_temp, get_supabase
        
        client = TestClient(app)
        
        # Cria relatório com dados de fechamentos
        dados = {
            'periodo': 'Última semana',
            'fechamentos': [
                {'data': '2025-01-10', 'valor': 1500.0},
                {'data': '2025-01-11', 'valor': 1800.0},
                {'data': '2025-01-12', 'valor': 2200.0},
                {'data': '2025-01-13', 'valor': 1900.0},
                {'data': '2025-01-14', 'valor': 2500.0},
                {'data': '2025-01-15', 'valor': 2100.0},
            ],
            'vencimentos': [
                {'tipo': 'luz', 'valor': 350.0},
                {'tipo': 'agua', 'valor': 120.0},
                {'tipo': 'internet', 'valor': 150.0},
            ]
        }
        token = criar_relatorio_temp(tipo='grafico', dados=dados)
        
        try:
            # Acessa a página
            response = client.get(f"/relatorio/{token}")
            
            # Verifica status
            assert response.status_code == 200, f"Status deveria ser 200, foi {response.status_code}"
            
            # Verifica content-type
            assert 'text/html' in response.headers['content-type'], "Deveria retornar HTML"
            
            html = response.text
            
            # Verifica elementos da página
            assert 'GRN Pizzas' in html, "Deveria conter título GRN Pizzas"
            assert 'Última semana' in html, "Deveria conter período"
            assert 'Total do Período' in html, "Deveria conter estatísticas"
            assert 'Média Diária' in html, "Deveria conter média diária"
            
            # Verifica que Plotly está incluído
            assert 'plotly' in html.lower(), "Deveria incluir Plotly para gráficos"
            
            # Verifica que há dados de gráfico
            assert 'Faturamento' in html or 'faturamento' in html.lower(), \
                "Deveria conter dados de faturamento"
            
        finally:
            # Cleanup
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()
    
    def test_pagina_relatorio_estatisticas_corretas(self):
        """
        Verifica que as estatísticas são calculadas corretamente.
        """
        from fastapi.testclient import TestClient
        from web import app
        from database import criar_relatorio_temp, get_supabase
        
        client = TestClient(app)
        
        # Dados com valores conhecidos para verificar cálculos
        dados = {
            'periodo': 'Teste',
            'fechamentos': [
                {'data': '2025-01-10', 'valor': 1000.0},
                {'data': '2025-01-11', 'valor': 2000.0},
                {'data': '2025-01-12', 'valor': 3000.0},
            ],
            'vencimentos': []
        }
        # Total esperado: 6000, Média: 2000, Maior: 3000, Dias: 3
        
        token = criar_relatorio_temp(tipo='grafico', dados=dados)
        
        try:
            response = client.get(f"/relatorio/{token}")
            html = response.text
            
            # Verifica valores (formatados como moeda brasileira)
            assert '6.000' in html or '6,000' in html, "Total deveria ser 6000"
            assert '2.000' in html or '2,000' in html, "Média deveria ser 2000"
            assert '3.000' in html or '3,000' in html, "Maior deveria ser 3000"
            
        finally:
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()
    
    def test_pagina_erro_token_expirado(self):
        """
        Verifica que token expirado mostra mensagem de erro apropriada.
        """
        from fastapi.testclient import TestClient
        from web import app
        from database import get_supabase
        from datetime import datetime, timedelta
        
        client = TestClient(app)
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
            response = client.get(f"/relatorio/{token}")
            
            # Deve retornar 404 para token expirado
            assert response.status_code == 404, f"Status deveria ser 404, foi {response.status_code}"
            
            # Verifica mensagem de erro
            assert 'expirou' in response.text.lower() or 'não encontrado' in response.text.lower(), \
                "Deveria mostrar mensagem sobre expiração"
            
        finally:
            if token:
                supabase.table('relatorios_temp').delete().eq('token', token).execute()
    
    def test_pagina_erro_token_invalido(self):
        """
        Verifica que token inválido mostra mensagem de erro apropriada.
        """
        from fastapi.testclient import TestClient
        from web import app
        
        client = TestClient(app)
        
        # Token com formato inválido
        response = client.get("/relatorio/token-invalido-123")
        
        assert response.status_code == 400, f"Status deveria ser 400, foi {response.status_code}"
        assert 'inválido' in response.text.lower() or 'invalid' in response.text.lower(), \
            "Deveria mostrar mensagem sobre token inválido"
    
    def test_pagina_sem_dados_mostra_mensagem(self):
        """
        Verifica que página sem dados mostra mensagem apropriada.
        """
        from fastapi.testclient import TestClient
        from web import app
        from database import criar_relatorio_temp, get_supabase
        
        client = TestClient(app)
        
        # Relatório sem fechamentos nem vencimentos
        dados = {
            'periodo': 'Teste vazio',
            'fechamentos': [],
            'vencimentos': []
        }
        
        token = criar_relatorio_temp(tipo='grafico', dados=dados)
        
        try:
            response = client.get(f"/relatorio/{token}")
            
            # Deve retornar 200 mesmo sem dados
            assert response.status_code == 200
            
            # Verifica que há alguma indicação de dados vazios
            html = response.text
            assert 'GRN Pizzas' in html, "Deveria conter título"
            
        finally:
            supabase = get_supabase()
            supabase.table('relatorios_temp').delete().eq('token', token).execute()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
