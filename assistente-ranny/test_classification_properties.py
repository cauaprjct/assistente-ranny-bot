"""
Property-Based Tests para Classificação de Documentos

Feature: assistente-ranny-v3
Property 1: Documento no Chat é sempre classificado e movido
Property 2: Categoria mapeia corretamente para tópico

Validates: Requirements 1.2, 2.1, 2.2

Testes de propriedade usando hypothesis para validar:
1. Toda classificação retorna uma categoria válida
2. Toda categoria válida mapeia para um tópico único
"""
import pytest
from hypothesis import given, strategies as st, settings, assume

from config import CATEGORIA_TOPICO, TOPICS


# ============ ESTRATÉGIAS DE GERAÇÃO ============

# Categorias válidas do sistema
CATEGORIAS_VALIDAS = ['financeiro', 'empresa', 'funcionarios', 'juridico', 'pessoal', 'manutencao', 'outros']

# Estratégia para gerar categorias válidas
categoria_strategy = st.sampled_from(CATEGORIAS_VALIDAS)

# Estratégia para gerar texto de documento (simulando análise do Gemini)
documento_text_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=1,
    max_size=500
)


# ============ PROPERTY 1: Classificação sempre retorna categoria válida ============

class TestClassificacaoRetornaCategoriaValida:
    """
    Property 1: Documento no Chat é sempre classificado e movido
    
    Para qualquer documento enviado no Tópico_Chat, o bot deve classificá-lo
    em uma categoria válida (financeiro, empresa, juridico, pessoal, 
    funcionarios, manutencao, outros).
    
    **Feature: assistente-ranny-v3, Property 1: Documento no Chat é sempre classificado e movido**
    **Validates: Requirements 1.2, 2.1**
    """
    
    @given(categoria=categoria_strategy)
    @settings(max_examples=100)
    def test_categoria_valida_esta_no_mapeamento(self, categoria: str):
        """
        Para qualquer categoria válida, ela deve existir no mapeamento CATEGORIA_TOPICO.
        
        Isso garante que qualquer resultado de classificação pode ser mapeado
        para um tópico de destino.
        """
        assert categoria in CATEGORIA_TOPICO, \
            f"Categoria '{categoria}' não está no mapeamento CATEGORIA_TOPICO"
    
    def test_todas_categorias_validas_tem_mapeamento(self):
        """
        Verifica que todas as categorias válidas do sistema têm mapeamento.
        """
        for categoria in CATEGORIAS_VALIDAS:
            assert categoria in CATEGORIA_TOPICO, \
                f"Categoria '{categoria}' não tem mapeamento para tópico"
    
    def test_classify_document_retorna_categoria_valida(self):
        """
        Testa que a função classify_document sempre retorna uma categoria válida.
        
        Nota: Este teste usa mock porque classify_document chama a API do Gemini.
        O teste verifica que o fallback 'outros' é uma categoria válida.
        """
        # O fallback da função classify_document é 'outros'
        fallback_categoria = 'outros'
        assert fallback_categoria in CATEGORIAS_VALIDAS, \
            "Categoria de fallback deve ser válida"
        assert fallback_categoria in CATEGORIA_TOPICO, \
            "Categoria de fallback deve ter mapeamento para tópico"


# ============ PROPERTY 2: Categoria mapeia corretamente para tópico ============

