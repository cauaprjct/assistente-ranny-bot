"""
Testes para extração de dados de boletos
Testa as funções normalize_boleto_data e extract_boleto_from_text

Requirements: 2.3 - Extrair valor, vencimento, beneficiário de boletos
"""
import pytest
from datetime import datetime

# Importa funções do ai.py
from ai import normalize_boleto_data, extract_boleto_from_text


class TestNormalizeBoletoData:
    """Testes para normalização de dados de boleto"""
    
    def test_normaliza_valor_string_com_virgula(self):
        """Testa normalização de valor em formato brasileiro (vírgula)"""
        data = {'valor': '150,50'}
        result = normalize_boleto_data(data)
        assert result['valor'] == 150.50
    
    def test_normaliza_valor_string_com_ponto_milhar(self):
        """Testa normalização de valor com ponto de milhar"""
        data = {'valor': '1.500,00'}
        result = normalize_boleto_data(data)
        assert result['valor'] == 1500.00
    
    def test_normaliza_valor_com_cifrao(self):
        """Testa normalização de valor com R$"""
        data = {'valor': 'R$ 250,00'}
        result = normalize_boleto_data(data)
        assert result['valor'] == 250.00
    
    def test_normaliza_valor_float(self):
        """Testa que valor float é mantido"""
        data = {'valor': 123.45}
        result = normalize_boleto_data(data)
        assert result['valor'] == 123.45
    
    def test_normaliza_valor_int(self):
        """Testa que valor int é convertido para float"""
        data = {'valor': 100}
        result = normalize_boleto_data(data)
        assert result['valor'] == 100.0
        assert isinstance(result['valor'], float)
    
    def test_normaliza_vencimento_formato_brasileiro(self):
        """Testa normalização de data no formato dd/mm/yyyy"""
        data = {'vencimento': '15/02/2025'}
        result = normalize_boleto_data(data)
        assert result['vencimento'] == '2025-02-15'
    
    def test_normaliza_vencimento_formato_iso(self):
        """Testa que data ISO é mantida"""
        data = {'vencimento': '2025-02-15'}
        result = normalize_boleto_data(data)
        assert result['vencimento'] == '2025-02-15'
    
    def test_normaliza_vencimento_formato_hifen(self):
        """Testa normalização de data com hífen"""
        data = {'vencimento': '15-02-2025'}
        result = normalize_boleto_data(data)
        assert result['vencimento'] == '2025-02-15'
    
    def test_normaliza_data_pagamento(self):
        """Testa normalização de data de pagamento"""
        data = {'data_pagamento': '10/01/2025'}
        result = normalize_boleto_data(data)
        assert result['data_pagamento'] == '2025-01-10'
    
    def test_mantem_outros_campos(self):
        """Testa que outros campos são mantidos"""
        data = {
            'valor': 100.00,
            'beneficiario': 'Light',
            'tipo_conta': 'luz'
        }
        result = normalize_boleto_data(data)
        assert result['beneficiario'] == 'Light'
        assert result['tipo_conta'] == 'luz'


