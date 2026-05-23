# Arcane - Workshop de programação web + IA

Workshop prático de dois dias focado em desenvolvimento web com Python/Django e integração de IA usando LangChain. O projeto base é o **PetCare**, um sistema veterinário com agentes inteligentes, RAG e chat em tempo real.

- [Contexto e capabilities do projeto](PETCARE.md)
- [Material didático do workshop](MATERIAL.md)

## Tecnologias

- **Python** - linguagem principal do back-end, escolhido pelo ecossistema maduro de IA (LangChain, OpenAI SDK, etc.)
- **Django** - framework web responsável por rotas, banco de dados, autenticação e templates
- **LangChain** - framework para construir aplicações com LLMs de forma estruturada e modular
- **OpenAI** - modelos de linguagem (embeddings e geração de texto)
- **Django Channels** - suporte a WebSockets para chat em tempo real

## Como executar

### 1. Criar e ativar o ambiente virtual

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\Activate
```

> Se o Windows retornar erro de permissão, execute antes:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Aplicar as migrações

```bash
python manage.py migrate
```

### 4. Criar um superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 5. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse em `http://127.0.0.1:8000/users/cadastro/`.
