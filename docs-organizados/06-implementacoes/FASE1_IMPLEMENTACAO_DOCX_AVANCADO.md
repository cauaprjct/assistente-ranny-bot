# Fase 1: Atualização de DOCX - Implementação Completa

## Resumo

Esta documentação descreve a implementação da **Fase 1** do plano de melhoria do sistema de processamento de documentos Word do Assistente Ranny.

---

## Mudanças Realizadas

### 1. Atualização de Biblioteca

**Arquivo**: [`requirements.txt`](assistente-ranny/requirements.txt)

```diff
- python-docx>=1.1.0
+ # python-docx>=1.1.0  # Substituido por skelmis (fork melhorado)
+ skelmis-python-docx>=1.1.0
```

**Benefícios**:
- Suporte a imagens flutuantes
- Melhor suporte a tabelas
- TOC (índice) automático
- API compatível com python-docx original

---

### 2. Importação Inteligente

**Arquivo**: [`pdf_tools.py`](assistente-ranny/pdf_tools.py:44-66)

```python
try:
    # Tenta importar skelmis (fork melhorado com imagens flutuantes)
    try:
        from skelmis.docx import Document
        from skelmis.docx.shared import Inches, Pt, Cm
        HAS_SKELMIS_DOCX = True
        logger.info("Usando skelmis-python-docx (fork melhorado)")
    except ImportError:
        # Fallback para python-docx original
        from docx import Document
        from docx.shared import Inches, Pt, Cm
        HAS_SKELMIS_DOCX = False
        logger.info("Usando python-docx original")
except ImportError:
    HAS_DOCX = False
    logger.warning("python-docx não instalado")
```

**Benefícios**:
- Compatibilidade com ambas bibliotecas
- Fallback automático se skelmis não estiver instalado
- Log informativo sobre qual biblioteca está sendo usada

---

### 3. Novas Funções Implementadas

#### 3.1 Leitura de Headers/Footers

```python
def ler_docx_headers_footers(docx_bytes: bytes) -> Optional[dict]
```

**Uso**:
```python
resultado = ler_docx_headers_footers(docx_bytes)
# Retorna: {'headers': [...], 'footers': [...], 'num_secoes': N}
```

#### 3.2 Edição de Header

```python
def editar_docx_header(docx_bytes: bytes, novo_texto: str, secao_idx: int = 0) -> Optional[bytes]
```

**Uso**:
```python
docx_editado = editar_docx_header(docx_bytes, "GRN Pizzas - Documento Confidencial")
```

#### 3.3 Edição de Footer

```python
def editar_docx_footer(docx_bytes: bytes, novo_texto: str, secao_idx: int = 0) -> Optional[bytes]
```

**Uso**:
```python
docx_editado = editar_docx_footer(docx_bytes, "Página 1 de 10")
```

#### 3.4 Contagem de Imagens

```python
def contar_imagens_docx(docx_bytes: bytes) -> int
```

**Uso**:
```python
num_imagens = contar_imagens_docx(docx_bytes)
if num_imagens > 0:
    print(f"Documento contém {num_imagens} imagens")
```

#### 3.5 Validação de Integridade

```python
def validar_integridade_docx(docx_bytes: bytes, original_bytes: bytes = None) -> dict
```

**Uso**:
```python
validacao = validar_integridade_docx(docx_editado, docx_original)
if not validacao['valido']:
    print(f"Alertas: {validacao['alertas']}")
```

#### 3.6 Substituição Preservando Imagens

```python
def editar_docx_preservar_imagens(docx_bytes: bytes, texto_antigo: str, texto_novo: str) -> Optional[Tuple[bytes, int]]
```

**Uso**:
```python
docx_editado, num_subs = editar_docx_preservar_imagens(
    docx_bytes, 
    "João Silva", 
    "Maria Santos"
)
```

#### 3.7 Adicionar Imagem Inline

```python
def adicionar_imagem_docx(docx_bytes: bytes, imagem_bytes: bytes, posicao: str = 'fim', largura_polegadas: float = 4.0) -> Optional[bytes]
```

**Uso**:
```python
with open('logo.png', 'rb') as f:
    imagem = f.read()
docx_com_imagem = adicionar_imagem_docx(docx_bytes, imagem, posicao='fim', largura_polegadas=3.0)
```

#### 3.8 Adicionar Imagem Flutuante (skelmis)

```python
def adicionar_imagem_flutuante(docx_bytes: bytes, imagem_bytes: bytes, pos_x: float, pos_y: float, largura_polegadas: float = 2.0, altura_polegadas: float = 2.0) -> Optional[bytes]
```

**Uso**:
```python
docx_com_imagem = adicionar_imagem_flutuante(
    docx_bytes, 
    logo_bytes, 
    pos_x=100,  # pontos
    pos_y=50,   # pontos
    largura_polegadas=2.0,
    altura_polegadas=1.5
)
```

---

## Comparativo: Antes vs Depois

| Funcionalidade | Antes | Depois |
|----------------|-------|--------|
| Headers | Não acessado | Leitura e edição |
| Footers | Não acessado | Leitura e edição |
| Imagens inline | Preservado (não editado) | Preservado e adicionável |
| Imagens flutuantes | Não suportado | Suportado (skelmis) |
| Validação de integridade | Não existia | Completa |
| Contagem de imagens | Não existia | Disponível |

---

## Instalação

Para usar as novas funcionalidades, instale a nova dependência:

```bash
pip install skelmis-python-docx
```

Ou instale todas as dependências atualizadas:

```bash
cd assistente-ranny
pip install -r requirements.txt
```

---

## Próximos Passos (Fase 2)

1. **Integrar python-docx-template** para templates
2. **Criar templates padrão**:
   - `contrato_entregador.docx`
   - `relatorio_semanal.docx`
   - `comprovante_pagamento.docx`
3. **Implementar sistema de templates** no bot

---

## Testes Recomendados

```python
# Teste de validação
def testar_validacao():
    docx_bytes = criar_docx_texto("Teste de documento", "Título")
    validacao = validar_integridade_docx(docx_bytes)
    assert validacao['valido'] == True
    assert validacao['num_paragrafos'] > 0

# Teste de header/footer
def testar_header_footer():
    docx_bytes = criar_docx_texto("Conteúdo", "Título")
    docx_com_header = editar_docx_header(docx_bytes, "Header Teste")
    resultado = ler_docx_headers_footers(docx_com_header)
    assert len(resultado['headers']) > 0

# Teste de imagem
def testar_imagem():
    docx_bytes = criar_docx_texto("Conteúdo", "Título")
    imagem_bytes = criar_imagem_teste()  # Criar imagem PNG de teste
    docx_com_imagem = adicionar_imagem_docx(docx_bytes, imagem_bytes)
    assert contar_imagens_docx(docx_com_imagem) == 1
```

---

## Autor

Implementação realizada como parte da melhoria do sistema de processamento de documentos do Assistente Ranny V3.
