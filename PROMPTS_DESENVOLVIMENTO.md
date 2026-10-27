# Biblioteca de Prompts de Desenvolvimento: WPILib 2020 Robot Wizard

Este arquivo contém uma suíte de **Prompts Estruturados** prontos para serem usados durante o desenvolvimento e evolução do software de geração de código. Cada prompt é focado em um módulo específico e projetado para produzir código limpo, robusto e sem valores *hardcoded*.

---

### Prompt 1: Motor de Templates Java e Geração de Arquivos do Projeto

```text
Atue como especialista em WPILib 2020 e Java para Robótica (Studica VMX-pi / Titan Quad).
Crie um módulo Python chamado `project_generator.py` responsável por criar a estrutura inicial de um novo projeto WPILib 2020 a partir do zero.

Requisitos:
1. Receber como parâmetros: `project_name`, `target_dir`, `titan_can_id` (padrão 42), `include_studica` (bool), `include_navx` (bool), `include_commands` (bool).
2. Criar a estrutura padrão:
   - `build.gradle` configurado com plugin GradleRIO 2020.3.2.30, Java 11 e target `vmxpi("roborio")`.
   - `settings.gradle` com o nome do projeto.
   - `.wpilib/wpilib_preferences.json` com linguagem Java.
   - Pasta `vendordeps/` copiando os arquivos JSON disponíveis em `/python/vendors/`.
   - `src/main/java/frc/robot/` contendo `Main.java`, `Robot.java`, `RobotContainer.java` e `Constants.java`.
3. Todos os identificadores, nomes de pacotes e caminhos devem ser dinâmicos.
4. O `Constants.java` deve ser gerado limpo, contendo a constante `TITAN_ID`.
5. Retorne funções claras para testar a criação de um projeto de teste.
```

---

### Prompt 2: Sistema de Acoplamento Automático (`Constants` e `RobotContainer`)

```text
Atue como engenheiro de software com foco em meta-programação e manipulação de código Java em Python.
Crie um módulo `coupler.py` capaz de ler um projeto WPILib existente e injetar automaticamente as referências de um novo subsistema ou comando sem quebrar a formatação original.

Requisitos:
1. Injeção no `Constants.java`:
   - Método `inject_constants(file_path, class_name, constants_dict)`: adiciona uma classe estática interna (ex: `public static final class GarraConstants { ... }`) ou constantes globais com portas de motor, canais de encoder e cálculos de redução.
   - Evitar duplicar variáveis que já existam.
2. Injeção no `RobotContainer.java`:
   - Método `inject_subsystem(file_path, subsystem_class, var_name, constructor_args, default_command_code=None)`:
     * Adiciona o `import frc.robot.subsystems.<SubsystemClass>;` se não existir.
     * Adiciona a declaração do atributo: `private final <SubsystemClass> <var_name>;`
     * Adiciona a instanciação dentro do construtor `RobotContainer()`: `<var_name> = new <SubsystemClass>(<args>);`
     * Se houver comando padrão, injeta `<var_name>.setDefaultCommand(...);`
3. Injeção de Botões no `configureButtonBindings()`:
   - Método `bind_button(file_path, joystick_button_enum, command_instantiation_code, trigger_type="whenHeld")`:
     * Cria e vincula o `JoystickButton` ao comando especificado.
4. Inclua testes unitários para garantir que arquivos existentes como `lab1Introducao/src/main/java/frc/robot/RobotContainer.java` possam ser lidos e atualizados com segurança.
```

---

### Prompt 3: Gerador de Classes e Presets com Parâmetros Customizáveis

