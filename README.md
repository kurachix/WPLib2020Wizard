# 🤖 WPILib 2020 Robot Wizard & Class Generator

Ferramenta visual desenvolvida para acelerar a criação de projetos WPILib 2020 para o ecossistema **Studica VMX-pi / Titan Quad** (WorldSkills Mobile Robotics & FRC).

---

## 🚀 Como Executar

Abra o terminal na pasta `python/` e execute:

```bash
python main.py
```

---

## 🛠️ Funcionalidades Principais

### 1. 📁 Criador de Novo Projeto (Scaffolding)
- Gera a estrutura de pastas oficial do WPILib 2020 (`build.gradle`, `.wpilib/`, `src/main/java/frc/robot/`).
- Copia automaticamente as dependências de fornecedor (`Studica.json`, `WPILibNewCommands.json`, `navx_frc.json`) da pasta `vendors/`.
- Configura o GradleRIO `2020.3.2.30` com target `vmxpi` para Raspberry Pi.

### 2. ⚙️ Gerador de Classes com Presets
Gera classes com **todos os parâmetros personalizáveis** pelo usuário antes da escrita do código:
- **Tração Omni 3 Rodas (Kiwi Holonômico)**: Portas de motores (Right, Back, Left), raio da roda em mm, PPR do encoder, relação de redução (`1.0 / 61.0`) e cinemática holonômica.
- **Tração Diferencial / Tanque (2 Motores)**: Portas de motores, inversão de lado, raio da roda e controle arcade/tank drive.
- **Garra / Manipulador**: Motor Titan, encoder opcional, velocidade padrão, threshold de RPM e telemetria no `SmartDashboard`.
- **Atuador Servo**: Canal do servo no Titan e ângulo inicial.
- **Comando Personalizado (`CommandBase`)**: Temporizado ou contínuo com ciclo de vida WPILib (`initialize`, `execute`, `end`, `isFinished`).

### 3. 🔗 Acoplamento Automático (Injeção de Dependências)
Não gera apenas o arquivo solto. Conecta automaticamente o subsistema ao projeto:
- Injeta as constantes em `Constants.java`.
- Declara o atributo privado em `RobotContainer.java`.
- Instancia o subsistema no construtor `RobotContainer()` passando `titan`.
- Vincula ações a botões do controle Xbox (`whenHeld`, `whenPressed`).

### 4. 📄 Pré-Visualizador de Código
Permite inspecionar o código Java e os blocos de constantes antes de gravar no disco.

---

## 📂 Arquivos do Repositório

- **[main.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/main.py)**: Interface Desktop moderna em PySide6 (Dark Mode).
- **[class_generator.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/class_generator.py)**: Motor de geração de código Java e presets.
- **[coupler.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/coupler.py)**: Sistema de injeção e acoplamento em `RobotContainer.java` e `Constants.java`.
- **[project_generator.py](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/project_generator.py)**: Gerador da estrutura de novo projeto WPILib.
- **[PLANO_DE_ACAO.md](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/PLANO_DE_ACAO.md)**: Plano estratégico e roadmap da ferramenta.
- **[PROMPTS_DESENVOLVIMENTO.md](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/PROMPTS_DESENVOLVIMENTO.md)**: Prompts modulares prontos para expandir a solução.
- **[vendors/](file:///c:/Users/WorldSkills/Downloads/lab1Introducao/python/vendors)**: Arquivos JSON de dependências (Studica, NavX, Commands).
