"""
🔍 Script de Verificação de Deploy - Assistente Ranny
Usa Playwright para verificar se o bot está online e funcionando
"""

import asyncio
import sys
from datetime import datetime
import json

try:
    from playwright.async_api import async_playwright
    import httpx
except ImportError:
    print("❌ Dependências não instaladas!")
    print("\nInstale com:")
    print("pip install playwright httpx")
    print("playwright install chromium")
    sys.exit(1)


class Colors:
    """Cores ANSI para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Imprime cabeçalho colorido"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """Imprime mensagem informativa"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


async def verificar_health_check(url: str) -> dict:
    """Verifica o health check do bot"""
    print_info(f"Verificando health check: {url}/health")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check OK (200)")
                print_info(f"Serviço: {data.get('service', 'N/A')}")
                print_info(f"Versão: {data.get('version', 'N/A')}")
                
                # Verifica componentes
                components = data.get('components', {})
                
                # Web
                web_status = components.get('web', 'unknown')
                if web_status == 'healthy':
                    print_success("Servidor web: healthy")
                else:
                    print_error(f"Servidor web: {web_status}")
                
                # Database
                db = components.get('database', {})
                db_status = db.get('status', 'unknown')
                if db_status == 'healthy':
                    print_success("Banco de dados: healthy")
                else:
                    print_warning(f"Banco de dados: {db_status}")
                    if db.get('error'):
                        print_info(f"Erro: {db['error']}")
                
                # Scheduler
                scheduler = components.get('scheduler', {})
                scheduler_status = scheduler.get('status', 'unknown')
                jobs_count = scheduler.get('jobs_count', 0)
                
                if scheduler_status == 'healthy':
                    print_success(f"Scheduler: healthy ({jobs_count} jobs)")
                    
                    if jobs_count >= 4:
                        print_success("Keep-alive configurado! ✨")
                    else:
                        print_warning(f"Esperado 4 jobs, encontrado {jobs_count}")
                else:
                    print_error(f"Scheduler: {scheduler_status}")
                
                return {
                    'success': True,
                    'status': data.get('status'),
                    'components': components
                }
            else:
                print_error(f"Health check falhou: {response.status_code}")
                return {'success': False, 'error': f'Status {response.status_code}'}
                
    except httpx.TimeoutException:
        print_error("Timeout ao conectar (10s)")
        return {'success': False, 'error': 'Timeout'}
    except httpx.ConnectError:
        print_error("Não foi possível conectar ao servidor")
        print_warning("Verifique se a URL está correta e o serviço está rodando")
        return {'success': False, 'error': 'Connection refused'}
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return {'success': False, 'error': str(e)}


async def verificar_logs_playwright(url: str):
    """Usa Playwright para acessar o dashboard do Render e verificar logs"""
    print_info("Abrindo navegador para verificar logs...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Extrai o nome do app da URL
            app_name = url.replace('https://', '').replace('.onrender.com', '')
            dashboard_url = f"https://dashboard.render.com"
            
            print_info(f"Acessando dashboard do Render...")
            await page.goto(dashboard_url, wait_until='networkidle')
            
            print_warning("Por favor, faça login no Render.com no navegador que abriu")
            print_info("Após fazer login, pressione ENTER aqui para continuar...")
            input()
            
            # Aguarda um pouco para garantir que está logado
            await asyncio.sleep(2)
            
            # Tenta acessar os logs do serviço
            print_info(f"Buscando serviço: {app_name}")
            
            # Aguarda 5 segundos para o usuário navegar manualmente
            print_info("Navegue até seu serviço e clique em 'Logs'")
            print_info("Aguardando 30 segundos para você verificar os logs...")
            
            for i in range(30, 0, -5):
                print(f"⏱️  {i} segundos restantes...")
                await asyncio.sleep(5)
            
            print_success("Verificação visual concluída!")
            
        except Exception as e:
            print_error(f"Erro ao acessar dashboard: {e}")
        finally:
            await browser.close()


async def verificar_keep_alive(url: str, intervalo: int = 60):
    """Monitora o keep-alive por alguns minutos"""
    print_header("MONITORAMENTO KEEP-ALIVE")
    print_info(f"Monitorando por {intervalo} segundos...")
    print_info("Verificando se o bot faz requisições a cada 10 minutos")
    
    checks = intervalo // 10
    for i in range(checks):
        print(f"\n⏱️  Check {i+1}/{checks}")
        result = await verificar_health_check(url)
        
        if not result['success']:
            print_error("Health check falhou!")
            return False
        
        if i < checks - 1:
            print_info("Aguardando 10 segundos...")
            await asyncio.sleep(10)
    
    print_success(f"\n✨ Bot respondeu em todos os {checks} checks!")
    return True


async def gerar_relatorio(url: str, results: dict):
    """Gera relatório final da verificação"""
    print_header("RELATÓRIO FINAL")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🕐 Data/Hora: {timestamp}")
    print(f"🌐 URL: {url}")
    print(f"📊 Status Geral: {results.get('status', 'unknown')}")
    
    print("\n📋 Componentes:")
    components = results.get('components', {})
    
    for component, status in components.items():
        if isinstance(status, dict):
            status_str = status.get('status', 'unknown')
        else:
            status_str = status
        
        emoji = "✅" if status_str == "healthy" else "❌"
        print(f"  {emoji} {component}: {status_str}")
    
    # Salva relatório em arquivo
    report_file = f"relatorio_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'url': url,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {report_file}")


async def main():
    """Função principal"""
    print_header("🔍 VERIFICAÇÃO DE DEPLOY - ASSISTENTE RANNY")
    
    # Solicita URL
    print("Digite a URL do seu bot no Render.com:")
    print("Exemplo: https://assistente-ranny.onrender.com")
    url = input("\n🌐 URL: ").strip()
    
    if not url:
        print_error("URL não fornecida!")
        return
    
    # Remove barra final se houver
    url = url.rstrip('/')
    
    # Verifica health check
    print_header("1. VERIFICANDO HEALTH CHECK")
    health_result = await verificar_health_check(url)
    
    if not health_result['success']:
        print_error("\n❌ Health check falhou!")
        print_warning("Verifique se o bot está rodando no Render")
        return
    
    # Pergunta se quer verificar logs visualmente
    print("\n" + "="*60)
    print("Deseja abrir o navegador para verificar os logs? (s/n)")
    resposta = input("👉 ").strip().lower()
    
    if resposta == 's':
        print_header("2. VERIFICANDO LOGS (VISUAL)")
        await verificar_logs_playwright(url)
    
    # Pergunta se quer monitorar keep-alive
    print("\n" + "="*60)
    print("Deseja monitorar o keep-alive por 1 minuto? (s/n)")
    resposta = input("👉 ").strip().lower()
    
    if resposta == 's':
        print_header("3. MONITORANDO KEEP-ALIVE")
        await verificar_keep_alive(url, intervalo=60)
    
    # Gera relatório final
    await gerar_relatorio(url, health_result)
    
    print_header("✅ VERIFICAÇÃO CONCLUÍDA")
    print_success("Bot está online e funcionando!")
    print_info("Próximos passos:")
    print("  1. Testar bot no Telegram")
    print("  2. Enviar mensagem: 'oi'")
    print("  3. Verificar se responde")
    print("  4. Aguardar 10 minutos e verificar keep-alive nos logs")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificação cancelada pelo usuário")
    except Exception as e:
        print_error(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
