"""
Script para poblar la base de datos con datos iniciales.
Ejecutar una vez después de crear las tablas.
"""
from core.database import get_db, engine
from core.auth import hash_password
from models.base import Base
from models.rol import Rol
from models.usuario import Usuario
from models.permiso import Modulo, Permiso, RolPermiso

ACCIONES = ["ver", "crear", "editar", "eliminar", "exportar"]

MODULOS_INICIALES = [
    {"codigo": "empleados", "nombre": "Gestión de Empleados", "icono": "people", "orden": 1},
    {"codigo": "nomina", "nombre": "Nómina y Liquidaciones", "icono": "payments", "orden": 2},
    {"codigo": "admin", "nombre": "Administración del Sistema", "icono": "settings", "orden": 99},
]

ROLES_INICIALES = [
    {"nombre": "Administrador", "descripcion": "Acceso total al sistema"},
    {"nombre": "RRHH", "descripcion": "Gestión de empleados y nómina"},
    {"nombre": "Consulta", "descripcion": "Solo lectura"},
]


def seed():
    # Crear tablas
    Base.metadata.create_all(engine)

    with get_db() as db:
        # Roles
        roles = {}
        for r in ROLES_INICIALES:
            rol = Rol(**r)
            db.add(rol)
            db.flush()
            roles[rol.nombre] = rol

        # Módulos y permisos
        todos_los_permisos = []
        for m in MODULOS_INICIALES:
            modulo = Modulo(**m)
            db.add(modulo)
            db.flush()
            for accion in ACCIONES:
                permiso = Permiso(modulo_id=modulo.id, accion=accion)
                db.add(permiso)
                db.flush()
                todos_los_permisos.append(permiso)

        # Asignar TODOS los permisos al Administrador
        for permiso in todos_los_permisos:
            db.add(RolPermiso(rol_id=roles["Administrador"].id, permiso_id=permiso.id))

        # Usuario admin por defecto
        admin = Usuario(
            username="admin",
            password_hash=hash_password("admin123"),
            nombre_completo="Administrador del Sistema",
            email="admin@empresa.com",
            rol_id=roles["Administrador"].id,
        )
        db.add(admin)

    print("[OK] Seed completado: roles, modulos, permisos y usuario admin creados.")
    print("     Usuario: admin / Password: admin123")


if __name__ == "__main__":
    seed()
