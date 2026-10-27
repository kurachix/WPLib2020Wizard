"""
Script de automação de compilação em .exe usando PyInstaller.
Empacota a aplicação PySide6 e inclui a pasta vendors.
"""

import os
import sys
import subprocess
import shutil

def build():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
    
    vendors_dir = os.path.join(current_dir, "vendors")
    main_script = os.path.join(current_dir, "main.py")
    
    print("=" * 60)
    print("Iniciando build do WPILib 2020 Robot Wizard para .exe...")
    print("=" * 60)

    # Comando PyInstaller
    # --onefile: Gera um unico arquivo executavel
    # --windowed: Nao abre janela preta do prompt de comando
    # --name: Nome do arquivo executavel
    # --add-data: Inclui a pasta vendors dentro do pacote
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name", "WPILib2020Wizard",
        "--add-data", f"{vendors_dir};vendors",
        main_script
    ]
    
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=current_dir)
    
    if result.returncode == 0:
        dist_dir = os.path.join(current_dir, "dist")
        print("\n" + "=" * 60)
        print("BUILD CONCLUIDO COM SUCESSO!")
        print(f"Executavel gerado em: {dist_dir}\\WPILib2020Wizard")
        print("=" * 60)
    else:
        print("\nFalha na compilacao com PyInstaller.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
