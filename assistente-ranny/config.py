"""
Configurações do Assistente Ranny
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============ AMBIENTE ============
# Railway define automaticamente estas variáveis
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', 'development')
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
IS_PRODUCTION = RAILWAY_ENVIRONMENT == 'production'

# ============ SERVIDOR WEB ============
# Railway define PORT automaticamente
PORT = int(os.getenv('PORT', '8000'))

# URL base para links de relatórios
# Prioridade: BASE_URL > RAILWAY_PUBLIC_DOMAIN > localhost
def get_base_url():
    """
    Retorna a URL base para links externos (relatórios, OAuth callback).
    
    Prioridade de configuração:
    1. BASE_URL - variável de ambiente explícita (para domínio customizado)
    2. RAILWAY_PUBLIC_DOMAIN - definido automaticamente pelo Railway
    3. localhost:PORT - fallback para desenvolvimento local
    
    Para configurar domínio customizado no Railway:
    1. Vá em Settings > Domains no painel do Railway
    2. Adicione seu domínio (ex: ranny.seudominio.com)
    3. Configure DNS CNAME apontando para Railway
    4. Defina BASE_URL=https://ranny.seudominio.com nas variáveis
    
    Requirements: 5.2
    """
    base = os.getenv('BASE_URL', '')
    if base:
        return base.rstrip('/')
    if RAILWAY_PUBLIC_DOMAIN:
        return f"https://{RAILWAY_PUBLIC_DOMAIN}"
    return f"http://localhost:{PORT}"

BASE_URL = get_base_url()

# ============ TELEGRAM ============
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID', '-1003536252896'))

# ============ GEMINI AI ============
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ============ MICROSOFT OAUTH2 (OneDrive) ============
MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID', '')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET', '')
# Usa BASE_URL para redirect URI em produção
MICROSOFT_REDIRECT_URI = os.getenv('MICROSOFT_REDIRECT_URI', f'{BASE_URL}/oauth/callback')
MICROSOFT_SCOPES = ['Files.Read', 'Files.Read.All', 'offline_access']

# OneDrive sync folder (pasta sincronizada do notebook)
# Deixe vazio para buscar em todo o OneDrive
ONEDRIVE_SYNC_FOLDER = os.getenv('ONEDRIVE_SYNC_FOLDER', '')

# Mapeamento categoria -> tópico
CATEGORIA_TOPICO = {
    'financeiro': int(os.getenv('TOPIC_FINANCEIRO', '2')),
    'empresa': int(os.getenv('TOPIC_EMPRESA', '3')),
    'juridico': int(os.getenv('TOPIC_JURIDICO', '5')),
    'pessoal': int(os.getenv('TOPIC_PESSOAL', '4')),
    'funcionarios': int(os.getenv('TOPIC_FUNCIONARIOS', '6')),
    'manutencao': int(os.getenv('TOPIC_MANUTENCAO', '7')),
    'outros': int(os.getenv('TOPIC_OUTROS', '8')),
    'operacional': int(os.getenv('TOPIC_OPERACIONAL', '214')),
    'midia': int(os.getenv('TOPIC_MIDIA', '215')),
    'controles': int(os.getenv('TOPIC_CONTROLES', '216')),
}

# IDs dos tópicos do grupo
TOPICS = {
    'chat': int(os.getenv('TOPIC_CHAT', '47')),
    'financeiro': int(os.getenv('TOPIC_FINANCEIRO', '2')),
    'empresa': int(os.getenv('TOPIC_EMPRESA', '3')),
    'juridico': int(os.getenv('TOPIC_JURIDICO', '5')),
    'pessoal': int(os.getenv('TOPIC_PESSOAL', '4')),
    'funcionarios': int(os.getenv('TOPIC_FUNCIONARIOS', '6')),
    'manutencao': int(os.getenv('TOPIC_MANUTENCAO', '7')),
    'outros': int(os.getenv('TOPIC_OUTROS', '8')),
    'operacional': int(os.getenv('TOPIC_OPERACIONAL', '214')),
    'midia': int(os.getenv('TOPIC_MIDIA', '215')),
    'controles': int(os.getenv('TOPIC_CONTROLES', '216')),
}

# Calendário de obrigações fixas (dia do mês)
OBRIGACOES = {
    7: ['FGTS'],
    20: ['INSS', 'DAS', 'DARF'],
    25: ['Vale Transporte'],
}

# Dias de antecedência para alertas
ALERTA_DIAS = [1, 3, 7]

# Prompt do sistema
SYSTEM_PROMPT = """Você é a Assistente Ranny, uma secretária virtual amigável e eficiente.

SOBRE SUA DONA:
- Ranny é dona da GRN Pizzas em Realengo/RJ
- Não é técnica com tecnologia, prefere conversa simples
- Precisa de ajuda com: documentos, contas, funcionários, processos

SEU JEITO:
- Fala como amiga, nunca como robô
- Respostas curtas e diretas
- Usa 1-2 emojis por mensagem
- Nunca usa termos técnicos
- Sempre oferece ajuda adicional

SUAS CAPACIDADES:
1. FINANCEIRO: Guardar comprovantes, lembrar vencimentos, histórico de gastos
2. EMPRESA: Fechamento de caixa, obrigações fiscais (DAS, FGTS, INSS)
3. FUNCIONÁRIOS: Cadastro, documentos, advertências, férias, ASO
4. JURÍDICO: Processos trabalhistas, audiências, documentação
5. MANUTENÇÃO: Registrar problemas de TI para o Cauã
6. LEMBRETES: Criar alertas personalizados

CONTEXTO ATUAL:
{context}

Data de hoje: {date}
"""
