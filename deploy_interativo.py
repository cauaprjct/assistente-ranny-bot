"""
Deploy Interativo com Playwright
Abre navegador para voce fazer login manualmente
"""

import asyncio
import os
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright nao instalado!")
    print("Instalando...")
    os.system("pip install playwright")
    os.system("playwright install chromium")
    sys.exit(1)


async def deploy_interativo():
    print("DEPLOY INTERATIVO - ASSISTENTE RANNY")
    print("="*60)
    print("\nVou abrir o navegador para voce fazer login")
    print("Depois eu automatizo o resto!\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("\nPASSO 1: GITHUB")
            print("="*60)
            
            await page.goto("https://github.com/login", timeout=60000)
            
            print("\nFACA LOGIN NO GITHUB")
            print("Aguardando voce fazer login...")
            
            try:
                await page.wait_for_url("https://github.com/**", timeout=300000)
                print("Login realizado!")
            except:
                print("Timeout - continuando...")
            
            await asyncio.sleep(2)
            
            print("\nCriando repositorio 'assistente-ranny'...")
            await page.goto("https://github.com/new", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            try:
                await page.fill('input[name="repository[name]"]', "assistente-ranny")
                await page.fill('textarea[name="repository[description]"]', 
                              "Bot Telegram inteligente para gestao da GRN Pizzas - Com IA Gemini")
                
                await page.click('input[value="public"]')
                await asyncio.sleep(1)
                
                await page.click('button:has-text("Create repository")')
                await page.wait_for_load_state("networkidle")
                
                repo_url = page.url
                print(f"Repositorio criado: {repo_url}")
                
            except Exception as e:
                print(f"Erro ao criar repositorio: {e}")
                print("Pode ser que ja exista - continuando...")
            
            await asyncio.sleep(3)
            
            print("\nPASSO 2: ENVIANDO CODIGO")
            print("="*60)
            
            current_url = page.url
            if "github.com/" in current_url:
                username = current_url.split("github.com/")[1].split("/")[0]
                print(f"Username detectado: {username}")
                
                print("\nIMPORTANTE: Vou tentar fazer push")
                print("Se pedir senha, use um Personal Access Token")
                print("(Crie em: https://github.com/settings/tokens)")
                
                input("\nPressione ENTER quando estiver pronto...")
                
                print("\nConfigurando git...")
                os.system('git config user.name "Ranny"')
                os.system('git config user.email "ranny@grnpizzas.com"')
                
                print("Adicionando arquivos...")
                os.system('git add assistente-ranny/')
                os.system('git add requirements.txt')
                os.system('git add Procfile')
                os.system('git add .gitignore')
                
                print("Fazendo commit...")
                os.system('git commit -m "Deploy inicial - Assistente Ranny com keep-alive"')
                
                print("Configurando remote...")
                os.system('git remote remove origin 2>nul')
                remote_url = f"https://github.com/{username}/assistente-ranny.git"
                os.system(f'git remote add origin {remote_url}')
                
                print("Renomeando branch para main...")
                os.system('git branch -M main')
                
                print("Fazendo push...")
                print("Se pedir senha, use seu Personal Access Token!")
                result = os.system('git push -u origin main')
                
                if result == 0:
                    print("Codigo enviado com sucesso!")
                else:
                    print("Erro no push - voce pode fazer manualmente depois")
                
            await asyncio.sleep(3)
            
            print("\nPASSO 3: RENDER.COM")
            print("="*60)
            
            print("\nAbrindo Render.com...")
            await page.goto("https://dashboard.render.com/login", timeout=60000)
            
            print("\nFACA LOGIN NO RENDER.COM")
            print("Aguardando voce fazer login...")
            
            try:
                await page.wait_for_url("https://dashboard.render.com/**", timeout=300000)
                print("Login realizado!")
            except:
                print("Timeout - continuando...")
            
            await asyncio.sleep(3)
            
            print("\nCriando Web Service...")
            
            try:
                await page.click('button:has-text("New")', timeout=10000)
            except:
                try:
                    await page.click('a:has-text("New")', timeout=10000)
                except:
                    print("Nao encontrei botao New - clique manualmente")
                    input("Pressione ENTER depois de clicar em New...")
            
            await asyncio.sleep(2)
            
            try:
                await page.click('text=Web Service')
                await asyncio.sleep(3)
            except:
                print("Nao encontrei Web Service - clique manualmente")
                input("Pressione ENTER depois de clicar em Web Service...")
            
            print("\nCONECTE O REPOSITORIO:")
            print("1. Procure por 'assistente-ranny'")
            print("2. Clique em 'Connect'")
            input("\nPressione ENTER depois de conectar...")
            
            await asyncio.sleep(2)
            
            print("\nConfigurando servico...")
            
            try:
                await page.fill('input[name="name"]', "assistente-ranny")
                print("Nome: assistente-ranny")
            except:
                print("Nome ja preenchido")
            
            try:
                await page.fill('input[placeholder*="Root"]', "assistente-ranny")
                print("Root: assistente-ranny")
            except:
                print("Root ja preenchido")
            
            try:
                await page.fill('input[placeholder*="Build"]', "pip install -r requirements.txt")
                print("Build: pip install -r requirements.txt")
            except:
                print("Build ja preenchido")
            
            try:
                await page.fill('input[placeholder*="Start"]', "python bot.py")
                print("Start: python bot.py")
            except:
                print("Start ja preenchido")
            
            await asyncio.sleep(2)
            
            print("\nSelecionando plano Free...")
            try:
                await page.click('text=Free')
                print("Plano Free selecionado")
            except:
                print("Plano ja selecionado")
            
            await asyncio.sleep(2)
            
            print("\nAdicionando variaveis de ambiente...")
            print("Clique em 'Advanced' se nao estiver aberto")
            
            try:
                await page.click('button:has-text("Advanced")')
                await asyncio.sleep(2)
            except:
                pass
            
            env_path = Path("assistente-ranny/.env")
            env_vars = {}
            
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key] = value
            
            vars_importantes = [
                'TELEGRAM_BOT_TOKEN',
                'GEMINI_API_KEY',
                'GROUP_ID',
                'TOPIC_FINANCEIRO',
                'TOPIC_EMPRESA',
                'TOPIC_JURIDICO',
                'TOPIC_PESSOAL',
                'TOPIC_FUNCIONARIOS',
                'TOPIC_OPERACIONAL',
                'TOPIC_MIDIA',
                'TOPIC_CONTROLES',
                'TOPIC_OUTROS'
            ]
            
            print("\nVariaveis a adicionar:")
            for var in vars_importantes:
                if var in env_vars:
                    valor = env_vars[var]
                    if 'TOKEN' in var or 'KEY' in var:
                        valor_mostrar = valor[:10] + "..." if len(valor) > 10 else valor
                    else:
                        valor_mostrar = valor
                    print(f"• {var} = {valor_mostrar}")
            
            print("\nADICIONE AS VARIAVEIS MANUALMENTE:")
            print("1. Clique em 'Add Environment Variable'")
            print("2. Cole cada variavel (nome e valor)")
            print("3. Repita para todas as variaveis acima")
            
            input("\nPressione ENTER depois de adicionar todas...")
            
            print("\nCriando servico...")
            print("Clique em 'Create Web Service'")
            
            input("\nPressione ENTER depois de clicar...")
            
            print("\n" + "="*60)
            print("DEPLOY INICIADO!")
            print("="*60)
            print("\nProximos passos:")
            print("1. Aguarde o build terminar (5-10 min)")
            print("2. Quando aparecer 'Live', esta pronto!")
            print("3. Teste no Telegram: envie 'oi'")
            print("\nDeixando navegador aberto para voce acompanhar...")
            
            input("\nPressione ENTER quando o deploy terminar...")
            
        finally:
            await browser.close()
            print("\nProcesso concluido!")


if __name__ == "__main__":
    try:
        asyncio.run(deploy_interativo())
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuario")
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()
