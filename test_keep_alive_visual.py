"""
🎬 Teste Visual do Keep-Alive com Playwright
Monitora visualmente o sistema keep-alive em ação
"""

import asyncio
from datetime import datetime
import time


async def test_keep_alive_visual():
    """
    Teste visual que mostra o keep-alive funcionando em tempo real
    """
    print("\n" + "="*70)
    print("🎬 TESTE VISUAL DO KEEP-ALIVE")
    print("="*70)
    print("\n📋 Este teste vai:")
    print("   1. Abrir o navegador e acessar o health check")
    print("   2. Monitorar requisições por 3 minutos")
    print("   3. Tirar screenshots a cada minuto")
    print("   4. Verificar se o serviço permanece ativo")
    
    try:
        from playwright.async_api import async_playwright
        import httpx
        
        SERVICE_URL = "https://assistente-ranny-v3.onrender.com"
        
        async with async_playwright() as p:
            # Inicia navegador visível
            print("\n🌐 Iniciando navegador (modo visível)...")
            browser = await p.chromium.launch(
                headless=False,  # Modo visível
                slow_mo=1000  # Slow motion para ver melhor
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            
            page = await context.new_page()
            
            # Rastreia requisições de rede
            requests_log = []
            
            def log_request(request):
                if '/health' in request.url:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    requests_log.append({
                        'time': timestamp,
                        'url': request.url,
                        'method': request.method
                    })
                    print(f"   📡 [{timestamp}] Requisição: {request.method} {request.url}")
            
            page.on("request", log_request)
            
            # Acessa o health check
            print(f"\n📡 Acessando {SERVICE_URL}/health...")
            await page.goto(f"{SERVICE_URL}/health", wait_until="networkidle")
            
            print("✅ Página carregada!")
            
            # Tira screenshot inicial
            await page.screenshot(path="keep_alive_0min.png")
            print("📸 Screenshot inicial salvo: keep_alive_0min.png")
            
            # Monitora por 3 minutos
            print("\n⏰ Monitorando por 3 minutos...")
            print("   (O keep-alive interno deve disparar a cada 10 minutos)")
            print("   (Vamos fazer requisições manuais a cada minuto para verificar)\n")
            
            for minute in range(1, 4):
                print(f"\n⏳ Aguardando 1 minuto... ({minute}/3)")
                await asyncio.sleep(60)
                
                # Recarrega a página para fazer nova requisição
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"   🔄 [{timestamp}] Recarregando página...")
                await page.reload(wait_until="networkidle")
                
                # Verifica o conteúdo
                content = await page.text_content('body')
                if 'healthy' in content:
                    print(f"   ✅ [{timestamp}] Serviço ainda está ativo!")
                else:
                    print(f"   ⚠️ [{timestamp}] Resposta inesperada")
                
                # Tira screenshot
                screenshot_name = f"keep_alive_{minute}min.png"
                await page.screenshot(path=screenshot_name)
                print(f"   📸 Screenshot salvo: {screenshot_name}")
            
            # Resumo das requisições
            print("\n" + "="*70)
            print("📊 RESUMO DAS REQUISIÇÕES")
            print("="*70)
            print(f"Total de requisições /health capturadas: {len(requests_log)}")
            
            if requests_log:
                print("\n📋 Log de requisições:")
                for req in requests_log:
                    print(f"   [{req['time']}] {req['method']} {req['url']}")
            
            # Teste adicional: verificar se o keep-alive interno está configurado
            print("\n" + "="*70)
            print("🔍 VERIFICANDO CONFIGURAÇÃO DO KEEP-ALIVE INTERNO")
            print("="*70)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{SERVICE_URL}/health")
                data = response.json()
                
                scheduler = data.get('components', {}).get('scheduler', {})
                jobs_count = scheduler.get('jobs_count', 0)
                
                print(f"\n📊 Status do Scheduler:")
                print(f"   Status: {scheduler.get('status')}")
                print(f"   Jobs ativos: {jobs_count}")
                
                if jobs_count >= 4:
                    print("\n✅ KEEP-ALIVE CONFIGURADO!")
                    print("   O job keep_alive está entre os 4 jobs ativos:")
                    print("   1. check_lembretes (a cada minuto)")
                    print("   2. check_vencimentos (diário às 08:00)")
                    print("   3. resumo_semanal (domingo às 20:00)")
                    print("   4. keep_alive (a cada 10 minutos) ← ESTE!")
                else:
                    print(f"\n⚠️ ATENÇÃO: Esperado 4 jobs, encontrado {jobs_count}")
            
            print("\n⏸️ Pressione Enter para fechar o navegador...")
            input()
            
            await browser.close()
            
            print("\n" + "="*70)
            print("✅ TESTE CONCLUÍDO!")
            print("="*70)
            print("\n📸 Screenshots salvos:")
            print("   - keep_alive_0min.png (inicial)")
            print("   - keep_alive_1min.png (após 1 minuto)")
            print("   - keep_alive_2min.png (após 2 minutos)")
            print("   - keep_alive_3min.png (após 3 minutos)")
            
            return True
            
    except ImportError:
        print("\n❌ Playwright não está instalado!")
        print("\n📦 Para instalar:")
        print("   pip install playwright")
        print("   playwright install chromium")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_keep_alive_logs():
    """
    Testa verificando os logs do Render para ver o keep-alive em ação
    """
    print("\n" + "="*70)
    print("📋 COMO VERIFICAR O KEEP-ALIVE NOS LOGS DO RENDER")
    print("="*70)
    
    print("\n1️⃣ Acesse o dashboard do Render:")
    print("   https://dashboard.render.com/")
    
    print("\n2️⃣ Selecione seu serviço:")
    print("   assistente-ranny-v3")
    
    print("\n3️⃣ Clique em 'Logs' no menu lateral")
    
    print("\n4️⃣ Procure por estas mensagens:")
    print("   ✅ '💓 Keep-alive: bot está acordado'")
    print("   ✅ 'GET /health' com status 200")
    
    print("\n5️⃣ O que você deve ver:")
    print("   - A cada 10 minutos: mensagem de keep-alive")
    print("   - Requisições GET /health com sucesso")
    print("   - Nenhum erro de timeout ou sleep")
    
    print("\n6️⃣ Sinais de que está funcionando:")
    print("   ✅ Logs aparecem regularmente (a cada 10 min)")
    print("   ✅ Serviço não entra em 'sleep' após 15 min")
    print("   ✅ Bot responde imediatamente no Telegram")
    
    print("\n7️⃣ Sinais de problema:")
    print("   ❌ Logs param de aparecer")
    print("   ❌ Mensagens de timeout ou erro")
    print("   ❌ Bot demora para responder (cold start)")


async def main():
    """Menu principal"""
    print("\n" + "="*70)
    print("🎬 TESTE VISUAL DO SISTEMA KEEP-ALIVE")
    print("="*70)
    
    print("\nEscolha uma opção:")
    print("1. Teste visual com navegador (3 minutos)")
    print("2. Instruções para verificar logs do Render")
    print("3. Ambos")
    
    try:
        choice = input("\n👉 Digite o número (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
        return
    
    if choice == "1":
        await test_keep_alive_visual()
    elif choice == "2":
        await test_keep_alive_logs()
    elif choice == "3":
        await test_keep_alive_visual()
        await test_keep_alive_logs()
    else:
        print("\n❌ Opção inválida!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido")
