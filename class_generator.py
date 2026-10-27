"""
Módulo gerador de classes e código Java para WPILib 2020 (Studica VMX-pi / Titan Quad).
Gera código limpo, documentado e com parâmetros 100% customizáveis pelo usuário.
"""

from typing import Dict, Any, Tuple


class ClassGenerator:
    """Gera arquivos Java de Subsystems, Commands e Constantes a partir de presets."""

    @staticmethod
    def generate_omni3_drivetrain(params: Dict[str, Any]) -> Tuple[str, str]:
        """
        Preset: Tração Holonômica Omni de 3 Rodas (Kiwi Drive a 120 graus).
        Retorna: (codigo_subsystem_java, codigo_constantes_java)
        """
        class_name = params.get("class_name", "DriveTrain")
        m_right = params.get("motor_right", 0)
        m_back = params.get("motor_back", 2)
        m_left = params.get("motor_left", 3)
        wheel_radius = params.get("wheel_radius_mm", 55.0)
        ppr = params.get("ppr", 1440.0)
        gear_ratio_str = params.get("gear_ratio", "1.0 / 61.0")

        constants_code = f"""    // Constantes de Tração Omni 3 Rodas ({class_name})
    public static final class {class_name}Constants {{
        public static final int MOTOR_RIGHT_ID       = {m_right};
        public static final int MOTOR_BACK_ID        = {m_back};
        public static final int MOTOR_LEFT_ID        = {m_left};

        public static final double WHEEL_RADIUS_MM   = {wheel_radius};
        public static final double PULSES_PER_REV    = {ppr};
        public static final double GEAR_RATIO        = {gear_ratio_str};
        public static final double DIST_PER_TICK     = (Math.PI * 2.0 * WHEEL_RADIUS_MM) / PULSES_PER_REV;
    }}"""

        java_code = f"""package frc.robot.subsystems;

import edu.wpi.first.wpilibj2.command.SubsystemBase;
import edu.wpi.first.wpilibj2.command.Command;
import edu.wpi.first.wpilibj2.command.RunCommand;
import com.studica.frc.Titan;
import frc.robot.Constants.{class_name}Constants;

/**
 * Tração Omni 3 Rodas (Holonômica) com Titan Quad.
 * Gerada automaticamente com parâmetros personalizados.
 */
public class {class_name} extends SubsystemBase {{

    private final Titan titan;
    private final Titan.Motor motorRight;
    private final Titan.Motor motorBack;
    private final Titan.Motor motorLeft;

    public {class_name}(Titan titan) {{
        this.titan = titan;
        this.motorRight = titan.getMotor({class_name}Constants.MOTOR_RIGHT_ID);
        this.motorBack  = titan.getMotor({class_name}Constants.MOTOR_BACK_ID);
        this.motorLeft  = titan.getMotor({class_name}Constants.MOTOR_LEFT_ID);
    }}

    @Override
    public void periodic() {{
        // Telemetria ou rotinas periódicas
    }}

    /**
     * Define velocidade individual de cada motor (-1.0 a 1.0)
     */
    public void setMotors(double right, double back, double left) {{
        motorRight.set(right);
        motorBack.set(back);
        motorLeft.set(left);
    }}

    /**
     * Controle Holonômico (Cinemática Kiwi a 120 graus)
     * @param vx Velocidade no eixo X (frente/trás)
     * @param vy Velocidade no eixo Y (lateral)
     * @param omega Velocidade de rotação
     */
    public void driveHolonomic(double vx, double vy, double omega) {{
        double sqrt3 = Math.sqrt(3.0);
        double vRight = -0.5 * vx - (sqrt3 / 2.0) * vy + omega;
        double vLeft  = -0.5 * vx + (sqrt3 / 2.0) * vy + omega;
        double vBack  = vx + omega;

        // Normalização caso ultrapasse 1.0
        double max = Math.max(Math.abs(vRight), Math.max(Math.abs(vLeft), Math.abs(vBack)));
        if (max > 1.0) {{
            vRight /= max;
            vLeft  /= max;
            vBack  /= max;
        }}

        setMotors(vRight, vBack, vLeft);
    }}

    /**
     * Para todos os motores da tração
     */
    public void stop() {{
        motorRight.stopMotor();
        motorBack.stopMotor();
        motorLeft.stopMotor();
    }}
}}
"""
        return java_code, constants_code

    @staticmethod
    def generate_differential_drivetrain(params: Dict[str, Any]) -> Tuple[str, str]:
        """
        Preset: Tração Diferencial / Tanque (2 motores).
        """
        class_name = params.get("class_name", "DriveTrain")
        m_left = params.get("motor_left", 0)
        m_right = params.get("motor_right", 1)
        invert_right = "true" if params.get("invert_right", True) else "false"
        wheel_radius = params.get("wheel_radius_mm", 50.0)
        ppr = params.get("ppr", 1440.0)

        constants_code = f"""    // Constantes de Tração Tanque ({class_name})
    public static final class {class_name}Constants {{
        public static final int MOTOR_LEFT_ID        = {m_left};
        public static final int MOTOR_RIGHT_ID       = {m_right};
        public static final boolean INVERT_RIGHT     = {invert_right};
        public static final double WHEEL_RADIUS_MM   = {wheel_radius};
        public static final double PULSES_PER_REV    = {ppr};
    }}"""

        java_code = f"""package frc.robot.subsystems;

import edu.wpi.first.wpilibj2.command.SubsystemBase;
import com.studica.frc.Titan;
import frc.robot.Constants.{class_name}Constants;

/**
 * Tração Diferencial (Tanque) com Titan Quad.
 */
public class {class_name} extends SubsystemBase {{

    private final Titan titan;
    private final Titan.Motor motorLeft;
    private final Titan.Motor motorRight;

    public {class_name}(Titan titan) {{
        this.titan = titan;
        this.motorLeft = titan.getMotor({class_name}Constants.MOTOR_LEFT_ID);
        this.motorRight = titan.getMotor({class_name}Constants.MOTOR_RIGHT_ID);
        this.motorRight.setInverted({class_name}Constants.INVERT_RIGHT);
    }}

    public void tankDrive(double leftSpeed, double rightSpeed) {{
        motorLeft.set(leftSpeed);
        motorRight.set(rightSpeed);
    }}

    public void arcadeDrive(double speed, double rotation) {{
        double left = speed + rotation;
        double right = speed - rotation;
        tankDrive(left, right);
    }}

    public void stop() {{
        motorLeft.stopMotor();
        motorRight.stopMotor();
    }}
}}
"""
        return java_code, constants_code

    @staticmethod
    def generate_mechanism_subsystem(params: Dict[str, Any]) -> Tuple[str, str]:
        """
        Preset: Mecanismo Garra / Manipulador (Motor Titan + Encoder com SmartDashboard).
        """
        class_name = params.get("class_name", "GarraSubsystem")
        motor_id = params.get("motor_id", 2)
        has_encoder = params.get("has_encoder", True)
        encoder_channel = params.get("encoder_channel", 2)
        ppr = params.get("ppr", 1440.0)
        speed_default = params.get("default_speed", 0.8)
        threshold_rpm = params.get("threshold_rpm", 100.0)

        constants_code = f"""    // Constantes do Mecanismo ({class_name})
    public static final class {class_name}Constants {{
        public static final int MOTOR_ID             = {motor_id};
        public static final int ENCODER_CHANNEL      = {encoder_channel};
        public static final double PULSES_PER_REV    = {ppr};
        public static final double DEFAULT_SPEED     = {speed_default};
        public static final double THRESHOLD_RPM     = {threshold_rpm};
    }}"""

        encoder_fields = """    private final Titan.Encoder encoder;""" if has_encoder else ""
        encoder_init = f"""        this.encoder = titan.getEncoder({class_name}Constants.ENCODER_CHANNEL, 1.0);
        this.motor.setEncoderResolution((int) {class_name}Constants.PULSES_PER_REV);""" if has_encoder else ""

        encoder_methods = f"""    public double getRPM() {{
        return encoder.getSpeed();
    }}

    public boolean isAtSpeed() {{
        return Math.abs(getRPM()) > {class_name}Constants.THRESHOLD_RPM;
    }}""" if has_encoder else """    public boolean isAtSpeed() {
        return true;
    }"""

        periodic_body = f"""        SmartDashboard.putNumber("{class_name} Motor RPM", motor.getRPM());
        SmartDashboard.putBoolean("{class_name} isAtSpeed", isAtSpeed());""" if has_encoder else f"""        SmartDashboard.putString("{class_name} Status", "Ativo");"""

        java_code = f"""package frc.robot.subsystems;

import edu.wpi.first.wpilibj2.command.SubsystemBase;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
import com.studica.frc.Titan;
import frc.robot.Constants.{class_name}Constants;

/**
 * Mecanismo / Garra gerado automaticamente.
 */
public class {class_name} extends SubsystemBase {{

    private final Titan titan;
    private final Titan.Motor motor;
{encoder_fields}

    public {class_name}(Titan titan) {{
        this.titan = titan;
        this.motor = titan.getMotor({class_name}Constants.MOTOR_ID);
{encoder_init}
    }}

    @Override
    public void periodic() {{
{periodic_body}
    }}

    public void activate() {{
        motor.set({class_name}Constants.DEFAULT_SPEED);
    }}

    public void setSpeed(double speed) {{
        motor.set(speed);
    }}

    public void stop() {{
        motor.stopMotor();
    }}

{encoder_methods}
}}
"""
        return java_code, constants_code

    @staticmethod
    def generate_servo_subsystem(params: Dict[str, Any]) -> Tuple[str, str]:
        """
        Preset: Controle de Servo Motor no conector Servo da Titan / VMX.
        """
        class_name = params.get("class_name", "ServoSubsystem")
        servo_channel = params.get("servo_channel", 0)
        default_angle = params.get("default_angle", 90.0)

        constants_code = f"""    // Constantes de Servo ({class_name})
    public static final class {class_name}Constants {{
        public static final int SERVO_CHANNEL        = {servo_channel};
        public static final double DEFAULT_ANGLE     = {default_angle};
    }}"""

        java_code = f"""package frc.robot.subsystems;

import edu.wpi.first.wpilibj2.command.SubsystemBase;
import com.studica.frc.Titan;
import frc.robot.Constants.{class_name}Constants;

/**
 * Controle de Servo Motor através do Titan / VMX-pi.
 */
public class {class_name} extends SubsystemBase {{

    private final Titan titan;
    private final Titan.Servo servo;

    public {class_name}(Titan titan) {{
        this.titan = titan;
        this.servo = titan.getServo({class_name}Constants.SERVO_CHANNEL);
        setAngle({class_name}Constants.DEFAULT_ANGLE);
    }}

    public void setAngle(double degrees) {{
        servo.setAngle(degrees);
    }}

    public double getAngle() {{
        return servo.getAngle();
    }}
}}
"""
        return java_code, constants_code

    @staticmethod
    def generate_command(params: Dict[str, Any]) -> str:
        """
        Gera um CommandBase personalizado com vínculo ao Subsystem.
        """
        command_name = params.get("command_name", "SimpleActionCommand")
        subsystem_class = params.get("subsystem_class", "DriveTrain")
        subsystem_var = params.get("subsystem_var", "subsystem")
        action_type = params.get("action_type", "timed")  # "timed" ou "continuous"
        duration_sec = params.get("duration_sec", 3.0)

        end_condition = f"timer.get() >= {duration_sec}" if action_type == "timed" else "false"
        timer_import = "import edu.wpi.first.wpilibj.Timer;\n" if action_type == "timed" else ""
        timer_field = "    private final Timer timer = new Timer();\n" if action_type == "timed" else ""
        timer_init = "        timer.reset();\n        timer.start();\n" if action_type == "timed" else ""

        return f"""package frc.robot.commands;

import edu.wpi.first.wpilibj2.command.CommandBase;
{timer_import}import frc.robot.subsystems.{subsystem_class};

/**
 * Comando gerado automaticamente para o subsistema {subsystem_class}.
 */
public class {command_name} extends CommandBase {{

    private final {subsystem_class} {subsystem_var};
{timer_field}
    public {command_name}({subsystem_class} {subsystem_var}) {{
        this.{subsystem_var} = {subsystem_var};
        addRequirements({subsystem_var});
    }}

    @Override
    public void initialize() {{
{timer_init}    }}

    @Override
    public void execute() {{
        // Ação no subsistema
    }}

    @Override
    public void end(boolean interrupted) {{
        {subsystem_var}.stop();
    }}

    @Override
    public boolean isFinished() {{
        return {end_condition};
    }}
}}
"""
