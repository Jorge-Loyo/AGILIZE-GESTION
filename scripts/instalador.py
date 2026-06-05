"""
Instalador grafico de Agilize Gestion.
Se compila como exe independiente para distribuir.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import shutil
import os
import sys
from pathlib import Path
import threading


class InstaladorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Agilize Gestion - Instalador")
        self.root.geometry("550x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a1a")

        self.app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.install_dir = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "AgilizeGestion")

        self._step = 0
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#D4AF37", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Agilize Gestion", font=("Segoe UI", 18, "bold"),
                 bg="#D4AF37", fg="#0f0f0f").pack(pady=15)

        # Container
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
        tk.Radiobutton(tipo_frame, text="Servidor (BD local)", variable=self.var_tipo,
                       value="servidor", bg="#1a1a1a", fg="#F8F9FA", selectcolor="#2a2a2a",
                       command=self._on_tipo_change).pack(side="left")
        tk.Radiobutton(tipo_frame, text="Cliente (BD remota)", variable=self.var_tipo,
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

        # Boton instalar
        btn_frame = tk.Frame(self.container, bg="#1a1a1a")
        btn_frame.pack(fill="x", pady=20)
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
        password = self.entry_pass.get()
        if not password:
            messagebox.showwarning("Error", "Ingresa la contrasena de PostgreSQL.")
            return

        self.config = {
            "tipo": self.var_tipo.get(),
            "host": self.entry_host.get(),
            "port": self.entry_port.get(),
            "user": self.entry_user.get(),
            "password": password,
            "install_dir": self.entry_dir.get(),
        }
        self._show_progress_page()
        threading.Thread(target=self._do_install, daemon=True).start()

    def _show_progress_page(self):
        self._clear_container()

        tk.Label(self.container, text="Instalando...",
                 font=("Segoe UI", 14, "bold"), bg="#1a1a1a", fg="#F8F9FA").pack(anchor="w")

        self.progress = ttk.Progressbar(self.container, length=450, mode="determinate")
        self.progress.pack(pady=20)

        self.lbl_status = tk.Label(self.container, text="Iniciando...",
                                   font=("Segoe UI", 10), bg="#1a1a1a", fg="#888888")
        self.lbl_status.pack(anchor="w")

        self.txt_log = tk.Text(self.container, height=10, bg="#0f0f0f", fg="#F8F9FA",
                               font=("Consolas", 9), state="disabled")
        self.txt_log.pack(fill="both", expand=True, pady=10)

    def _log(self, msg):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
        self.lbl_status.configure(text=msg)
        self.root.update_idletasks()

    def _do_install(self):
        try:
            install_dir = self.config["install_dir"]
            total_steps = 5 if self.config["tipo"] == "servidor" else 3

            # Paso 1: Copiar archivos
            self._log("[1] Copiando archivos...")
            self.progress["value"] = 10
            os.makedirs(install_dir, exist_ok=True)
            # Copiar el contenido de dist/AgilizeGestion
            src = os.path.join(self.app_dir, "AgilizeGestion")
            if os.path.exists(src):
                shutil.copytree(src, install_dir, dirs_exist_ok=True)
            else:
                # Si se ejecuta desde el mismo directorio del build
                for item in os.listdir(self.app_dir):
                    if item in ("instalador.exe", "Instalador.exe"):
                        continue
                    s = os.path.join(self.app_dir, item)
                    d = os.path.join(install_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
            self._log("[OK] Archivos copiados")
            self.progress["value"] = 30

            # Paso 2: Crear .env
            self._log("[2] Configurando conexion...")
            env_content = f"""# Base de Datos
DB_HOST={self.config['host']}
DB_PORT={self.config['port']}
DB_NAME=agilize_gestion
DB_USER={self.config['user']}
DB_PASSWORD={self.config['password']}

# Aplicacion
APP_NAME=Agilize Gestion
APP_VERSION=1.0.0
SESSION_TIMEOUT_MINUTES=30

