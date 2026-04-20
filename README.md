# PUC Encontra - Sistema de Achados e Perdidos Inteligente

Projeto da G1 da disciplina de Programação para Web de 2026.1.

LINK: https://puc-encontra.vercel.app/

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
- **Banco de dados:** SQLite no desenvolvimento e PostgreSQL na produção
- **Imagens:** Pillow no desenvolvimento e Cloudinary na produção

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

O arquivo `.env` é opcional no desenvolvimento local.

### Configuração opcional de e-mail

O projeto funciona em desenvolvimento mesmo sem `.env`.

### **Para testar o envio de email crie sua propria senha de app em um email pelo gmail.**

- Sem configurar `EMAIL_BACKEND` nem credenciais SMTP, os e-mails de verificação e recuperação de senha são exibidos no terminal/console.
- Se você definir `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` no `.env`, o ambiente de desenvolvimento passa a usar SMTP e tenta enviar e-mails reais.
- Também é possível forçar outro backend via `EMAIL_BACKEND`.

```env
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-ou-app-password
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### Ambientes de settings

- Desenvolvimento local: `puc_encontra.settings.development`
- Produção no vercel: `puc_encontra.settings.production`

O `manage.py` usa desenvolvimento por padrão. Em produção, configure `DJANGO_SETTINGS_MODULE=puc_encontra.settings.production`.

### Deploy no vercel

O projeto usa `puc_encontra.settings.production` em produção e a Vercel já consegue detectar Django automaticamente. Este repositório não precisa de `vercel.json` para o fluxo básico atual.

Variáveis necessárias em produção:

```env
DJANGO_SETTINGS_MODULE=puc_encontra.settings.production
DJANGO_SECRET_KEY=gere-uma-chave-segura
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
DJANGO_ALLOWED_HOSTS=seu-app.up.vercel.app,seu-dominio.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://seu-app.up.vercel.app,https://seu-dominio.com
CLOUD_NAME=seu-cloudinary-cloud-name
CLOUD_API_KEY=sua-cloudinary-api-key
CLOUD_API_SECRET=sua-cloudinary-api-secret
```

Variáveis opcionais para envio real de e-mails em produção:

```env
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-ou-app-password
```

Observações de deploy:

- Em produção, os uploads de mídia usam Cloudinary, não disco local.
- `DATABASE_URL` deve apontar para um PostgreSQL acessível pela Vercel.
- As migrações do Django precisam ser executadas contra o banco de produção antes ou durante o processo de publicação.
- Não há configuração de `DJANGO_MEDIA_ROOT` no projeto atual.

---

## Usuário Administrador Padrão

Após executar `python manage.py seed`, um administrador é criado

| Campo    | Valor      |
| -------- | ---------- |
| Username | `admin`    |
| Senha    | `admin123` |

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
- Consulta pública de itens em `/itens/`
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
