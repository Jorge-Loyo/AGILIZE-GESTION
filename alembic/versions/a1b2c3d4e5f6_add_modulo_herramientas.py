"""add_modulo_herramientas

Revision ID: a1b2c3d4e5f6
Revises: c7b2d4e56f01
Create Date: 2026-06-19 17:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'c7b2d4e56f01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Insertar modulo herramientas
    conn.execute(sa.text(
        "INSERT INTO modulos (codigo, nombre, icono, orden, activo) "
        "VALUES ('herramientas', 'Herramientas de Datos', 'build', 3, true) "
        "ON CONFLICT (codigo) DO NOTHING"
    ))

    # Obtener el id del modulo
    result = conn.execute(sa.text("SELECT id FROM modulos WHERE codigo = 'herramientas'"))
    row = result.fetchone()
    if not row:
        return
    modulo_id = row[0]

    # Crear permisos
    acciones = ['ver', 'crear', 'editar', 'eliminar', 'exportar']
    for accion in acciones:
        conn.execute(sa.text(
            "INSERT INTO permisos (modulo_id, accion) VALUES (:mid, :accion) "
            "ON CONFLICT DO NOTHING"
        ), {"mid": modulo_id, "accion": accion})

    # Asignar todos los permisos nuevos al rol Administrador
    result = conn.execute(sa.text("SELECT id FROM roles WHERE nombre = 'Administrador'"))
    admin_row = result.fetchone()
    if not admin_row:
        return
    admin_id = admin_row[0]

    permisos = conn.execute(sa.text(
        "SELECT id FROM permisos WHERE modulo_id = :mid"
    ), {"mid": modulo_id})
    for (pid,) in permisos:
        conn.execute(sa.text(
            "INSERT INTO roles_permisos (rol_id, permiso_id) VALUES (:rid, :pid) "
            "ON CONFLICT DO NOTHING"
        ), {"rid": admin_id, "pid": pid})


def downgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM modulos WHERE codigo = 'herramientas'"))
    row = result.fetchone()
    if row:
        modulo_id = row[0]
        conn.execute(sa.text("DELETE FROM roles_permisos WHERE permiso_id IN (SELECT id FROM permisos WHERE modulo_id = :mid)"), {"mid": modulo_id})
        conn.execute(sa.text("DELETE FROM permisos WHERE modulo_id = :mid"), {"mid": modulo_id})
        conn.execute(sa.text("DELETE FROM modulos WHERE id = :mid"), {"mid": modulo_id})
