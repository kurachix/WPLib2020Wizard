# WPILib 2020 Robot Wizard & Class Generator

Assistente gráfico para criação, parametrização e acoplamento automático de projetos e subsistemas WPILib 2020 (Java / GradleRIO), desenvolvido com foco em plataformas robóticas educacionais e de competição (WorldSkills Mobile Robotics / FRC / Studica VMX-pi com Titan Quad).

---

## 1. Visao Geral

Configurar um novo projeto no WPILib 2020 frequentemente exige tarefas repetitivas e propensas a erros:
- Criar a estrutura base do projeto GradleRIO;
- Copiar e configurar arquivos de dependencias de fornecedores (*vendor JSONs* como TitanQuad e WPILibNewCommands);
- Definir o numero da equipe e nome do projeto em multiplos arquivos de configuracao;
- Escrever classes de subsistemas (*Subsystems*) instanciando motores Titan, encoders, servos e sensores de fim de curso;
- Registrar constantes de portas e canais no arquivo `Constants.java`;
- Instanciar subsistemas e injetar comandos no arquivo `RobotContainer.java`.

Este software automatiza todo esse fluxo por meio de uma interface grafica moderna desenvolvida em PySide6 (Qt para Python), com validacao em tempo real, gerador universal parametrizavel e sistema de acoplamento automatico de codigo.

---

## 2. Estrutura do Repositorio

```
lab1Introducao/
│
├── build_exe.bat              # Script em lote para compilacao facil em .exe
├── requirements.txt           # Dependencias Python do projeto
├── README.md                  # Documentacao principal
│
├── template/                  # Template base limpo do projeto WPILib 2020
│   ├── build.gradle
│   ├── settings.gradle
│   ├── .project
│   ├── .wpilib/
│   │   └── wpilib_preferences.json
│   ├── vendordeps/
│   └── src/main/java/frc/robot/
│       ├── Main.java
│       ├── Robot.java
│       ├── RobotContainer.java
│       └── Constants.java
│
└── python/                    # Codigo-fonte do assistente em Python
    ├── main.py                # Interface grafica (PySide6)
    ├── class_generator.py     # Motor de geracao de codigo Java (Universal + Presets)
    ├── project_generator.py   # Gerenciador de criacao e clonagem de projetos
    ├── coupler.py             # Injetor automatico de codigo em Constants e RobotContainer
    ├── build.py               # Script de automacao PyInstaller
    ├── build_exe.bat          # Atalho local de compilacao
    └── vendors/               # Bibliotecas de terceiros (Studica / VMX / WPILib)
        ├── Studica-2020.1.1.json
        ├── TitanQuad-2020.1.1.json
        ├── VMX-pi-2020.1.1.json
        └── WPILibNewCommands.json
```

---

## 3. Pre-requisitos

Para rodar o assistente em ambiente de desenvolvimento ou gerar uma nova versao em executavel:
- Python 3.10 ou superior instalado no Windows;
- Pip devidamente configurado nas variaveis de ambiente do sistema.

Para compilar e descarregar o codigo Java gerado no robo:
- Java JDK 11 (padrao WPILib 2020);
- VS Code com a extensao WPILib 2020 ou GradleRIO configurado.

---

## 4. Instalacao

Abra um terminal (PowerShell ou Prompt de Comando) na pasta raiz do repositorio e execute:

```powershell
pip install -r requirements.txt
```

Isso instalara as bibliotecas necessarias:
- `PySide6`: Interface grafica com suporte nativo a dark mode e widgets Qt;
- `pyinstaller`: Ferramenta para empacotamento em arquivo `.exe` autocontido.

---

## 5. Como Executar

### Opcao A: Execucao Direta via Python
Na pasta raiz do projeto, execute:

```powershell
python python/main.py
```

### Opcao B: Executar via Aplicativo Compilado (.exe)
Caso o executavel ja tenha sido compilado, basta executar:

```powershell
python\dist\WPILib2020Wizard\WPILib2020Wizard.exe
```

---

