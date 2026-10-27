"""
Módulo criador de novos projetos WPILib 2020.
Copia e adapta os arquivos da pasta 'template' para o novo projeto fornecido pelo usuário.
"""

import os
import shutil
import re
import json
from typing import Dict, Any, List


class ProjectGenerator:
    """Cria a estrutura de um novo projeto WPILib 2020 a partir da pasta template."""

    IGNORED_DIRS = {".gradle", "build", "bin", ".settings"}

    @classmethod
    def find_template_dir(cls) -> str:
        """Localiza a pasta template no workspace."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

        # Possíveis caminhos da pasta template
        candidates = [
            os.path.join(parent_dir, "template"),
            os.path.join(current_dir, "template"),
            os.path.join(parent_dir, "lab1Introducao")
        ]

        for cand in candidates:
            if os.path.isdir(cand) and os.path.exists(os.path.join(cand, "build.gradle")):
                return cand

        return ""

    @classmethod
    def create_project(cls, params: Dict[str, Any]) -> str:
        """
        Cria a estrutura do projeto WPILib no diretório especificado,
        copiando da pasta template e adaptando o nome e as configurações.
        """
        project_name = params.get("project_name", "RoboWPILib2020")
        target_dir = params.get("target_dir", ".")
        team_number = params.get("team_number", 502)
        titan_id = params.get("titan_id", 42)
        selected_vendors: List[str] = params.get("vendors", ["Studica.json", "WPILibNewCommands.json", "navx_frc.json"])

        project_path = os.path.join(target_dir, project_name)
        os.makedirs(project_path, exist_ok=True)

        template_dir = cls.find_template_dir()

        if template_dir and os.path.exists(template_dir):
            # 1. Copiar recursivamente ignorando caches (.gradle, build, bin)
            for item in os.listdir(template_dir):
                if item in cls.IGNORED_DIRS:
                    continue
                s = os.path.join(template_dir, item)
                d = os.path.join(project_path, item)
                if os.path.isdir(s):
                    if not os.path.exists(d):
                        shutil.copytree(s, d, ignore=shutil.ignore_patterns("*.class", "*.log", ".gradle", "build", "bin"))
                else:
                    shutil.copy2(s, d)

            # 2. Adaptar o arquivo .project com o novo nome
            dot_project_path = os.path.join(project_path, ".project")
            if os.path.exists(dot_project_path):
                with open(dot_project_path, "r", encoding="utf-8") as f:
                    proj_content = f.read()
                proj_content = re.sub(r"<name>[^<]+</name>", f"<name>{project_name}</name>", proj_content, count=1)
                with open(dot_project_path, "w", encoding="utf-8") as f:
                    f.write(proj_content)

            # 3. Adaptar settings.gradle
            settings_path = os.path.join(project_path, "settings.gradle")
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings_content = f.read()
                if "rootProject.name" in settings_content:
                    settings_content = re.sub(r'rootProject\.name\s*=\s*["\'][^"\']+["\']', f'rootProject.name = "{project_name}"', settings_content)
                else:
                    settings_content = f'rootProject.name = "{project_name}"\n' + settings_content
                with open(settings_path, "w", encoding="utf-8") as f:
                    f.write(settings_content)

            # 4. Adaptar Constants.java para incluir TITAN_ID
            constants_path = os.path.join(project_path, "src", "main", "java", "frc", "robot", "Constants.java")
            if os.path.exists(constants_path):
                with open(constants_path, "r", encoding="utf-8") as f:
                    const_content = f.read()
                if "TITAN_ID" not in const_content:
                    # Injeta a constante TITAN_ID dentro da classe
                    last_brace = const_content.rfind("}")
                    if last_brace != -1:
                        titan_def = f"\n    /**\n     * Titan Quad CAN ID\n     */\n    public static final int TITAN_ID = {titan_id};\n"
                        const_content = const_content[:last_brace] + titan_def + const_content[last_brace:]
                        with open(constants_path, "w", encoding="utf-8") as f:
                            f.write(const_content)

        else:
            # Fallback caso a pasta template não exista: gera estrutura nativamente
            cls._create_from_scratch(project_path, project_name, titan_id, team_number)

        # 5. Adaptar o arquivo .wpilib/wpilib_preferences.json com o teamNumber
        wpilib_prefs_path = os.path.join(project_path, ".wpilib", "wpilib_preferences.json")
        os.makedirs(os.path.dirname(wpilib_prefs_path), exist_ok=True)
        prefs_data = {
            "enableCppIntellisense": False,
            "currentLanguage": "java",
            "projectYear": "2020",
            "teamNumber": team_number
        }
        if os.path.exists(wpilib_prefs_path):
            try:
                with open(wpilib_prefs_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        prefs_data = loaded
            except Exception:
                pass
        prefs_data["teamNumber"] = team_number
        with open(wpilib_prefs_path, "w", encoding="utf-8") as f:
            json.dump(prefs_data, f, indent=4)

        # 5. Garantir que as pastas commands e subsystems existam
        os.makedirs(os.path.join(project_path, "src", "main", "java", "frc", "robot", "commands"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "src", "main", "java", "frc", "robot", "subsystems"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "vendordeps"), exist_ok=True)

        # 6. Copiar Vendors da pasta /python/vendors para vendordeps
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vendors_source_dir = os.path.join(script_dir, "vendors")
        if os.path.exists(vendors_source_dir):
            for vendor_file in selected_vendors:
                src_file = os.path.join(vendors_source_dir, vendor_file)
                dst_file = os.path.join(project_path, "vendordeps", vendor_file)
                if os.path.exists(src_file):
                    shutil.copy2(src_file, dst_file)

        return project_path

    @classmethod
    def _create_from_scratch(cls, project_path: str, project_name: str, titan_id: int, team_number: int = 502):
        """Cria estrutura básica se a pasta template não for encontrada."""
        subdirs = [
            ".wpilib",
            "vendordeps",
            "src/main/java/frc/robot/commands",
            "src/main/java/frc/robot/subsystems",
            "src/main/deploy"
        ]
        for d in subdirs:
            os.makedirs(os.path.join(project_path, d), exist_ok=True)

        # build.gradle para VMX-pi
        build_gradle = """plugins {
    id "java"
    id "com.kauailabs.first.GradleRIO" version "2020.3.2.30"
}

