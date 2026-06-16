"""
Desinstalador grafico de Agilize Gestion.
"""
import tkinter as tk
from tkinter import messagebox
import shutil
import os
import sys
import subprocess
from pathlib import Path


class DesinstaladorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Agilize Gestion - Desinstalar")
        self.root.geometry("450, 300")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a1a")

        self.install_dir = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "AgilizeGestion")
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#ef4444", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Desinstalar Agilize Gestion", font=("Segoe UI", 14, "bold"),
                 bg="#ef4444", fg="#ffffff").pack(pady=12)

        # Contenido
        container = tk.Frame(self.root, bg="#1a1a1a", padx=30, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Se eliminara la aplicacion del sistema.",
                 font=("Segoe UI", 11), bg="#1a1a1a", fg="#F8F9FA").pack(anchor="w", pady=(0, 10))

        tk.Label(container, text="La base de datos NO se eliminara.",
                 font=("Segoe UI", 10, "bold"), bg="#1a1a1a", fg="#10b981").pack(anchor="w")

        tk.Label(container, text="Los datos se mantienen para una futura reinstalacion.",
                 font=("Segoe UI", 9), bg="#1a1a1a", fg="#888888").pack(anchor="w", pady=(2, 20))

        tk.Label(container, text=f"Ubicacion: {self.install_dir}",
                 font=("Segoe UI", 9), bg="#1a1a1a", fg="#888888").pack(anchor="w", pady=(0, 20))

        # Botones
        btn_frame = tk.Frame(container, bg="#1a1a1a")
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Cancelar", font=("Segoe UI", 10),
                  bg="#2D2D2D", fg="#F8F9FA", width=12,
                  command=self.root.destroy).pack(side="left")

        tk.Button(btn_frame, text="Desinstalar", font=("Segoe UI", 10, "bold"),
                  bg="#ef4444", fg="#ffffff", width=15,
                  command=self._desinstalar).pack(side="right")

    def _desinstalar(self):
        resp = messagebox.askyesno(
            "Confirmar",
            "Estas seguro que deseas desinstalar Agilize Gestion?\n\n"
            "La base de datos NO se eliminara."
        )
        if not resp:
            return

        try:
            # Eliminar acceso directo
            self._eliminar_acceso_directo()

            # Eliminar carpeta de instalacion
            if os.path.exists(self.install_dir):
                shutil.rmtree(self.install_dir, ignore_errors=True)

            messagebox.showinfo(
                "Desinstalacion Completada",
                "Agilize Gestion fue desinstalado correctamente.\n\n"
                "La base de datos se mantiene intacta.\n"
                "Si reinstala, los datos se recuperan automaticamente."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al desinstalar:\n{str(e)}")

        self.root.destroy()

    def _eliminar_acceso_directo(self):
        """Elimina el acceso directo del escritorio."""
        try:
            vbs = '''Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set fso = CreateObject("Scripting.FileSystemObject")
If fso.FileExists(strDesktop & "\\Agilize Gestion.lnk") Then
    fso.DeleteFile(strDesktop & "\\Agilize Gestion.lnk")
End If'''
            vbs_path = os.path.join(os.environ.get("TEMP", "."), "_del_shortcut.vbs")
            with open(vbs_path, "w") as f:
                f.write(vbs)
            subprocess.run(["cscript", "//nologo", vbs_path], capture_output=True)
            os.remove(vbs_path)
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DesinstaladorApp()
    app.run()
