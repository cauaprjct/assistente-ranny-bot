# Fase 2: Sistema de Templates - Implementação Completa

## Resumo

Esta documentação descreve a implementação da **Fase 2** do plano de melhoria do sistema de processamento de documentos Word do Assistente Ranny.

---

## Arquivos Criados/Modificados

### 1. Novo Arquivo: [`docx_templates.py`](assistente-ranny/docx_templates.py)

Módulo completo de templates com:

- **5 templates pré-definidos**:
  - `contrato_entregador` - Contrato de prestação de serviços
  - `relatorio_semanal` - Relatório semanal de entregas
  - `comprovante_pagamento` - Comprovante para entregadores
  - `recibo_simples` - Recibo de pagamento
  - `lista_presenca` - Lista de presença para reuniões

- **Funções disponíveis**:
  - `listar_templates()` - Lista todos os templates
  - `obter_template(nome)` - Obtém informações de um template
  - `renderizar_template(nome, contexto)` - Renderiza template com variáveis
  - `criar_template_personalizado()` - Salva novo template

### 2. Modificado: [`requirements.txt`](assistente-ranny/requirements.txt)

```diff
+ docxtpl>=0.16.7  # Templates Jinja2 para DOCX
```

### 3. Modificado: [`ai.py`](assistente-ranny/ai.py)

Nova função:
```python
async def extrair_variaveis_template(texto: str, template_nome: str, variaveis_necessarias: list) -> dict
```

### 4. Modificado: [`bot.py`](assistente-ranny/bot.py)

- Importado módulo `docx_templates`
- Adicionado handler `handle_templates()`
- Integrado no fluxo principal

---

## Como Usar

### Exemplo 1: Criar Contrato de Entregador

```
Ranny: "cria um contrato para o entregador João Silva, CPF 123.456.789-00, RG 12.345.678-9, começando dia 01/03/2024"

Bot: "Vou criar o documento: Contrato Entregador

Dados:
• Nome Entregador: João Silva
• Cpf: 123.456.789-00
• Rg: 12.345.678-9
• Data Inicio: 01/03/2024

Confirma? (sim/não)"

Ranny: "sim"

Bot: [Envia documento contrato_entregador.docx]
```

### Exemplo 2: Criar Relatório Semanal

```
Ranny: "gera relatório semanal de 10 a 17 de fevereiro, 150 entregas, 3 entregadores, valor total R$ 1.800,00"

Bot: "Vou criar o documento: Relatorio Semanal

Dados:
• Periodo: 10 a 17 de fevereiro
• Total Entregas: 150
• Total Entregadores: 3
• Valor Total: R$ 1.800,00

Confirma? (sim/não)"

Ranny: "sim"

Bot: [Envia documento relatorio_semanal.docx]
```

### Exemplo 3: Criar Recibo

```
Ranny: "faz um recibo de R$ 500,00 para Maria Santos, CPF 987.654.321-00, referente a serviços de limpeza"

Bot: [Envia recibo preenchido]
```

---

## Templates Disponíveis

| Template | Descrição | Variáveis |
|----------|-----------|-----------|
| `contrato_entregador` | Contrato de prestação de serviços | nome_entregador, cpf, rg, data_inicio, valor_entrega, dias_trabalho |
| `relatorio_semanal` | Relatório semanal de entregas | periodo, total_entregas, total_entregadores, valor_total, dias |
| `comprovante_pagamento` | Comprovante de pagamento | nome, periodo, valor, data_pagamento, forma_pagamento |
| `recibo_simples` | Recibo simples de pagamento | valor, valor_extenso, referente, nome_recebedor, cpf_recebedor, data |
| `lista_presenca` | Lista de presença | titulo_reuniao, data_reuniao, participantes |

---

## Fluxo de Processamento

```
Mensagem do usuário
    |
    v
handle_templates() detecta template
    |
    v
ai.extrair_variaveis_template() extrai dados
    |
    v
Mostra resumo e pede confirmação
    |
    v
Usuário confirma?
    |
    +-- SIM --> docx_templates.renderizar_template()
    |                    |
    |                    v
    |              Envia documento .docx
    |
    +-- NÃO --> Cancela operação
```

---

## Criar Template Personalizado

Para adicionar um novo template:

1. Crie um arquivo `.docx` com variáveis Jinja2:
   ```
   Nome: {{ nome }}
   Data: {{ data_hoje }}
   ```

2. Salve em `assistente-ranny/templates/`

3. Registre no código:
   ```python
   TEMPLATES_DISPONIVEIS['meu_template'] = {
       'descricao': 'Descrição do template',
       'variaveis': ['nome', 'data'],
       'arquivo': 'meu_template.docx'
   }
   ```

---

## Instalação

```bash
cd assistente-ranny
pip install -r requirements.txt
```

---

## Próximos Passos (Fase 3)

1. **Avaliar Spire.Doc** para documentos críticos
2. **Implementar fallback** skelmis → Spire.Doc
3. **Validação automática** de integridade pós-edição

---

## Autor

Implementação realizada como parte da melhoria do sistema de processamento de documentos do Assistente Ranny V3.