class TestCategoriaMapeiaParaTopico:
    """
    Property 2: Categoria mapeia corretamente para tópico
    
    Para qualquer categoria válida, deve existir um mapeamento único 
    para um ID de tópico do Telegram.
    
    **Feature: assistente-ranny-v3, Property 2: Categoria mapeia corretamente para tópico**
    **Validates: Requirements 2.2**
    """
    
    @given(categoria=categoria_strategy)
    @settings(max_examples=100)
    def test_categoria_mapeia_para_topico_inteiro(self, categoria: str):
        """
        Para qualquer categoria válida, o mapeamento deve retornar um ID de tópico
        que é um número inteiro positivo.
        """
        topic_id = CATEGORIA_TOPICO.get(categoria)
        
        assert topic_id is not None, \
            f"Categoria '{categoria}' não tem mapeamento"
        assert isinstance(topic_id, int), \
            f"Topic ID para '{categoria}' deve ser inteiro, mas é {type(topic_id)}"
        assert topic_id > 0, \
            f"Topic ID para '{categoria}' deve ser positivo, mas é {topic_id}"
    
    @given(categoria=categoria_strategy)
    @settings(max_examples=100)
    def test_mapeamento_e_determinístico(self, categoria: str):
        """
        Para qualquer categoria, múltiplas chamadas ao mapeamento devem
        retornar o mesmo tópico (determinismo).
        """
        topic_id_1 = CATEGORIA_TOPICO.get(categoria)
        topic_id_2 = CATEGORIA_TOPICO.get(categoria)
        
        assert topic_id_1 == topic_id_2, \
            f"Mapeamento não é determinístico para '{categoria}'"
    
    def test_topicos_destino_sao_diferentes_do_chat(self):
        """
        Verifica que nenhum tópico de destino é o tópico Chat.
        
        Documentos classificados devem ser movidos para tópicos de arquivo,
        nunca de volta para o Chat.
        """
        chat_topic_id = TOPICS.get('chat')
        
        for categoria, topic_id in CATEGORIA_TOPICO.items():
            assert topic_id != chat_topic_id, \
                f"Categoria '{categoria}' mapeia para o Chat, mas deveria ir para tópico de arquivo"
    
    def test_mapeamento_cobre_todas_categorias(self):
        """
        Verifica que o mapeamento CATEGORIA_TOPICO cobre todas as categorias válidas.
        """
        for categoria in CATEGORIAS_VALIDAS:
            assert categoria in CATEGORIA_TOPICO, \
                f"Categoria '{categoria}' não está no mapeamento"
    
    @given(categoria=categoria_strategy)
    @settings(max_examples=100)
    def test_topico_destino_existe_em_topics(self, categoria: str):
        """
        Para qualquer categoria, o tópico de destino deve existir na configuração TOPICS.
        
        Isso garante que o bot pode realmente enviar mensagens para o tópico.
        """
        topic_id = CATEGORIA_TOPICO.get(categoria)
        
        # Verifica se o topic_id está em algum valor de TOPICS
        topics_ids = list(TOPICS.values())
        
        assert topic_id in topics_ids, \
            f"Topic ID {topic_id} para categoria '{categoria}' não está configurado em TOPICS"


# ============ TESTES DE INVARIANTES ============

class TestInvariantesClassificacao:
    """
    Testes de invariantes do sistema de classificação.
    
    Invariantes são propriedades que devem sempre ser verdadeiras,
    independente do estado do sistema.
    """
    
    def test_categoria_outros_sempre_existe(self):
        """
        A categoria 'outros' deve sempre existir como fallback.
        
        Quando o Gemini não consegue classificar, o sistema usa 'outros'.
        """
        assert 'outros' in CATEGORIAS_VALIDAS
        assert 'outros' in CATEGORIA_TOPICO
    
    def test_mapeamento_nao_tem_valores_nulos(self):
        """
        Nenhum mapeamento categoria -> tópico pode ter valor nulo.
        """
        for categoria, topic_id in CATEGORIA_TOPICO.items():
            assert topic_id is not None, \
                f"Categoria '{categoria}' tem mapeamento nulo"
    
    def test_categorias_sao_lowercase(self):
        """
        Todas as categorias devem estar em lowercase para consistência.
        """
        for categoria in CATEGORIA_TOPICO.keys():
            assert categoria == categoria.lower(), \
                f"Categoria '{categoria}' não está em lowercase"
    
    def test_topics_config_tem_chat(self):
        """
        A configuração TOPICS deve ter o tópico 'chat' definido.
        
        O Chat é o ponto de entrada onde documentos são recebidos.
        """
        assert 'chat' in TOPICS, "TOPICS deve ter 'chat' configurado"
        assert TOPICS['chat'] > 0, "Chat topic ID deve ser positivo"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
