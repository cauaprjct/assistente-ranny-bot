# 📦 Instalação de Dependências

## ⚠️ Problema Atual

A biblioteca `supabase` não está instalada no ambiente Python.

## ✅ Solução

### Opção 1: Instalar Todas as Dependências (Recomendado)

```bash
cd assistente-ranny
pip install -r requirements.txt
```

**Nota:** Se você estiver no Windows e encontrar erro com `pyroaring` (dependência do storage3), isso é normal. O bot funcionará mesmo assim, pois essa dependência é opcional.

### Opção 2: Instalar Apenas o Essencial

Se a instalação completa falhar, instale apenas o necessário:

```bash
pip install python-telegram-bot
pip install google-generativeai
pip install python-dotenv
pip install fastapi
pip install uvicorn
pip install apscheduler
pip install pytz
pip install httpx
pip install pdfplumber
pip install PyMuPDF
pip install Pillow
pip install python-docx
pip install openpyxl
pip install reportlab
pip install plotly
```

E para o Supabase (pode dar erro no Windows, mas tente):

```bash
pip install supabase
```

### Opção 3: Usar Ambiente Virtual (Melhor Prática)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 🐛 Erro: "Microsoft Visual C++ 14.0 or greater is required"

Este erro acontece ao tentar instalar `pyroaring` (dependência do `storage3` que é dependência do `supabase`).

### Solução 1: Instalar Build Tools (Recomendado)

1. Baixe: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instale "Desktop development with C++"
3. Reinicie o terminal
4. Execute `pip install -r requirements.txt` novamente

### Solução 2: Pular pyroaring (Temporário)

O `pyroaring` é usado apenas para otimizações no storage do Supabase. O bot funcionará sem ele.

Edite `requirements.txt` e comente a linha do supabase:

```txt
# supabase>=2.10.0  # Comentado temporariamente
```

Depois instale manualmente uma versão mais antiga:

```bash
pip install supabase==2.0.0
```

### Solução 3: Usar Supabase via REST API

Se não conseguir instalar a biblioteca, você pode usar a API REST do Supabase diretamente com `httpx` (que já está instalado).

## ✅ Verificar Instalação

Após instalar, teste:

```python
python -c "import supabase; print('✅ Supabase instalado!')"
```

Ou execute o teste de imports:

```bash
python test_imports.py
```

Deve mostrar:
```
✅ import database as db - OK
✅ bot.py usa database (Supabase) - OK
✅ ai.py usa database (Supabase) - OK
✅ jobs.py usa database (Supabase) - OK
✅ TODOS OS IMPORTS ESTÃO CORRETOS!
```

## 📝 Dependências Principais

| Biblioteca | Versão | Uso |
|------------|--------|-----|
| python-telegram-bot | >=21.0 | Bot Telegram |
| google-generativeai | >=0.8.0 | IA Gemini |
| supabase | >=2.10.0 | Banco de dados |
| fastapi | >=0.115.0 | Servidor web |
| uvicorn | >=0.30.0 | ASGI server |
| apscheduler | >=3.10.4 | Jobs agendados |
| pdfplumber | >=0.11.0 | Ler PDFs |
| python-docx | >=1.1.0 | Criar/editar Word |
| openpyxl | >=3.1.2 | Criar/editar Excel |
| plotly | >=5.24.0 | Gráficos |

## 🚀 Deploy no Railway

No Railway, as dependências são instaladas automaticamente do `requirements.txt`.

Se houver erro com `pyroaring`, adicione no `railway.toml`:

```toml
[build]
builder = "nixpacks"

[build.nixpacksConfig]
packages = ["gcc", "g++", "make"]
```

Ou use a Solução 2 acima (versão mais antiga do supabase).

## 💡 Dica

Se você só quer testar o bot localmente e não quer lidar com problemas de compilação, use SQLite temporariamente:

1. Mantenha `database_sqlite.py`
2. Nos arquivos, use `import database_sqlite as db`
3. Quando for fazer deploy no Railway, aí sim configure o Supabase

Mas lembre-se: **Supabase é a solução recomendada para produção!**
