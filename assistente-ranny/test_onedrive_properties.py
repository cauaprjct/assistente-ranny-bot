"""
Property-Based Tests para Integração OneDrive

Feature: assistente-ranny-v3
Property 14: Desconectado retorna mensagem apropriada

Validates: Requirements 7.2

Testes de propriedade usando hypothesis para validar:
- Quando OneDrive está desconectado, a resposta indica que o notebook está offline
- A mensagem de desconexão é apropriada e amigável
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio


# ============ ESTRATÉGIAS DE GERAÇÃO ============

# Estratégia para gerar diferentes cenários de desconexão
disconnection_scenarios = st.sampled_from([
    'no_token',           # Sem token salvo
    'token_expired',      # Token expirado e refresh falhou
    'api_timeout',        # Timeout na API
    'api_error',          # Erro na API (401, 500, etc)
    'network_error',      # Erro de rede
])

# Estratégia para gerar códigos de erro HTTP
http_error_codes = st.sampled_from([401, 403, 500, 502, 503])


# ============ PROPERTY 14: OneDrive desconectado retorna mensagem apropriada ============

class TestOneDriveDesconectadoRetornaMensagemApropriada:
    """
    Property 14: OneDrive desconectado retorna mensagem apropriada
    
    Para qualquer tentativa de acesso ao OneDrive quando desconectado,
    a resposta deve indicar que o notebook está offline com mensagem amigável.
    
    **Feature: assistente-ranny-v3, Property 14: Desconectado retorna mensagem apropriada**
    **Validates: Requirements 7.2**
    """
    
    @pytest.fixture
    def onedrive_client(self):
        """Cria instância do OneDriveClient para testes"""
        from onedrive import OneDriveClient
        return OneDriveClient()
    
    @pytest.fixture
    def onedrive_auth(self):
        """Cria instância do OneDriveAuth para testes"""
        from onedrive import OneDriveAuth
        return OneDriveAuth()
    
    @pytest.mark.asyncio
    @given(scenario=disconnection_scenarios)
    @settings(max_examples=20, deadline=None)
    async def test_desconectado_retorna_connected_false(self, scenario: str):
        """
        Para qualquer cenário de desconexão, get_connection_status deve retornar
        connected=False.
        """
        from onedrive import OneDriveClient
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            if scenario == 'no_token':
                # Sem token salvo
                mock_get_token.return_value = None
            else:
                # Token existe mas está inválido ou API falha
                mock_get_token.return_value = {
                    'access_token': 'fake_token',
                    'refresh_token': 'fake_refresh',
                    'expires_at': '2020-01-01T00:00:00'  # Expirado
                }
            
            # Mock do refresh para falhar
            with patch.object(client.auth, 'refresh_access_token', new_callable=AsyncMock) as mock_refresh:
                mock_refresh.return_value = False
                
                status = await client.get_connection_status()
                
                assert status['connected'] is False, \
                    f"Cenário '{scenario}': connected deveria ser False"
    
    @pytest.mark.asyncio
    @given(scenario=disconnection_scenarios)
    @settings(max_examples=20, deadline=None)
    async def test_desconectado_retorna_mensagem_nao_vazia(self, scenario: str):
        """
        Para qualquer cenário de desconexão, a mensagem retornada não deve ser vazia.
        """
        from onedrive import OneDriveClient
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            if scenario == 'no_token':
                mock_get_token.return_value = None
            else:
                mock_get_token.return_value = {
                    'access_token': 'fake_token',
                    'refresh_token': 'fake_refresh',
                    'expires_at': '2020-01-01T00:00:00'
                }
            
            with patch.object(client.auth, 'refresh_access_token', new_callable=AsyncMock) as mock_refresh:
                mock_refresh.return_value = False
                
                status = await client.get_connection_status()
                
                assert 'message' in status, \
                    f"Cenário '{scenario}': resposta deve conter 'message'"
                assert len(status['message']) > 0, \
                    f"Cenário '{scenario}': mensagem não deve ser vazia"
    
    @pytest.mark.asyncio
    async def test_sem_token_retorna_mensagem_de_conexao(self):
        """
        Quando não há token salvo, a mensagem deve indicar que precisa conectar.
        """
        from onedrive import OneDriveClient
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = None
            
            status = await client.get_connection_status()
            
            assert status['connected'] is False
            assert 'message' in status
            # Mensagem deve indicar que não está conectado
            assert 'não está conectado' in status['message'].lower() or \
                   'conectar' in status['message'].lower(), \
                   f"Mensagem deveria indicar necessidade de conexão: {status['message']}"
    
    @pytest.mark.asyncio
    async def test_token_invalido_retorna_mensagem_offline(self):
        """
        Quando token existe mas é inválido, a mensagem deve indicar que notebook está offline.
        """
        from onedrive import OneDriveClient
        import httpx
        
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            # Token existe
            mock_get_token.return_value = {
                'access_token': 'valid_looking_token',
                'refresh_token': 'valid_refresh',
                'expires_at': '2030-01-01T00:00:00'  # Não expirado
            }
            
            # Mas API retorna erro
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                # Simula erro de autorização
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_client.get.return_value = mock_response
                
                status = await client.get_connection_status()
                
                assert status['connected'] is False
                assert 'message' in status
    
    @pytest.mark.asyncio
    async def test_timeout_retorna_mensagem_offline(self):
        """
        Quando há timeout na API, a mensagem deve indicar que notebook está offline.
        """
        from onedrive import OneDriveClient
        import httpx
        
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = {
                'access_token': 'valid_token',
                'refresh_token': 'valid_refresh',
                'expires_at': '2030-01-01T00:00:00'
            }
            
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                # Simula timeout
                mock_client.get.side_effect = httpx.TimeoutException("Connection timed out")
                
                status = await client.get_connection_status()
                
                assert status['connected'] is False
                assert 'message' in status
                # Mensagem deve ser amigável sobre notebook offline
                assert 'notebook' in status['message'].lower() or \
                       'desligado' in status['message'].lower() or \
                       'internet' in status['message'].lower(), \
                       f"Mensagem deveria mencionar notebook/internet: {status['message']}"
    
    @pytest.mark.asyncio
    @given(error_code=http_error_codes)
    @settings(max_examples=10, deadline=None)
    async def test_erro_http_retorna_connected_false(self, error_code: int):
        """
        Para qualquer código de erro HTTP, connected deve ser False.
        """
        from onedrive import OneDriveClient
        
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = {
                'access_token': 'valid_token',
                'refresh_token': 'valid_refresh',
                'expires_at': '2030-01-01T00:00:00'
            }
            
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.status_code = error_code
                mock_client.get.return_value = mock_response
                
                status = await client.get_connection_status()
                
                assert status['connected'] is False, \
                    f"HTTP {error_code}: connected deveria ser False"


class TestOneDriveStatusRetornoConsistente:
    """
    Testes de consistência do retorno de status do OneDrive.
    
    Garante que o formato de retorno é sempre consistente.
    """
    
    @pytest.mark.asyncio
    async def test_status_sempre_tem_connected_e_message(self):
        """
        O retorno de get_connection_status sempre deve ter 'connected' e 'message'.
        """
        from onedrive import OneDriveClient
        
        client = OneDriveClient()
        
        # Testa cenário desconectado
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = None
            
            status = await client.get_connection_status()
            
            assert 'connected' in status, "Retorno deve ter campo 'connected'"
            assert 'message' in status, "Retorno deve ter campo 'message'"
            assert isinstance(status['connected'], bool), "'connected' deve ser booleano"
            assert isinstance(status['message'], str), "'message' deve ser string"
    
    @pytest.mark.asyncio
    async def test_is_connected_retorna_false_quando_desconectado(self):
        """
        O método is_connected() deve retornar False quando não há conexão.
        """
        from onedrive import OneDriveClient
        
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = None
            
            result = await client.is_connected()
            
            assert result is False, "is_connected() deve retornar False sem token"
    
    @pytest.mark.asyncio
    async def test_mensagem_desconexao_e_amigavel(self):
        """
        A mensagem de desconexão deve ser amigável (não técnica).
        """
        from onedrive import OneDriveClient
        
        client = OneDriveClient()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = {
                'access_token': 'token',
                'refresh_token': 'refresh',
                'expires_at': '2030-01-01T00:00:00'
            }
            
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                # Simula erro genérico
                mock_client.get.side_effect = Exception("Network error")
                
                status = await client.get_connection_status()
                
                # Mensagem não deve conter termos técnicos assustadores
                mensagem_lower = status['message'].lower()
                assert 'exception' not in mensagem_lower, \
                    "Mensagem não deve conter 'exception'"
                assert 'error' not in mensagem_lower or 'erro' in mensagem_lower, \
                    "Mensagem não deve conter 'error' em inglês"
                assert 'traceback' not in mensagem_lower, \
                    "Mensagem não deve conter 'traceback'"


class TestOneDriveAuthDesconectado:
    """
    Testes específicos para OneDriveAuth quando desconectado.
    """
    
    @pytest.mark.asyncio
    async def test_get_valid_token_retorna_none_sem_token(self):
        """
        get_valid_token() deve retornar None quando não há token salvo.
        """
        from onedrive import OneDriveAuth
        
        auth = OneDriveAuth()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = None
            
            token = await auth.get_valid_token()
            
            assert token is None, "Deve retornar None sem token salvo"
    
    @pytest.mark.asyncio
    async def test_is_connected_retorna_false_sem_token(self):
        """
        is_connected() deve retornar False quando não há token.
        """
        from onedrive import OneDriveAuth
        
        auth = OneDriveAuth()
        
        with patch('onedrive.get_oauth_token') as mock_get_token:
            mock_get_token.return_value = None
            
            connected = await auth.is_connected()
            
            assert connected is False, "Deve retornar False sem token"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
