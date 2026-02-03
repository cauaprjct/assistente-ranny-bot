"""
Teste do bot Ranny usando Playwright no Telegram Web
"""
import asyncio
import os
from playwright.async_api import async_playwright

async def test_telegram_web():
    """Testa o bot no Telegram Web"""
    
    async with async_playwright() as p:
        # Abre o navegador (headless=False para ver o que está acontecendo)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🌐 Abrindo Telegram Web...")
        await page.goto('https://web.telegram.org/k/')
        
        # Aguarda login manual (se necessário)
        print("⏳ Aguardando login... (faça login manualmente se necessário)")
        await page.wait_for_timeout(10000)  # 10 segundos para login
        
        # Procura pelo chat do bot
        print("🔍 Procurando pelo bot...")
        await page.wait_for_selector('input[type="text"]', timeout=30000)
        search_input = page.locator('input[type="text"]').first
        await search_input.fill('Assistente Ranny')
        await page.wait_for_timeout(2000)
        
        # Clica no chat do bot
        print("💬 Abrindo chat do bot...")
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(2000)
        
        # Testes de funcionalidades
        testes = [
            {
                'nome': 'Comando /start',
                'mensagem': '/start',
                'esperado': 'Olá'
            },
            {
                'nome': 'Busca de documento',
                'mensagem': 'buscar boleto',
                'esperado': 'encontr'
            },
            {
                'nome': 'Criar lembrete',
                'mensagem': 'lembrar reunião amanhã 14h',
                'esperado': 'lembrete'
            },
            {
                'nome': 'Listar lembretes',
                'mensagem': '/lembretes',
                'esperado': 'lembrete'
            }
        ]
        
        for teste in testes:
            print(f"\n📝 Testando: {teste['nome']}")
            
            # Localiza o campo de mensagem
            message_input = page.locator('div[contenteditable="true"]').last
            await message_input.click()
            await message_input.fill(teste['mensagem'])
            await page.wait_for_timeout(500)
            
            # Envia a mensagem
            await page.keyboard.press('Enter')
            print(f"   ✉️  Enviado: {teste['mensagem']}")
            
            # Aguarda resposta
            await page.wait_for_timeout(3000)
            
            # Captura as mensagens recentes
            messages = await page.locator('.message').all()
            if messages:
                last_message = messages[-1]
                text = await last_message.inner_text()
                print(f"   📨 Resposta: {text[:100]}...")
                
                # Verifica se contém o texto esperado
                if teste['esperado'].lower() in text.lower():
                    print(f"   ✅ Teste passou!")
                else:
                    print(f"   ⚠️  Resposta não contém '{teste['esperado']}'")
            else:
                print(f"   ❌ Nenhuma mensagem encontrada")
            
            await page.wait_for_timeout(2000)
        
        # Teste de upload de arquivo
        print(f"\n📎 Testando upload de arquivo...")
        
        # Clica no botão de anexar
        attach_button = page.locator('button[title="Attach"]').first
        if await attach_button.count() > 0:
            await attach_button.click()
            await page.wait_for_timeout(1000)
            
            # Seleciona "Document"
            doc_option = page.locator('text=Document').first
            if await doc_option.count() > 0:
                await doc_option.click()
                await page.wait_for_timeout(1000)
                
                # Aqui você pode fazer upload de um arquivo de teste
                print("   📄 Opção de upload disponível")
            else:
                print("   ⚠️  Opção de documento não encontrada")
        else:
            print("   ⚠️  Botão de anexar não encontrado")
        
        print("\n✅ Testes concluídos!")
        print("🔍 Verifique visualmente os resultados no navegador")
        
        # Mantém o navegador aberto por 30 segundos para inspeção
        await page.wait_for_timeout(30000)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_telegram_web())
