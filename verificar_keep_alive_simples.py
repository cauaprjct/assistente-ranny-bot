"""
✅ Verificação Simples do Keep-Alive
Script rápido para verificar se o keep-alive está funcionando
"""

import asyncio
import httpx
from datetime import datetime


async def verificar_agora():
    """Verificação rápida do status atual"""
    print("\n" + "="*60)
    print("🔍 VERIFICAÇÃO RÁPIDA DO KEEP-ALIVE")
    print("="*60)
    
    SERVICE_URL = "https://assistente-ranny-v3.onrender.com"
    
    try:
        print(f"\n📡 Conectando a {SERVICE_URL}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Faz requisição
            start_time = datetime.now()
            response = await client.get(f"{SERVICE_URL}/health")
            end_time = datetime.now()
            
            # Calcula tempo de resposta
            response_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Serviço está ONLINE!")
                print(f"⏱️ Tempo de resposta: {response_time:.2f}s")
                
                # Analisa resposta
                print(f"\n📊 Status do Serviço:")
                print(f"   Status geral: {data.get('status')}")
                print(f"   Versão: {data.get('version')}")
                print(f"   Timestamp: {data.get('timestamp', '')[:19]}")
                
                # Verifica componentes
                components = data.get('components', {})
                scheduler = components.get('scheduler', {})
                
                print(f"\n🔧 Componentes:")
                print(f"   Web: {components.get('web')}")
                print(f"   Scheduler: {scheduler.get('status')}")
                print(f"   Jobs ativos: {scheduler.get('jobs_count')}")
                
                # Verifica keep-alive
                jobs_count = scheduler.get('jobs_count', 0)
                
                print(f"\n💓 Keep-Alive:")
                if jobs_count >= 4:
                    print("   ✅ CONFIGURADO E ATIVO!")
                    print("   ✅ O bot está fazendo requisições a cada 10 minutos")
                    print("   ✅ O serviço não vai dormir")
                else:
                    print(f"   ⚠️ ATENÇÃO: Esperado 4 jobs, encontrado {jobs_count}")
                    print("   ⚠️ O keep-alive pode não estar configurado")
                
                # Análise do tempo de resposta
                print(f"\n⚡ Análise de Performance:")
                if response_time < 1:
                    print(f"   ✅ EXCELENTE! ({response_time:.2f}s)")
                    print("   ✅ Bot está acordado e respondendo rápido")
                elif response_time < 5:
                    print(f"   ✅ BOM ({response_time:.2f}s)")
                    print("   ✅ Bot está acordado")
                elif response_time < 30:
                    print(f"   ⚠️ LENTO ({response_time:.2f}s)")
                    print("   ⚠️ Bot pode estar acordando (cold start)")
                else:
                    print(f"   ❌ MUITO LENTO ({response_time:.2f}s)")
                    print("   ❌ Possível problema de rede ou serviço")
                
                # Conclusão
                print("\n" + "="*60)
                if jobs_count >= 4 and response_time < 5:
                    print("🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
                    print("="*60)
                    print("\n✅ O keep-alive está ativo")
                    print("✅ O bot não vai dormir")
                    print("✅ Lembretes e alertas vão funcionar 24/7")
                elif jobs_count >= 4:
                    print("✅ KEEP-ALIVE CONFIGURADO")
                    print("="*60)
                    print("\n✅ O keep-alive está ativo")
                    print("⚠️ Mas o tempo de resposta está alto")
                    print("💡 Pode ter sido cold start, tente novamente")
                else:
                    print("⚠️ ATENÇÃO: VERIFICAR CONFIGURAÇÃO")
                    print("="*60)
                    print("\n⚠️ O keep-alive pode não estar configurado")
                    print("💡 Verifique os logs do Render")
                
                return True
                
            else:
                print(f"❌ Erro: Status {response.status_code}")
                return False
                
    except httpx.TimeoutException:
        print("❌ TIMEOUT: Serviço não respondeu em 30 segundos")
        print("💡 O serviço pode estar dormindo (cold start)")
        print("💡 Aguarde 1 minuto e tente novamente")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def monitorar_continuo(minutos=5):
    """Monitora continuamente por alguns minutos"""
    print("\n" + "="*60)
    print(f"📊 MONITORAMENTO CONTÍNUO ({minutos} minutos)")
    print("="*60)
    print(f"\n⏰ Vou verificar o serviço a cada 30 segundos por {minutos} minutos")
    print("   Isso vai mostrar se o keep-alive está mantendo o bot acordado\n")
    
    SERVICE_URL = "https://assistente-ranny-v3.onrender.com"
    
    checks = []
    total_checks = (minutos * 60) // 30  # A cada 30 segundos
    
    for i in range(total_checks):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start = datetime.now()
                response = await client.get(f"{SERVICE_URL}/health")
                elapsed = (datetime.now() - start).total_seconds()
                
                if response.status_code == 200:
                    status = "✅ ONLINE"
                    checks.append(True)
                else:
                    status = f"⚠️ STATUS {response.status_code}"
                    checks.append(False)
                
                print(f"[{timestamp}] Check {i+1}/{total_checks}: {status} ({elapsed:.2f}s)")
                
        except Exception as e:
            print(f"[{timestamp}] Check {i+1}/{total_checks}: ❌ ERRO ({str(e)[:50]})")
            checks.append(False)
        
        # Aguarda 30 segundos (exceto na última iteração)
        if i < total_checks - 1:
            await asyncio.sleep(30)
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DO MONITORAMENTO")
    print("="*60)
    
    success_count = sum(checks)
    total_count = len(checks)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n✅ Checks bem-sucedidos: {success_count}/{total_count}")
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 PERFEITO! O serviço ficou online durante todo o teste!")
        print("✅ O keep-alive está funcionando corretamente")
    elif success_rate >= 80:
        print("\n✅ BOM! O serviço ficou online na maior parte do tempo")
        print("⚠️ Algumas falhas podem ser normais (rede, etc)")
    else:
        print("\n⚠️ ATENÇÃO! Muitas falhas detectadas")
        print("💡 Verifique os logs do Render para mais detalhes")


async def main():
    """Menu principal"""
    print("\n" + "="*60)
    print("💓 VERIFICADOR DO KEEP-ALIVE")
    print("="*60)
    
    print("\nEscolha uma opção:")
    print("1. Verificação rápida (10 segundos)")
    print("2. Monitoramento contínuo (5 minutos)")
    print("3. Monitoramento longo (15 minutos)")
    
    try:
        choice = input("\n👉 Digite o número (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
        return
    
    if choice == "1":
        await verificar_agora()
    elif choice == "2":
        await verificar_agora()
        print("\n" + "="*60)
        continuar = input("\n👉 Deseja iniciar o monitoramento? (s/n): ").strip().lower()
        if continuar == 's':
            await monitorar_continuo(minutos=5)
    elif choice == "3":
        await verificar_agora()
        print("\n" + "="*60)
        continuar = input("\n👉 Deseja iniciar o monitoramento longo? (s/n): ").strip().lower()
        if continuar == 's':
            await monitorar_continuo(minutos=15)
    else:
        print("\n❌ Opção inválida!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Interrompido pelo usuário")
