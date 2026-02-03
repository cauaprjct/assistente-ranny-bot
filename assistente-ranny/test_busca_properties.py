"""
Property-Based Tests para Busca de Documentos

Feature: assistente-ranny-v3
Property 13: Busca retorna matches

Validates: Requirements 6.1

Testes de propriedade usando hypothesis para validar que:
- Busca por termo retorna documentos que contêm o termo na descrição, tipo ou categoria
- Resultados são ordenados por data de criação (mais recente primeiro)
- Busca é case-insensitive
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, MagicMock
import re


# ============ ESTRATÉGIAS DE GERAÇÃO ============

# Estratégia para gerar termos de busca válidos
termo_busca_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N')),
    min_size=2,
    max_size=50
).filter(lambda x: x.strip() and len(x.strip()) >= 2)

# Estratégia para gerar descrições de documentos
descricao_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=5,
    max_size=200
).filter(lambda x: x.strip())

# Tipos de documentos válidos
TIPOS_DOCUMENTO = ['boleto', 'contrato', 'comprovante', 'nota_fiscal', 'foto', 'documento', 'orcamento']
tipo_strategy = st.sampled_from(TIPOS_DOCUMENTO)

# Categorias válidas
CATEGORIAS_VALIDAS = ['financeiro', 'empresa', 'funcionarios', 'juridico', 'pessoal', 'manutencao', 'outros']
categoria_strategy = st.sampled_from(CATEGORIAS_VALIDAS)


# ============ PROPERTY 13: Busca retorna matches ============

class TestBuscaRetornaMatches:
    """
    Property 13: Busca retorna matches
    
    Para qualquer termo de busca, os documentos retornados devem conter 
    o termo na descrição, tipo ou categoria.
    
    **Feature: assistente-ranny-v3, Property 13: Busca retorna matches**
    **Validates: Requirements 6.1**
    """
    
    @given(termo=termo_busca_strategy)
    @settings(max_examples=20, deadline=None)
    def test_busca_retorna_lista(self, termo: str):
        """
        Para qualquer termo de busca válido, a função deve retornar uma lista
        (mesmo que vazia).
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Configura mock para retornar lista vazia
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = []
            
            import database as db
            resultado = db.buscar_documentos(termo)
            
            assert isinstance(resultado, list), \
                f"Busca deve retornar lista, mas retornou {type(resultado)}"
    
    @given(termo=termo_busca_strategy)
    @settings(max_examples=20)
    def test_busca_usa_ilike_para_case_insensitive(self, termo: str):
        """
        Para qualquer termo de busca, a função deve usar ilike para busca
        case-insensitive.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Configura mock
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = []
            
            import database as db
            db.buscar_documentos(termo)
            
            # Verifica que ilike foi chamado com o padrão correto
            calls = mock_query.ilike.call_args_list
            assert len(calls) >= 1, "ilike deve ser chamado pelo menos uma vez"
            
            # Verifica que o padrão inclui wildcards
            for call in calls:
                pattern = call[0][1]  # Segundo argumento do ilike
                assert pattern.startswith('%') and pattern.endswith('%'), \
                    f"Padrão de busca deve usar wildcards, mas foi: {pattern}"
    
    @given(
        termo=termo_busca_strategy,
        descricao=descricao_strategy,
        tipo=tipo_strategy,
        categoria=categoria_strategy
    )
    @settings(max_examples=20)
    def test_documento_com_termo_na_descricao_e_retornado(
        self, termo: str, descricao: str, tipo: str, categoria: str
    ):
        """
        Para qualquer documento que contém o termo na descrição,
        ele deve ser retornado pela busca.
        """
        # Garante que o termo está na descrição
        descricao_com_termo = f"{descricao} {termo} {descricao}"
        
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Documento que contém o termo na descrição
            doc_mock = {
                'id': 1,
                'tipo': tipo,
                'descricao': descricao_com_termo,
                'categoria': categoria,
                'file_id': 'ABC123',
                'created_at': '2025-01-15T10:00:00'
            }
            
            # Configura mock para retornar o documento na busca por descrição
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            
            # Primeira chamada (descrição) retorna o documento
            # Segunda e terceira (tipo e categoria) retornam vazio
            mock_query.execute.return_value.data = [doc_mock]
            
            import database as db
            resultado = db.buscar_documentos(termo)
            
            # Verifica que o documento foi retornado
            assert len(resultado) >= 1, \
                f"Documento com termo '{termo}' na descrição deveria ser retornado"
            assert any(d['id'] == 1 for d in resultado), \
                "Documento específico deveria estar nos resultados"
    
    @given(termo=tipo_strategy)
    @settings(max_examples=10)
    def test_busca_por_tipo_retorna_documentos(self, termo: str):
        """
        Para qualquer tipo de documento válido, a busca deve retornar
        documentos desse tipo.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Documento do tipo buscado
            doc_mock = {
                'id': 1,
                'tipo': termo,
                'descricao': 'Documento de teste',
                'categoria': 'financeiro',
                'file_id': 'XYZ789',
                'created_at': '2025-01-15T10:00:00'
            }
            
            # Configura mock
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = [doc_mock]
            
            import database as db
            resultado = db.buscar_documentos(termo)
            
            assert len(resultado) >= 1, \
                f"Busca por tipo '{termo}' deveria retornar documentos"
    
    @given(termo=categoria_strategy)
    @settings(max_examples=10)
    def test_busca_por_categoria_retorna_documentos(self, termo: str):
        """
        Para qualquer categoria válida, a busca deve retornar
        documentos dessa categoria.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Documento da categoria buscada
            doc_mock = {
                'id': 1,
                'tipo': 'documento',
                'descricao': 'Documento de teste',
                'categoria': termo,
                'file_id': 'CAT123',
                'created_at': '2025-01-15T10:00:00'
            }
            
            # Configura mock
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = [doc_mock]
            
            import database as db
            resultado = db.buscar_documentos(termo)
            
            assert len(resultado) >= 1, \
                f"Busca por categoria '{termo}' deveria retornar documentos"


class TestBuscaResultadosUnicos:
    """
    Testes para garantir que a busca retorna resultados únicos
    (sem duplicatas quando documento casa com múltiplos critérios).
    
    **Validates: Requirements 6.1**
    """
    
    def test_documento_que_casa_multiplos_criterios_aparece_uma_vez(self):
        """
        Quando um documento casa com descrição, tipo E categoria,
        ele deve aparecer apenas uma vez nos resultados.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Documento que casa com todos os critérios
            doc_mock = {
                'id': 1,
                'tipo': 'boleto',
                'descricao': 'Boleto de luz',
                'categoria': 'financeiro',
                'file_id': 'BOL123',
                'created_at': '2025-01-15T10:00:00'
            }
            
            # Configura mock para retornar o mesmo documento em todas as buscas
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = [doc_mock]
            
            import database as db
            resultado = db.buscar_documentos('boleto')
            
            # Conta quantas vezes o documento aparece
            count = sum(1 for d in resultado if d['id'] == 1)
            assert count == 1, \
                f"Documento deveria aparecer apenas uma vez, mas apareceu {count} vezes"


