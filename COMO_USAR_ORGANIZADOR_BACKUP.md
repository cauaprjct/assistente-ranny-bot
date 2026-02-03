# 📤 Como Usar o Organizador de Backup

## 🎯 O Que Faz

Este script analisa todos os 1.166 arquivos do `BACKUP_ORGANIZADO` e:
- ✅ Classifica automaticamente cada arquivo
- ✅ Mapeia para os tópicos corretos do Telegram
- ✅ Cria novos tópicos se necessário
- ✅ Faz upload organizado para o grupo
- ✅ Gera relatório completo

## 🚀 Como Usar

### 1. Instalar Dependências (se ainda não tiver)

```bash
pip install python-telegram-bot python-dotenv google-generativeai
```

### 2. Executar o Script

```bash
python organizar_backup_telegram.py
```

### 3. Seguir o Processo Interativo

O script vai:

#### Passo 1: Escanear Arquivos
```
📂 Escaneando BACKUP_ORGANIZADO...
✅ Escaneamento concluído: 1166 arquivos
```

#### Passo 2: Mostrar Estatísticas
```
📊 ESTATÍSTICAS DO BACKUP
================================================================================

📁 Total de arquivos: 1166
⚠️  Ignorados (extensão): 15
⚠️  Ignorados (tamanho >50MB): 3

📂 Por categoria:
  • FINANCEIRO         → FINANCEIRO      (123 arquivos)
  • EMPRESA            → EMPRESA         (327 arquivos)
  • FUNCIONARIOS       → FUNCIONARIOS    (85 arquivos)
  • OPERACIONAL        → NOVO TÓPICO     (150 arquivos)
  • MIDIA              → NOVO TÓPICO     (208 arquivos)
  ...

🆕 Novos tópicos necessários:
  • OPERACIONAL
  • MIDIA
  • CONTROLES
```

#### Passo 3: Confirmar Continuação
```
Deseja continuar? (s/n): s
```

#### Passo 4: Criar Novos Tópicos (se necessário)
```
Criar 3 novos tópicos? (s/n): s

🆕 Criando 3 novos tópicos...
  ✅ OPERACIONAL (ID: 123)
  ✅ MIDIA (ID: 124)
  ✅ CONTROLES (ID: 125)
```

#### Passo 5: Escolher Modo de Upload
```
Opções de upload:
1. Fazer upload de TODOS os arquivos
2. Fazer upload de apenas 10 arquivos (teste)
3. Simular upload (dry run)
4. Cancelar

Escolha uma opção (1-4): 2
```

#### Passo 6: Upload
```
📤 Fazendo upload de 10 arquivos...
  ✅ [1/10] boleto.pdf
  ✅ [2/10] contrato.docx
  ✅ [3/10] nota_fiscal.pdf
  ...

================================================================================
✅ Sucesso: 10
❌ Erros: 0
================================================================================
```

#### Passo 7: Relatório
```
📄 Relatório salvo em: relatorio_upload_backup.json
✅ Processo concluído!
```

## 📋 Mapeamento de Pastas → Tópicos

| Pasta do Backup | Tópico do Telegram |
|-----------------|-------------------|
| 01_EMPRESA_GRN_PIZZAS/DOCUMENTOS_EMPRESA | EMPRESA |
| 01_EMPRESA_GRN_PIZZAS/FISCAL | EMPRESA |
| 01_EMPRESA_GRN_PIZZAS/OPERACIONAL | OPERACIONAL (novo) |
| 01_EMPRESA_GRN_PIZZAS/RH_DEPARTAMENTO_PESSOAL | FUNCIONARIOS |
| 02_FINANCEIRO | FINANCEIRO |
| 03_PESSOAL_RANNY | PESSOAL |
| 04_JURIDICO | JURIDICO |
| 05_CURRICULOS | FUNCIONARIOS |
| 07_MIDIA | MIDIA (novo) |
| 08_PLANILHAS_CONTROLES | CONTROLES (novo) |
| 10_ARQUIVOS_TEMPORARIOS | ❌ Não envia |
| 11_OUTROS | OUTROS |

## 🆕 Novos Tópicos Criados

O script cria automaticamente 3 novos tópicos:

1. **OPERACIONAL** - Para escalas, estoque, entregas, inventários, POPs
2. **MIDIA** - Para fotos, vídeos, capturas de tela, WhatsApp
3. **CONTROLES** - Para planilhas de controle e relatórios

## ⚙️ Configurações

### Arquivos Ignorados

O script ignora automaticamente:
- ❌ Arquivos temporários (`~$`, `.DS_Store`, `Thumbs.db`)
- ❌ Arquivos maiores que 50MB (limite do Telegram)
- ❌ Extensões não suportadas
- ❌ Pasta `10_ARQUIVOS_TEMPORARIOS`

### Extensões Suportadas

- 📄 Documentos: `.pdf`, `.doc`, `.docx`, `.txt`
- 📊 Planilhas: `.xls`, `.xlsx`, `.csv`
- 🖼️ Imagens: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`
- 📦 Compactados: `.zip`, `.rar`, `.7z`
- 🎵 Mídia: `.mp3`, `.mp4`, `.avi`, `.mov`
- 📋 Dados: `.xml`, `.json`

## 🔒 Segurança

- ✅ Pede confirmação antes de fazer upload
- ✅ Permite testar com apenas 10 arquivos
- ✅ Modo dry run para simular sem enviar
- ✅ Delay de 2 segundos entre uploads (não sobrecarrega)
- ✅ Gera relatório completo em JSON

## 📊 Relatório Gerado

O arquivo `relatorio_upload_backup.json` contém:
- Data e hora da execução
- Estatísticas completas
- Lista de todos os arquivos processados
- Tópicos criados
- Erros encontrados

## 💡 Dicas

### Teste Primeiro!
```bash
# Opção 2: Upload de apenas 10 arquivos
# ou
# Opção 3: Simular (dry run)
```

### Pausar e Retomar
Se precisar pausar, pressione `Ctrl+C`. O script pode ser executado novamente e vai processar os arquivos que faltam.

### Verificar Antes
Revise as estatísticas e o mapeamento antes de confirmar o upload!

## ⚠️ Limitações

- Telegram tem limite de 50MB por arquivo
- Gemini tem rate limit (15 requests/minuto)
- Upload de 1.166 arquivos pode levar ~1 hora (2s por arquivo)

## 🐛 Troubleshooting

### Erro: "TELEGRAM_BOT_TOKEN não encontrado"
Verifique se o arquivo `assistente-ranny/.env` existe e tem o token.

### Erro: "GROUP_ID não encontrado"
Adicione `GROUP_ID=-1003536252896` no `.env`

### Erro ao criar tópico
Verifique se o bot tem permissões de administrador no grupo.

### Upload muito lento
É normal! O script adiciona delay de 2 segundos entre uploads para não sobrecarregar o Telegram.

## 📞 Suporte

Se tiver problemas, verifique:
1. Bot está online? (`python assistente-ranny/bot.py`)
2. Bot é admin no grupo?
3. Variáveis de ambiente estão corretas?
4. Tem internet estável?

---

**Criado em:** 18 de Janeiro de 2026
**Versão:** 1.0
