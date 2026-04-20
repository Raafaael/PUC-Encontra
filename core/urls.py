from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("itens/", views.itens_publico, name="itens_publico"),
    path("registro/", views.registro, name="registro"),
    path("registro/verificar/", views.verificar_email, name="verificar_email"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/trocar-senha/", views.trocar_senha, name="trocar_senha"),
    path("perfil/desativar/", views.desativar_conta, name="desativar_conta"),
    path(
        "senha/resetar/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url="/senha/resetar/enviado/",
        ),
        name="password_reset",
    ),
    path(
        "senha/resetar/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "senha/resetar/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/senha/resetar/completo/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "senha/resetar/completo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    # Dashboard e Meus Registros
    path("dashboard/", views.dashboard, name="dashboard"),
    path("meus-registros/", views.meus_registros, name="meus_registros"),
    # Objetos (CRUD unificado)
    path("itens/novo/", views.objeto_criar, name="objeto_create"),
    path("itens/<int:pk>/", views.objeto_detalhe, name="objeto_detail"),
    path("itens/<int:pk>/editar/", views.objeto_editar, name="objeto_update"),
    path("itens/<int:pk>/excluir/", views.objeto_excluir, name="objeto_delete"),
    path("itens/<int:pk>/devolver/", views.objeto_marcar_devolvido, name="objeto_devolver"),
    # Solicitações de Posse
    path(
        "solicitacoes/nova/<int:objeto_id>/",
        views.solicitacao_criar,
        name="solicitacao_create",
    ),
    path("solicitacoes/<int:pk>/", views.solicitacao_detalhe, name="solicitacao_detail"),
    path(
        "solicitacoes/<int:pk>/validar/",
        views.solicitacao_avaliar,
        name="solicitacao_validar",
    ),
    # Aprovações (Admin)
    path("aprovacoes/", views.aprovacoes, name="aprovacoes"),
    path("aprovacoes/<int:pk>/", views.aprovar_item, name="aprovar_item"),
    # Categorias (Admin)
    path("categorias/", views.categoria_listar, name="categoria_list"),
    path("categorias/nova/", views.categoria_criar, name="categoria_create"),
    path(
        "categorias/<int:pk>/editar/", views.categoria_editar, name="categoria_update"
    ),
    path(
        "categorias/<int:pk>/excluir/", views.categoria_excluir, name="categoria_delete"
    ),
    # Locais (Admin)
    path("locais/", views.local_listar, name="local_list"),
    path("locais/novo/", views.local_criar, name="local_create"),
    path("locais/<int:pk>/editar/", views.local_editar, name="local_update"),
    path("locais/<int:pk>/excluir/", views.local_excluir, name="local_delete"),
    # Gerenciamento de Usuários (Admin)
    path("admin-painel/usuarios/", views.listar_usuarios_admin, name="admin_usuarios"),
    path(
        "admin-painel/usuarios/novo-admin/",
        views.criar_usuario_admin,
        name="admin_usuario_create",
    ),
    path(
        "admin-painel/usuarios/<int:pk>/editar/",
        views.editar_usuario_admin,
        name="admin_usuario_edit",
    ),
]
