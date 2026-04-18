from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("perdidos/", views.perdidos_publico, name="perdidos_publico"),
    path("encontrados/", views.encontrados_publico, name="encontrados_publico"),
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
    # Objetos Perdidos (CRUD)
    path("perdidos/novo/", views.objeto_perdido_create, name="objeto_perdido_create"),
    path(
        "perdidos/<int:pk>/", views.objeto_perdido_detail, name="objeto_perdido_detail"
    ),
    path(
        "perdidos/<int:pk>/marcar-encontrado/",
        views.objeto_perdido_mark_found,
        name="objeto_perdido_mark_found",
    ),
    path(
        "perdidos/<int:pk>/editar/",
        views.objeto_perdido_update,
        name="objeto_perdido_update",
    ),
    path(
        "perdidos/<int:pk>/excluir/",
        views.objeto_perdido_delete,
        name="objeto_perdido_delete",
    ),
    # Objetos Encontrados (CRUD)
    path(
        "encontrados/novo/",
        views.objeto_encontrado_create,
        name="objeto_encontrado_create",
    ),
    path(
        "encontrados/<int:pk>/",
        views.objeto_encontrado_detail,
        name="objeto_encontrado_detail",
    ),
    path(
        "encontrados/<int:pk>/editar/",
        views.objeto_encontrado_update,
        name="objeto_encontrado_update",
    ),
    path(
        "encontrados/<int:pk>/excluir/",
        views.objeto_encontrado_delete,
        name="objeto_encontrado_delete",
    ),
    # Solicitações de Posse
    path(
        "solicitacoes/nova/<int:encontrado_id>/",
        views.solicitacao_create,
        name="solicitacao_create",
    ),
    path("solicitacoes/<int:pk>/", views.solicitacao_detail, name="solicitacao_detail"),
    path(
        "solicitacoes/<int:pk>/validar/",
        views.solicitacao_validar,
        name="solicitacao_validar",
    ),
    # Aprovações (Admin)
    path("aprovacoes/", views.aprovacoes, name="aprovacoes"),
    path("aprovacoes/<str:tipo>/<int:pk>/", views.aprovar_item, name="aprovar_item"),
    # Categorias (Admin)
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nova/", views.categoria_create, name="categoria_create"),
    path(
        "categorias/<int:pk>/editar/", views.categoria_update, name="categoria_update"
    ),
    path(
        "categorias/<int:pk>/excluir/", views.categoria_delete, name="categoria_delete"
    ),
    # Locais (Admin)
    path("locais/", views.local_list, name="local_list"),
    path("locais/novo/", views.local_create, name="local_create"),
    path("locais/<int:pk>/editar/", views.local_update, name="local_update"),
    path("locais/<int:pk>/excluir/", views.local_delete, name="local_delete"),
    # Gerenciamento de Usuários (Admin)
    path("admin-painel/usuarios/", views.admin_usuarios, name="admin_usuarios"),
    path(
        "admin-painel/usuarios/novo-admin/",
        views.admin_usuario_create,
        name="admin_usuario_create",
    ),
    path(
        "admin-painel/usuarios/<int:pk>/editar/",
        views.admin_usuario_edit,
        name="admin_usuario_edit",
    ),
]
