# Implementation Plan: Assistente Ranny V3

## Overview

Implementação incremental do assistente virtual completo. Cada fase entrega funcionalidade testável.

## Tasks

- [ ] 1. Configurar infraestrutura base
  - [x] 1.1 Criar projeto Supabase e configurar schema do banco
    - Executar SQL do design para criar tabelas
    - Configurar variáveis de ambiente
    - **🔧 Usar: MCP Supabase** para criar tabelas e configurar RLS
    - _Requirements: 9.1_
  - [x] 1.2 Refatorar database.py para usar Supabase
    - Substituir JSON local por cliente Supabase
    - Manter interface das funções existentes
    - **🔧 Usar: MCP Supabase** para testar queries
    - _Requirements: 9.1_
  - [x] 1.3 Adicionar FastAPI ao projeto
    - Criar web.py com rota /health
    - Configurar para rodar junto com bot
    - _Requirements: 5.1, 9.4_
  - [x] 1.4 Escrever testes de conexão com Supabase
    - Testar CRUD básico em cada tabela
    - **🔧 Usar: MCP Supabase** para validar operações
    - _Requirements: 9.1_

- [ ] 2. Implementar fluxo de documentos com classificação automática
  - [x] 2.1 Atualizar handle_file para detectar tópico de origem
    - Se Chat (47), classificar e mover
    - Se outro tópico, apenas confirmar
    - _Requirements: 1.2, 2.5_
  - [x] 2.2 Implementar repost de documento para tópico correto
    - Usar bot.forward_message ou bot.send_document
    - Salvar message_id e topic_id no banco
    - _Requirements: 2.2_
  - [x] 2.3 Melhorar extração de dados de boletos
    - Extrair valor, vencimento, beneficiário
    - Perguntar se quer criar lembrete
    - _Requirements: 2.3_
  - [x] 2.4 Escrever property test para classificação
    - **Property 1: Documento no Chat é sempre classificado e movido**
    - **Property 2: Categoria mapeia corretamente para tópico**
    - **Validates: Requirements 1.2, 2.1, 2.2**

- [x] 3. Checkpoint - Testar fluxo de documentos
  - Enviar documento no Chat e verificar se move pro tópico certo
  - Enviar documento direto no Financeiro e verificar que não move
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implementar sistema de lembretes completo
  - [x] 4.1 Melhorar parsing de datas em português
    - Suportar: amanhã, segunda, dia 15, próxima semana, daqui 3 dias
    - Extrair hora se especificada, senão usar 09:00
    - **🧠 Usar: Sequential Thinking** para mapear todos os padrões de data
    - _Requirements: 3.1, 3.2_
  - [x] 4.2 Implementar listagem de lembretes
    - Detectar "quais meus lembretes?" ou similar
    - Listar apenas ativos, ordenados por data
    - _Requirements: 3.4_
  - [x] 4.3 Implementar cancelamento de lembretes
    - Detectar "cancela lembrete do FGTS" ou similar
    - Marcar como ativo=FALSE
    - _Requirements: 3.5_
  - [x] 4.4 Implementar lembretes recorrentes
    - Após disparar, criar próximo baseado em recorrência
    - Suportar: diário, semanal, mensal
    - _Requirements: 3.6_
  - [x] 4.5 Escrever property tests para lembretes
    - **Property 4: Pedido de lembrete cria lembrete no banco**
    - **Property 5: Lembrete sem hora usa 09:00**
    - **Property 6: Listagem retorna apenas ativos**
    - **Property 7: Cancelamento marca como inativo**
    - **Property 8: Recorrente gera próximo após disparo**
    - **Validates: Requirements 3.1-3.6**

- [ ] 5. Implementar scheduler para alertas automáticos
  - [x] 5.1 Configurar APScheduler com AsyncIOScheduler
    - Integrar com loop do bot
    - Configurar timezone Brasil
    - _Requirements: 3.3, 8.1_
  - [x] 5.2 Implementar job de lembretes (9h diário)
    - Buscar lembretes do dia com hora <= agora
    - Enviar no Tópico_Chat
    - Marcar como disparado
    - _Requirements: 3.3_
  - [x] 5.3 Implementar job de alertas de vencimento (8h diário)
    - Buscar vencimentos não pagos
    - Alertar se dias_restantes em [7, 3, 1]
    - _Requirements: 8.1, 8.2, 8.3_
  - [x] 5.4 Escrever property test para alertas
    - **Property 15: Alertas baseados em dias restantes**
    - **Property 16: Vencimento pago não gera alertas**
    - **Validates: Requirements 8.1-8.4**