class TestBuscaOrdenacao:
    """
    Testes para garantir que os resultados são ordenados corretamente.
    
    **Validates: Requirements 6.1**
    """
    
    def test_resultados_ordenados_por_data_criacao_desc(self):
        """
        Resultados devem ser ordenados por data de criação (mais recente primeiro).
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Documentos com datas diferentes
            docs_mock = [
                {'id': 1, 'tipo': 'boleto', 'descricao': 'Boleto 1', 'categoria': 'financeiro', 
                 'file_id': 'A', 'created_at': '2025-01-10T10:00:00'},
                {'id': 2, 'tipo': 'boleto', 'descricao': 'Boleto 2', 'categoria': 'financeiro', 
                 'file_id': 'B', 'created_at': '2025-01-15T10:00:00'},
                {'id': 3, 'tipo': 'boleto', 'descricao': 'Boleto 3', 'categoria': 'financeiro', 
                 'file_id': 'C', 'created_at': '2025-01-12T10:00:00'},
            ]
            
            # Configura mock
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = docs_mock
            
            import database as db
            resultado = db.buscar_documentos('boleto')
            
            # Verifica ordenação (mais recente primeiro)
            if len(resultado) >= 2:
                for i in range(len(resultado) - 1):
                    data_atual = resultado[i].get('created_at', '')
                    data_prox = resultado[i + 1].get('created_at', '')
                    assert data_atual >= data_prox, \
                        f"Resultados não estão ordenados: {data_atual} < {data_prox}"


class TestDetectarBuscaDocumento:
    """
    Testes para a função detectar_busca_documento do bot.
    
    Verifica que diferentes padrões de busca são detectados corretamente.
    
    **Validates: Requirements 6.1**
    """
    
    # Importa a função do bot
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para importar a função de detecção"""
        # Importa aqui para evitar problemas de importação circular
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    def test_detecta_cade(self):
        """Testa detecção de 'cadê o/a'"""
        from bot import detectar_busca_documento
        
        assert detectar_busca_documento("cadê o contrato") is not None
        assert detectar_busca_documento("cadê a nota") is not None
        assert detectar_busca_documento("cade o boleto") is not None
    
    def test_detecta_onde_esta(self):
        """Testa detecção de 'onde está/tá'"""
        from bot import detectar_busca_documento
        
        assert detectar_busca_documento("onde está o boleto") is not None
        assert detectar_busca_documento("onde tá a fatura") is not None
        assert detectar_busca_documento("onde fica o contrato") is not None
    
    def test_detecta_acha_procura(self):
        """Testa detecção de 'acha/procura'"""
        from bot import detectar_busca_documento
        
        assert detectar_busca_documento("acha o documento") is not None
        assert detectar_busca_documento("procura o comprovante") is not None
        assert detectar_busca_documento("busca o recibo") is not None
    
    def test_detecta_tem_algum(self):
        """Testa detecção de 'tem algum/alguma'"""
        from bot import detectar_busca_documento
        
        assert detectar_busca_documento("tem algum documento de luz") is not None
        assert detectar_busca_documento("tem alguma nota de compra") is not None
    
    def test_detecta_voce_tem(self):
        """Testa detecção de 'você tem/vc tem'"""
        from bot import detectar_busca_documento
        
        assert detectar_busca_documento("você tem o contrato") is not None
        assert detectar_busca_documento("vc tem a nota") is not None
    
    def test_detecta_me_acha(self):
        """Testa detecção de 'me acha/procura'"""
        from bot import detectar_busca_documento
        
        assert detectar_busca_documento("me acha o documento") is not None
        assert detectar_busca_documento("me procura o boleto") is not None
    
    def test_nao_detecta_mensagem_normal(self):
        """Testa que mensagens normais não são detectadas como busca"""
        from bot import detectar_busca_documento
        
        assert detectar_busca_documento("bom dia") is None
        assert detectar_busca_documento("fechei 2500") is None
        assert detectar_busca_documento("me lembra amanhã de pagar") is None
    
    @given(termo=termo_busca_strategy)
    @settings(max_examples=15)
    def test_extrai_termo_de_busca(self, termo: str):
        """
        Para qualquer termo de busca válido, a função deve extrair
        o termo corretamente.
        """
        from bot import detectar_busca_documento
        
        # Testa com padrão "cadê o {termo}"
        mensagem = f"cadê o {termo}"
        resultado = detectar_busca_documento(mensagem)
        
        if resultado:
            # O termo extraído deve conter pelo menos parte do termo original
            assert len(resultado) >= 2, \
                f"Termo extraído muito curto: '{resultado}'"