sourceCompatibility = JavaVersion.VERSION_11
targetCompatibility = JavaVersion.VERSION_11

def ROBOT_MAIN_CLASS = "frc.robot.Main"

deploy {
    targets {
        vmxpi("roborio") {
            team = frc.getTeamNumber()
        }
    }
    artifacts {
        frcJavaArtifact('frcJava') {
            targets << "roborio"
            debug = frc.getDebugOrDefault(false)
        }
        fileTreeArtifact('frcStaticFileDeploy') {
            files = fileTree(dir: 'src/main/deploy')
            targets << "roborio"
            directory = '/home/lvuser/deploy'
        }
    }
}

dependencies {
    implementation wpi.deps.wpilib()
    nativeZip wpi.deps.wpilibJni(wpi.platforms.raspbian)
    nativeDesktopZip wpi.deps.wpilibJni(wpi.platforms.desktop)

    implementation wpi.deps.vendor.java()
    nativeZip wpi.deps.vendor.jni(wpi.platforms.raspbian)
    nativeDesktopZip wpi.deps.vendor.jni(wpi.platforms.desktop)

    testImplementation 'junit:junit:4.12'
    simulation wpi.deps.sim.gui(wpi.platforms.desktop, false)
}

jar {
    from { configurations.runtimeClasspath.collect { it.isDirectory() ? it : zipTree(it) } }
    manifest edu.wpi.first.gradlerio.GradleRIOPlugin.javaManifest(ROBOT_MAIN_CLASS)
}
"""
        with open(os.path.join(project_path, "build.gradle"), "w", encoding="utf-8") as f:
            f.write(build_gradle)

        with open(os.path.join(project_path, "settings.gradle"), "w", encoding="utf-8") as f:
            f.write(f'rootProject.name = "{project_name}"\n')

        with open(os.path.join(project_path, "src", "main", "java", "frc", "robot", "Constants.java"), "w", encoding="utf-8") as f:
            f.write(f"package frc.robot;\n\npublic final class Constants {{\n    public static final int TITAN_ID = {titan_id};\n}}\n")
