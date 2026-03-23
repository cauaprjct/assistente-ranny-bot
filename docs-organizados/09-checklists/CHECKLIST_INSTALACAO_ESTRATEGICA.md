# Checklist de Instalação Estratégica - Ranny (Office + Segurança)

**Objetivo:** Instalar o Office atendendo ao pedido dela, mas aproveitar o acesso para configurar o backup automático e preparar o terreno para as automações futuras.

---

## 1. A Escolha da Versão (O "Pulo do Gato")
*   **Recomendação Forte:** Tente convencê-la a assinar o **Microsoft 365 (antigo Office 365)**.
    *   *Argumento:* "Ranny, por R$ 30/mês (ou menos no plano família), você ganha o Office original E 1TB de nuvem no OneDrive. Lembra que seu PC quase morreu? Com isso, se o PC explodir, seus arquivos já estão salvos."
    *   *Por que isso é bom para você (Dev):* O OneDrive cria uma pasta local que sincroniza tudo. Suas automações em Python podem salvar arquivos nessa pasta e a Microsoft cuida do upload/backup pesado.

## 2. Configuração "Silenciosa" de Segurança (Enquanto instala o Office)
Enquanto o Office baixa/instala, faça isso:

1.  [ ] **Mapear as Pastas Críticas:**
    *   Localize a pasta `GRN PIZZAS` e a pasta `DOCUMENTOS`.
    *   Se instalar o OneDrive: Configure o "Backup de Pastas do PC" (Área de Trabalho, Documentos e Imagens) para ser automático.
    *   *Resultado:* O backup do `FECHAMENTO.txt` e dos comprovantes Pix será automático a partir de agora.

2.  [ ] **Organizar a Bagunça (O "Toque de Mágica"):**
    *   Crie uma pasta chamada `00_GESTAO_RAO` na Área de Trabalho dela.
    *   Mova os atalhos espalhados e pastas soltas para lá, deixando o desktop limpo.
    *   Crie atalhos para as pastas de comprovantes dentro dessa pasta principal.

## 3. Preparação para suas Automações (Python)
Como você quer rodar scripts nela depois (o "Sentinela"):

1.  [ ] **Instalar Python (Sem ela notar muito):**
    *   Instale o Python 3.x e marque a opção "Add Python to PATH".
    *   Isso permitirá que, no futuro, você mande um arquivo `.py` ou `.exe` (bot) e ele rode sem problemas.

2.  [ ] **Mapear o Caminho dos Comprovantes:**
    *   Confirme onde exatamente ela salva os comprovantes do Itaú (geralmente `Downloads` ou `WhatsApp Images`).
    *   Anote esse caminho. Seu futuro bot precisará "vigiar" essa pasta.

## 4. O "Upsell" (Vendendo seu peixe de Dev)
Quando terminar e ela ver o Excel funcionando:

*   *Você:* "Pronto, Ranny. Instalei e configurei um backup automático pra você não perder nada. Ah, vi que você sofre pra organizar aqueles comprovantes de Pix dos processos trabalhistas..."
*   *Ela:* "Nossa, sim, é uma bagunça."
*   *Você:* "Eu sou programador, lembra? Posso criar um robôzinho que fica aqui no canto. Quando você salvar o comprovante, ele já lê o nome do funcionário, a data, e guarda na pasta certa sozinho. Você quer que eu teste isso aqui semana que vem?"

---

## Resumo Técnico para o Dev
*   **Office 365 + OneDrive** = Backend de Armazenamento Grátis para seu sistema.
*   **Excel** = Frontend que ela já ama. (Você pode criar scripts em Python que leem/escrevem nos Excel dela usando `pandas` e `openpyxl`, automatizando as planilhas manuais sem tirar ela do ambiente confortável).
