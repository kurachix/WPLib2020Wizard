# WPILib 2020 Robot Wizard & Class Generator

Ferramenta visual desenvolvida para acelerar a criacao de projetos WPILib 2020 para o ecossistema **Studica VMX-pi / Titan Quad** (WorldSkills Mobile Robotics & FRC).

---

## Como Executar

Abra o terminal na pasta `python/` e execute:

```bash
python main.py
```

---

## Funcionalidades Principais

### 1. Criador de Novo Projeto (Scaffolding)
- Gera a estrutura de pastas oficial do WPILib 2020 (`build.gradle`, `.wpilib/`, `src/main/java/frc/robot/`).
- Copia automaticamente as dependencias de fornecedor (`Studica.json`, `WPILibNewCommands.json`, `navx_frc.json`) da pasta `vendors/`.
- Configura o GradleRIO `2020.3.2.30` com target `vmxpi` para Raspberry Pi.
- Inclui botao de informacoes detalhadas com explicacao passo a passo do processo.

### 2. Gerador de Classes com Presets
Gera classes com **todos os parametros personalizaveis** pelo usuario antes da escrita do codigo:
- **Gerador Universal (N Motores, Encoders, Sensores e Servos)**: Escolha quantos motores o robo tem (1 a 4), definindo para cada um o nome da variavel, canal no Titan (M0 a M3) e inversao. Tambem permite adicionar de 0 a 4 encoders, 0 a 4 fins de curso digitais (DigitalInput) e 0 a 4 servomotores, com geracao de metodos de controle individual, conjunto, telemetria no SmartDashboard e botao de seguranca `stop()`.
- **Tracao Omni 3 Rodas (Kiwi Holonomico)**: Portas de motores (Right, Back, Left), raio da roda em mm, PPR do encoder, relacao de reducao (`1.0 / 61.0`) e cinematica holonomica.
- **Tracao Diferencial / Tanque (2 Motores)**: Portas de motores, inversao de lado, raio da roda e controle arcade/tank drive.
- **Garra / Manipulador**: Motor Titan, encoder opcional, velocidade padrao, threshold de RPM e telemetria no `SmartDashboard`.
- **Atuador Servo**: Canal do servo no Titan e angulo inicial.
- **Comando Personalizado (`CommandBase`)**: Temporizado ou continuo com ciclo de vida WPILib (`initialize`, `execute`, `end`, `isFinished`).
- Inclui botao de explicacao sobre o funcionamento de cada preset e calculos matematicos.

### 3. Acoplamento Automatico (Injecao de Dependencias)
Nao gera apenas o arquivo solto. Conecta automaticamente o subsistema ao projeto:
- Injeta as constantes em `Constants.java`.
- Declara o atributo privado em `RobotContainer.java`.
- Instancia o subsistema no construtor `RobotContainer()` passando a instancia de `titan`.
- Vincula acoes a botoes do controle Xbox (`whenHeld`, `whenPressed`).
- Inclui botao de ajuda explicando o padrao Command-Based e injecao de dependencias.

### 4. Pre-Visualizador de Codigo
Permite inspecionar o codigo Java e os blocos de constantes antes de gravar no disco.

---

## Arquivos do Repositorio

- **[main.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/main.py)**: Interface Desktop moderna em PySide6 (Dark Mode) com botoes de informacao em cada etapa.
- **[class_generator.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/class_generator.py)**: Motor de geracao de codigo Java e presets.
- **[coupler.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/coupler.py)**: Sistema de injecao e acoplamento em `RobotContainer.java` e `Constants.java`.
- **[project_generator.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/project_generator.py)**: Gerador da estrutura de novo projeto WPILib.
- **[PLANO_DE_ACAO.md](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/PLANO_DE_ACAO.md)**: Plano estrategico e roadmap da ferramenta.
- **[PROMPTS_DESENVOLVIMENTO.md](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/PROMPTS_DESENVOLVIMENTO.md)**: Prompts modulares prontos para expandir a solucao.
- **[vendors/](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/vendors)**: Arquivos JSON de dependencias (Studica, NavX, Commands).
