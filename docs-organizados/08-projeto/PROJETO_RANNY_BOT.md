# Projeto: Assistente Pessoal Inteligente (RannyBot)

**Conceito:** Um "contato" no WhatsApp da Ranny que funciona como uma secretária executiva 24h. Ela envia fotos, áudios ou textos, e o Bot organiza tudo automaticamente na nuvem e no PC dela.

---

## 1. O Fluxo "Mágico" (A Ponte Celular ↔ PC)
Como ela usa iPhone (sistema fechado) e pediu o Office no PC, a melhor arquitetura é usar a **Nuvem como Ponte**.

1.  **Ranny (No iPhone):** Recebe um comprovante de Pix no WhatsApp. Em vez de salvar na galeria e esquecer, ela **encaminha para o Bot**.
2.  **O Bot (Na Nuvem/Servidor):**
    *   Recebe o arquivo.
    *   **IA (Cérebro):** Analisa a imagem. *"Isso é um comprovante de Pix de R$ 1.250,00 para o Felipe, referente a Dezembro."*
    *   **Ação:** Renomeia o arquivo para `2025-12-01_Pagamento_Felipe.pdf`.
    *   **Armazenamento:** Salva na pasta `OneDrive/GRN PIZZAS/Funcionarios/Felipe` na nuvem.
3.  **O PC da Ranny:** Como o OneDrive está instalado lá, o arquivo **aparece magicamente** na pasta do computador dela segundos depois.

**Resultado:** Ela operou pelo celular, mas o arquivo está organizado no PC, pronto para defesa jurídica.

---

## 2. Funcionalidades do Bot (O que ele faz)

### A. Organizador Financeiro (O "Caurá" das Notas)
*   **Comando:** Enviar foto de Nota Fiscal ou Comprovante.
*   **IA:** Extrai CNPJ, Data, Valor e Itens.
*   **Ação:** Salva o PDF na pasta correta e **insere uma linha numa Planilha Excel** no OneDrive chamada `Fluxo_Caixa_2026.xlsx`.
*   **Resposta do Bot:** *"Salvei o comprovante de R$ 450,00 do Mercado. Já lancei na planilha de gastos."*

### B. O "Lembrete Jurídico"
*   **Cenário:** Ela recebe uma mensagem de um ex-funcionário ameaçando processo.
*   **Ação:** Ela encaminha o print da conversa para o Bot.
*   **Bot:** Salva na pasta `Juridico/Possiveis_Processos/[Nome_Funcionario]` e cria um dossiê.
*   **Valor:** Quando o advogado pedir provas, está tudo lá, cronológico.

### C. Consultas Rápidas (Q&A)
*   **Ranny pergunta:** *"Bot, quanto gastamos de motoboy essa semana?"*
*   **Bot:** Lê a planilha Excel (que ele mesmo alimenta) e responde: *"R$ 1.450,00 até agora."*

---

## 3. Arquitetura Técnica (Como vamos construir)

Para ser profissional e funcionar mesmo com o PC desligado:

1.  **Interface (WhatsApp):**
    *   **Opção Pro:** **Twilio API** (Pago, mas oficial e estável).
    *   **Opção Hacker:** **Evolution API** ou **WPPConnect** (Grátis, roda num servidorzinho simples ou Docker). Recomendo usar a Evolution API em um VPS barato (R$ 30/mês) para garantir que funcione 24h.

2.  **Inteligência (IA):**
    *   **OpenAI (GPT-4o-mini)** ou **Google Gemini Flash**: São modelos baratos e visionários. Eles conseguem "ler" os comprovantes de Pix perfeitamente.

3.  **Armazenamento (O Ecossistema):**
    *   **Microsoft Graph API (OneDrive):** Já que ela vai ter o Office, usamos a API do OneDrive.
    *   Assim, tudo que o Bot salva vai direto para o ecossistema Microsoft dela.

---

## 4. Por que isso é melhor que um App?
1.  **Zero Instalação:** Ela já usa o WhatsApp o dia todo. A curva de aprendizado é zero.
2.  **Funciona Offline (no PC):** Se o PC estiver desligado, o Bot salva na nuvem. Quando ela ligar o PC, o OneDrive baixa tudo.
3.  **Multi-Plataforma:** Funciona no iPhone dela, no Android se ela mudar, no WhatsApp Web do PC da loja.

---

## Próximo Passo
Se você concordar, podemos começar criando um **protótipo simples em Python** que roda no PC dela mesmo (enquanto você instala o Office).
1.  Você roda o script.
2.  Manda uma mensagem no WhatsApp.
3.  Vê o arquivo aparecendo na pasta.
Isso vai explodir a cabeça dela ("Mind blowing").
