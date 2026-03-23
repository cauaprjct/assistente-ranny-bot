"""
🧪 Teste do Sistema Keep-Alive com Playwright
Verifica se o bot está fazendo requisições automáticas para evitar sleep
"""

import asyncio
import time
from datetime import datetime
import sys

# Configuração da URL do serviço
# Altere para a URL do seu deploy no Render
SERVICE_URL = "https://assistente-ranny-v3.onrender.com"


async def test_health_endpoint():
    """Testa se o endpoint /health está respondendo"""
    print("\n" + "="*60)
    print("🔍 TESTE 1: Verificando endpoint /health")
    print("="*60)
    
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"📡 Fazendo requisição para {SERVICE_URL}/health...")
            response = await client.get(f"{SERVICE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Endpoint /health está respondendo!")
                print(f"   Status: {data.get('status')}")
                print(f"   Serviço: {data.get('service')}")
                print(f"   Versão: {data.get('version')}")
                
                # Verifica componentes
                components = data.get('components', {})
                scheduler = components.get('scheduler', {})
                
                print(f"\n📊 Componentes:")
                print(f"   Web: {components.get('web')}")
                print(f"   Scheduler: {scheduler.get('status')}")
                print(f"   Jobs ativos: {scheduler.get('jobs_count')}")
                
                if scheduler.get('jobs_count', 0) >= 4:
                    print("   ✅ Keep-alive job está configurado!")
                else:
                    print("   ⚠️ Esperado 4 jobs (incluindo keep_alive)")
                
                return True
            else:
                print(f"❌ Endpoint retornou status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False


async def monitor_keep_alive_logs(duration_minutes=15):
    """
    Monitora se o keep-alive está funcionando observando os logs
    
    Args:
        duration_minutes: Tempo de monitoramento em minutos
    """
    print("\n" + "="*60)
    print(f"🔍 TESTE 2: Monitorando keep-alive por {duration_minutes} minutos")
    print("="*60)
    print("\n⏰ O keep-alive deve fazer requisições a cada 10 minutos")
    print("   Vamos verificar se o serviço permanece ativo...\n")
    
    try:
        import httpx
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        check_count = 0
        success_count = 0
        
        while time.time() < end_time:
            check_count += 1
            elapsed = int(time.time() - start_time)
            remaining = int(end_time - time.time())
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{SERVICE_URL}/health")
                    
                    if response.status_code == 200:
                        success_count += 1
                        print(f"[{timestamp}] ✅ Check #{check_count} - Serviço ativo "
                              f"(tempo decorrido: {elapsed//60}m{elapsed%60}s, "
                              f"restante: {remaining//60}m{remaining%60}s)")
                    else:
                        print(f"[{timestamp}] ⚠️ Check #{check_count} - Status {response.status_code}")
                        
            except Exception as e:
                print(f"[{timestamp}] ❌ Check #{check_count} - Erro: {e}")
            
            # Aguarda 2 minutos entre cada verificação
            await asyncio.sleep(120)
        
        # Resultado final
        print("\n" + "="*60)
        print("📊 RESULTADO DO MONITORAMENTO")
        print("="*60)
        print(f"✅ Verificações bem-sucedidas: {success_count}/{check_count}")
        print(f"⏱️ Tempo total: {duration_minutes} minutos")
        
        if success_count == check_count:
            print("\n🎉 SUCESSO! O serviço permaneceu ativo durante todo o teste!")
            print("   O keep-alive está funcionando corretamente.")
            return True
        elif success_count > 0:
            print(f"\n⚠️ PARCIAL: {success_count}/{check_count} verificações bem-sucedidas")
            print("   O keep-alive pode estar com problemas intermitentes.")
            return False
        else:
            print("\n❌ FALHA: Nenhuma verificação bem-sucedida")
            print("   O keep-alive não está funcionando.")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro durante monitoramento: {e}")
        return False


async def test_keep_alive_timing():
    """
    Testa se o keep-alive está fazendo requisições no intervalo correto (10 min)
    """
    print("\n" + "="*60)
    print("🔍 TESTE 3: Verificando intervalo do keep-alive")
    print("="*60)
    print("\n⏰ Aguardando 12 minutos para verificar se o keep-alive dispara...")
    print("   (O keep-alive deve disparar a cada 10 minutos)\n")
    
    try:
        import httpx
        
        # Faz requisição inicial para "acordar" o serviço
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.get(f"{SERVICE_URL}/health")
        
        print("✅ Serviço acordado. Aguardando 12 minutos...")
        print("   (Isso garante que pelo menos 1 keep-alive deve ter disparado)\n")
        
        # Aguarda 12 minutos (720 segundos)
        for i in range(12):
            await asyncio.sleep(60)  # 1 minuto
            print(f"   ⏳ {i+1}/12 minutos decorridos...")
        
        # Verifica se o serviço ainda está ativo
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{SERVICE_URL}/health")
            
            if response.status_code == 200:
                print("\n✅ SUCESSO! Serviço ainda está ativo após 12 minutos!")
                print("   O keep-alive está funcionando e mantendo o bot acordado.")
                return True
            else:
                print(f"\n❌ FALHA: Serviço retornou status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"\n❌ Erro durante teste de timing: {e}")
        return False


async def test_with_playwright():
    """
    Testa o keep-alive usando Playwright para simular navegador
    """
    print("\n" + "="*60)
    print("🔍 TESTE 4: Verificando com Playwright (navegador real)")
    print("="*60)
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # Inicia navegador
            print("\n🌐 Iniciando navegador...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Acessa o health check
            print(f"📡 Acessando {SERVICE_URL}/health...")
            response = await page.goto(f"{SERVICE_URL}/health", wait_until="networkidle")
            
            if response.status == 200:
                print("✅ Página carregada com sucesso!")
                
                # Captura o conteúdo JSON
                content = await page.content()
                print("\n📄 Resposta do servidor:")
                print(content[:500] + "..." if len(content) > 500 else content)
                
                # Tira screenshot
                screenshot_path = "keep_alive_health_check.png"
                await page.screenshot(path=screenshot_path)
                print(f"\n📸 Screenshot salvo em: {screenshot_path}")
                
                await browser.close()
                return True
            else:
                print(f"❌ Página retornou status {response.status}")
                await browser.close()
                return False
                
    except ImportError:
        print("⚠️ Playwright não está instalado")
        print("   Instale com: pip install playwright")
        print("   E depois: playwright install chromium")
        return None
    except Exception as e:
        print(f"❌ Erro ao usar Playwright: {e}")
        return False


async def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("🧪 TESTE COMPLETO DO SISTEMA KEEP-ALIVE")
    print("="*70)
    print(f"\n🎯 URL do serviço: {SERVICE_URL}")
    print(f"⏰ Hora de início: {datetime.now().strftime('%H:%M:%S')}")
    
    # Menu de opções
    print("\n" + "="*70)
    print("ESCOLHA O TIPO DE TESTE:")
    print("="*70)
    print("1. Teste rápido (apenas health check) - ~30 segundos")
    print("2. Teste médio (monitoramento 5 min) - ~5 minutos")
    print("3. Teste completo (monitoramento 15 min) - ~15 minutos")
    print("4. Teste de timing (aguarda 12 min) - ~12 minutos")
    print("5. Teste com Playwright (navegador) - ~1 minuto")
    print("6. Todos os testes (exceto timing longo)")
    print("="*70)
    
    try:
        choice = input("\n👉 Digite o número da opção (1-6): ").strip()
    except KeyboardInterrupt:
        print("\n\n❌ Teste cancelado pelo usuário")
        return
    
    results = {}
    
    if choice == "1":
        results['health'] = await test_health_endpoint()
    
    elif choice == "2":
        results['health'] = await test_health_endpoint()
        if results['health']:
            results['monitor'] = await monitor_keep_alive_logs(duration_minutes=5)
    
    elif choice == "3":
        results['health'] = await test_health_endpoint()
        if results['health']:
            results['monitor'] = await monitor_keep_alive_logs(duration_minutes=15)
    
    elif choice == "4":
        results['health'] = await test_health_endpoint()
        if results['health']:
            results['timing'] = await test_keep_alive_timing()
    
    elif choice == "5":
        results['playwright'] = await test_with_playwright()
    
    elif choice == "6":
        results['health'] = await test_health_endpoint()
        if results['health']:
            results['playwright'] = await test_with_playwright()
            results['monitor'] = await monitor_keep_alive_logs(duration_minutes=5)
    
    else:
        print("\n❌ Opção inválida!")
        return
    
    # Resumo final
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    for test_name, result in results.items():
        if result is None:
            status = "⚠️ NÃO EXECUTADO"
        elif result:
            status = "✅ PASSOU"
        else:
            status = "❌ FALHOU"
        
        print(f"{status} - {test_name.upper()}")
    
    # Conclusão
    print("\n" + "="*70)
    if all(r for r in results.values() if r is not None):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("   O sistema keep-alive está funcionando corretamente.")
    elif any(r for r in results.values() if r is not None):
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("   Verifique os logs acima para mais detalhes.")
    else:
        print("❌ TODOS OS TESTES FALHARAM")
        print("   O sistema keep-alive pode não estar funcionando.")
    print("="*70)
    
    print(f"\n⏰ Hora de término: {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido pelo usuário")
        sys.exit(1)
