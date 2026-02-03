"""
🌐 Servidor Web FastAPI - Assistente Ranny V3
Serve relatórios interativos e health check para Railway
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

# Carrega variáveis de ambiente
load_dotenv()

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from database_adapter import get_relatorio_temp, get_vencimentos_periodo

# Logging
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Assistente Ranny API",
    description="API para relatórios e health check",
    version="3.0.0"
)


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint para Railway e monitoramento.
    
    Verifica:
    - Status do servidor web
    - Conexão com Supabase (banco de dados)
    - Status do scheduler
    
    Retorna status detalhado para monitoramento.
    
    Requirements: 9.2, 9.3
    """
    import scheduler as sched
    from database import check_connection
    
    # Verifica conexão com banco de dados
    db_status = "healthy"
    db_error = None
    try:
        if not check_connection():
            db_status = "unhealthy"
            db_error = "Connection test failed"
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
    
    # Verifica status do scheduler
    scheduler_status = "healthy"
    scheduler_jobs = 0
    try:
        scheduler = sched.get_scheduler()
        if scheduler and scheduler.running:
            scheduler_jobs = len(scheduler.get_jobs())
        else:
            scheduler_status = "not_running"
    except Exception as e:
        scheduler_status = "error"
        logger.warning(f"Erro ao verificar scheduler: {e}")
    
    # Status geral
    overall_status = "healthy"
    if db_status != "healthy":
        overall_status = "degraded"
    
    response_data = {
        "status": overall_status,
        "service": "assistente-ranny",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "web": "healthy",
            "database": {
                "status": db_status,
                "error": db_error
            },
            "scheduler": {
                "status": scheduler_status,
                "jobs_count": scheduler_jobs
            }
        }
    }
    
    # Retorna 200 mesmo se degradado (Railway precisa de 200 para considerar healthy)
    # Mas inclui detalhes para monitoramento
    return JSONResponse(
        content=response_data,
        status_code=200
    )


@app.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(None, description="Authorization code from Microsoft"),
    error: str = Query(None, description="Error code if authorization failed"),
    error_description: str = Query(None, description="Error description")
) -> HTMLResponse:
    """
    OAuth2 callback endpoint para Microsoft Graph API.
    
    Recebe o código de autorização após o usuário autorizar o acesso
    e troca por tokens de acesso.
    
    Requirements: 7.1
    """
    # Import aqui para evitar circular import
    from onedrive import onedrive_auth
    
    # Se houve erro na autorização
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        return HTMLResponse(
            content=_gerar_html_oauth_resultado(
                sucesso=False,
                titulo="Autorização Negada",
                mensagem=f"Não foi possível conectar ao OneDrive. {error_description or error}"
            ),
            status_code=400
        )
    
    # Se não veio código
    if not code:
        return HTMLResponse(
            content=_gerar_html_oauth_resultado(
                sucesso=False,
                titulo="Código Ausente",
                mensagem="Não foi recebido o código de autorização. Tente novamente."
            ),
            status_code=400
        )
    
    # Troca código por tokens
    try:
        success = await onedrive_auth.exchange_code(code)
        
        if success:
            # Notifica no Telegram que a conexão foi bem-sucedida
            await _notificar_telegram_oauth_sucesso()
            
            return HTMLResponse(
                content=_gerar_html_oauth_resultado(
                    sucesso=True,
                    titulo="Conectado com Sucesso! 🎉",
                    mensagem="Seu OneDrive foi conectado à Assistente Ranny. "
                             "Agora você pode buscar arquivos do seu notebook pelo Telegram!"
                ),
                status_code=200
            )
        else:
            return HTMLResponse(
                content=_gerar_html_oauth_resultado(
                    sucesso=False,
                    titulo="Erro na Conexão",
                    mensagem="Não foi possível completar a conexão. Tente novamente."
                ),
                status_code=500
            )
            
    except Exception as e:
        logger.error(f"Erro no callback OAuth: {e}")
        return HTMLResponse(
            content=_gerar_html_oauth_resultado(
                sucesso=False,
                titulo="Erro Interno",
                mensagem="Ocorreu um erro ao processar a autorização. Tente novamente mais tarde."
            ),
            status_code=500
        )