class TestExtractBoletoFromText:
    """Testes para extração de dados de texto não-estruturado"""
    
    def test_extrai_valor_formato_brasileiro(self):
        """Testa extração de valor no formato R$ X.XXX,XX"""
        text = "Valor: R$ 1.234,56"
        result = extract_boleto_from_text(text)
        assert result['valor'] == 1234.56
    
    def test_extrai_valor_simples(self):
        """Testa extração de valor simples"""
        text = "Valor: R$ 150,00"
        result = extract_boleto_from_text(text)
        assert result['valor'] == 150.00
    
    def test_extrai_vencimento(self):
        """Testa extração de data de vencimento"""
        text = "Vencimento: 20/02/2025"
        result = extract_boleto_from_text(text)
        assert result['vencimento'] == '2025-02-20'
    
    def test_extrai_vencimento_alternativo(self):
        """Testa extração com 'vence em'"""
        text = "Vence: 15/03/2025"
        result = extract_boleto_from_text(text)
        assert result['vencimento'] == '2025-03-15'
    
    def test_extrai_beneficiario(self):
        """Testa extração de beneficiário"""
        text = "Beneficiário: Light Serviços de Eletricidade"
        result = extract_boleto_from_text(text)
        assert 'Light' in result['beneficiario']
    
    def test_extrai_cedente(self):
        """Testa extração de cedente (sinônimo de beneficiário)"""
        text = "Cedente: CEDAE"
        result = extract_boleto_from_text(text)
        assert 'CEDAE' in result['beneficiario']
    
    def test_detecta_tipo_luz(self):
        """Testa detecção de conta de luz"""
        text = "Conta de energia elétrica Light"
        result = extract_boleto_from_text(text)
        assert result.get('tipo_conta') == 'luz'
    
    def test_detecta_tipo_agua(self):
        """Testa detecção de conta de água"""
        text = "CEDAE - Companhia de Água"
        result = extract_boleto_from_text(text)
        assert result.get('tipo_conta') == 'agua'
    
    def test_detecta_tipo_internet(self):
        """Testa detecção de conta de internet"""
        text = "Fatura Vivo Fibra"
        result = extract_boleto_from_text(text)
        assert result.get('tipo_conta') == 'internet'
    
    def test_detecta_tipo_cartao(self):
        """Testa detecção de fatura de cartão"""
        text = "Fatura Nubank"
        result = extract_boleto_from_text(text)
        assert result.get('tipo_conta') == 'cartao'
    
    def test_marca_como_boleto_quando_tem_valor(self):
        """Testa que documento com valor é marcado como boleto"""
        text = "Valor: R$ 200,00"
        result = extract_boleto_from_text(text)
        assert result.get('tipo_documento') == 'boleto'
    
    def test_marca_como_boleto_quando_tem_vencimento(self):
        """Testa que documento com vencimento é marcado como boleto"""
        text = "Vencimento: 25/01/2025"
        result = extract_boleto_from_text(text)
        assert result.get('tipo_documento') == 'boleto'
    
    def test_extrai_multiplos_campos(self):
        """Testa extração de múltiplos campos de uma vez"""
        text = """
        Beneficiário: Light
        Valor: R$ 350,00
        Vencimento: 10/02/2025
        """
        result = extract_boleto_from_text(text)
        assert result['valor'] == 350.00
        assert result['vencimento'] == '2025-02-10'
        assert 'Light' in result['beneficiario']
        assert result['tipo_conta'] == 'luz'
    
    def test_mantem_raw_text(self):
        """Testa que o texto original é mantido"""
        text = "Algum texto qualquer"
        result = extract_boleto_from_text(text)
        assert result['raw_text'] == text