```text
Atue como programador líder de robótica autônoma (WorldSkills Mobile Robotics).
Crie um módulo `class_generator.py` que gere o código de subsistemas Java WPILib 2020 para o Titan Quad Motor Controller.

O módulo deve suportar os seguintes Presets:
1. Preset `Omni3DriveTrain` (Tração Holonômica Kiwi 3 Rodas):
   - Parâmetros: `motor_right_id`, `motor_left_id`, `motor_back_id`, `wheel_radius_mm`, `encoder_ppr`, `gear_ratio`, `chassis_radius_mm`.
   - Gera a cinemática de 3 rodas a 120 graus, métodos `driveHolonomic(vx, vy, omega)`, `stop()` e leitura individual de velocidade/distância de cada roda.
2. Preset `DifferentialDriveTrain` (Tração Tanque 2 ou 4 Motores):
   - Parâmetros: `left_motor_id`, `right_motor_id`, `invert_right` (bool), `wheel_radius_mm`, `encoder_ppr`, `gear_ratio`.
   - Gera métodos `arcadeDrive(speed, rotation)`, `tankDrive(leftSpeed, rightSpeed)` e odometria simples.
3. Preset `MechanismSubsystem` (Garra / Ingestor / Rolo):
   - Parâmetros: `subsystem_name`, `motor_id`, `encoder_channel` (opcional), `encoder_ppr`, `default_speed`, `threshold_rpm`.
   - Gera métodos `run(speed)`, `stop()`, `getRPM()`, `isAtSpeed()` e telemetria no SmartDashboard.
4. Preset `ArmElevatorSubsystem` (Braço / Elevador com Controle de Posição):
   - Parâmetros: `subsystem_name`, `motor_id`, `encoder_channel`, `ppr`, `gear_ratio`, `min_limit_channel`, `max_limit_channel`.
   - Gera proteção com fim de curso (DigitalInput) e leitura contínua de altura/ângulo.

Regra crítica: NENHUM valor deve ser fixo no template. O usuário precisa fornecer ou confirmar todos os parâmetros.
```

---

### Prompt 4: Interface Gráfica Moderna em PySide6 (Desktop GUI)

```text
Atue como designer de UI/UX e desenvolvedor Desktop Python utilizando PySide6 (Qt 6).
Crie o aplicativo principal `main.py` com visual moderno (tema Dark Mode elegante, paleta de cores consistente e tipografia nítida).

A janela principal deve conter abas:
- **Aba 1: Novo Projeto**:
  * Campos para: Nome do Projeto, Pasta de Destino (com seletor de arquivos), CAN ID do Titan, Checkboxes para Vendors (Studica, NavX, Commands).
  * Botão de ação: "Criar Projeto Base".
- **Aba 2: Gerador de Classes (Presets)**:
  * Dropdown para seleção do Preset:
    - Tração Omni 3 Rodas (Studica VMX)
    - Tração Diferencial Tanque
    - Garra / Manipulador
    - Braço / Elevador com Sensores
    - Servo Motor
    - Comando Personalizado
  * Formulário dinâmico que atualiza os campos de entrada de acordo com o preset selecionado (ex: raio da roda, portas de motor, PPR, redução).
  * Botão de "Pré-visualizar Código" e "Salvar Classe no Projeto".
- **Aba 3: Acoplamento & Conexões**:
  * Permite selecionar um projeto existente e conectar o subsistema gerado diretamente ao `RobotContainer.java` e ao `Constants.java`.
  * Configuração de botão do controle Xbox (A, B, X, Y, Bumpers, Gatilhos) para acionar ações do subsistema.
- **Aba 4: Pré-Visualização de Código**:
  * Editor de texto com visualização colorida/syntax highlight do código Java que será gerado antes de salvar no disco.
```

---

### Prompt 5: Validador de Conflitos e Prevenção de Falhas de Hardware

```text
Atue como engenheiro de testes e QA para robótica.
Crie um módulo `hardware_validator.py` em Python para validar as configurações informadas pelo usuário antes da geração dos arquivos.

Regras de Validação:
1. O controlador Titan Quad possui apenas 4 canais de motor (M0, M1, M2, M3). O validador deve impedir que dois mecanismos usem a mesma porta de motor.
2. Canais de Encoder (0, 1, 2, 3) também não podem ser duplicados no mesmo Titan.
3. Se o Gear Ratio for informado como fração (ex: "1/61"), garantir que a conversão em Java utilize números de ponto flutuante (`1.0 / 61.0`) para evitar o erro clássico de divisão inteira (`1/61 == 0`).
4. Validar se o nome da classe segue o padrão Java CamelCase (ex: `GarraSubsystem`, sem espaços ou caracteres especiais).
5. Exibir mensagens de erro claras e amigáveis para o usuário na interface gráfica caso alguma regra seja violada.
```
