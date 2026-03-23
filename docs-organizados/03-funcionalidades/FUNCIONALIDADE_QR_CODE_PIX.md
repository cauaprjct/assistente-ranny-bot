# 📱 Nova Funcionalidade: Leitura de QR Code PIX

## 🎯 O Que Foi Adicionado

O bot agora consegue **detectar e decodificar QR codes PIX** automaticamente quando você envia uma imagem de boleto!

### ✨ Funcionalidades

1. **Detecção Automática de QR Code**
   - Quando você envia uma imagem, o bot primeiro tenta detectar QR codes
   - Se encontrar um QR code PIX, decodifica automaticamente
   - Funciona com qualquer imagem que contenha QR code visível

2. **Extração de Dados do PIX**
   - 👤 **Beneficiário** - Nome de quem vai receber
   - 🔑 **Chave PIX** - Email, telefone, CPF, CNPJ ou chave aleatória
   - 💰 **Valor** - Se estiver definido no QR code
   - 📍 **Cidade** - Localização do beneficiário
   - 🔖 **Referência** - Identificador da transação
   - 📱 **QR Code completo** - Para copiar e colar

3. **Apresentação Formatada**
   - Dados organizados e fáceis de ler
   - Emojis para identificação visual
   - Máscaras de privacidade em CPF/CNPJ
   - Informações técnicas do QR code

4. **Compatibilidade com Código de Barras**
   - Continua extraindo código de barras tradicional (47-48 dígitos)
   - Agora também extrai QR code PIX
   - Apresenta ambos quando disponíveis

---

## 🔧 Como Funciona

### Fluxo de Processamento

```
1. Usuário envia imagem de boleto
         ↓
2. Bot tenta detectar QR code
         ↓
3a. QR code PIX encontrado?
    → SIM: Decodifica e apresenta dados do PIX
    → NÃO: Continua com análise Gemini Vision
         ↓
4. Extrai código de barras tradicional (se houver)
         ↓
5. Apresenta todos os dados encontrados
```

### Tecnologias Utilizadas

- **pyzbar** - Biblioteca para detectar e decodificar QR codes
- **Pillow (PIL)** - Processamento de imagens
- **Regex** - Parsing do formato EMV QR Code (BR Code)

---

## 📋 Exemplo de Uso

### Antes (Só Código de Barras)

```
📄 BOLETO DETECTADO

💰 Valor: R$ 150,00
📅 Vencimento: 20/01/2025
🏢 Beneficiário: NATURGY GÁS NATURAL
📊 Tipo: Conta de Gás

🔢 Código de Barras:
34191234567890123456789012345678901234567
```

### Agora (Com QR Code PIX)

```
📱 QR CODE PIX DETECTADO

👤 Beneficiário: NATURGY GÁS NATURAL
🔑 Chave PIX (cnpj): 12.***.***/****.45
💰 Valor: R$ 150,00
📍 Cidade: SAO PAULO
🔖 Referência: CONTA123456

ℹ️ Informação Técnica:
• Tamanho do QR Code: 156 caracteres
• Código: `00020126580014br.gov.bcb.pix0136...`

✅ Este QR Code pode ser usado para pagamento via PIX

---

🔢 CÓDIGO DE BARRAS TRADICIONAL:
34191.23456 78901.234567 89012.345678 9 01234567890123
```

---

## 🚀 Instalação

### 1. Instalar Dependências Python

```bash
pip install pyzbar Pillow
```

### 2. Instalar Biblioteca ZBar (Sistema)

O `pyzbar` precisa da biblioteca ZBar instalada no sistema:

#### Windows:
1. Baixar ZBar DLL: http://zbar.sourceforge.net/download.html
2. Extrair `libzbar-64.dll` para `C:\Windows\System32\`

Ou usar Chocolatey:
```bash
choco install zbar
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install libzbar0
```

#### Linux (Fedora/CentOS):
```bash
sudo yum install zbar
```

#### macOS:
```bash
brew install zbar
```

---

## 🧪 Testar a Funcionalidade

### Teste Rápido

```bash
cd assistente-ranny
python qrcode_reader.py
```

**Saída esperada:**
```
============================================================
🧪 TESTE DO LEITOR DE QR CODE PIX
============================================================

1️⃣  Verificando bibliotecas...
   ✅ pyzbar instalado
   ✅ Pillow instalado

2️⃣  Testando decodificação PIX...
   ✅ PIX decodificado com sucesso!
   Beneficiário: Fulano de Tal
   Valor: R$ 10.00

3️⃣  Testando formatação de código de barras...
   Original: 34191234567890123456789012345678901234567
   Formatado: 34191.23456 78901.234567 89012.345678 9 01234567890123

