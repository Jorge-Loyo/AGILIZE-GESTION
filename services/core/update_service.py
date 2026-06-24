import subprocess
from pathlib import Path
from core.config import BASE_DIR

REPO_URL = "https://github.com/Jorge-Loyo/AGILIZE-GESTION.git"
BRANCH = "Deploy-Ferrelum"


class UpdateService:
    def verificar_git(self) -> bool:
        """Verifica si git está disponible."""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def es_repositorio(self) -> bool:
        """Verifica si el directorio actual es un repo git."""
        return (BASE_DIR / ".git").exists()

    def inicializar_repo(self) -> str:
        """Inicializa el repo si no existe."""
        if self.es_repositorio():
            return "Repositorio ya inicializado."
        result = subprocess.run(
            ["git", "init"],
            cwd=str(BASE_DIR), capture_output=True, text=True
        )
        subprocess.run(
            ["git", "remote", "add", "origin", REPO_URL],
            cwd=str(BASE_DIR), capture_output=True, text=True
        )
        return result.stdout or "Repositorio inicializado."

    def obtener_version_actual(self) -> str:
        """Obtiene el hash del commit actual."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(BASE_DIR), capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "Sin commit"
        except Exception:
            return "Desconocida"

    def verificar_actualizaciones(self) -> dict:
        """Verifica si hay actualizaciones disponibles."""
        try:
            # Fetch
            subprocess.run(
                ["git", "fetch", "origin", BRANCH],
                cwd=str(BASE_DIR), capture_output=True, text=True
            )
            # Comparar
            result = subprocess.run(
                ["git", "log", f"HEAD..origin/{BRANCH}", "--oneline"],
                cwd=str(BASE_DIR), capture_output=True, text=True
            )
            commits = result.stdout.strip().split("\n") if result.stdout.strip() else []
            return {
                "disponible": len(commits) > 0,
                "commits": len(commits),
                "detalle": result.stdout.strip(),
            }
        except Exception as e:
            return {"disponible": False, "commits": 0, "detalle": str(e)}

    def actualizar(self) -> dict:
        """Ejecuta la actualización desde el repositorio."""
        try:
            # Stash cambios locales
            subprocess.run(
                ["git", "stash"],
                cwd=str(BASE_DIR), capture_output=True, text=True
            )
            # Pull
            result = subprocess.run(
                ["git", "pull", "origin", BRANCH],
                cwd=str(BASE_DIR), capture_output=True, text=True
            )
            if result.returncode == 0:
                return {"exito": True, "mensaje": result.stdout.strip()}
            else:
                return {"exito": False, "mensaje": result.stderr.strip()}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}


update_service = UpdateService()