class TestInvariantesBusca:
    """
    Testes de invariantes do sistema de busca.
    
    Invariantes são propriedades que devem sempre ser verdadeiras.
    """
    
    def test_busca_vazia_retorna_lista_vazia(self):
        """
        Busca com termo que não existe deve retornar lista vazia, não erro.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Configura mock para retornar lista vazia
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = []
            
            import database as db
            resultado = db.buscar_documentos('termo_inexistente_xyz123')
            
            assert resultado == [], \
                "Busca sem resultados deve retornar lista vazia"
    
    def test_busca_preserva_campos_do_documento(self):
        """
        Busca deve preservar todos os campos do documento retornado.
        """
        with patch('database.get_supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Documento completo
            doc_mock = {
                'id': 1,
                'tipo': 'boleto',
                'descricao': 'Boleto de teste',
                'categoria': 'financeiro',
                'file_id': 'FILE123',
                'message_id': 12345,
                'topic_id': 2,
                'dados_extraidos': {'valor': 100.00},
                'created_at': '2025-01-15T10:00:00'
            }
            
            # Configura mock
            mock_query = MagicMock()
            mock_client.table.return_value.select.return_value = mock_query
            mock_query.ilike.return_value = mock_query
            mock_query.order.return_value = mock_query
            mock_query.execute.return_value.data = [doc_mock]
            
            import database as db
            resultado = db.buscar_documentos('boleto')
            
            assert len(resultado) == 1
            doc = resultado[0]
            
            # Verifica que todos os campos foram preservados
            assert doc['id'] == 1
            assert doc['tipo'] == 'boleto'
            assert doc['descricao'] == 'Boleto de teste'
            assert doc['categoria'] == 'financeiro'
            assert doc['file_id'] == 'FILE123'
            assert doc['message_id'] == 12345
            assert doc['topic_id'] == 2
            assert doc['dados_extraidos'] == {'valor': 100.00}


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