def _gerar_html_oauth_resultado(sucesso: bool, titulo: str, mensagem: str) -> str:
    """Gera HTML para página de resultado do OAuth"""
    cor = "#27ae60" if sucesso else "#e74c3c"
    emoji = "✅" if sucesso else "❌"
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <title>{titulo} - Assistente Ranny</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 450px;
            }}
            h1 {{ color: {cor}; margin-bottom: 20px; }}
            p {{ color: #666; line-height: 1.6; }}
            .emoji {{ font-size: 64px; margin-bottom: 20px; }}
            .close-hint {{
                margin-top: 30px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                font-size: 14px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">{emoji}</div>
            <h1>{titulo}</h1>
            <p>{mensagem}</p>
            <div class="close-hint">
                Você pode fechar esta janela e voltar ao Telegram.
            </div>
        </div>
    </body>
    </html>
    """


async def _notificar_telegram_oauth_sucesso():
    """
    Envia notificação no Telegram quando OAuth do OneDrive é bem-sucedido.
    Usa a API do Telegram diretamente via httpx.
    """
    from config import TELEGRAM_BOT_TOKEN, GROUP_ID, TOPICS
    
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN não configurado, não foi possível notificar")
        return
    
    topic_chat = TOPICS.get('chat', 47)
    
    mensagem = (
        "✅ *OneDrive conectado com sucesso!*\n\n"
        "Agora posso acessar seus arquivos do notebook. "
        "Me peça para buscar qualquer documento! 📁"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_ID,
        "message_thread_id": topic_chat,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Notificação de OAuth enviada ao Telegram")
            else:
                logger.error(f"Erro ao enviar notificação: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Erro ao notificar Telegram sobre OAuth: {e}")


@app.get("/")
async def root() -> JSONResponse:
    """
    Rota raiz - informações básicas da API.
    """
    return JSONResponse(
        content={
            "name": "Assistente Ranny API",
            "version": "3.0.0",
            "endpoints": {
                "/health": "Health check",
                "/relatorio/{token}": "Relatório interativo"
            }
        }
    )


def _gerar_html_erro(titulo: str, mensagem: str) -> str:
    """Gera HTML para páginas de erro"""
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <title>{titulo} - Assistente Ranny</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 400px;
            }}
            h1 {{ color: #e74c3c; margin-bottom: 20px; }}
            p {{ color: #666; line-height: 1.6; }}
            .emoji {{ font-size: 48px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">😕</div>
            <h1>{titulo}</h1>
            <p>{mensagem}</p>
        </div>
    </body>
    </html>
    """


def _agregar_por_semana(fechamentos: list) -> dict:
    """
    Agrega fechamentos por semana para comparativo semanal.
    
    Args:
        fechamentos: Lista de fechamentos com 'data' e 'valor'
    
    Returns:
        Dict com semanas como chave e total como valor
    """
    from datetime import datetime
    from collections import defaultdict
    
    semanas = defaultdict(float)
    
    for f in fechamentos:
        try:
            data_str = f.get('data', '')
            valor = float(f.get('valor', 0))
            
            # Parse da data
            if isinstance(data_str, str):
                data = datetime.strptime(data_str, '%Y-%m-%d')
            else:
                data = data_str
            
            # Número da semana do ano
            semana_num = data.isocalendar()[1]
            ano = data.year
            semana_key = f"{ano}-S{semana_num:02d}"
            
            semanas[semana_key] += valor
        except (ValueError, TypeError):
            continue
    
    # Ordenar por semana
    return dict(sorted(semanas.items()))


def _preparar_dados_pizza(vencimentos: list) -> tuple:
    """
    Prepara dados para gráfico de pizza de gastos por categoria.
    
    Args:
        vencimentos: Lista de vencimentos com 'tipo' e 'valor'
    
    Returns:
        Tuple (categorias, valores, cores)
    """
    from collections import defaultdict
    
    # Cores por categoria
    CORES_CATEGORIA = {
        'luz': '#f1c40f',
        'agua': '#3498db',
        'aluguel': '#9b59b6',
        'internet': '#1abc9c',
        'telefone': '#e67e22',
        'fgts': '#27ae60',
        'inss': '#2980b9',
        'das': '#8e44ad',
        'funcionario': '#e74c3c',
        'fornecedor': '#d35400',
        'manutencao': '#c0392b',
        'outros': '#95a5a6'
    }
    
    categorias_valores = defaultdict(float)
    
    for v in vencimentos:
        tipo = v.get('tipo', 'outros').lower()
        valor = float(v.get('valor', 0))
        categorias_valores[tipo] += valor
    
    if not categorias_valores:
        return [], [], []
    
    # Ordenar por valor (maior primeiro)
    sorted_items = sorted(categorias_valores.items(), key=lambda x: x[1], reverse=True)
    
    categorias = [item[0].title() for item in sorted_items]
    valores = [item[1] for item in sorted_items]
    cores = [CORES_CATEGORIA.get(item[0].lower(), '#95a5a6') for item in sorted_items]
    
    return categorias, valores, cores


def _gerar_graficos_plotly(dados: dict) -> str:
    """
    Gera gráficos Plotly a partir dos dados do relatório.
    
    Gráficos gerados:
    1. Gráfico de linha: fechamentos últimos 30 dias
    2. Gráfico de barras: comparativo semanal
    3. Gráfico de pizza: gastos por categoria
    
    Args:
        dados: Dicionário com dados do relatório:
            - fechamentos: Lista de {data, valor}
            - vencimentos: Lista de {tipo, valor} (opcional)
            - periodo: String descritiva
    
    Returns:
        HTML dos gráficos Plotly
    
    Requirements: 5.1
    """
    if not PLOTLY_AVAILABLE:
        return "<p>Gráficos não disponíveis (Plotly não instalado)</p>"
    
    fechamentos = dados.get('fechamentos', [])
    vencimentos = dados.get('vencimentos', [])
    
    if not fechamentos and not vencimentos:
        return "<p>Sem dados para exibir</p>"
    
    # Preparar dados de fechamentos
    datas = [f.get('data', '') for f in fechamentos]
    valores = [float(f.get('valor', 0)) for f in fechamentos]
    
    # Calcular média
    media = sum(valores) / len(valores) if valores else 0
    
    # Agregar por semana para comparativo
    semanas_dados = _agregar_por_semana(fechamentos)
    semanas_labels = list(semanas_dados.keys())
    semanas_valores = list(semanas_dados.values())
    media_semanal = sum(semanas_valores) / len(semanas_valores) if semanas_valores else 0
    
    # Preparar dados do gráfico de pizza
    cat_labels, cat_valores, cat_cores = _preparar_dados_pizza(vencimentos)
    
    # Determinar número de linhas baseado nos dados disponíveis
    tem_fechamentos = len(fechamentos) > 0
    tem_semanas = len(semanas_dados) > 1
    tem_categorias = len(cat_labels) > 0
    
    # Calcular altura e configurar subplots
    num_rows = sum([tem_fechamentos, tem_semanas, tem_categorias])
    if num_rows == 0:
        return "<p>Sem dados suficientes para gráficos</p>"
    
    # Títulos dos subplots
    subplot_titles = []
    if tem_fechamentos:
        subplot_titles.append('📈 Faturamento Diário (Últimos 30 dias)')
    if tem_semanas:
        subplot_titles.append('📊 Comparativo Semanal')
    if tem_categorias:
        subplot_titles.append('🥧 Gastos por Categoria')
    
    # Configurar specs para o gráfico de pizza
    specs = []
    for i, titulo in enumerate(subplot_titles):
        if '🥧' in titulo:
            specs.append([{"type": "pie"}])
        else:
            specs.append([{"type": "xy"}])
    
    # Criar figura com subplots
    fig = make_subplots(
        rows=num_rows, 
        cols=1,
        subplot_titles=subplot_titles,
        vertical_spacing=0.12,
        specs=specs
    )
    
    current_row = 1
    
    # ========== GRÁFICO 1: LINHA - Faturamento Diário ==========
    if tem_fechamentos:
        # Linha principal com área preenchida
        fig.add_trace(
            go.Scatter(
                x=datas,
                y=valores,
                mode='lines+markers',
                name='Faturamento',
                line=dict(color='#667eea', width=3, shape='spline'),
                marker=dict(size=8, color='#764ba2', line=dict(width=2, color='white')),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)',
                hovertemplate='<b>%{x}</b><br>💰 R$ %{y:,.2f}<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Linha de média
        if media > 0:
            fig.add_hline(
                y=media, 
                line_dash="dash", 
                line_color="#f39c12",
                line_width=2,
                annotation_text=f"Média: R$ {media:,.2f}",
                annotation_position="right",
                row=current_row, col=1
            )
        
        current_row += 1
    
    # ========== GRÁFICO 2: BARRAS - Comparativo Semanal ==========
    if tem_semanas:
        # Cores baseadas na média semanal
        cores_barras = [
            '#27ae60' if v >= media_semanal else '#e74c3c' 
            for v in semanas_valores
        ]
        
        fig.add_trace(
            go.Bar(
                x=semanas_labels,
                y=semanas_valores,
                name='Total Semanal',
                marker_color=cores_barras,
                marker_line_color='white',
                marker_line_width=2,
                text=[f'R$ {v:,.0f}' for v in semanas_valores],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>📊 Total: R$ %{y:,.2f}<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Linha de média semanal
        if media_semanal > 0:
            fig.add_hline(
                y=media_semanal, 
                line_dash="dot", 
                line_color="#f39c12",
                line_width=2,
                annotation_text=f"Média Semanal: R$ {media_semanal:,.2f}",
                annotation_position="right",
                row=current_row, col=1
            )
        
        current_row += 1
    
    # ========== GRÁFICO 3: PIZZA - Gastos por Categoria ==========
    if tem_categorias:
        fig.add_trace(
            go.Pie(
                labels=cat_labels,
                values=cat_valores,
                marker_colors=cat_cores,
                hole=0.4,  # Donut chart
                textinfo='label+percent',
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>💸 R$ %{value:,.2f}<br>📊 %{percent}<extra></extra>',
                pull=[0.05 if i == 0 else 0 for i in range(len(cat_labels))]  # Destaca o maior
            ),
            row=current_row, col=1
        )
    
    # ========== LAYOUT GERAL ==========
    altura_base = 350
    altura_total = altura_base * num_rows + 100
    
    fig.update_layout(
        title=dict(
            text='📊 Relatório Financeiro - GRN Pizzas',
            font=dict(size=24, color='#333', family='Segoe UI, Arial'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=False,
        height=altura_total,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(t=100, b=50, l=70, r=70),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Formatar eixos Y como moeda (apenas para gráficos xy)
    for i in range(1, num_rows + 1):
        if i <= (1 if tem_fechamentos else 0) + (1 if tem_semanas else 0):
            fig.update_yaxes(
                tickprefix='R$ ', 
                tickformat=',.0f',
                gridcolor='rgba(0,0,0,0.1)',
                row=i, col=1
            )
            fig.update_xaxes(
                gridcolor='rgba(0,0,0,0.1)',
                row=i, col=1
            )
    
    # Converter para HTML
    return fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'responsive': True
        }
    )


def _calcular_estatisticas(dados: dict) -> dict:
    """Calcula estatísticas dos fechamentos"""
    fechamentos = dados.get('fechamentos', [])
    if not fechamentos:
        return {}
    
    valores = [float(f.get('valor', 0)) for f in fechamentos]
    
    return {
        'total': sum(valores),
        'media': sum(valores) / len(valores),
        'maior': max(valores),
        'menor': min(valores),
        'dias': len(valores)
    }


@app.get("/relatorio/{token}")
async def get_relatorio(token: str) -> HTMLResponse:
    """
    Endpoint para relatórios interativos com gráficos Plotly.
    
    - Busca dados do token no banco
    - Verifica se não expirou (TTL 24h)
    - Retorna HTML com gráficos interativos
    
    Requirements: 5.1, 5.3
    Property 12: Token tem TTL de 24h
    """
    # Validar formato UUID básico
    import re
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
    if not uuid_pattern.match(token):
        return HTMLResponse(
            content=_gerar_html_erro(
                "Link inválido",
                "Este link não é válido. Verifique se copiou o link completo."
            ),
            status_code=400
        )
    
    # Buscar relatório no banco
    try:
        relatorio = get_relatorio_temp(token)
    except Exception as e:
        logger.error(f"Erro ao buscar relatório: {e}")
        return HTMLResponse(
            content=_gerar_html_erro(
                "Erro Interno",
                "Ocorreu um erro ao buscar o relatório. Tente novamente mais tarde."
            ),
            status_code=500
        )
    
    # Verificar se token existe e não expirou
    if not relatorio:
        return HTMLResponse(
            content=_gerar_html_erro(
                "Relatório não encontrado",
                "Este link expirou ou não existe. Os relatórios ficam disponíveis por 24 horas. "
                "Peça um novo relatório para a Ranny no Telegram!"
            ),
            status_code=404
        )
    
    # Extrair dados
    dados = relatorio.get('dados', {})
    tipo = relatorio.get('tipo', 'geral')
    created_at = relatorio.get('created_at', '')
    expires_at = relatorio.get('expires_at', '')
    
    # Gerar gráficos
    graficos_html = _gerar_graficos_plotly(dados)
    
    # Calcular estatísticas
    stats = _calcular_estatisticas(dados)
    
    # Formatar período
    periodo = dados.get('periodo', 'Últimos 30 dias')
    
    # Gerar HTML completo
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <title>Relatório {tipo.title()} - GRN Pizzas</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            .header {{
                background: white;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                margin-bottom: 20px;
                text-align: center;
            }}
            .header h1 {{
                color: #333;
                margin: 0 0 10px 0;
                font-size: 28px;
            }}
            .header .periodo {{
                color: #666;
                font-size: 16px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-card .value {{
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
            }}
            .stat-card .label {{
                color: #888;
                font-size: 14px;
                margin-top: 5px;
            }}
            .chart-container {{
                background: white;
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }}
            .footer {{
                text-align: center;
                color: white;
                padding: 20px;
                font-size: 14px;
                opacity: 0.8;
            }}
            .footer a {{
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍕 Relatório GRN Pizzas</h1>
                <p class="periodo">📅 {periodo}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="value">R$ {stats.get('total', 0):,.2f}</div>
                    <div class="label">Total do Período</div>
                </div>
                <div class="stat-card">
                    <div class="value">R$ {stats.get('media', 0):,.2f}</div>
                    <div class="label">Média Diária</div>
                </div>
                <div class="stat-card">
                    <div class="value">R$ {stats.get('maior', 0):,.2f}</div>
                    <div class="label">Maior Dia</div>
                </div>
                <div class="stat-card">
                    <div class="value">{stats.get('dias', 0)}</div>
                    <div class="label">Dias Registrados</div>
                </div>
            </div>
            
            <div class="chart-container">
                {graficos_html}
            </div>
            
            <div class="footer">
                <p>Gerado em {created_at[:16].replace('T', ' ') if created_at else 'N/A'}</p>
                <p>Este link expira em {expires_at[:16].replace('T', ' ') if expires_at else 'N/A'}</p>
                <p>🤖 Assistente Ranny - Sua secretária virtual</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
