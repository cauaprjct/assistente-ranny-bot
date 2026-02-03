"""Testa todas as chaves do Gemini"""
import google.generativeai as genai

keys = [
    "AIzaSyDoCP1dgiwZN4WEpWDqkk8oSlwI4UlO_LA",
    "AIzaSyBCcH1pDSVK9HQ26H2zu9QRqpraP9-WP9Q",
    "AIzaSyATesCPbtwnzeTVBqgwJ2zuGdQptmYlreo",
    "AIzaSyDOIHI0pV-JiEeUft0c67WhqOo74tVlrg4",
    "AIzaSyAGwFyKZ6oxxvG4Qvq8at0SCFyTovCSrMM",
    "AIzaSyAHiPyr9UpnrALfOt-ys1BdMIO_gTxYsDw",
    "AIzaSyCODbx_Z8oz7nMp3m2AzOx2L9w0qreQa2Y",
    "AIzaSyBgZ-H9gnFFrNpjd5FNtBbcRwzDSIcrklM",
    "AIzaSyAixjNlYVAEJRyNIyuO9z_4SYOcsEvRuJY",
    "AIzaSyCJZUx_dZpXpusMPl9TLgexyPA9i7ml0So",
    "AIzaSyDyLg0DiwBSkE6z65KxUXL1JarBsYMeuLk",
    "AIzaSyBVPa6xkGbf0uYyGwEzIsZa0AyVCvpcyxU",
    "AIzaSyBcwruQSgaqBd0Hg6-zBkWlqPSadqyOF3I",
    "AIzaSyBYi-fCnSiy_JkualFJXV0VG2Pblwh21OI",
]

print("Testando chaves do Gemini...\n")

for i, key in enumerate(keys, 1):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Diga apenas: OK")
        print(f"✅ Chave {i}: FUNCIONA! - {key[:20]}...")
        print(f"   Resposta: {response.text.strip()[:50]}")
    except Exception as e:
        error_msg = str(e)[:60]
        print(f"❌ Chave {i}: FALHOU - {key[:20]}...")
        print(f"   Erro: {error_msg}")
    print()
