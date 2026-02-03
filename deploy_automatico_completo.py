"""
🤖 Deploy 100% Automático - Assistente Ranny
Lê TODAS as credenciais do .env e faz deploy completo
"""

import asyncio
import os
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    import httpx
except ImportError:
    print("❌ Dependências não instaladas!")
    print("\nInstale com:")
    print("pip install playwright httpx")
    print("playwright install chromium")
    sys.exit(1)


class DeployAutomaticoCompleto:
    """Deploy 100% automático usando .env"""
    
    def __init__(self):
        self.config = {}
        
    def carregar_env(self):
        """Carrega TODAS as credenciais do .env"""
        print("📄 Carregando configurações do .env...")
        
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
                    self.config[key] = value
        
        # Verificar credenciais obrigatórias
        required = {
            'TELEGRAM_BOT_TOKEN': 'Telegram',
            'GEMINI_API_KEY': 'Gemini AI',
            'GITHUB_USERNAME': 'GitHub Username',
            'GITHUB_TOKEN': 'GitHub Token',
            'RENDER_EMAIL': 'Render Email',
            'RENDER_PASSWORD': 'Render Password'
        }
        
        missing = []
        for key, name in required.items():
            if key in self.config:
                print(f"  ✅ {name} carregado")
            else:
                print(f"  ❌ {name} NÃO encontrado")
                missing.append(key)
        
        if missing:
            print(f"\n❌ Faltam credenciais no .env:")
            for key in missing:
                print(f"   - {key}")
            print("\nAdicione essas linhas no assistente-ranny/.env:")
            print("\n# GitHub")
            print("GITHUB_USERNAME=seu_username")
            print("GITHUB_TOKEN=seu_token_ou_senha")
            print("\n# Render.com")
            print("RENDER_EMAIL=seu_email@example.com")
            print("RENDER_PASSWORD=sua_senha")
            sys.exit(1)
        
        print("\n✅ Todas as credenciais carregadas!")
        return True
    
    async def criar_repositorio_github(self, page):
        """Cria repositório no GitHub via navegador"""
        print("\n🐙 CRIANDO REPOSITÓRIO NO GITHUB...")
        
        try:
            # Login no GitHub
            print("  → Acessando GitHub...")
            await page.goto("https://github.com/login", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            print("  → Fazendo login...")
            await page.fill('input[name="login"]', self.config['GITHUB_USERNAME'])
            await page.fill('input[name="password"]', self.config['GITHUB_TOKEN'])
            await page.click('input[type="submit"]')
            
            # Aguarda login (pode ter 2FA)
            try:
                await page.wait_for_url("https://github.com/**", timeout=60000)
                print("  ✅ Login realizado!")
            except:
                print("  ⚠️  Aguardando 2FA (se necessário)...")
                print("  ⏳ Complete o 2FA no navegador e aguarde...")
                await page.wait_for_url("https://github.com/**", timeout=120000)
                print("  ✅ Login realizado!")
            
            # Criar novo repositório
            print("  → Criando repositório...")
            await page.goto("https://github.com/new", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            # Preencher formulário
            await page.fill('input[name="repository[name]"]', "assistente-ranny")
            await page.fill('textarea[name="repository[description]"]', 
                          "Bot Telegram inteligente para gestão da GRN Pizzas - Com IA Gemini e keep-alive")
            
            # Selecionar público
            await page.click('input[value="public"]')
            
            # Criar repositório
            await page.click('button:has-text("Create repository")')
            await page.wait_for_load_state("networkidle")
            
            # Pegar URL do repositório
            repo_url = page.url
            print(f"  ✅ Repositório criado: {repo_url}")
            
            return repo_url
            
        except Exception as e:
            print(f"  ❌ Erro ao criar repositório: {e}")
            return None
    
    async def fazer_push_codigo(self):
        """Faz push do código para o GitHub"""
        print("\n📤 ENVIANDO CÓDIGO PARA GITHUB...")
        
        try:
            username = self.config['GITHUB_USERNAME']
            token = self.config['GITHUB_TOKEN']
            
            # Adicionar remote
            remote_url = f"https://{username}:{token}@github.com/{username}/assistente-ranny.git"
            
            print("  → Removendo remote antigo (se existir)...")
            os.system('git remote remove origin 2>nul')
            
            print("  → Adicionando remote...")
            os.system(f'git remote add origin {remote_url}')
            
            print("  → Renomeando branch para main...")
            os.system('git branch -M main')
            
            print("  → Fazendo push...")
            result = os.system('git push -u origin main 2>&1')
            
            if result == 0:
                print("  ✅ Código enviado com sucesso!")
                return True
            else:
                print("  ⚠️  Push pode ter falhado, mas continuando...")
                return True  # Continua mesmo com erro
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            return False
    
    async def fazer_deploy_render(self, page):
        """Faz deploy no Render.com via navegador"""
        print("\n🚀 FAZENDO DEPLOY NO RENDER.COM...")
        
        try:
            # Login no Render
            print("  → Acessando Render...")
            await page.goto("https://dashboard.render.com/login", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            print("  → Fazendo login...")
            await page.fill('input[type="email"]', self.config['RENDER_EMAIL'])
            await page.fill('input[type="password"]', self.config['RENDER_PASSWORD'])
            await page.click('button[type="submit"]')
            
            # Aguarda dashboard
            await page.wait_for_url("https://dashboard.render.com/**", timeout=60000)
            print("  ✅ Login realizado!")
            
            # Aguarda um pouco
            await asyncio.sleep(3)
            
            # Criar novo serviço
            print("  → Criando novo serviço...")
            
            # Procurar botão New
            try:
                await page.click('button:has-text("New")', timeout=10000)
            except:
                await page.click('a:has-text("New")', timeout=10000)
            
            await asyncio.sleep(2)
            await page.click('text=Web Service')
            await asyncio.sleep(3)
            
            # Conectar repositório
            print("  → Conectando repositório GitHub...")
            
            # Aguardar página carregar
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # Procurar pelo repositório
            print("  → Procurando repositório assistente-ranny...")
            
            # Tentar encontrar e clicar em Connect
            try:
                # Procurar por assistente-ranny
                await page.fill('input[placeholder*="Search"]', "assistente-ranny")
                await asyncio.sleep(3)
                
                # Clicar em Connect
                await page.click('button:has-text("Connect")')
                await page.wait_for_load_state("networkidle")
                print("  ✅ Repositório conectado!")
            except:
                print("  ⚠️  Não encontrou repositório automaticamente")
                print("  ℹ️  Você pode precisar conectar manualmente")
                await asyncio.sleep(10)  # Aguarda usuário conectar
            
            # Configurar serviço
            print("  → Configurando serviço...")
            await asyncio.sleep(2)
            
            # Nome
            try:
                await page.fill('input[name="name"]', "assistente-ranny")
            except:
                print("  ℹ️  Nome já preenchido")
            
            # Root Directory
            try:
                await page.fill('input[placeholder*="Root"]', "assistente-ranny")
            except:
                print("  ℹ️  Root directory já preenchido")
            
            # Build Command
            try:
                await page.fill('input[placeholder*="Build"]', "pip install -r requirements.txt")
            except:
                print("  ℹ️  Build command já preenchido")
            
            # Start Command
            try:
                await page.fill('input[placeholder*="Start"]', "python bot.py")
            except:
                print("  ℹ️  Start command já preenchido")
            
            # Selecionar plano Free
            print("  → Selecionando plano Free...")
            try:
                await page.click('text=Free')
                await asyncio.sleep(1)
            except:
                print("  ℹ️  Plano Free já selecionado")
            
            # Adicionar variáveis de ambiente
            print("  → Adicionando variáveis de ambiente...")
            try:
                await page.click('button:has-text("Advanced")')
                await asyncio.sleep(2)
            except:
                print("  ℹ️  Seção Advanced já aberta")
            
            # Adicionar variáveis
            vars_to_add = [
                ('TELEGRAM_BOT_TOKEN', self.config['TELEGRAM_BOT_TOKEN']),
                ('GEMINI_API_KEY', self.config['GEMINI_API_KEY']),
                ('GROUP_ID', self.config['GROUP_ID'])
            ]
            
            for key, value in vars_to_add:
                try:
                    await page.click('button:has-text("Add Environment Variable")')
                    await asyncio.sleep(1)
                    
                    # Preencher última variável adicionada
                    key_inputs = await page.query_selector_all('input[placeholder="Key"]')
                    value_inputs = await page.query_selector_all('input[placeholder="Value"]')
                    
                    if key_inputs and value_inputs:
                        await key_inputs[-1].fill(key)
                        await value_inputs[-1].fill(value)
                        print(f"    ✅ {key} adicionado")
                except Exception as e:
                    print(f"    ⚠️  Erro ao adicionar {key}: {e}")
            
            # Criar serviço
            print("  → Iniciando deploy...")
            await page.click('button:has-text("Create Web Service")')
            
            print("  ✅ Deploy iniciado!")
            print("\n⏳ Aguardando build (pode levar 5-10 minutos)...")
            print("  ℹ️  Você pode acompanhar no navegador")
            
            # Aguardar um pouco e pegar URL
            await asyncio.sleep(10)
            
            try:
                # Tentar pegar URL do serviço
                url_element = await page.query_selector('a[href*=".onrender.com"]')
                if url_element:
                    service_url = await url_element.get_attribute('href')
                    print(f"\n🌐 URL do serviço: {service_url}")
                    return service_url
            except:
                pass
            
            print("\n  ℹ️  Aguarde o build terminar no navegador")
            print("  ℹ️  Quando aparecer 'Live', o deploy está completo!")
            
            # Aguardar mais tempo para o usuário ver
            await asyncio.sleep(60)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao fazer deploy: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def executar(self):
        """Executa todo o processo de deploy"""
        print("🤖 DEPLOY 100% AUTOMÁTICO - ASSISTENTE RANNY")
        print("="*60)
        
        # Carregar credenciais do .env
        if not self.carregar_env():
            return
        
        # Iniciar Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 1. Criar repositório no GitHub
                repo_url = await self.criar_repositorio_github(page)
                if not repo_url:
                    print("\n❌ Falha ao criar repositório no GitHub")
                    print("  ℹ️  Você pode criar manualmente e continuar")
                
                # 2. Fazer push do código
                if not await self.fazer_push_codigo():
                    print("\n⚠️  Falha ao enviar código, mas continuando...")
                
                # 3. Fazer deploy no Render
                service_url = await self.fazer_deploy_render(page)
                
                if service_url:
                    print("\n" + "="*60)
                    print("🎉 DEPLOY INICIADO COM SUCESSO!")
                    print("="*60)
                    print(f"\n🌐 URL: {service_url}")
                    print(f"📊 Health: {service_url}/health")
                    print("\n✅ Próximos passos:")
                    print("  1. Aguardar build terminar (5-10 min)")
                    print("  2. Testar bot no Telegram")
                    print("  3. Enviar mensagem: 'oi'")
                    print("  4. Verificar logs no Render")
                else:
                    print("\n⚠️  Deploy iniciado, acompanhe no navegador")
                
                # Manter navegador aberto
                print("\n  ℹ️  Navegador ficará aberto para você acompanhar")
                print("  ℹ️  Pressione ENTER quando o deploy terminar...")
                input()
                
            finally:
                await browser.close()


async def main():
    """Função principal"""
    deploy = DeployAutomaticoCompleto()
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
