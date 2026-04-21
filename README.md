# PUC Encontra - Sistema de Achados e Perdidos

Projeto da G1 da disciplina de Programação para Web de 2026.1.

**Link:** https://puc-encontra.vercel.app/

## Integrantes

- `Dante Honorato Navaza` - Matrícula: `2321406`
- `Rafael Soares Estevão` - Matrícula: `2320470`

---

## Escopo do Projeto

O **PUC Encontra** é um sistema web de achados e perdidos desenvolvido para a comunidade da PUC. Usuários podem registrar objetos perdidos ou encontrados, visualizar itens de outros usuários e entrar em contato diretamente com quem registrou. Administradores aprovam novos registros, avaliam edições enviadas por usuários e podem marcar itens como devolvidos.

### Funcionalidades

- Cadastro com verificação de e-mail e validação de telefone
- CRUD completo de itens (perdidos e encontrados), categorias e locais
- Gerenciamento administrativo de usuários (listagem, criação de administradores, edição e ativação/desativação)
- Fluxo de aprovação administrativa para novos itens e edições
- Exibição de contato (e-mail e telefone) para usuários logados
- Filtros por tipo (Perdidos / Encontrados / Devolvidos), categoria, local e busca por texto
- Upload de imagens
- Correspondências automáticas por categoria entre itens perdidos e encontrados
- Dashboard personalizado por perfil (usuário e administrador)
- Recuperação de senha por e-mail

### Tecnologias

- **Backend:** Python 3.12 + Django 4.2
- **Frontend:** HTML5 + CSS3
- **Banco de dados:** SQLite no desenvolvimento e PostgreSQL na produção
- **Imagens:** Pillow no desenvolvimento e Cloudinary na produção

---

## Como Executar Localmente

### Pré-requisitos

- Python 3.12 ou superior

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Raafaael/PUC-Encontra.git
cd PUC-Encontra

# 2. Crie e ative um ambiente virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
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

### Configuração de E-mail

O projeto funciona em desenvolvimento mesmo sem `.env`.

> **Nota:** Para testar o envio de e-mail localmente, crie uma senha de app no Gmail.

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
DJANGO_ALLOWED_HOSTS=seu-app.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://seu-app.vercel.app
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

---

## Usuário Administrador Padrão

Após executar `python manage.py seed`, um administrador é criado.

| Campo    | Valor      |
| -------- | ---------- |
| Username | `admin`    |
| Senha    | `admin123` |

---

## Manual do Usuário

### Área do Usuário

#### Página Inicial (`/`)

Exibe estatísticas gerais do sistema (total de perdidos, encontrados e devolvidos) e links para login e cadastro.

#### Cadastro (`/registro/`)

Crie uma conta informando nome, sobrenome, username, e-mail, telefone e senha. Um código de verificação será enviado para o e-mail informado. Administradores só podem ser criados por outro administrador.

#### Login (`/login/`)

Aceita username ou e-mail. Caso esqueça a senha, use o link "Esqueci minha senha" para receber instruções de redefinição por e-mail.

#### Itens Públicos (`/itens/`)

Lista todos os itens públicos publicados no sistema, incluindo itens ativos e devolvidos. Use os filtros de tag (Todos / Perdidos / Encontrados / Devolvidos) ou a barra de busca para encontrar um item específico. Clique em um item para ver os detalhes e o contato de quem registrou (disponível apenas para usuários logados).

#### Registrar um Item (`/itens/novo/`)

Escolha se o item é **Perdido** ou **Encontrado**, preencha título, descrição, categoria, local e data. A data não pode ser futura nem anterior a 1 ano. O item ficará pendente até aprovação do administrador (exceto se criado por um admin).

#### Meus Registros (`/meus-registros/`)

Visualize e gerencie seus itens. É possível editar ou excluir enquanto o item não estiver marcado como devolvido. Edições feitas por usuários comuns são enviadas para aprovação do administrador antes de serem aplicadas.

#### Perfil (`/perfil/`)

Atualize nome, e-mail, matrícula e telefone.

### Área do Administrador

#### Dashboard (`/dashboard/`)

Exibe estatísticas gerais, quantidade de itens pendentes de aprovação e registros recentes.

#### Aprovações (`/aprovacoes/`)

Avalia itens recém-registrados (aprovar publica o item; rejeitar o remove) e solicitações de edição enviadas por usuários (comparação lado a lado da versão atual e da versão proposta).

#### Categorias (`/categorias/`) e Locais (`/locais/`)

CRUD completo de categorias e locais disponíveis no sistema.

#### Usuários (`/admin-painel/usuarios/`)

Visualize usuários, crie novos administradores e edite dados, tipo e status de ativação das contas. Apenas administradores têm acesso.

---

## O que Funcionou

- [x] Cadastro com verificação de e-mail
- [x] Autenticação por username ou e-mail
- [x] Recuperação de senha por e-mail
- [x] CRUD de itens (perdidos e encontrados)
- [x] CRUD de categorias e locais
- [x] CRUD de usuários (painel admin, com o delete sendo a desativacao de ususarios)
- [x] Fluxo de aprovação de novos itens
- [x] Fluxo de aprovação de edições com comparação visual
- [x] Exibição de contato para usuários logados
- [x] Filtros por tipo, categoria, local e busca
- [x] Upload de imagens
- [x] Correspondências automáticas por categoria
- [x] Dashboard personalizado por perfil

## O que Não Funcionou

- Nenhuma falha encontrada nas funcionalidades que decidimos desenvolver.
