# Plano de Ação: Gerador de Projetos e Classes WPILib 2020 (Studica VMX-pi / Titan)

> **Objetivo:** Automatizar a criação de projetos, geração de subsistemas/comandos com presets pré-configurados e acoplamento automático (injeção de dependências no `RobotContainer` e `Constants`), eliminando o tempo morto de setup e prevenindo erros de configuração durante treinos e competições (WorldSkills Mobile Robotics / FRC).

---

## 1. Visão Geral e Diagnóstico do Código Base

Através da análise do projeto de referência (`lab1Introducao`), identificamos o fluxo que um programador percorre manualmente a cada novo projeto:

1. **Configuração de Dependências (`vendordeps/`):**
   - Cópia obrigatória de `Studica.json`, `WPILibNewCommands.json` e `navx_frc.json`.
   - Sem eles, as classes essenciais (`Titan`, `SubsystemBase`, `AHRS`) não compilam no GradleRIO 2020.3.2.30.
2. **Definição de Constantes (`Constants.java`):**
   - Configuração de CAN IDs (Titan padrão 42).
   - Portas dos motores (M0 a M3).
   - Resolução dos encoders (ex: 1440 PPR) e reduções mecânicas (ex: `1.0 / 61.0`).
   - Cálculos matemáticos derivados (como `wheelDistPerTick = (2 * PI * r) / PPR`).
3. **Criação de Subsistemas (`subsystems/`):**
   - Criação da classe herdando de `SubsystemBase`.
   - Injeção do objeto `Titan` no construtor.
   - Instanciação de `Titan.Motor` e `Titan.Encoder`.
   - Métodos de controle (`setMotorSpeed`, `stopMotor`) e telemetria via `SmartDashboard`.
4. **Acoplamento no `RobotContainer.java`:**
   - Instanciação do `Titan`.
   - Instanciação de cada subsistema criado.
   - Criação de comandos padrão (`setDefaultCommand`).
   - Mapeamento de botões do controle Xbox (`JoystickButton`, `Trigger`).
   - Adição de rotinas ao seletor autônomo (`SendableChooser`).

---

## 2. Princípios de Design do Software

Para atender às necessidades do usuário:
1. **Zero Valores "Mágicos" Ocultos (Totalmente Customizável):** O usuário deve sempre poder visualizar, ajustar e validar:
   - Portas de motores (M0, M1, M2, M3);
   - Canais de encoders (0, 1, 2, 3);
   - Raio da roda (mm), Pulsos por volta (PPR) e Relação de redução (Gear Ratio);
   - Nomes de classes e comandos.
2. **Acoplamento Automático Inteligente:** Ao criar uma classe, o software não gera apenas o arquivo isolado; ele:
   - Insere as constantes no `Constants.java`;
   - Declara e instancia o subsistema em `RobotContainer.java`;
   - Vincula os botões solicitados no `configureButtonBindings()`.
3. **Arquitetura Baseada em Presets:** Presets específicos para o hardware da Studica / WorldSkills que já trazem a matemática e o boilerplate correto, necessitando apenas de ajuste fino pelo programador.

---

## 3. Módulos do Software

### Módulo 1: Gerenciador de Novo Projeto (Project Scaffolder)
- **Entradas do Usuário:** Nome do projeto, diretório de destino, CAN ID do Titan, vendors necessários.
- **Saídas:** Estrutura completa de pastas WPILib 2020 (`build.gradle`, `.wpilib/`, `vendordeps/`, `src/main/java/frc/robot/`).

### Módulo 2: Gerador de Classes com Presets (Class Generator)
Permite gerar classes individualmente ou em lote para projetos novos ou já existentes:

| Preset | Descrição | Parâmetros Customizáveis pelo Usuário |
| :--- | :--- | :--- |
| **Drivetrain Diferencial (Tanque)** | 2 ou 4 motores em tração tanque direta ou com redução. | Portas M0/M1, Raio roda, PPR, Gear Ratio, Inversão de lado. |
| **Drivetrain Omni 3 Rodas (Kiwi)** | Tração holonômica a 120° com 3 rodas omnidirecionais. | Portas M0/M1/M2, Raio roda, PPR, Geometria (R do chassi). |
| **Drivetrain Omni/Mecanum 4 Rodas** | Tração holonômica com 4 motores Titan. | Portas M0/M1/M2/M3, Encoders, Fatores de translação/rotação. |
| **Mecanismo Garra / Ingestão** | Motor individual com encoder de velocidade / stop limit. | Porta Motor, Canal Encoder, PPR, Velocidade padrão, Threshold isAtSpeed. |
| **Elevador / Braço Linear** | Motor com controle de posição e sensores fim de curso. | Porta Motor, Encoder, Alturas alvo (Preset ticks), Sensores digitais. |
| **Atuador Servo (Studica)** | Controle de servomotores pelo conector do Titan. | Canal Servo (0-7), Ângulo mínimo/máximo, Posição padrão. |
| **Sensor NavX IMU** | Subsistema para bússola/giroscópio NavX via porta MXP. | Tipo de comunicação (SPI/I2C), Zero Yaw, Leitura contínua no Dashboard. |
| **Comando de Teleoperado (Drive)** | Comando vinculado ao Joystick Xbox para dirigir. | Eixos do analógico, Deadband (zona morta), Sensibilidade. |
| **Comando Temporizado (Timed)** | Executa uma ação de subsistema durante X segundos. | Subsistema alvo, Ação, Tempo em segundos. |

### Módulo 3: Motor de Injeção & Acoplamento Automático (AST/Code Injector)
- Analisa o `Constants.java` existente e insere de forma limpa as novas variáveis (evitando IDs duplicados).
- Analisa o `RobotContainer.java` e:
  - Adiciona o campo privado: `private final <Subsystem> m_<subsystem>;`
  - Adiciona a instanciação no construtor: `m_<subsystem> = new <Subsystem>(titan);`
  - Adiciona os botões no método `configureButtonBindings()`.

### Módulo 4: Validador de Recursos de Hardware
- Impede que o usuário selecione a mesma porta do Titan para dois mecanismos diferentes (ex: impedir que M2 seja Garra e Roda Traseira simultaneamente).
- Alerta sobre divisões inteiras (ex: alertar se o usuário digitar `1/61` em vez de `1.0/61.0`).

---

## 4. Fases de Execução

- [x] **Fase 1: Mapeamento e Estruturação dos Vendors** (Concluído: `Studica.json`, `WPILibNewCommands.json`, `navx_frc.json` em `/python/vendors`).
- [ ] **Fase 2: Motor de Templates (Jinja2 / String Templates)** em Python para cada tipo de classe Java.
- [ ] **Fase 3: Mecanismo de Acoplamento (Parser / Injector)** para atualizar `Constants.java` e `RobotContainer.java` existentes.
- [ ] **Fase 4: Interface Gráfica Interativa (PySide6 / Qt6)** moderna, intuitiva, com abas para cada Preset e visualização de código em tempo real.
- [ ] **Fase 5: Testes de Validação e Deploy** com compilação direta via `gradlew build`.