- [x] 6. Checkpoint - Testar lembretes e alertas
  - Criar lembrete para daqui 2 minutos e verificar notificação
  - Criar vencimento para amanhã e verificar alerta
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implementar relatórios financeiros interativos
  - [x] 7.1 Criar endpoint /relatorio/{token} no FastAPI
    - Buscar dados do token no banco
    - Verificar se não expirou
    - Retornar HTML com gráficos Plotly
    - **🔧 Usar: MCP Supabase** para queries de dados
    - _Requirements: 5.1, 5.3_
  - [x] 7.2 Implementar geração de gráficos com Plotly
    - Gráfico de linha: fechamentos últimos 30 dias
    - Gráfico de barras: comparativo semanal
    - Gráfico de pizza: gastos por categoria
    - **🧠 Usar: Sequential Thinking** para definir melhor visualização
    - _Requirements: 5.1_
  - [x] 7.3 Implementar detecção de pedido de relatório
    - Detectar "mostra gráfico", "como foi o mês", "relatório"
    - Gerar token, salvar dados, retornar link
    - _Requirements: 5.1, 5.2_
  - [x] 7.4 Implementar resumo semanal automático (domingo 20h)
    - Job no scheduler
    - Gerar relatório e enviar no Chat
    - _Requirements: 5.4_
  - [x] 7.5 Escrever property test para relatórios
    - **Property 12: Token tem TTL de 24h**
    - **Validates: Requirements 5.1, 5.2**

- [x] 8. Checkpoint - Testar relatórios
  - Pedir "mostra gráfico da semana" e verificar link
  - Acessar link e verificar gráficos
  - **🎭 Usar: Playwright** para testar página de relatório no browser
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implementar busca de documentos
  - [x] 9.1 Melhorar detecção de busca
    - Suportar mais padrões: "acha", "procura", "tem algum"
    - Extrair termo de busca
    - _Requirements: 6.1_
  - [x] 9.2 Implementar busca no banco de documentos
    - Buscar por descrição, tipo, categoria
    - Retornar com link para mensagem original
    - _Requirements: 6.1, 6.2_
  - [x] 9.3 Implementar reenvio de documento encontrado
    - Usar file_id salvo para reenviar
    - Ou enviar link para mensagem no tópico
    - _Requirements: 6.2_
  - [x] 9.4 Escrever property test para busca
    - **Property 13: Busca retorna matches**
    - **Validates: Requirements 6.1**

- [ ] 10. Implementar integração OneDrive
  - [x] 10.1 Configurar OAuth2 com Microsoft Graph API
    - Registrar app no Azure AD
    - Implementar fluxo de autenticação
    - Salvar tokens no banco
    - **🧠 Usar: Sequential Thinking** para planejar fluxo OAuth
    - **🔧 Usar: MCP Supabase** para salvar tokens
    - _Requirements: 7.1_
  - [x] 10.2 Implementar verificação de conexão
    - Testar se token válido
    - Retornar status conectado/desconectado
    - _Requirements: 7.2_
  - [x] 10.3 Implementar busca de arquivos no OneDrive
    - Buscar na pasta sincronizada
    - Retornar lista de matches
    - _Requirements: 7.1_
  - [x] 10.4 Implementar download e envio para Telegram
    - Baixar arquivo do OneDrive
    - Enviar para tópico correto
    - Salvar referência no banco
    - _Requirements: 7.4_
  - [x] 10.5 Escrever property test para OneDrive
    - **Property 14: Desconectado retorna mensagem apropriada**
    - **Validates: Requirements 7.2**

- [x] 11. Checkpoint - Testar busca e OneDrive
  - Buscar documento existente no Telegram
  - Testar mensagem quando OneDrive desconectado
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implementar vencimentos automáticos
  - [x] 12.1 Criar vencimento a partir de boleto
    - Quando boleto é classificado, criar vencimento
    - Vincular documento ao vencimento
    - _Requirements: 2.3, 8.1_
  - [x] 12.2 Implementar marcação de pago
    - Detectar "paguei a luz" ou similar
    - Marcar vencimento como pago
    - _Requirements: 8.4_
  - [x] 12.3 Implementar vencimentos recorrentes
    - Após pagar, criar próximo se recorrente
    - Calcular próxima data baseado em tipo
    - _Requirements: 8.5_
  - [x] 12.4 Escrever property test para vencimentos
    - **Property 17: Recorrente gera próximo**
    - **Property 18: Boleto tem valor e vencimento extraídos**
    - **Validates: Requirements 8.5, 2.3**

- [ ] 13. Preparar para deploy no Railway
  - [x] 13.1 Criar Procfile e configurações Railway
    - Configurar para rodar bot + web
    - Definir variáveis de ambiente
    - _Requirements: 9.1, 9.4_
  - [x] 13.2 Implementar health check e graceful shutdown
    - Endpoint /health para Railway
    - Tratamento de SIGTERM
    - _Requirements: 9.2, 9.3_
  - [x] 13.3 Configurar domínio para relatórios
    - URL pública para links de relatório
    - _Requirements: 5.2_

- [x] 14. Deploy e teste final
  - [x] 14.1 Deploy no Railway
    - Push para repositório
    - Verificar logs
    - _Requirements: 9.1_
  - [x] 14.2 Teste completo com Ranny
    - Testar todas as funcionalidades
    - Ajustar baseado em feedback
    - **🎭 Usar: Playwright** para testar página de relatórios em produção
    - _Requirements: All_

## Notes

- Checkpoints são pontos de validação com o usuário
- Cada fase entrega funcionalidade utilizável
- OneDrive (task 10) pode ser feito depois do deploy se necessário

## Ferramentas MCP Utilizadas

| Ferramenta | Uso |
|------------|-----|
| **🔧 MCP Supabase** | Criar tabelas, executar queries, validar dados |
| **🧠 Sequential Thinking** | Planejar lógica complexa (parsing datas, OAuth, gráficos) |
| **🎭 Playwright** | Testar páginas web de relatórios no browser |
