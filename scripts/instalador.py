"""
Instalador grafico de Agilize Gestion.
Se compila como exe independiente para distribuir.
Instala todo lo necesario: app + PostgreSQL (servidor) o solo app (cliente).
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import shutil
import os
import sys
import socket
from pathlib import Path
import threading


class InstaladorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Agilize Gestion - Instalador")
        self.root.geometry("600x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a1a")

        self.app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.install_dir = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "AgilizeGestion")

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#D4AF37", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Agilize Gestion", font=("Segoe UI", 18, "bold"),
                 bg="#D4AF37", fg="#0f0f0f").pack(pady=15)

        self.container = tk.Frame(self.root, bg="#1a1a1a", padx=30, pady=20)
        self.container.pack(fill="both", expand=True)

        self._show_config_page()

    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _show_config_page(self):
        self._clear_container()

        tk.Label(self.container, text="Configuracion de Conexion",
                 font=("Segoe UI", 14, "bold"), bg="#1a1a1a", fg="#F8F9FA").pack(anchor="w")
        tk.Label(self.container, text="Configura la conexion a la base de datos PostgreSQL.",
                 font=("Segoe UI", 9), bg="#1a1a1a", fg="#888888").pack(anchor="w", pady=(2, 15))

        form = tk.Frame(self.container, bg="#1a1a1a")
        form.pack(fill="x")

        # Tipo de instalacion
        tk.Label(form, text="Tipo de instalacion:", bg="#1a1a1a", fg="#F8F9FA",
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.var_tipo = tk.StringVar(value="servidor")
        tipo_frame = tk.Frame(form, bg="#1a1a1a")
        tipo_frame.grid(row=0, column=1, sticky="w", pady=5)
        tk.Radiobutton(tipo_frame, text="Servidor (BD incluida)", variable=self.var_tipo,
                       value="servidor", bg="#1a1a1a", fg="#F8F9FA", selectcolor="#2a2a2a",
                       command=self._on_tipo_change).pack(side="left")
        tk.Radiobutton(tipo_frame, text="Cliente (conectar a servidor)", variable=self.var_tipo,
                       value="cliente", bg="#1a1a1a", fg="#F8F9FA", selectcolor="#2a2a2a",
                       command=self._on_tipo_change).pack(side="left", padx=10)

        # Host
        tk.Label(form, text="Host:", bg="#1a1a1a", fg="#F8F9FA",
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_host = tk.Entry(form, width=30, font=("Segoe UI", 10))
        self.entry_host.insert(0, "localhost")
        self.entry_host.grid(row=1, column=1, sticky="w", pady=5)

        # Puerto
        tk.Label(form, text="Puerto:", bg="#1a1a1a", fg="#F8F9FA",
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_port = tk.Entry(form, width=10, font=("Segoe UI", 10))
        self.entry_port.insert(0, "5432")
        self.entry_port.grid(row=2, column=1, sticky="w", pady=5)

        # Usuario
        tk.Label(form, text="Usuario BD:", bg="#1a1a1a", fg="#F8F9FA",
                 font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_user = tk.Entry(form, width=20, font=("Segoe UI", 10))
        self.entry_user.insert(0, "postgres")
        self.entry_user.grid(row=3, column=1, sticky="w", pady=5)

        # Password
        tk.Label(form, text="Contrasena BD:", bg="#1a1a1a", fg="#F8F9FA",
                 font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", pady=5)
        self.entry_pass = tk.Entry(form, width=20, show="*", font=("Segoe UI", 10))
        self.entry_pass.insert(0, "agilize2025")
        self.entry_pass.grid(row=4, column=1, sticky="w", pady=5)

        # Directorio
        tk.Label(form, text="Instalar en:", bg="#1a1a1a", fg="#F8F9FA",
                 font=("Segoe UI", 10)).grid(row=5, column=0, sticky="w", pady=5)
        dir_frame = tk.Frame(form, bg="#1a1a1a")
        dir_frame.grid(row=5, column=1, sticky="w", pady=5)
        self.entry_dir = tk.Entry(dir_frame, width=25, font=("Segoe UI", 9))
        self.entry_dir.insert(0, self.install_dir)
        self.entry_dir.pack(side="left")
        tk.Button(dir_frame, text="...", command=self._browse_dir, width=3).pack(side="left", padx=5)

        # Info
        info_text = (
            "Servidor: instala PostgreSQL + App (usar en la PC principal)\n"
            "Cliente: solo instala la App (se conecta al servidor por red)"
        )
        tk.Label(self.container, text=info_text, font=("Segoe UI", 8),
                 bg="#1a1a1a", fg="#666666", justify="left").pack(anchor="w", pady=(10, 0))

        # Boton instalar
        btn_frame = tk.Frame(self.container, bg="#1a1a1a")
        btn_frame.pack(fill="x", pady=15)
        tk.Button(btn_frame, text="Instalar", font=("Segoe UI", 12, "bold"),
                  bg="#D4AF37", fg="#0f0f0f", width=20, height=2,
                  command=self._start_install).pack()

    def _on_tipo_change(self):
        if self.var_tipo.get() == "cliente":
            self.entry_host.delete(0, "end")
            self.entry_host.insert(0, "192.168.1.100")
        else:
            self.entry_host.delete(0, "end")
            self.entry_host.insert(0, "localhost")

    def _browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.entry_dir.delete(0, "end")
            self.entry_dir.insert(0, d)

    def _start_install(self):
        self.config = {
            "tipo": self.var_tipo.get(),
            "host": self.entry_host.get().strip(),
            "port": self.entry_port.get().strip(),
            "user": self.entry_user.get().strip(),
            "password": self.entry_pass.get() or "agilize2025",
            "install_dir": self.entry_dir.get().strip(),
        }
        self._show_progress_page()
        threading.Thread(target=self._do_install, daemon=True).start()

    def _show_progress_page(self):
        self._clear_container()

        tk.Label(self.container, text="Instalando...",
                 font=("Segoe UI", 14, "bold"), bg="#1a1a1a", fg="#F8F9FA").pack(anchor="w")

        self.progress = ttk.Progressbar(self.container, length=500, mode="determinate")
        self.progress.pack(pady=20)

        self.lbl_status = tk.Label(self.container, text="Iniciando...",
                                   font=("Segoe UI", 10), bg="#1a1a1a", fg="#888888")
        self.lbl_status.pack(anchor="w")

        self.txt_log = tk.Text(self.container, height=12, bg="#0f0f0f", fg="#F8F9FA",
                               font=("Consolas", 9), state="disabled")
        self.txt_log.pack(fill="both", expand=True, pady=10)

    def _log(self, msg):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
        self.lbl_status.configure(text=msg)
        self.root.update_idletasks()

    def _set_progress(self, value):
        self.progress["value"] = value
        self.root.update_idletasks()

    def _do_install(self):
        try:
            install_dir = self.config["install_dir"]

            # === PASO 1: Copiar archivos ===
            self._log("[1/5] Copiando archivos de la aplicacion...")
            self._set_progress(5)
            os.makedirs(install_dir, exist_ok=True)

            src = os.path.join(self.app_dir, "AgilizeGestion")
            if os.path.exists(src):
                shutil.copytree(src, install_dir, dirs_exist_ok=True)
            else:
                for item in os.listdir(self.app_dir):
                    if item.lower() in ("instalador.exe",):
                        continue
                    s = os.path.join(self.app_dir, item)
                    d = os.path.join(install_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
            self._log("[OK] Archivos copiados")
            self._set_progress(15)

            # === PASO 2: PostgreSQL (servidor) o validar conexion (cliente) ===
            if self.config["tipo"] == "servidor":
                self._log("[2/5] Instalando PostgreSQL...")
                self._set_progress(20)
                pg_ok = self._setup_server_postgres(install_dir)
                if not pg_ok:
                    return
                self._set_progress(70)
            else:
                self._log("[2/5] Verificando conexion al servidor...")
                self._set_progress(20)
                self._validate_client_connection()
                self._set_progress(40)

            # === PASO 3: Crear .env con datos definitivos ===
            self._log("[3/5] Creando configuracion (.env)...")
            self._write_env(install_dir)
            self._log("[OK] Configuracion guardada")
            self._set_progress(80)

            # === PASO 4: Migraciones ===
            self._log("[4/5] Las migraciones se aplicaran al iniciar la app")
            self._set_progress(90)

            # === PASO 5: Acceso directo ===
            self._log("[5/5] Creando acceso directo...")
            self._create_shortcut(install_dir)
            self._set_progress(100)

            # Resultado
            self._log("")
            self._log("=" * 45)
            self._log("  INSTALACION COMPLETADA EXITOSAMENTE!")
            self._log("=" * 45)
            self._log(f"  Ubicacion: {install_dir}")
            self._log(f"  BD: {self.config['host']}:{self.config['port']}")
            self._log("  Usuario app: master / master2025")

            messagebox.showinfo(
                "Instalacion Completada",
                f"Agilize Gestion se instalo correctamente.\n\n"
                f"Ubicacion: {install_dir}\n"
                f"Base de datos: {self.config['host']}:{self.config['port']}\n\n"
                f"Usuario: master\n"
                f"Contrasena: master2025\n\n"
                f"Ejecuta desde el acceso directo en el escritorio."
            )

        except Exception as e:
            self._log(f"\n[ERROR FATAL] {str(e)}")
            messagebox.showerror("Error", f"Error durante la instalacion:\n{str(e)}")

    def _setup_server_postgres(self, install_dir):
        """Configura PostgreSQL para modo servidor. Retorna True si exito."""
        # Estrategia 1: usar setup_postgres.py portable
        try:
            scripts_dir = os.path.join(install_dir, "scripts")
            setup_script = os.path.join(scripts_dir, "setup_postgres.py")

            if os.path.exists(setup_script):
                sys.path.insert(0, scripts_dir)
                from setup_postgres import setup_postgres, create_startup_task
                pg_info = setup_postgres(install_dir, self.config["password"], self._log)
                self.config["host"] = pg_info["host"]
                self.config["port"] = pg_info["port"]
                self.config["user"] = pg_info["user"]
                self.config["password"] = pg_info["password"]
                create_startup_task(install_dir)
                self._log("[OK] PostgreSQL instalado y configurado")
                return True
        except Exception as e:
            self._log(f"[WARN] PostgreSQL portable: {e}")

        # Estrategia 2: buscar PostgreSQL ya instalado en el sistema
        self._log("[INFO] Buscando PostgreSQL instalado en el sistema...")
        pg_path = self._find_system_postgres()
        if pg_path:
            self._log(f"[OK] Encontrado: {pg_path}")
            if self._test_port(self.config["host"], int(self.config["port"])):
                self._log("[OK] PostgreSQL ya esta corriendo")
                self._create_db_if_needed()
                return True
            else:
                self._log("[INFO] Intentando iniciar servicio...")
                self._try_start_pg_service()
                if self._test_port(self.config["host"], int(self.config["port"])):
                    self._log("[OK] PostgreSQL iniciado")
                    self._create_db_if_needed()
                    return True

        # Estrategia 3: fallo total
        self._log("")
        self._log("[ERROR] No se pudo instalar ni encontrar PostgreSQL.")
        self._log("Opciones:")
        self._log("  1. Verifica tu conexion a internet y reintenta")
        self._log("  2. Instala PostgreSQL manualmente desde:")
        self._log("     https://www.postgresql.org/download/windows/")
        self._log("  3. Ejecuta este instalador nuevamente")
        messagebox.showwarning(
            "PostgreSQL no disponible",
            "No se pudo instalar PostgreSQL automaticamente.\n\n"
            "Opciones:\n"
            "1. Verifica internet y reintenta\n"
            "2. Instala manualmente desde:\n"
            "   postgresql.org/download/windows\n"
            "3. Ejecuta este instalador de nuevo\n\n"
            "La aplicacion necesita PostgreSQL para funcionar."
        )
        return False

    def _validate_client_connection(self):
        """Valida conexion en modo cliente, advierte si no conecta."""
        if self._test_port(self.config["host"], int(self.config["port"])):
            self._log(f"[OK] Conexion exitosa a {self.config['host']}:{self.config['port']}")
        else:
            self._log(f"[WARN] No se pudo conectar a {self.config['host']}:{self.config['port']}")
            self._log("Posibles causas:")
            self._log("  - La PC servidor no esta encendida")
            self._log("  - PostgreSQL no esta corriendo en el servidor")
            self._log("  - Firewall bloquea el puerto 5432")
            self._log("  - La IP del servidor es incorrecta")
            self._log("")
            self._log("La app se instalara, pero corrige la conexion antes de usarla.")
            messagebox.showwarning(
                "Sin conexion al servidor",
                f"No se pudo conectar a {self.config['host']}:{self.config['port']}\n\n"
                "La app se instalara igual.\n"
                "Antes de usarla, verifica que:\n"
                "1. El servidor este encendido\n"
                "2. PostgreSQL este corriendo\n"
                "3. El firewall permita puerto 5432\n"
                "4. La IP sea correcta\n\n"
                "Podes editar el archivo .env para corregir."
            )

    def _write_env(self, install_dir):
        """Escribe el .env con la configuracion definitiva."""
        env_content = (
            f"# Base de Datos\n"
            f"DB_HOST={self.config['host']}\n"
            f"DB_PORT={self.config['port']}\n"
            f"DB_NAME=agilize_gestion\n"
            f"DB_USER={self.config['user']}\n"
            f"DB_PASSWORD={self.config['password']}\n"
            f"\n"
            f"# Aplicacion\n"
            f"APP_NAME=Agilize Gestion\n"
            f"APP_VERSION=1.0.0\n"
            f"SESSION_TIMEOUT_MINUTES=30\n"
            f"\n"
            f"# Seguridad\n"
            f"SECRET_KEY=agilize_{os.urandom(8).hex()}\n"
            f"BCRYPT_ROUNDS=12\n"
        )
        with open(os.path.join(install_dir, ".env"), "w") as f:
            f.write(env_content)

    def _find_system_postgres(self):
        """Busca PostgreSQL instalado en el sistema."""
        for ver in ["18", "17", "16", "15", "14"]:
            path = f"C:\\Program Files\\PostgreSQL\\{ver}\\bin\\psql.exe"
            if os.path.exists(path):
                return path
        result = subprocess.run('where psql', shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
        return None

    def _try_start_pg_service(self):
        """Intenta iniciar el servicio de PostgreSQL del sistema."""
        import time
        for ver in ["18", "17", "16", "15", "14"]:
            subprocess.run(
                f'net start postgresql-x64-{ver}', shell=True, capture_output=True
            )
        time.sleep(3)

    def _test_port(self, host, port):
        """Prueba conexion TCP a un puerto."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _create_db_if_needed(self):
        """Crea la BD si no existe."""
        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config["password"]

            # Buscar psql
            psql = "psql"
            for ver in ["18", "17", "16", "15", "14"]:
                p = f"C:\\Program Files\\PostgreSQL\\{ver}\\bin\\psql.exe"
                if os.path.exists(p):
                    psql = p
                    break

            result = subprocess.run(
                [psql, "-U", self.config["user"], "-h", self.config["host"],
                 "-p", self.config["port"], "-tc",
                 "SELECT 1 FROM pg_database WHERE datname='agilize_gestion'"],
                capture_output=True, text=True, env=env
            )

            if "1" not in result.stdout:
                self._log("[INFO] Creando base de datos agilize_gestion...")
                subprocess.run(
                    [psql, "-U", self.config["user"], "-h", self.config["host"],
                     "-p", self.config["port"], "-c",
                     "CREATE DATABASE agilize_gestion;"],
                    capture_output=True, text=True, env=env
                )
                self._log("[OK] Base de datos creada")
            else:
                self._log("[OK] Base de datos ya existe")
        except Exception as e:
            self._log(f"[WARN] No se pudo verificar/crear BD: {e}")

    def _create_shortcut(self, install_dir):
        """Crea acceso directo en el escritorio."""
        try:
            vbs = (
                'Set WshShell = WScript.CreateObject("WScript.Shell")\n'
                'strDesktop = WshShell.SpecialFolders("Desktop")\n'
                f'Set oShortcut = WshShell.CreateShortcut(strDesktop & "\\Agilize Gestion.lnk")\n'
                f'oShortcut.TargetPath = "{install_dir}\\AgilizeGestion.exe"\n'
                f'oShortcut.WorkingDirectory = "{install_dir}"\n'
                'oShortcut.WindowStyle = 1\n'
                'oShortcut.Description = "Agilize Gestion"\n'
                'oShortcut.Save\n'
            )
            vbs_path = os.path.join(install_dir, "_shortcut.vbs")
            with open(vbs_path, "w") as f:
                f.write(vbs)
            subprocess.run(["cscript", "//nologo", vbs_path], capture_output=True)
            os.remove(vbs_path)
            self._log("[OK] Acceso directo creado en el escritorio")
        except Exception as e:
            self._log(f"[WARN] No se pudo crear acceso directo: {e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = InstaladorApp()
    app.run()