## 6. Como Compilar para Executavel (.exe)

O projeto possui rotinas automatizadas para gerar um executavel standalone do Windows sem necessidade de abrir o terminal.

### Metodo 1: Script em Lote (Recomendado)
De um duplo clique no arquivo:
```
build_exe.bat
```
localizado na raiz do projeto. O script chamara o compilador e gerara a pasta da aplicacao.

### Metodo 2: Linha de Comando
Execute o script de build em Python:
```powershell
python python/build.py
```

O executavel sera gerado no seguinte diretorio:
```
python/dist/WPILib2020Wizard/WPILib2020Wizard.exe
```
Todas as dependencias e a pasta `vendors` sao automaticamente empacotadas junto ao executavel.

---

## 7. Funcionalidades do Software

### 7.1. Assistente de Novo Projeto
1. **Nome do Projeto**: Configura o nome do robo e altera automaticamente o `.project` e o `settings.gradle`.
2. **Numero da Equipe**: Atualiza automaticamente a chave `teamNumber` no arquivo `.wpilib/wpilib_preferences.json`.
3. **Diretorio de Destino**: Permite selecionar qualquer pasta do computador para onde o template completo sera copiado.
4. **Selecao de Vendors**: Copia seletivamente as definicoes JSON dos fornecedores (TitanQuad, Studica, VMX-pi, WPILibNewCommands) diretamente para a pasta `vendordeps/` do novo projeto.
5. **Configuracao Inicial de Hardware**: Gera subsistemas iniciais e acoplamento basico logo na criacao do projeto.

### 7.2. Gerador Universal de Classes & Presets
O gerador de classes permite criar subsistemas e comandos de forma rapida e padronizada:
- **Gerador Universal (Preset Principal)**:
  - Definicao customizada de 1 a 4 motores Titan (Canais 0 a 3, inversoes independentes);
  - Adicao opcional de 0 a 4 encoders (Distancia por pulso, reset);
  - Adicao opcional de 0 a 4 sensores de fim de curso digitais;
  - Adicao opcional de 0 a 4 servomotores;
  - Metodos prontos de teleoperado, parada e telemetria via SmartDashboard.
- **Preset Chassi Omni 3 Rodas**:
  - Cinematica de holonomica com 3 motores Titan (M0, M1, M2 posicionados a 120 graus);
  - Controle integrado de translacao (X/Y) e rotacao com calculo trigonometrico;
  - Integracao opcional com giroscopio VMX-pi (Yaw).
- **Preset Chassi Diferencial (Tank Drive)**:
  - Configuracao tradicional de robo com tracao esquerda e direita;
  - Modos Arcade Drive e Tank Drive prontos para joystick.
- **Preset Garra Mecanica / Manipulador**:
  - Suporte a acionamento por Servo ou Motor Titan com sensores de abertura e fechamento.
- **Preset Braco Elevador com Limite de Curso**:
  - Controle de subida/descida com paradas de seguranca por microswitches ou encoders.
- **Gerador de Comandos**:
  - Comandos instantaneos (*InstantCommand*) ou comandos sequenciais continuos (*CommandBase*) ja integrados ao subsistema escolhido.

### 7.3. Modulo de Acoplamento Automatico
Permite associar automaticamente qualquer subsistema gerado ao projeto:
- **Constants.java**: Insere de forma segura os IDs dos canais de motores, inversoes e portas de sensores, sem sobrescrever constantes existentes.
- **RobotContainer.java**: Adiciona os imports necessarios, declara e instancia o subsistema como atributo de `RobotContainer` e cria os metodos de acesso (*getters*).

### 7.4. Modais de Informacoes Tecnicas
Cada aba e etapa da interface grafica conta com o botao **[ ? ] Informacoes Desta Etapa**, fornecendo orientacoes contextuais e instrucoes tecnicas para programadores de todos os niveis de experiencia.

---

## 8. Licenca

Desenvolvido para fins educacionais e de capacitacao técnica em robotica movel e sistemas embarcados.
