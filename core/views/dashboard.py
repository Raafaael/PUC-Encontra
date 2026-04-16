from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render

from ..access import get_user_tipo
from ..models import Categoria, ObjetoEncontrado, ObjetoPerdido, SolicitacaoPosse


@login_required
def dashboard(request):
    user = request.user
    tipo = get_user_tipo(user)
    context = {"tipo": tipo}

    if tipo == "usuario":
        context["meus_perdidos"] = ObjetoPerdido.objects.filter(usuario=user)[:5]
        context["meus_encontrados"] = ObjetoEncontrado.objects.filter(usuario=user)[:5]
        context["encontrados_recentes"] = ObjetoEncontrado.objects.filter(
            status="disponivel"
        )[:5]
        categorias_perdidas = ObjetoPerdido.objects.filter(
            usuario=user,
            status="aberto",
        ).values_list("categoria_id", flat=True)
        context["sugestoes"] = ObjetoEncontrado.objects.filter(
            categoria_id__in=categorias_perdidas,
            status="disponivel",
        ).exclude(usuario=user)[:5]
    else:
        context["total_perdidos"] = ObjetoPerdido.objects.count()
        context["total_encontrados"] = ObjetoEncontrado.objects.count()
        context["total_devolvidos"] = ObjetoEncontrado.objects.filter(
            status="devolvido"
        ).count()
        context["total_usuarios"] = User.objects.count()
        context["pendentes_aprovacao"] = (
            ObjetoPerdido.objects.filter(status="pendente").count()
            + ObjetoEncontrado.objects.filter(status="pendente").count()
        )
        context["solicitacoes_pendentes"] = SolicitacaoPosse.objects.filter(
            status="pendente"
        )[:10]
        context["perdidos_recentes"] = ObjetoPerdido.objects.all()[:5]
        context["encontrados_recentes"] = ObjetoEncontrado.objects.all()[:5]
        context["stats_categorias"] = Categoria.objects.annotate(
            num_perdidos=Count("objetos_perdidos"),
            num_encontrados=Count("objetos_encontrados"),
        ).order_by("-num_perdidos")[:5]

    return render(request, "core/dashboard.html", context)


@login_required
def meus_registros(request):
    user = request.user
    tipo = get_user_tipo(user)
    filtro_tipo = request.GET.get("tipo_item", "")
    filtro_status = request.GET.get("status", "")

    perdidos = ObjetoPerdido.objects.filter(usuario=user)
    encontrados = ObjetoEncontrado.objects.filter(usuario=user)

    if filtro_status:
        perdidos = perdidos.filter(status=filtro_status)
        encontrados = encontrados.filter(status=filtro_status)

    context = {
        "tipo": tipo,
        "filtro_tipo": filtro_tipo,
        "filtro_status": filtro_status,
    }

    if filtro_tipo == "perdido":
        context["perdidos"] = perdidos
    elif filtro_tipo == "encontrado":
        context["encontrados"] = encontrados
    else:
        context["perdidos"] = perdidos
        context["encontrados"] = encontrados

    return render(request, "core/meus_registros.html", context)
