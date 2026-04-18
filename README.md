# PUC Encontra - Sistema de Achados e Perdidos Inteligente

Projeto da G1 da disciplina de Programação para Web de 2026.1.

## Integrantes

- `Dante Honorato Navaza` - Matricula: `2321406`
- `Rafael Soares Estevão` - Matricula: `2320470`

## Escopo do Projeto

O **PUC Encontra** é um sistema web de achados e perdidos desenvolvido para a PUC. O sistema permite que usuários registrem objetos perdidos e encontrados, enquanto administradores validam itens e solicitações de posse.

### Funcionalidades Implementadas

- CRUD completo para objetos perdidos, objetos encontrados, categorias, locais e solicitações de posse
- Sistema de correspondência por categoria entre itens perdidos e encontrados
- Perfis de acesso para usuário e administrador
- Filtros por texto, categoria, local e status
- Upload de imagens
- Dashboard por perfil de usuário
- Fluxo de solicitação de posse com validação administrativa
- Design responsivo

### Tecnologias

- **Backend:** Python 3.12 + Django 4.2
- **Frontend:** HTML5 + CSS3
- **Banco de dados:** SQLite
- **Imagens:** Pillow

---

## Como Executar Localmente

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Raafaael/PUC-Encontra.git
cd PUC-Encontra

# 2. Crie e ative um ambiente virtual
python -m venv venv

# No Windows:
venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute as migrações
python manage.py migrate

# 5. Popule o banco com dados iniciais
python manage.py seed

# 6. Inicie o servidor
python manage.py runserver
```

O site ficará disponível em `http://localhost:8000`.

### Configuração opcional de e-mail

O projeto funciona em desenvolvimento mesmo sem `.env`.

- Sem configurar credenciais SMTP, os e-mails de verificação e recuperação de senha são exibidos no terminal/console.
- Se quiser enviar e-mails reais, crie um arquivo `.env` na raiz do projeto com:

```env
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-ou-app-password
```

Também é possível sobrescrever o backend manualmente com `EMAIL_BACKEND`.

---

## Usuário Administrador Padrão

Após executar `python manage.py seed`, um administrador é criado

| Campo | Valor |
|-------|-------|
| Username | `admin` |
| Senha | `admin123` |

---

## Navegação do Sistema

### Página Inicial

Rota: `/`

- Exibe estatísticas gerais
- Apresenta o funcionamento do sistema
- Dá acesso ao login e ao cadastro

### Cadastro

Rota: `/registro/`

- Cria contas públicas do tipo **usuário**
- Solicita nome, sobrenome, username, e-mail e senha
- Permite informar matrícula opcionalmente
- Exige telefone para contato

Administradores devem ser configurados por um administrador do sistema.

### Login

Rota: `/login/`

- Aceita username ou e-mail

### Área do Usuário

- `Dashboard` em `/dashboard/`
- Registros pessoais em `/meus-registros/`
- Consulta pública de perdidos em `/perdidos/`
- Consulta pública de encontrados em `/encontrados/`
- Perfil em `/perfil/`

### Área do Administrador

- Painel de aprovações em `/aprovacoes/`
- Categorias em `/categorias/`
- Locais em `/locais/`
- Usuários em `/admin-painel/usuarios/`

---

## O que Funciona

- [x] Cadastro e autenticação
- [x] Perfis de acesso
- [x] CRUD de objetos perdidos
- [x] CRUD de objetos encontrados
- [x] CRUD de categorias e locais
- [x] Solicitações de posse
- [x] Aprovação administrativa de itens e solicitações
- [x] Upload de imagens
- [x] Busca e filtros
- [x] Dashboard por tipo de usuário

---

## Estrutura do Projeto

```text
PUC-Encontra/
|-- manage.py
|-- requirements.txt
|-- puc_encontra/
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- core/
|   |-- admin.py
|   |-- apps.py
|   |-- access.py
|   |-- backends.py
|   |-- decorators.py
|   |-- forms/
|   |   |-- __init__.py
|   |   |-- account.py
|   |   |-- admin.py
|   |   |-- claims.py
|   |   |-- items.py
|   |   `-- shared.py
|   |-- models.py
|   |-- signals.py
|   |-- tests/
|   |-- urls.py
|   |-- views/
|   |   |-- account.py
|   |   |-- admin_views.py
|   |   |-- claims.py
|   |   |-- dashboard.py
|   |   |-- items.py
|   |   `-- public.py
|   |-- management/commands/
|   |-- migrations/
|   `-- templatetags/
|-- templates/
|   |-- base.html
|   |-- registration/
|   `-- core/
|-- static/css/
|-- media/
`-- Enunciado/
```

---
