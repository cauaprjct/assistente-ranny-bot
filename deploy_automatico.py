"""
🤖 Deploy Automático - Assistente Ranny
Automatiza todo o processo de deploy usando Playwright
"""

import asyncio
import os
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright não instalado!")
    print("\nInstale com:")
    print("pip install playwright")
    print("playwright install chromium")
    sys.exit(1)


class DeployAutomatico:
    """Automatiza deploy no GitHub e Render.com"""
    
    def __init__(self):
        self.github_username = None
        self.github_password = None
        self.github_repo_url = None
        self.render_email = None
        self.render_password = None
        self.telegram_token = None
        self.gemini_key = None
        
    def carregar_env(self):
        """Carrega credenciais do arquivo .env"""
        print("📄 Carregando credenciais do .env...")
        
        env_path = Path("assistente-ranny/.env")
        if not env_path.exists():
            print("❌ Arquivo .env não encontrado!")
            sys.exit(1)
        
        # Ler .env
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'TELEGRAM_BOT_TOKEN':
                        self.telegram_token = value
                    elif key == 'GEMINI_API_KEY':
                        self.gemini_key = value
        
        if self.telegram_token and self.gemini_key:
            print("  ✅ Telegram token carregado")
            print("  ✅ Gemini API key carregada")
        else:
            print("  ❌ Credenciais não encontradas no .env")
            sys.exit(1)
        
    async def coletar_credenciais(self):
        """Coleta apenas credenciais do GitHub e Render"""
        print("\n🔐 CONFIGURAÇÃO DE CREDENCIAIS")
        print("="*60)
        
        # Carregar do .env
        self.carregar_env()
        
        print("\n🐙 GITHUB:")
        self.github_username = input("Username: ").strip()
        self.github_password = input("Password/Token: ").strip()
        
        print("\n🚀 RENDER.COM:")
        print("Você já tem conta no Render? (s/n)")
        tem_conta = input("👉 ").strip().lower()
        
        if tem_conta == 's':
            self.render_email = input("Email: ").strip()
            self.render_password = input("Password: ").strip()
        else:
            print("\n⚠️  Você precisa criar uma conta no Render.com primeiro")
            print("Acesse: https://render.com")
            print("Clique em 'Get Started' e crie sua conta")
            print("\nDepois execute este script novamente.")
            sys.exit(0)
    
    async def criar_repositorio_github(self, page):
        """Cria repositório no GitHub via navegador"""
        print("\n🐙 CRIANDO REPOSITÓRIO NO GITHUB...")
        
        try:
            # Login no GitHub
            print("  → Acessando GitHub...")
            await page.goto("https://github.com/login")
            await page.wait_for_load_state("networkidle")
            
            print("  → Fazendo login...")
            await page.fill('input[name="login"]', self.github_username)
            await page.fill('input[name="password"]', self.github_password)
            await page.click('input[type="submit"]')
            
            # Aguarda login
            await page.wait_for_url("https://github.com/**", timeout=30000)
            print("  ✅ Login realizado!")
            
            # Criar novo repositório
            print("  → Criando repositório...")
            await page.goto("https://github.com/new")
            await page.wait_for_load_state("networkidle")
            
            # Preencher formulário
            await page.fill('input[name="repository[name]"]', "assistente-ranny")
            await page.fill('textarea[name="repository[description]"]', 
                          "Bot Telegram inteligente para gestão da GRN Pizzas")
            
            # Selecionar público
            await page.click('input[value="public"]')
            
            # Criar repositório
            await page.click('button:has-text("Create repository")')
            await page.wait_for_load_state("networkidle")
            
            # Pegar URL do repositório
            self.github_repo_url = page.url.replace(".git", "")
            print(f"  ✅ Repositório criado: {self.github_repo_url}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao criar repositório: {e}")
            return False
    
    async def fazer_push_codigo(self):
        """Faz push do código para o GitHub"""
        print("\n📤 ENVIANDO CÓDIGO PARA GITHUB...")
        
        try:
            # Adicionar remote
            remote_url = f"https://{self.github_username}:{self.github_password}@github.com/{self.github_username}/assistente-ranny.git"
            
            print("  → Adicionando remote...")
            os.system(f'git remote add origin {remote_url}')
            
            print("  → Renomeando branch para main...")
            os.system('git branch -M main')
            
            print("  → Fazendo push...")
            result = os.system('git push -u origin main')
            
            if result == 0:
                print("  ✅ Código enviado com sucesso!")
                return True
            else:
                print("  ❌ Erro ao fazer push")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            return False
    
    async def fazer_deploy_render(self, page):
        """Faz deploy no Render.com via navegador"""
        print("\n🚀 FAZENDO DEPLOY NO RENDER.COM...")
        
        try:
            # Login no Render
            print("  → Acessando Render...")
            await page.goto("https://dashboard.render.com/login")
            await page.wait_for_load_state("networkidle")
            
            print("  → Fazendo login...")
            await page.fill('input[type="email"]', self.render_email)
            await page.fill('input[type="password"]', self.render_password)
            await page.click('button[type="submit"]')
            
            # Aguarda dashboard
            await page.wait_for_url("https://dashboard.render.com/**", timeout=30000)
            print("  ✅ Login realizado!")
            
            # Criar novo serviço
            print("  → Criando novo serviço...")
            await page.click('button:has-text("New")')
            await page.click('text=Web Service')
            
            # Conectar repositório
            print("  → Conectando repositório...")
            await page.wait_for_selector('text=Connect a repository')
            
            # Procurar pelo repositório assistente-ranny
            await page.fill('input[placeholder*="Search"]', "assistente-ranny")
            await asyncio.sleep(2)
            
            # Clicar em Connect
            await page.click('button:has-text("Connect")')
            await page.wait_for_load_state("networkidle")
            
            # Configurar serviço
            print("  → Configurando serviço...")
            
            # Nome
            await page.fill('input[name="name"]', "assistente-ranny")
            
            # Root Directory
            await page.fill('input[name="rootDir"]', "assistente-ranny")
            
            # Build Command
            await page.fill('input[name="buildCommand"]', "pip install -r requirements.txt")
            
            # Start Command
            await page.fill('input[name="startCommand"]', "python bot.py")
            
            # Selecionar plano Free
            await page.click('text=Free')
            
            # Adicionar variáveis de ambiente
            print("  → Adicionando variáveis de ambiente...")
            await page.click('text=Advanced')
            
            # TELEGRAM_BOT_TOKEN
            await page.click('button:has-text("Add Environment Variable")')
            await page.fill('input[placeholder="Key"]', "TELEGRAM_BOT_TOKEN")
            await page.fill('input[placeholder="Value"]', self.telegram_token)
            
            # GEMINI_API_KEY
            await page.click('button:has-text("Add Environment Variable")')
            inputs = await page.query_selector_all('input[placeholder="Key"]')
            await inputs[-1].fill("GEMINI_API_KEY")
            values = await page.query_selector_all('input[placeholder="Value"]')
            await values[-1].fill(self.gemini_key)
            
            # GROUP_ID
            await page.click('button:has-text("Add Environment Variable")')
            inputs = await page.query_selector_all('input[placeholder="Key"]')
            await inputs[-1].fill("GROUP_ID")
            values = await page.query_selector_all('input[placeholder="Value"]')
            await values[-1].fill("-1003536252896")
            
            # Criar serviço
            print("  → Iniciando deploy...")
            await page.click('button:has-text("Create Web Service")')
            
            print("  ✅ Deploy iniciado!")
            print("\n⏳ Aguardando build (3-5 minutos)...")
            
            # Aguardar até ver "Live" no status
            await page.wait_for_selector('text=Live', timeout=600000)  # 10 min max
            
            print("  ✅ Deploy concluído!")
            
            # Pegar URL do serviço
            url_element = await page.query_selector('a[href*=".onrender.com"]')
            if url_element:
                service_url = await url_element.get_attribute('href')
                print(f"\n🌐 URL do serviço: {service_url}")
                return service_url
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao fazer deploy: {e}")
            return False
    
    async def verificar_deploy(self, service_url):
        """Verifica se o deploy foi bem-sucedido"""
        print("\n🔍 VERIFICANDO DEPLOY...")
        
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{service_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    print("  ✅ Health check OK!")
                    print(f"  📊 Status: {data.get('status')}")
                    print(f"  🤖 Serviço: {data.get('service')}")
                    print(f"  📦 Versão: {data.get('version')}")
                    
                    # Verificar scheduler
                    scheduler = data.get('components', {}).get('scheduler', {})
                    jobs_count = scheduler.get('jobs_count', 0)
                    
                    if jobs_count >= 4:
                        print(f"  ✅ Keep-alive configurado! ({jobs_count} jobs)")
                    else:
                        print(f"  ⚠️  Jobs: {jobs_count} (esperado: 4)")
                    
                    return True
                else:
                    print(f"  ❌ Health check falhou: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Erro ao verificar: {e}")
            return False
    
    async def executar(self):
        """Executa todo o processo de deploy"""
        print("🤖 DEPLOY AUTOMÁTICO - ASSISTENTE RANNY")
        print("="*60)
        
        # Coletar credenciais
        await self.coletar_credenciais()
        
        # Iniciar Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                # 1. Criar repositório no GitHub
                if not await self.criar_repositorio_github(page):
                    print("\n❌ Falha ao criar repositório no GitHub")
                    return
                
                # 2. Fazer push do código
                if not await self.fazer_push_codigo():
                    print("\n❌ Falha ao enviar código")
                    return
                
                # 3. Fazer deploy no Render
                service_url = await self.fazer_deploy_render(page)
                if not service_url:
                    print("\n❌ Falha ao fazer deploy no Render")
                    return
                
                # 4. Verificar deploy
                await asyncio.sleep(30)  # Aguarda 30s para o serviço iniciar
                await self.verificar_deploy(service_url)
                
                print("\n" + "="*60)
                print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
                print("="*60)
                print(f"\n🌐 URL: {service_url}")
                print(f"📊 Health: {service_url}/health")
                print("\n✅ Próximos passos:")
                print("  1. Testar bot no Telegram")
                print("  2. Enviar mensagem: 'oi'")
                print("  3. Verificar logs no Render")
                print("  4. Aguardar 10 min e verificar keep-alive")
                
            finally:
                await browser.close()


async def main():
    """Função principal"""
    deploy = DeployAutomatico()
    await deploy.executar()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Deploy cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