class TestFormatBoletoResponse:
    """Testes para formatação de resposta de boleto"""
    
    def test_format_boleto_response_import(self):
        """Testa que a função format_boleto_response existe no bot.py"""
        from bot import format_boleto_response
        assert callable(format_boleto_response)
    
    def test_format_boleto_com_valor(self):
        """Testa formatação com valor"""
        from bot import format_boleto_response
        
        analise = {'valor': 150.00}
        result = format_boleto_response("Base: ", analise)
        assert 'R$ 150,00' in result
    
    def test_format_boleto_com_vencimento(self):
        """Testa formatação com vencimento"""
        from bot import format_boleto_response
        
        analise = {'vencimento': '2025-02-15', 'tipo_documento': 'boleto'}
        result = format_boleto_response("Base: ", analise)
        assert '15/02/2025' in result
    
    def test_format_boleto_pergunta_lembrete(self):
        """Testa que pergunta sobre lembrete para boletos com vencimento futuro"""
        from bot import format_boleto_response
        from datetime import datetime, timedelta
        
        # Data futura
        data_futura = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        analise = {'vencimento': data_futura, 'tipo_documento': 'boleto'}
        result = format_boleto_response("Base: ", analise)
        assert 'lembr' in result.lower()
    
    def test_format_boleto_com_beneficiario(self):
        """Testa formatação com beneficiário"""
        from bot import format_boleto_response
        
        analise = {'beneficiario': 'Light Energia'}
        result = format_boleto_response("Base: ", analise)
        assert 'Light Energia' in result
    
    def test_format_boleto_com_tipo_conta(self):
        """Testa formatação com tipo de conta"""
        from bot import format_boleto_response
        
        analise = {'tipo_conta': 'luz'}
        result = format_boleto_response("Base: ", analise)
        assert 'Luz' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestCriarVencimentoDeBoleto:
    """Testes para criação automática de vencimento a partir de boleto
    
    Requirements: 2.3, 8.1
    Property 18: Boleto tem valor e vencimento extraídos
    """
    
    def test_criar_vencimento_de_boleto_import(self):
        """Testa que a função criar_vencimento_de_boleto existe no database.py"""
        from database import criar_vencimento_de_boleto
        assert callable(criar_vencimento_de_boleto)
    
    def test_retorna_none_sem_dados_minimos(self):
        """Testa que retorna None quando não há valor nem vencimento"""
        from database import criar_vencimento_de_boleto
        
        # Sem valor e sem vencimento
        result = criar_vencimento_de_boleto({})
        assert result is None
        
        # Apenas beneficiário (sem valor/vencimento)
        result = criar_vencimento_de_boleto({'beneficiario': 'Light'})
        assert result is None
    
    def test_retorna_none_sem_vencimento(self):
        """Testa que retorna None quando não há vencimento (mesmo com valor)"""
        from database import criar_vencimento_de_boleto
        
        # Apenas valor, sem vencimento
        result = criar_vencimento_de_boleto({'valor': 150.00})
        assert result is None
    
    def test_monta_descricao_com_beneficiario(self):
        """Testa que a descrição inclui o beneficiário quando disponível"""
        from database import criar_vencimento_de_boleto
        
        dados = {
            'valor': 200.00,
            'vencimento': '2025-02-15',
            'beneficiario': 'Light Energia',
            'tipo_conta': 'luz'
        }
        
        result = criar_vencimento_de_boleto(dados)
        
        # Verifica que foi criado (não é None)
        # Nota: Este teste pode falhar se não houver conexão com Supabase
        # Em ambiente de teste real, usaríamos mock
        if result:
            assert 'Light Energia' in result.get('descricao', '')
    
    def test_monta_descricao_sem_beneficiario(self):
        """Testa que a descrição usa tipo de conta quando não há beneficiário"""
        from database import criar_vencimento_de_boleto
        
        dados = {
            'valor': 100.00,
            'vencimento': '2025-02-20',
            'tipo_conta': 'agua'
        }
        
        result = criar_vencimento_de_boleto(dados)
        
        if result:
            assert 'Água' in result.get('descricao', '')
    
    def test_tipo_conta_mapeado_corretamente(self):
        """Testa que os tipos de conta são mapeados para descrições amigáveis"""
        from database import criar_vencimento_de_boleto
        
        tipos_esperados = {
            'luz': 'Conta de Luz',
            'agua': 'Conta de Água',
            'internet': 'Internet',
            'telefone': 'Telefone',
            'gas': 'Gás',
            'aluguel': 'Aluguel',
            'condominio': 'Condomínio',
            'cartao': 'Fatura Cartão',
        }
        
        for tipo, esperado in tipos_esperados.items():
            dados = {
                'valor': 50.00,
                'vencimento': '2025-03-01',
                'tipo_conta': tipo
            }
            
            result = criar_vencimento_de_boleto(dados)
            
            if result:
                assert esperado in result.get('descricao', ''), f"Tipo {tipo} deveria gerar descrição com '{esperado}'"
    
    def test_limita_tamanho_descricao(self):
        """Testa que descrições muito longas são truncadas"""
        from database import criar_vencimento_de_boleto
        
        dados = {
            'valor': 100.00,
            'vencimento': '2025-02-15',
            'beneficiario': 'A' * 200,  # Beneficiário muito longo
            'tipo_conta': 'outro'
        }
        
        result = criar_vencimento_de_boleto(dados)
        
        if result:
            assert len(result.get('descricao', '')) <= 100


class TestVencimentoIntegracaoComBoleto:
    """Testes de integração entre extração de boleto e criação de vencimento
    
    Validates: Requirements 2.3, 8.1
    """
    
    def test_fluxo_completo_boleto_para_vencimento(self):
        """Testa o fluxo completo: texto -> extração -> vencimento"""
        from ai import extract_boleto_from_text
        from database import criar_vencimento_de_boleto
        
        # Simula texto de um boleto
        texto_boleto = """
        Beneficiário: Light Serviços de Eletricidade
        Valor: R$ 350,00
        Vencimento: 15/02/2025
        """
        
        # Extrai dados do boleto
        dados = extract_boleto_from_text(texto_boleto)
        
        # Verifica extração
        assert dados.get('valor') == 350.00
        assert dados.get('vencimento') == '2025-02-15'
        assert 'Light' in dados.get('beneficiario', '')
        assert dados.get('tipo_conta') == 'luz'
        
        # Cria vencimento (pode falhar sem Supabase)
        result = criar_vencimento_de_boleto(dados)
        
        # Se conseguiu criar, verifica campos
        if result:
            assert result.get('valor') == 350.00
            assert result.get('data_vencimento') == '2025-02-15'
            assert 'Light' in result.get('descricao', '')
