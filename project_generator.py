"""
Módulo criador de novos projetos WPILib 2020 para Studica VMX-pi / Titan Quad.
Gera a estrutura completa de pastas, arquivos gradle e vendordeps.
"""

import os
import shutil
from typing import Dict, Any, List


class ProjectGenerator:
    """Cria a estrutura de um novo projeto WPILib 2020."""

    @staticmethod
    def create_project(params: Dict[str, Any]) -> str:
        """
        Cria a estrutura do projeto WPILib no diretório especificado.
        """
        project_name = params.get("project_name", "RoboWPILib2020")
        target_dir = params.get("target_dir", ".")
        titan_id = params.get("titan_id", 42)
        selected_vendors: List[str] = params.get("vendors", ["Studica.json", "WPILibNewCommands.json", "navx_frc.json"])

        project_path = os.path.join(target_dir, project_name)
        os.makedirs(project_path, exist_ok=True)

        # 1. Estrutura de pastas
        subdirs = [
            ".wpilib",
            "vendordeps",
            "src/main/java/frc/robot/commands",
            "src/main/java/frc/robot/subsystems",
            "src/main/deploy"
        ]
        for d in subdirs:
            os.makedirs(os.path.join(project_path, d), exist_ok=True)

        # 2. Copiar Vendors da pasta /python/vendors
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vendors_source_dir = os.path.join(script_dir, "vendors")

        if os.path.exists(vendors_source_dir):
            for vendor_file in selected_vendors:
                src_file = os.path.join(vendors_source_dir, vendor_file)
                dst_file = os.path.join(project_path, "vendordeps", vendor_file)
                if os.path.exists(src_file):
                    shutil.copy2(src_file, dst_file)

        # 3. Gerar build.gradle
        build_gradle_content = """plugins {
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
            f.write(build_gradle_content)

        # 4. Gerar settings.gradle
        settings_gradle = f'rootProject.name = "{project_name}"\n'
        with open(os.path.join(project_path, "settings.gradle"), "w", encoding="utf-8") as f:
            f.write(settings_gradle)

        # 5. Gerar .wpilib/wpilib_preferences.json
        wpilib_prefs = f"""{{
    "currentLanguage": "java",
    "projectYear": "2020",
    "teamNumber": 0
}}
"""
        with open(os.path.join(project_path, ".wpilib", "wpilib_preferences.json"), "w", encoding="utf-8") as f:
            f.write(wpilib_prefs)

        # 6. Gerar Main.java
        main_java = """package frc.robot;

import edu.wpi.first.wpilibj.RobotBase;

public final class Main {
    private Main() {
    }

    public static void main(String... args) {
        RobotBase.startRobot(Robot::new);
    }
}
"""
        with open(os.path.join(project_path, "src/main/java/frc/robot/Main.java"), "w", encoding="utf-8") as f:
            f.write(main_java)

        # 7. Gerar Constants.java
        constants_java = f"""package frc.robot;

/**
 * Constantes globais do robô.
 */
public final class Constants {{
    /**
     * Titan Quad CAN ID
     */
    public static final int TITAN_ID = {titan_id};

}}
"""
        with open(os.path.join(project_path, "src/main/java/frc/robot/Constants.java"), "w", encoding="utf-8") as f:
            f.write(constants_java)

        # 8. Gerar Robot.java
        robot_java = """package frc.robot;

import edu.wpi.first.wpilibj.TimedRobot;
import edu.wpi.first.wpilibj2.command.Command;
import edu.wpi.first.wpilibj2.command.CommandScheduler;

public class Robot extends TimedRobot {
    private Command m_autonomousCommand;
    private RobotContainer m_robotContainer;

    @Override
    public void robotInit() {
        m_robotContainer = new RobotContainer();
    }

    @Override
    public void robotPeriodic() {
        CommandScheduler.getInstance().run();
    }

    @Override
    public void disabledInit() {}

    @Override
    public void disabledPeriodic() {}

    @Override
    public void autonomousInit() {
        m_autonomousCommand = m_robotContainer.getAutonomousCommand();
        if (m_autonomousCommand != null) {
            m_autonomousCommand.schedule();
        }
    }

    @Override
    public void autonomousPeriodic() {}

    @Override
    public void teleopInit() {
        if (m_autonomousCommand != null) {
            m_autonomousCommand.cancel();
        }
    }

    @Override
    public void teleopPeriodic() {}

    @Override
    public void testInit() {
        CommandScheduler.getInstance().cancelAll();
    }

    @Override
    public void testPeriodic() {}
}
"""
        with open(os.path.join(project_path, "src/main/java/frc/robot/Robot.java"), "w", encoding="utf-8") as f:
            f.write(robot_java)

        # 9. Gerar RobotContainer.java
        robot_container_java = """package frc.robot;

import edu.wpi.first.wpilibj.XboxController;
import edu.wpi.first.wpilibj.smartdashboard.SendableChooser;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
import edu.wpi.first.wpilibj2.command.Command;
import com.studica.frc.Titan;

public class RobotContainer {
    // Titan Quad Controller
    private final Titan titan = new Titan(Constants.TITAN_ID);

    // Joystick
    private final XboxController joystick = new XboxController(0);

    // Auto Chooser
    private final SendableChooser<Command> autoChooser = new SendableChooser<>();

    public RobotContainer() {
        configureButtonBindings();
    }

    private void configureButtonBindings() {
        SmartDashboard.putData("Auto Mode", autoChooser);
    }

    public Command getAutonomousCommand() {
        return autoChooser.getSelected();
    }
}
"""
        with open(os.path.join(project_path, "src/main/java/frc/robot/RobotContainer.java"), "w", encoding="utf-8") as f:
            f.write(robot_container_java)

        return project_path