# Seguridad
SECRET_KEY=agilize_{os.urandom(8).hex()}
BCRYPT_ROUNDS=12
"""
            with open(os.path.join(install_dir, ".env"), "w") as f:
                f.write(env_content)
            self._log("[OK] Configuracion creada")
            self.progress["value"] = 50

            if self.config["tipo"] == "servidor":
                # Paso 3: Crear BD
                self._log("[3] Verificando base de datos...")
                self._create_db_if_needed()
                self.progress["value"] = 70

                # Paso 4: Migraciones
                self._log("[4] Ejecutando migraciones...")
                exe_path = os.path.join(install_dir, "AgilizeGestion.exe")
                # Las migraciones se ejecutan al iniciar la app por primera vez
                self._log("[OK] Se aplicaran al iniciar")
                self.progress["value"] = 85

            # Paso final: Acceso directo
            self._log(f"[{total_steps}] Creando acceso directo...")
            self._create_shortcut(install_dir)
            self.progress["value"] = 100

            self._log("")
            self._log("=" * 40)
            self._log("  INSTALACION COMPLETADA!")
            self._log("=" * 40)
            self._log(f"  Ubicacion: {install_dir}")
            self._log("  Usuario: master / master2025")

            messagebox.showinfo("Instalacion Completada",
                              f"Agilize Gestion se instalo correctamente.\n\n"
                              f"Ubicacion: {install_dir}\n"
                              f"Usuario: master\n"
                              f"Contrasena: master2025\n\n"
                              f"Ejecuta desde el acceso directo en el escritorio.")

        except Exception as e:
            self._log(f"[ERROR] {str(e)}")
            messagebox.showerror("Error", f"Error durante la instalacion:\n{str(e)}")

    def _create_db_if_needed(self):
        """Crea la BD si no existe usando psql."""
        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config["password"]

            # Verificar si existe
            result = subprocess.run(
                ["psql", "-U", self.config["user"], "-h", self.config["host"],
                 "-p", self.config["port"], "-tc",
                 "SELECT 1 FROM pg_database WHERE datname='agilize_gestion'"],
                capture_output=True, text=True, env=env
            )

            if "1" not in result.stdout:
                self._log("[INFO] Creando base de datos...")
                subprocess.run(
                    ["psql", "-U", self.config["user"], "-h", self.config["host"],
                     "-p", self.config["port"], "-c",
                     "CREATE DATABASE agilize_gestion;"],
                    capture_output=True, text=True, env=env
                )
                self._log("[OK] Base de datos creada")
            else:
                self._log("[OK] Base de datos ya existe")
        except FileNotFoundError:
            # psql no en PATH, buscar en ubicaciones comunes
            for ver in ["18", "17", "16", "15"]:
                psql = f"C:\\Program Files\\PostgreSQL\\{ver}\\bin\\psql.exe"
                if os.path.exists(psql):
                    self._log(f"[INFO] Usando PostgreSQL {ver}")
                    env = os.environ.copy()
                    env["PGPASSWORD"] = self.config["password"]
                    result = subprocess.run(
                        [psql, "-U", self.config["user"], "-h", self.config["host"],
                         "-p", self.config["port"], "-tc",
                         "SELECT 1 FROM pg_database WHERE datname='agilize_gestion'"],
                        capture_output=True, text=True, env=env
                    )
                    if "1" not in result.stdout:
                        subprocess.run(
                            [psql, "-U", self.config["user"], "-h", self.config["host"],
                             "-p", self.config["port"], "-c",
                             "CREATE DATABASE agilize_gestion;"],
                            capture_output=True, text=True, env=env
                        )
                        self._log("[OK] Base de datos creada")
                    else:
                        self._log("[OK] Base de datos ya existe")
                    return
            self._log("[WARN] psql no encontrado, crea la BD manualmente")

    def _create_shortcut(self, install_dir):
        """Crea acceso directo en el escritorio."""
        try:
            vbs = f'''Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\\Agilize Gestion.lnk")
oShortcut.TargetPath = "{install_dir}\\AgilizeGestion.exe"
oShortcut.WorkingDirectory = "{install_dir}"
oShortcut.WindowStyle = 1
oShortcut.Description = "Agilize Gestion"
oShortcut.Save'''
            vbs_path = os.path.join(install_dir, "_shortcut.vbs")
            with open(vbs_path, "w") as f:
                f.write(vbs)
            subprocess.run(["cscript", "//nologo", vbs_path], capture_output=True)
            os.remove(vbs_path)
            self._log("[OK] Acceso directo creado")
        except Exception as e:
            self._log(f"[WARN] No se pudo crear acceso directo: {e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = InstaladorApp()
    app.run()
