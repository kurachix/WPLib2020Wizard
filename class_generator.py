"""
Módulo gerador de classes e código Java para WPILib 2020 (Studica VMX-pi / Titan Quad).
Gera código limpo, documentado e com parâmetros 100% customizáveis pelo usuário.
"""

from typing import Dict, Any, Tuple


class ClassGenerator:
    """Gera arquivos Java de Subsystems, Commands e Constantes a partir de presets."""

    @staticmethod
    def generate_universal_subsystem(params: Dict[str, Any]) -> Tuple[str, str]:
        """
        Preset 1: Gerador Universal de Subsistema.
        Permite customizar N motores (1 a 4), N encoders (0 a 4), N fins de curso (0 a 4) e N servos (0 a 4).
        Retorna: (codigo_subsystem_java, codigo_constantes_java)
        """
        class_name = params.get("class_name", "MecanismoUniversal")
        motors = params.get("motors", [{"name": "motorPrincipal", "port": 0, "inverted": False}])
        encoders = params.get("encoders", [])
        limit_switches = params.get("limit_switches", [])
        servos = params.get("servos", [])

        # ==================== CONSTANTES ====================
        const_lines = [f"    // Constantes do Subsistema Universal ({class_name})", f"    public static final class {class_name}Constants {{"]
        
        # Constantes de Motores
        for i, m in enumerate(motors):
            m_name = m.get("name", f"motor{i}").upper()
            port = m.get("port", i)
            inv = "true" if m.get("inverted", False) else "false"
            const_lines.append(f"        public static final int {m_name}_PORT = {port};")
            const_lines.append(f"        public static final boolean {m_name}_INVERTED = {inv};")

        # Constantes de Encoders
        for i, enc in enumerate(encoders):
            enc_name = enc.get("name", f"encoder{i}").upper()
            ch = enc.get("channel", i)
            ppr = enc.get("ppr", 1440.0)
            const_lines.append(f"        public static final int {enc_name}_CHANNEL = {ch};")
            const_lines.append(f"        public static final double {enc_name}_PPR = {ppr};")

        # Constantes de Fim de Curso
        for i, ls in enumerate(limit_switches):
            ls_name = ls.get("name", f"fimDeCurso{i}").upper()
            ch = ls.get("channel", i)
            const_lines.append(f"        public static final int {ls_name}_CHANNEL = {ch};")

        # Constantes de Servos
        for i, s in enumerate(servos):
            s_name = s.get("name", f"servo{i}").upper()
            ch = s.get("channel", i)
            angle = s.get("default_angle", 90.0)
            const_lines.append(f"        public static final int {s_name}_CHANNEL = {ch};")
            const_lines.append(f"        public static final double {s_name}_DEFAULT_ANGLE = {angle};")

        const_lines.append("    }")
        constants_code = "\n".join(const_lines)

        # ==================== CÓDIGO JAVA ====================
        imports = [
            "package frc.robot.subsystems;",
            "",
            "import edu.wpi.first.wpilibj2.command.SubsystemBase;",
            "import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;",
            "import com.studica.frc.Titan;",
            f"import frc.robot.Constants.{class_name}Constants;"
        ]
        if limit_switches:
            imports.append("import edu.wpi.first.wpilibj.DigitalInput;")

        fields = ["    private final Titan titan;"]
        init_lines = ["        this.titan = titan;"]
        periodic_lines = []

        # Motores
        for i, m in enumerate(motors):
            var_name = m.get("name", f"motor{i}")
            m_const = var_name.upper()
            fields.append(f"    private final Titan.Motor {var_name};")
            init_lines.append(f"        this.{var_name} = titan.getMotor({class_name}Constants.{m_const}_PORT);")
            init_lines.append(f"        this.{var_name}.setInverted({class_name}Constants.{m_const}_INVERTED);")
            periodic_lines.append(f'        SmartDashboard.putNumber("{class_name} {var_name} RPM", {var_name}.getRPM());')

        # Encoders
        for i, enc in enumerate(encoders):
            var_name = enc.get("name", f"encoder{i}")
            enc_const = var_name.upper()
            fields.append(f"    private final Titan.Encoder {var_name};")
            init_lines.append(f"        this.{var_name} = titan.getEncoder({class_name}Constants.{enc_const}_CHANNEL, 1.0);")
            periodic_lines.append(f'        SmartDashboard.putNumber("{class_name} {var_name} Speed", {var_name}.getSpeed());')

        # Limit Switches
        for i, ls in enumerate(limit_switches):
            var_name = ls.get("name", f"limitSwitch{i}")
            ls_const = var_name.upper()
            fields.append(f"    private final DigitalInput {var_name};")
            init_lines.append(f"        this.{var_name} = new DigitalInput({class_name}Constants.{ls_const}_CHANNEL);")
            periodic_lines.append(f'        SmartDashboard.putBoolean("{class_name} {var_name} Ativo", {var_name}.get());')

        # Servos
        for i, s in enumerate(servos):
            var_name = s.get("name", f"servo{i}")
            s_const = var_name.upper()
            fields.append(f"    private final Titan.Servo {var_name};")
            init_lines.append(f"        this.{var_name} = titan.getServo({class_name}Constants.{s_const}_CHANNEL);")
            init_lines.append(f"        this.{var_name}.setAngle({class_name}Constants.{s_const}_DEFAULT_ANGLE);")

        fields_block = "\n".join(fields)
        init_block = "\n".join(init_lines)
        periodic_block = "\n".join(periodic_lines) if periodic_lines else "        // Telemetria"

        # Métodos de controle
        methods = []

        # Métodos para cada motor individual
        for m in motors:
            v_name = m.get("name", "motor")
            cap_name = v_name[:1].upper() + v_name[1:]
            methods.append(f"""    /**
     * Define velocidade do {v_name} (-1.0 a 1.0)
     */
    public void set{cap_name}(double speed) {{
        {v_name}.set(speed);
    }}""")

        # Método de acionamento geral e parada
        stop_motor_lines = "\n".join([f"        {m.get('name')}.stopMotor();" for m in motors])
        set_all_lines = "\n".join([f"        {m.get('name')}.set(speed);" for m in motors])

        methods.append(f"""    /**
     * Define a mesma velocidade para todos os motores
     */
    public void setAllMotors(double speed) {{
{set_all_lines}
    }}

    /**
     * Para todos os motores do subsistema
     */
    public void stop() {{
{stop_motor_lines}
    }}""")

        # Métodos para cada encoder
        for enc in encoders:
            v_name = enc.get("name", "encoder")
            cap_name = v_name[:1].upper() + v_name[1:]
            methods.append(f"""    public double get{cap_name}Speed() {{
        return {v_name}.getSpeed();
    }}

    public int get{cap_name}Raw() {{
        return {v_name}.getRaw();
    }}""")

        # Métodos para cada limit switch
        for ls in limit_switches:
            v_name = ls.get("name", "limitSwitch")
            cap_name = v_name[:1].upper() + v_name[1:]
            methods.append(f"""    public boolean is{cap_name}Triggered() {{
        return {v_name}.get();
    }}""")

        # Métodos para cada servo
        for s in servos:
            v_name = s.get("name", "servo")
            cap_name = v_name[:1].upper() + v_name[1:]
            methods.append(f"""    public void set{cap_name}Angle(double degrees) {{
        {v_name}.setAngle(degrees);
    }}

    public double get{cap_name}Angle() {{
        return {v_name}.getAngle();
    }}""")

        methods_block = "\n\n".join(methods)

        java_code = f"""{chr(10).join(imports)}

/**
 * Subsistema Universal Gerado Automaticamente.
 * Contem {len(motors)} motor(es), {len(encoders)} encoder(s), {len(limit_switches)} sensor(es) fim de curso e {len(servos)} servo(s).
 */
public class {class_name} extends SubsystemBase {{

{fields_block}

    public {class_name}(Titan titan) {{
{init_block}
    }}

    @Override
    public void periodic() {{
{periodic_block}
    }}

{methods_block}
}}
"""
        return java_code, constants_code

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
