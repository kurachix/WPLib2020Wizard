"""
Script de automação para compilação do WPILib 2020 Robot Wizard em executável Windows (.exe).
Gera tanto a versão em pasta (inicialização ultra rápida) quanto a versão Standalone portátil (arquivo único).
Garante que todas as bibliotecas (PySide6) e pastas de dados ('vendors' e 'template') sejam empacotadas.
"""

import os
import sys
import shutil
import subprocess

def clean_build_artifacts(root_dir: str):
    """Limpa diretórios de build anteriores e caches."""
    print("-> Limpando arquivos temporarios e caches...")
    for folder in ["build", "dist"]:
        folder_path = os.path.join(root_dir, folder)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                print(f"   Aviso ao limpar {folder}: {e}")

    # Limpar caches de template que não devem ser empacotados
    template_dir = os.path.join(root_dir, "template")
    for cache_sub in [".gradle", "build", "bin"]:
        p = os.path.join(template_dir, cache_sub)
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
            except Exception:
                pass


def build():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    spec_onedir = os.path.join(root_dir, "WPILib2020Wizard.spec")
    spec_onefile = os.path.join(root_dir, "WPILib2020Wizard_Standalone.spec")
    
    clean_build_artifacts(root_dir)

    print("=" * 70)
    print(" INICIANDO BUILD DO WPILIB 2020 ROBOT WIZARD (.EXE)")
    print("=" * 70)

    # 1. Compilação da versão Onedir (pasta completa com inicialização instantânea)
    print("\n[1/3] Compilando versao Pasta (Onedir) via WPILib2020Wizard.spec...")
    cmd_onedir = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        spec_onedir
    ]
    res_onedir = subprocess.run(cmd_onedir, cwd=root_dir)
    if res_onedir.returncode != 0:
        print("[ERRO] Falha na compilacao da versao Onedir.")
        sys.exit(res_onedir.returncode)

    # Copiar pastas vendors e template ao lado do .exe também para redundância 100% segura
    dist_wizard_dir = os.path.join(root_dir, "dist", "WPILib2020Wizard")
    if os.path.exists(dist_wizard_dir):
        print("-> Sincronizando pastas de recursos na raiz do pacote...")
        dest_vendors = os.path.join(dist_wizard_dir, "vendors")
        dest_template = os.path.join(dist_wizard_dir, "template")
        if not os.path.exists(dest_vendors):
            shutil.copytree(os.path.join(root_dir, "vendors"), dest_vendors)
        if not os.path.exists(dest_template):
            shutil.copytree(os.path.join(root_dir, "template"), dest_template)

    # 2. Compilação da versão Standalone (arquivo único .exe portátil)
    print("\n[2/3] Compilando versao Standalone (Arquivo Unico Portatil)...")
    cmd_onefile = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        spec_onefile
    ]
    res_onefile = subprocess.run(cmd_onefile, cwd=root_dir)
    if res_onefile.returncode != 0:
        print("[ERRO] Falha na compilacao da versao Standalone.")
        sys.exit(res_onefile.returncode)

    print("\n[3/3] Validando os executaveis gerados...")
    exe_onedir = os.path.join(dist_wizard_dir, "WPILib2020Wizard.exe")
    exe_standalone = os.path.join(root_dir, "dist", "WPILib2020Wizard_Standalone.exe")

    if os.path.exists(exe_onedir) and os.path.exists(exe_standalone):
        print("\n" + "=" * 70)
        print("  BUILD CONCLUIDO COM 100% DE SUCESSO!")
        print("=" * 70)
        print(f" 1. Pacote Onedir (Inicializacao Instantanea):")
        print(f"    -> {exe_onedir}")
        print(f" 2. Executavel Standalone (Arquivo Unico Portatil):")
        print(f"    -> {exe_standalone}")
        print("=" * 70)
    else:
        print("[ERRO] Os arquivos executaveis esperados nao foram encontrados.")
        sys.exit(1)


if __name__ == "__main__":
    build()
