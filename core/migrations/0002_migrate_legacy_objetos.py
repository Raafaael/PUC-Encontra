from django.db import migrations


CURRENT_STATUSES = {"pendente", "ativo", "reivindicado", "devolvido", "encerrado"}
LEGACY_STATUS_MAP = {
    "aberto": "ativo",
    "disponivel": "ativo",
}


def normalize_status(status):
    if status in LEGACY_STATUS_MAP:
        return LEGACY_STATUS_MAP[status]
    if status in CURRENT_STATUSES:
        return status
    return "ativo"


def table_columns(cursor, table_name):
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    return {row[1] for row in cursor.fetchall()}


def migrate_legacy_tables(apps, schema_editor):
    connection = schema_editor.connection
    table_names = set(connection.introspection.table_names())

    Objeto = apps.get_model("core", "Objeto")
    SolicitacaoPosse = apps.get_model("core", "SolicitacaoPosse")

    legacy_perdidos = "core_objetoperdido"
    legacy_encontrados = "core_objetoencontrado"
    legacy_solicitacoes = "core_solicitacaoposse"
    current_objetos = "core_objeto"

    legacy_mapping = {
        "perdido": {},
        "encontrado": {},
    }

    if current_objetos not in table_names:
        schema_editor.create_model(Objeto)
        table_names.add(current_objetos)

    with connection.cursor() as cursor:
        if legacy_perdidos in table_names:
            cursor.execute(
                """
                SELECT
                    id,
                    usuario_id,
                    titulo,
                    descricao,
                    categoria_id,
                    local_perdido_id,
                    data_perda,
                    data_registro,
                    data_atualizacao,
                    status,
                    imagem
                FROM core_objetoperdido
                ORDER BY id
                """
            )
            for (
                legacy_id,
                usuario_id,
                titulo,
                descricao,
                categoria_id,
                local_id,
                data_ocorrencia,
                data_registro,
                data_atualizacao,
                status,
                imagem,
            ) in cursor.fetchall():
                cursor.execute(
                    """
                    INSERT INTO core_objeto (
                        tipo,
                        usuario_id,
                        titulo,
                        descricao,
                        categoria_id,
                        local_id,
                        data_ocorrencia,
                        data_registro,
                        data_atualizacao,
                        status,
                        imagem
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        "perdido",
                        usuario_id,
                        titulo,
                        descricao,
                        categoria_id,
                        local_id,
                        data_ocorrencia,
                        data_registro,
                        data_atualizacao,
                        normalize_status(status),
                        imagem,
                    ],
                )
                legacy_mapping["perdido"][legacy_id] = cursor.lastrowid

        if legacy_encontrados in table_names:
            cursor.execute(
                """
                SELECT
                    id,
                    usuario_id,
                    titulo,
                    descricao,
                    categoria_id,
                    local_encontrado_id,
                    data_encontrado,
                    data_registro,
                    data_atualizacao,
                    status,
                    imagem
                FROM core_objetoencontrado
                ORDER BY id
                """
            )
            for (
                legacy_id,
                usuario_id,
                titulo,
                descricao,
                categoria_id,
                local_id,
                data_ocorrencia,
                data_registro,
                data_atualizacao,
                status,
                imagem,
            ) in cursor.fetchall():
                cursor.execute(
                    """
                    INSERT INTO core_objeto (
                        tipo,
                        usuario_id,
                        titulo,
                        descricao,
                        categoria_id,
                        local_id,
                        data_ocorrencia,
                        data_registro,
                        data_atualizacao,
                        status,
                        imagem
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        "encontrado",
                        usuario_id,
                        titulo,
                        descricao,
                        categoria_id,
                        local_id,
                        data_ocorrencia,
                        data_registro,
                        data_atualizacao,
                        normalize_status(status),
                        imagem,
                    ],
                )
                legacy_mapping["encontrado"][legacy_id] = cursor.lastrowid

        if legacy_solicitacoes in table_names:
            columns = table_columns(cursor, legacy_solicitacoes)
            if "objeto_id" not in columns:
                backup_table = "core_solicitacaoposse_legacy"
                cursor.execute(
                    f'ALTER TABLE "{legacy_solicitacoes}" RENAME TO "{backup_table}"'
                )
                table_names.remove(legacy_solicitacoes)
                table_names.add(backup_table)

                schema_editor.create_model(SolicitacaoPosse)
                table_names.add(legacy_solicitacoes)

                cursor.execute(
                    """
                    SELECT
                        id,
                        solicitante_id,
                        objeto_encontrado_id,
                        objeto_perdido_id,
                        descricao_comprovacao,
                        data_solicitacao,
                        status,
                        resposta_admin,
                        data_resposta
                    FROM core_solicitacaoposse_legacy
                    ORDER BY id
                    """
                )
                for (
                    legacy_id,
                    solicitante_id,
                    legacy_encontrado_id,
                    legacy_perdido_id,
                    descricao_comprovacao,
                    data_solicitacao,
                    status,
                    resposta_admin,
                    data_resposta,
                ) in cursor.fetchall():
                    objeto_id = legacy_mapping["encontrado"].get(legacy_encontrado_id)
                    objeto_perdido_id = legacy_mapping["perdido"].get(legacy_perdido_id)

                    if objeto_id is None:
                        continue

                    cursor.execute(
                        """
                        INSERT INTO core_solicitacaoposse (
                            id,
                            solicitante_id,
                            objeto_id,
                            objeto_perdido_id,
                            descricao_comprovacao,
                            data_solicitacao,
                            status,
                            resposta_admin,
                            data_resposta
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            legacy_id,
                            solicitante_id,
                            objeto_id,
                            objeto_perdido_id,
                            descricao_comprovacao,
                            data_solicitacao,
                            status,
                            resposta_admin,
                            data_resposta,
                        ],
                    )

                cursor.execute('DROP TABLE "core_solicitacaoposse_legacy"')
                table_names.remove(backup_table)
        else:
            schema_editor.create_model(SolicitacaoPosse)
            table_names.add(legacy_solicitacoes)

        if legacy_encontrados in table_names:
            cursor.execute('DROP TABLE "core_objetoencontrado"')
            table_names.remove(legacy_encontrados)

        if legacy_perdidos in table_names:
            cursor.execute('DROP TABLE "core_objetoperdido"')
            table_names.remove(legacy_perdidos)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_legacy_tables, migrations.RunPython.noop),
    ]