============================================================
✅ TESTE CONCLUÍDO!
============================================================
```

### Teste com Imagem Real

1. Tire uma foto de um boleto com QR code PIX
2. Envie para o bot no Telegram
3. O bot deve detectar e decodificar automaticamente

---

## 📊 Tipos de Chave PIX Suportados

O bot identifica automaticamente o tipo de chave:

| Tipo | Formato | Exemplo | Emoji |
|------|---------|---------|-------|
| **Email** | email@dominio.com | joao@email.com | 📧 |
| **Telefone** | +5511999999999 | +5511987654321 | 📱 |
| **CPF** | 11 dígitos | 12345678901 | 🆔 |
| **CNPJ** | 14 dígitos | 12345678000195 | 🏢 |
| **Aleatória** | UUID | 123e4567-e89b-12d3-a456-426614174000 | 🔑 |

---

## 🔒 Privacidade e Segurança

### Máscaras de Proteção

Para proteger dados sensíveis, o bot mascara automaticamente:

- **CPF:** `123.***.***-01` (mostra só 3 primeiros e 2 últimos dígitos)
- **CNPJ:** `12.***.***/****.95` (mostra só 2 primeiros e 2 últimos dígitos)

### Dados Armazenados

O bot armazena:
- ✅ Beneficiário
- ✅ Valor
- ✅ Tipo de chave (mas não a chave completa se for CPF/CNPJ)
- ✅ Referência da transação

O bot NÃO armazena:
- ❌ Chave PIX completa (apenas tipo)
- ❌ QR code completo (apenas hash)

---

## 🎨 Formato do QR Code PIX (BR Code)

O PIX usa o padrão **EMV QR Code** (BR Code) com estrutura:

```
ID(2) + Tamanho(2) + Valor(N)
```

### Principais Tags:

| Tag | Descrição | Exemplo |
|-----|-----------|---------|
| 00 | Payload Format Indicator | 01 |
| 26 | Merchant Account (Chave PIX) | br.gov.bcb.pix |
| 52 | Merchant Category Code | 0000 |
| 53 | Transaction Currency | 986 (BRL) |
| 54 | Transaction Amount | 10.00 |
| 59 | Merchant Name | Nome do Beneficiário |
| 60 | Merchant City | Cidade |
| 62 | Additional Data | Referência |
| 63 | CRC | Checksum |

---

## 🐛 Troubleshooting

### Erro: "pyzbar não instalado"

**Solução:**
```bash
pip install pyzbar
```

Se ainda não funcionar, instale a biblioteca ZBar do sistema (ver seção Instalação).

---

### Erro: "Failed to load zbar library"

**Windows:**
1. Baixe ZBar DLL: http://zbar.sourceforge.net/download.html
2. Copie `libzbar-64.dll` para `C:\Windows\System32\`

**Linux:**
```bash
sudo apt-get install libzbar0
```

---

### QR Code não é detectado

**Possíveis causas:**
1. Imagem muito pequena ou de baixa qualidade
2. QR code parcialmente cortado
3. Muita distorção ou reflexo na imagem

**Soluções:**
- Tire foto mais próxima e centralizada
- Melhore a iluminação
- Evite reflexos e sombras
- Use câmera de melhor qualidade

---

### QR Code detectado mas não é PIX

O bot detecta qualquer QR code, mas só decodifica PIX.

Se o QR code não for PIX, o bot mostra:
```
📱 QR CODE DETECTADO

Conteúdo: https://exemplo.com/pagamento...
```

---

## 📈 Estatísticas de Uso

O bot registra nos logs:

```
✅ QR Code PIX detectado e decodificado!
PIX decodificado: NATURGY GÁS NATURAL
QR code detectado: 156 caracteres
```

---

## 🔄 Integração com Vencimentos

Quando um QR code PIX é detectado:

1. **Se tem valor e beneficiário:**
   - Cria vencimento automaticamente
   - Categoria: baseada no beneficiário
   - Valor: extraído do PIX
   - Data: hoje (ou vencimento se informado)

2. **Se não tem valor:**
   - Salva como documento
   - Categoria: financeiro
   - Observação: "PIX - aguardando valor"

---

## 🎯 Próximas Melhorias

Possíveis melhorias futuras:

- [ ] Gerar QR code PIX para recebimentos
- [ ] Validar checksum do QR code
- [ ] Suportar PIX Copia e Cola (texto)
- [ ] Histórico de QR codes lidos
- [ ] Integração com banco para pagamento direto
- [ ] Notificação quando PIX for pago

---

## 📚 Referências

- [Especificação PIX - Banco Central](https://www.bcb.gov.br/estabilidadefinanceira/pix)
- [EMV QR Code Specification](https://www.emvco.com/emv-technologies/qrcodes/)
- [pyzbar Documentation](https://github.com/NaturalHistoryMuseum/pyzbar)
- [ZBar Library](http://zbar.sourceforge.net/)

---

## 🤝 Contribuindo

Encontrou um bug ou tem uma sugestão?

1. Teste com diferentes tipos de boletos
2. Reporte problemas com exemplos
3. Sugira melhorias

---

**Documentação criada em:** 18/01/2026
**Versão:** 1.0
**Status:** ✅ Implementado e testado
