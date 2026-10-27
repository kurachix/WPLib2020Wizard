"""
WPILib 2020 Robot Wizard & Class Generator
Interface Grafica Desktop desenvolvida em PySide6 para Studica VMX-pi e Titan Quad.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QSpinBox, QDoubleSpinBox, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout, QDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from class_generator import ClassGenerator
from project_generator import ProjectGenerator
from coupler import ProjectCoupler


class InfoDialog(QDialog):
    """Janela modal para exibicao de informacoes e explicacoes detalhadas de cada etapa."""

    def __init__(self, title: str, subtitle: str, html_content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 560)

        layout = QVBoxLayout(self)

        # Cabecalho do Dialogo
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_title.setStyleSheet("color: #89b4fa;")
        layout.addWidget(lbl_title)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("color: #a6adc8; font-style: italic; margin-bottom: 8px;")
        layout.addWidget(lbl_sub)

        # Area de Texto Informativo com HTML formatado
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setHtml(html_content)
        text_area.setStyleSheet("""
            background-color: #181825;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 8px;
            padding: 12px;
            font-size: 13px;
            line-height: 1.5;
        """)
        layout.addWidget(text_area)

        # Botao Fechar
        btn_close = QPushButton("Entendido / Fechar")
        btn_close.setFixedHeight(38)
        btn_close.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        # Tema escuro para o dialogo
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WPILib 2020 Robot Wizard - Studica VMX-pi / Titan Quad")
        self.resize(960, 750)

        # Estado atual de codigo gerado
        self.current_subsystem_code = ""
        self.current_constants_code = ""
        self.current_class_name = ""

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Cabecalho Principal
        header_label = QLabel("WPILib 2020 Robot Wizard & Class Generator")
        header_font = QFont("Segoe UI", 16, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        subtitle_label = QLabel(
            "Criacao guiada de projetos, geracao de classes parametrizadas e acoplamento automatico de hardware."
        )
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #a6adc8; margin-bottom: 6px;")
        main_layout.addWidget(subtitle_label)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Inicializacao das Abas
        self.create_tab_new_project()
        self.create_tab_class_generator()
        self.create_tab_coupler()
        self.create_tab_code_preview()

        self.apply_dark_theme()

    # ==========================================
    # ABA 1: NOVO PROJETO
    # ==========================================
    def create_tab_new_project(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Barra Superior com Titulo e Botao de Informacoes
        top_bar = QHBoxLayout()
        lbl_section = QLabel("Configuracoes para Criacao do Projeto WPILib 2020")
        lbl_section.setFont(QFont("Segoe UI", 11, QFont.Bold))
        top_bar.addWidget(lbl_section)
        top_bar.addStretch()

        btn_info = QPushButton("[ ? ] Informacoes Desta Etapa")
        btn_info.setStyleSheet("background-color: #45475a; color: #89b4fa; padding: 6px 14px;")
        btn_info.clicked.connect(self.show_info_new_project)
        top_bar.addWidget(btn_info)
        layout.addLayout(top_bar)

        box = QGroupBox("Parametros do Projeto")
        form = QFormLayout(box)

        self.input_proj_name = QLineEdit("RoboWorldSkills2026")
        self.input_proj_name.setToolTip("Nome da pasta e identificador raiz do projeto Gradle.")
        form.addRow("Nome do Projeto:", self.input_proj_name)

        h_dir = QHBoxLayout()
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.input_proj_dir = QLineEdit(default_dir)
        self.input_proj_dir.setToolTip("Diretorio no disco onde a pasta do projeto sera gerada.")
        btn_browse_dir = QPushButton("Selecionar Pasta...")
        btn_browse_dir.clicked.connect(self.browse_project_dir)
        h_dir.addWidget(self.input_proj_dir)
        h_dir.addWidget(btn_browse_dir)
        form.addRow("Diretorio de Destino:", h_dir)

        self.input_team_number = QSpinBox()
        self.input_team_number.setRange(0, 99999)
        self.input_team_number.setValue(502)
        self.input_team_number.setToolTip("Numero da equipe gravado no arquivo .wpilib/wpilib_preferences.json.")
        form.addRow("Numero da Equipe (Team Number):", self.input_team_number)

        self.input_titan_id = QSpinBox()
        self.input_titan_id.setRange(1, 63)
        self.input_titan_id.setValue(42)
        self.input_titan_id.setToolTip("Endereco no barramento CAN da placa Titan Quad (Padrao de fabrica: 42).")
        form.addRow("Titan Quad CAN ID:", self.input_titan_id)

        # Vendors
        vendors_box = QGroupBox("Dependencias de Fornecedores (vendordeps)")
        v_layout = QVBoxLayout(vendors_box)
        self.chk_studica = QCheckBox("Studica.json (Bibliotecas do Titan Quad, VMX-pi, Motores e Servos)")
        self.chk_studica.setChecked(True)
        self.chk_commands = QCheckBox("WPILibNewCommands.json (Framework Command-Based: SubsystemBase e CommandBase)")
        self.chk_commands.setChecked(True)
        self.chk_navx = QCheckBox("navx_frc.json (Giroscopio / IMU NavX da KauaiLabs)")
        self.chk_navx.setChecked(True)
        v_layout.addWidget(self.chk_studica)
        v_layout.addWidget(self.chk_commands)
        v_layout.addWidget(self.chk_navx)
        form.addRow("Vendors Incluidos:", vendors_box)

        layout.addWidget(box)

        btn_create = QPushButton("Criar Estrutura Completa do Projeto WPILib")
        btn_create.setFixedHeight(45)
        btn_create.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_create.clicked.connect(self.action_create_project)
        layout.addWidget(btn_create)

        layout.addStretch()
        self.tabs.addTab(tab, "Novo Projeto")

    def show_info_new_project(self):
        title = "Informacoes: Criacao de Novo Projeto"
        subtitle = "Entenda como a estrutura do projeto WPILib 2020 e configurada para o VMX-pi / Studica"
        html = """
        <h3>O que esta etapa realiza?</h3>
        <p>Esta etapa clona a pasta base <b>template</b> oficial do WPILib 2020 e <b>adapta automaticamente todos os arquivos</b> para o novo nome escolhido pelo usuario.</p>
        
        <h3>Como a pasta template e adaptada:</h3>
        <ul>
            <li><b>Copia Limpa:</b> Todos os arquivos essenciais de configuracao (.vscode, gradlew, gradle wrapper, src/) sao copiados, ignorando automaticamente pastas temporarias de build (como .gradle, build e bin).</li>
            <li><b>Adaptacao do .project:</b> O nome do projeto dentro do arquivo <code>.project</code> e substituido de <i>template</i> para o novo nome informado.</li>
            <li><b>Adaptacao do settings.gradle:</b> A definicao <code>rootProject.name = "NovoNome"</code> e atualizada.</li>
            <li><b>Injecao do Titan CAN ID:</b> O arquivo <code>Constants.java</code> recebe a constante <code>TITAN_ID</code> configurada.</li>
            <li><b>Vendordeps Atualizados:</b> Os arquivos JSON selecionados da pasta <i>vendors/</i> sao transferidos para a pasta <code>vendordeps/</code> do novo projeto.</li>
        </ul>

        <h3>Explicacao dos campos:</h3>
        <ul>
            <li><b>Nome do Projeto:</b> Define o nome da pasta de destino e a propriedade do projeto Gradle.</li>
            <li><b>Diretorio de Destino:</b> O local no seu computador onde a nova pasta do projeto sera criada.</li>
            <li><b>Numero da Equipe (Team Number):</b> Gravado diretamente no arquivo <code>.wpilib/wpilib_preferences.json</code>. E utilizado pelo GradleRIO para identificar o robo na rede durante o deploy (IP mDNS <i>roborio-TEAM-frc.local</i> ou <i>10.TE.AM.2</i>).</li>
            <li><b>Titan Quad CAN ID (Padrao 42):</b> O identificador numerico unico da placa controladora de motores no barramento CAN.</li>
            <li><b>Vendors Incluidos:</b> Copia Studica.json, WPILibNewCommands.json e navx_frc.json para que todas as bibliotecas de hardware compilem imediatamente.</li>
        </ul>
        """
        dlg = InfoDialog(title, subtitle, html, self)
        dlg.exec()

    def browse_project_dir(self):
        dir_selected = QFileDialog.getExistingDirectory(self, "Selecionar Diretorio de Destino")
        if dir_selected:
            self.input_proj_dir.setText(dir_selected)

    def action_create_project(self):
        vendors = []
        if self.chk_studica.isChecked():
            vendors.append("Studica.json")
        if self.chk_commands.isChecked():
            vendors.append("WPILibNewCommands.json")
        if self.chk_navx.isChecked():
            vendors.append("navx_frc.json")

        params = {
            "project_name": self.input_proj_name.text().strip(),
            "target_dir": self.input_proj_dir.text().strip(),
            "team_number": self.input_team_number.value(),
            "titan_id": self.input_titan_id.value(),
            "vendors": vendors
        }

        try:
            path = ProjectGenerator.create_project(params)
            QMessageBox.information(
                self, "Projeto Criado",
                f"Estrutura gerada com sucesso em:\n{path}\n\nO projeto esta pronto para ser aberto no VS Code."
            )
            self.input_couple_proj_path.setText(path)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao criar projeto", str(e))

    # ==========================================
    # ABA 2: GERADOR DE CLASSES COM PRESETS
    # ==========================================
    def create_tab_class_generator(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Barra Superior com Titulo e Botao de Informacoes
        top_bar = QHBoxLayout()
        lbl_section = QLabel("Gerador de Classes e Subsistemas com Presets Parametrizados")
        lbl_section.setFont(QFont("Segoe UI", 11, QFont.Bold))
        top_bar.addWidget(lbl_section)
        top_bar.addStretch()

        btn_info = QPushButton("[ ? ] Informacoes Desta Etapa")
        btn_info.setStyleSheet("background-color: #45475a; color: #89b4fa; padding: 6px 14px;")
        btn_info.clicked.connect(self.show_info_class_generator)
        top_bar.addWidget(btn_info)
        layout.addLayout(top_bar)

        top_h = QHBoxLayout()
        top_h.addWidget(QLabel("Selecione o Preset:"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItems([
            "Gerador Universal (N Motores, Encoders, Sensores e Servos)",
            "Tracao Omni 3 Rodas (Kiwi Drive - Studica VMX)",
            "Tracao Diferencial / Tanque (2 Motores)",
            "Garra / Manipulador (Motor + Encoder)",
            "Atuador Servo Motor (Studica Titan)",
            "Comando Personalizado (CommandBase)"
        ])
        self.combo_preset.currentIndexChanged.connect(self.on_preset_changed)
        top_h.addWidget(self.combo_preset)
        layout.addLayout(top_h)

        # Area de Formulario Dinamico
        self.preset_form_group = QGroupBox("Parametros Personalizados (Defina os Valores Antes de Gerar)")
        self.preset_form = QFormLayout(self.preset_form_group)
        layout.addWidget(self.preset_form_group)

        # Botoes de Acao
        btn_h = QHBoxLayout()
        btn_preview = QPushButton("Pre-visualizar Codigo")
        btn_preview.clicked.connect(self.action_preview_preset_code)
        btn_save = QPushButton("Salvar Classe no Projeto")
        btn_save.clicked.connect(self.action_save_preset_code)
        btn_h.addWidget(btn_preview)
        btn_h.addWidget(btn_save)
        layout.addLayout(btn_h)

        self.build_preset_form(0)

        layout.addStretch()
        self.tabs.addTab(tab, "Gerador de Classes")

    def show_info_class_generator(self):
        title = "Informacoes: Gerador de Classes e Presets"
        subtitle = "Como funcionam os subsistemas, calculos de cinemática e parametros fisicos"
        html = """
        <h3>O que e um Subsistema (Subsystem)?</h3>
        <p>No modelo WPILib Command-Based, um <b>Subsystem</b> e uma classe Java que herda de <code>SubsystemBase</code>. Ele e responsavel por encapsular o hardware fisico do robo (motores, atuadores, sensores) e disponibilizar metodos publicos de controle de alto nivel (como <code>setMotors</code>, <code>stop</code>, <code>getRPM</code>).</p>

        <h3>Explicacao detalhada de cada Preset disponivel:</h3>
        <ul>
            <li><b>Gerador Universal (N Motores, Encoders, Sensores e Servos):</b>
                <p><b>A solucao definitiva sob medida:</b> voce escolhe exatamente quantos motores o robo possui (1, 2, 3 ou 4), o nome de cada motor, a porta no Titan (M0 a M3) e se o sentido deve ser invertido. Tambem permite adicionar de 0 a 4 encoders, de 0 a 4 sensores digitais de fim de curso e de 0 a 4 servomotores. O codigo e gerado com metodos de acionamento individual, conjunto, telemetria completa no SmartDashboard e botao de seguranca <code>stop()</code>.</p>
            </li>
            <li><b>Tracao Omni 3 Rodas (Kiwi Drive - Holonomica):</b>
                <p>E a configuracao classica da modalidade WorldSkills Autonomous Mobile Robotics. Tres rodas omnidirecionais montadas a 120 graus entre si permitem que o robo se desloque para qualquer direcao no plano (frente, tras, esquerda, direita) simultaneamente com rotacao.</p>
                <ul>
                    <li><i>Portas dos Motores (Direito, Traseiro, Esquerdo):</i> Indicam os canais M0, M1, M2 ou M3 do Titan Quad onde cada cabo de motor esta fisicamente ligado.</li>
                    <li><i>Raio da Roda (mm):</i> Utilizado na formula geometrica de deslocamento linear.</li>
                    <li><i>Pulsos por Revolucao (PPR):</i> Quantidade de pulsos gerados pelo encoder para cada 1 volta completa do eixo do motor (o encoder Studica gera tipicamente 1440 pulsos).</li>
                    <li><i>Relacao de Reducao (Gear Ratio):</i> Razao mecanica da caixa de reducao. <b>Importante:</b> Deve ser expressa com casas decimais (ex: <code>1.0 / 61.0</code>) para evitar o erro de divisao inteira do Java, onde <code>1 / 61</code> resulta em <code>0</code>.</li>
                </ul>
            </li>
            <li><b>Tracao Diferencial / Tanque (2 Motores):</b>
                <p>Configuracao tradicional com duas rodas motrizes independentes (esquerda e direita). O gerador implementa controle estilo <i>Arcade Drive</i> (um eixo controla velocidade e o outro controla rotacao) e inversao automatica do motor direito.</p>
            </li>
            <li><b>Garra / Manipulador (Motor + Encoder):</b>
                <p>Mecanismo de captura, ingestao ou rolamentos. Inclui leitura em tempo real de rotacao por minuto (RPM) e o metodo <code>isAtSpeed()</code>, que indica se a garra atingiu a velocidade necessaria ou se encontrou resistencia (objeto capturado).</p>
            </li>
            <li><b>Atuador Servo Motor:</b>
                <p>Controla servomotores padrao atraves das saidas dedicadas de 3 pinos (PWM) do Titan Quad (canais 0 a 7), aceitando angulos de 0 a 180 graus.</p>
            </li>
            <li><b>Comando Personalizado (CommandBase):</b>
                <p>Cria uma acao independente que opera sobre um subsistema. Gerencia o ciclo de vida: <code>initialize()</code> (inicio da acao), <code>execute()</code> (repetido a cada 20ms), <code>end()</code> (parada e limpeza) e <code>isFinished()</code> (condicao de termino por tempo ou sensor).</p>
            </li>
        </ul>
        """
        dlg = InfoDialog(title, subtitle, html, self)
        dlg.exec()

    def on_preset_changed(self, index):
        self.build_preset_form(index)

    def clear_preset_form(self):
        while self.preset_form.rowCount() > 0:
            self.preset_form.removeRow(0)

    def update_universal_motor_visibility(self, count):
        for i, w in enumerate(self.u_motor_widgets):
            w.setVisible(i < count)

    def update_universal_encoder_visibility(self, count):
        for i, w in enumerate(self.u_encoder_widgets):
            w.setVisible(i < count)

    def update_universal_limit_visibility(self, count):
        for i, w in enumerate(self.u_limit_widgets):
            w.setVisible(i < count)

    def update_universal_servo_visibility(self, count):
        for i, w in enumerate(self.u_servo_widgets):
            w.setVisible(i < count)

    def build_preset_form(self, index):
        self.clear_preset_form()

        if index == 0:  # Gerador Universal
            self.u_class_name = QLineEdit("MecanismoUniversal")
            self.u_class_name.setToolTip("Nome da classe Java do subsistema.")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.u_class_name)

            # --- MOTORES ---
            self.u_motor_count = QSpinBox()
            self.u_motor_count.setRange(1, 4)
            self.u_motor_count.setValue(2)
            self.u_motor_count.setToolTip("Quantos motores Titan serao instanciados no subsistema.")
            self.preset_form.addRow("Quantidade de Motores (1 a 4):", self.u_motor_count)

            self.u_motor_widgets = []
            self.u_motors_data = []
            default_motor_names = ["motorPrincipal", "motorSecundario", "motorExtra1", "motorExtra2"]
            for i in range(4):
                m_widget = QWidget()
                m_layout = QHBoxLayout(m_widget)
                m_layout.setContentsMargins(0, 2, 0, 2)

                name_input = QLineEdit(default_motor_names[i])
                name_input.setPlaceholderText(f"Nome do Motor {i+1}")

                port_spin = QSpinBox()
                port_spin.setRange(0, 3)
                port_spin.setValue(i)
                port_spin.setPrefix("Canal M")

                inv_chk = QCheckBox("Inverter")
                inv_chk.setChecked(False)

                m_layout.addWidget(QLabel(f"Motor {i+1}:"))
                m_layout.addWidget(name_input, 2)
                m_layout.addWidget(port_spin, 1)
                m_layout.addWidget(inv_chk, 1)

                self.preset_form.addRow(m_widget)
                self.u_motor_widgets.append(m_widget)
                self.u_motors_data.append((name_input, port_spin, inv_chk))
                m_widget.setVisible(i < self.u_motor_count.value())

            self.u_motor_count.valueChanged.connect(self.update_universal_motor_visibility)

            # --- ENCODERS ---
            self.u_encoder_count = QSpinBox()
            self.u_encoder_count.setRange(0, 4)
            self.u_encoder_count.setValue(1)
            self.u_encoder_count.setToolTip("Quantos encoders opticos serao lidos pelo Titan.")
            self.preset_form.addRow("Quantidade de Encoders (0 a 4):", self.u_encoder_count)

            self.u_encoder_widgets = []
            self.u_encoders_data = []
            default_enc_names = ["encoder1", "encoder2", "encoder3", "encoder4"]
            for i in range(4):
                e_widget = QWidget()
                e_layout = QHBoxLayout(e_widget)
                e_layout.setContentsMargins(0, 2, 0, 2)

                e_name = QLineEdit(default_enc_names[i])
                e_ch = QSpinBox()
                e_ch.setRange(0, 3)
                e_ch.setValue(i)
                e_ch.setPrefix("Canal ")

                e_ppr = QDoubleSpinBox()
                e_ppr.setRange(1.0, 10000.0)
                e_ppr.setValue(1440.0)
                e_ppr.setSuffix(" PPR")

                e_layout.addWidget(QLabel(f"Encoder {i+1}:"))
                e_layout.addWidget(e_name, 2)
                e_layout.addWidget(e_ch, 1)
                e_layout.addWidget(e_ppr, 1)

                self.preset_form.addRow(e_widget)
                self.u_encoder_widgets.append(e_widget)
                self.u_encoders_data.append((e_name, e_ch, e_ppr))
                e_widget.setVisible(i < self.u_encoder_count.value())

            self.u_encoder_count.valueChanged.connect(self.update_universal_encoder_visibility)

            # --- FIM DE CURSO (DIGITALINPUT) ---
            self.u_limit_count = QSpinBox()
            self.u_limit_count.setRange(0, 4)
            self.u_limit_count.setValue(0)
            self.u_limit_count.setToolTip("Quantos sensores fim de curso digitais (DigitalInput) serao conectados.")
            self.preset_form.addRow("Sensores Fim de Curso (0 a 4):", self.u_limit_count)

            self.u_limit_widgets = []
            self.u_limits_data = []
            default_limit_names = ["limiteInferior", "limiteSuperior", "sensorFim3", "sensorFim4"]
            for i in range(4):
                l_widget = QWidget()
                l_layout = QHBoxLayout(l_widget)
                l_layout.setContentsMargins(0, 2, 0, 2)

                l_name = QLineEdit(default_limit_names[i])
                l_ch = QSpinBox()
                l_ch.setRange(0, 7)
                l_ch.setValue(i)
                l_ch.setPrefix("DIO ")

                l_layout.addWidget(QLabel(f"Sensor {i+1}:"))
                l_layout.addWidget(l_name, 2)
                l_layout.addWidget(l_ch, 1)

                self.preset_form.addRow(l_widget)
                self.u_limit_widgets.append(l_widget)
                self.u_limits_data.append((l_name, l_ch))
                l_widget.setVisible(i < self.u_limit_count.value())

            self.u_limit_count.valueChanged.connect(self.update_universal_limit_visibility)

            # --- SERVOS ---
            self.u_servo_count = QSpinBox()
            self.u_servo_count.setRange(0, 4)
            self.u_servo_count.setValue(0)
            self.preset_form.addRow("Servos Motores (0 a 4):", self.u_servo_count)

            self.u_servo_widgets = []
            self.u_servos_data = []
            default_servo_names = ["servoGarra", "servoCamera", "servoExtra3", "servoExtra4"]
            for i in range(4):
                s_widget = QWidget()
                s_layout = QHBoxLayout(s_widget)
                s_layout.setContentsMargins(0, 2, 0, 2)

                s_name = QLineEdit(default_servo_names[i])
                s_ch = QSpinBox()
                s_ch.setRange(0, 7)
                s_ch.setValue(i)
                s_ch.setPrefix("PWM ")

                s_angle = QDoubleSpinBox()
                s_angle.setRange(0.0, 180.0)
                s_angle.setValue(90.0)
                s_angle.setSuffix(" °")

                s_layout.addWidget(QLabel(f"Servo {i+1}:"))
                s_layout.addWidget(s_name, 2)
                s_layout.addWidget(s_ch, 1)
                s_layout.addWidget(s_angle, 1)

                self.preset_form.addRow(s_widget)
                self.u_servo_widgets.append(s_widget)
                self.u_servos_data.append((s_name, s_ch, s_angle))
                s_widget.setVisible(i < self.u_servo_count.value())

            self.u_servo_count.valueChanged.connect(self.update_universal_servo_visibility)

        elif index == 1:  # Omni 3 Rodas
            self.f_class_name = QLineEdit("DriveTrain")
            self.f_class_name.setToolTip("Nome do arquivo Java e da classe do subsistema.")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.f_class_name)

            self.f_m_right = QSpinBox()
            self.f_m_right.setRange(0, 3)
            self.f_m_right.setValue(0)
            self.f_m_right.setToolTip("Canal no Titan Quad (M0 a M3) para a roda direita.")
            self.preset_form.addRow("Porta Motor Direito (Right):", self.f_m_right)

            self.f_m_back = QSpinBox()
            self.f_m_back.setRange(0, 3)
            self.f_m_back.setValue(2)
            self.f_m_back.setToolTip("Canal no Titan Quad (M0 a M3) para a roda traseira.")
            self.preset_form.addRow("Porta Motor Traseiro (Back):", self.f_m_back)

            self.f_m_left = QSpinBox()
            self.f_m_left.setRange(0, 3)
            self.f_m_left.setValue(3)
            self.f_m_left.setToolTip("Canal no Titan Quad (M0 a M3) para a roda esquerda.")
            self.preset_form.addRow("Porta Motor Esquerdo (Left):", self.f_m_left)

            self.f_wheel_radius = QDoubleSpinBox()
            self.f_wheel_radius.setRange(1.0, 500.0)
            self.f_wheel_radius.setValue(55.0)
            self.f_wheel_radius.setSuffix(" mm")
            self.f_wheel_radius.setToolTip("Raio da roda omnidirecional em milimetros (ex: 55 mm para roda de 110 mm de diametro).")
            self.preset_form.addRow("Raio da Roda (Omni):", self.f_wheel_radius)

            self.f_ppr = QDoubleSpinBox()
            self.f_ppr.setRange(1.0, 10000.0)
            self.f_ppr.setValue(1440.0)
            self.f_ppr.setToolTip("Pulsos por Revolucao do encoder optico do motor (Padrao Studica: 1440).")
            self.preset_form.addRow("Pulsos por Revolucao (PPR):", self.f_ppr)

            self.f_gear_ratio = QLineEdit("1.0 / 61.0")
            self.f_gear_ratio.setToolTip("Relacao de reducao mecânica da caixa de transmissao. Sempre em formato de ponto flutuante.")
            self.preset_form.addRow("Relacao de Reducao (Gear Ratio):", self.f_gear_ratio)

        elif index == 2:  # Tracao Tanque
            self.f_class_name = QLineEdit("DriveTrain")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.f_class_name)

            self.f_m_left = QSpinBox()
            self.f_m_left.setRange(0, 3)
            self.f_m_left.setValue(0)
            self.preset_form.addRow("Porta Motor Esquerdo:", self.f_m_left)

            self.f_m_right = QSpinBox()
            self.f_m_right.setRange(0, 3)
            self.f_m_right.setValue(1)
            self.preset_form.addRow("Porta Motor Direito:", self.f_m_right)

            self.f_invert_right = QCheckBox("Inverter sentido do motor direito")
            self.f_invert_right.setChecked(True)
            self.preset_form.addRow("Inversao de Rotacao:", self.f_invert_right)

            self.f_wheel_radius = QDoubleSpinBox()
            self.f_wheel_radius.setValue(50.0)
            self.f_wheel_radius.setSuffix(" mm")
            self.preset_form.addRow("Raio da Roda:", self.f_wheel_radius)

            self.f_ppr = QDoubleSpinBox()
            self.f_ppr.setValue(1440.0)
            self.preset_form.addRow("Pulsos por Revolucao (PPR):", self.f_ppr)

        elif index == 3:  # Garra
            self.f_class_name = QLineEdit("GarraSubsystem")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.f_class_name)

            self.f_motor_id = QSpinBox()
            self.f_motor_id.setRange(0, 3)
            self.f_motor_id.setValue(2)
            self.preset_form.addRow("Porta do Motor no Titan:", self.f_motor_id)

            self.f_has_encoder = QCheckBox("Instanciar Encoder Optico")
            self.f_has_encoder.setChecked(True)
            self.preset_form.addRow("Encoder:", self.f_has_encoder)

            self.f_encoder_ch = QSpinBox()
            self.f_encoder_ch.setRange(0, 3)
            self.f_encoder_ch.setValue(2)
            self.preset_form.addRow("Canal do Encoder:", self.f_encoder_ch)

            self.f_ppr = QDoubleSpinBox()
            self.f_ppr.setValue(1440.0)
            self.preset_form.addRow("Pulsos por Revolucao (PPR):", self.f_ppr)

            self.f_speed = QDoubleSpinBox()
            self.f_speed.setRange(0.0, 1.0)
            self.f_speed.setSingleStep(0.1)
            self.f_speed.setValue(0.8)
            self.preset_form.addRow("Velocidade Padrao (0 a 1):", self.f_speed)

            self.f_threshold = QDoubleSpinBox()
            self.f_threshold.setRange(0.0, 5000.0)
            self.f_threshold.setValue(100.0)
            self.preset_form.addRow("Threshold de RPM (isAtSpeed):", self.f_threshold)

        elif index == 4:  # Servo
            self.f_class_name = QLineEdit("ServoSubsystem")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.f_class_name)

            self.f_servo_ch = QSpinBox()
            self.f_servo_ch.setRange(0, 7)
            self.f_servo_ch.setValue(0)
            self.preset_form.addRow("Canal do Servo no Titan (0-7):", self.f_servo_ch)

            self.f_servo_angle = QDoubleSpinBox()
            self.f_servo_angle.setRange(0.0, 180.0)
            self.f_servo_angle.setValue(90.0)
            self.f_servo_angle.setSuffix(" °")
            self.preset_form.addRow("Angulo Inicial Padrao:", self.f_servo_angle)

        elif index == 5:  # Comando
            self.f_command_name = QLineEdit("AtivarMecanismo")
            self.preset_form.addRow("Nome da Classe Command:", self.f_command_name)

            self.f_target_subsystem = QLineEdit("GarraSubsystem")
            self.preset_form.addRow("Classe do Subsistema Alvo:", self.f_target_subsystem)

            self.f_cmd_type = QComboBox()
            self.f_cmd_type.addItems(["Temporizado (Executa por X segundos)", "Continuo (Até ser cancelado)"])
            self.preset_form.addRow("Tipo de Execucao:", self.f_cmd_type)

            self.f_cmd_duration = QDoubleSpinBox()
            self.f_cmd_duration.setRange(0.1, 60.0)
            self.f_cmd_duration.setValue(2.5)
            self.f_cmd_duration.setSuffix(" s")
            self.preset_form.addRow("Duracao do Comando:", self.f_cmd_duration)

    def generate_current_preset(self):
        index = self.combo_preset.currentIndex()
        if index == 0:  # Gerador Universal
            motors = []
            for i in range(self.u_motor_count.value()):
                name_w, port_w, inv_w = self.u_motors_data[i]
                motors.append({
                    "name": name_w.text().strip() or f"motor{i+1}",
                    "port": port_w.value(),
                    "inverted": inv_w.isChecked()
                })

            encoders = []
            for i in range(self.u_encoder_count.value()):
                name_w, ch_w, ppr_w = self.u_encoders_data[i]
                encoders.append({
                    "name": name_w.text().strip() or f"encoder{i+1}",
                    "channel": ch_w.value(),
                    "ppr": ppr_w.value()
                })

            limit_switches = []
            for i in range(self.u_limit_count.value()):
                name_w, ch_w = self.u_limits_data[i]
                limit_switches.append({
                    "name": name_w.text().strip() or f"fimDeCurso{i+1}",
                    "channel": ch_w.value()
                })

            servos = []
            for i in range(self.u_servo_count.value()):
                name_w, ch_w, angle_w = self.u_servos_data[i]
                servos.append({
                    "name": name_w.text().strip() or f"servo{i+1}",
                    "channel": ch_w.value(),
                    "default_angle": angle_w.value()
                })

            params = {
                "class_name": self.u_class_name.text().strip() or "MecanismoUniversal",
                "motors": motors,
                "encoders": encoders,
                "limit_switches": limit_switches,
                "servos": servos
            }
            code_java, code_const = ClassGenerator.generate_universal_subsystem(params)
            self.current_class_name = params["class_name"]
            self.current_subsystem_code = code_java
            self.current_constants_code = code_const
            return code_java, code_const, "subsystems"

        elif index == 1:  # Omni 3
            params = {
                "class_name": self.f_class_name.text().strip(),
                "motor_right": self.f_m_right.value(),
                "motor_back": self.f_m_back.value(),
                "motor_left": self.f_m_left.value(),
                "wheel_radius_mm": self.f_wheel_radius.value(),
                "ppr": self.f_ppr.value(),
                "gear_ratio": self.f_gear_ratio.text().strip()
            }
            code_java, code_const = ClassGenerator.generate_omni3_drivetrain(params)
            self.current_class_name = params["class_name"]
            self.current_subsystem_code = code_java
            self.current_constants_code = code_const
            return code_java, code_const, "subsystems"

        elif index == 2:  # Diferencial
            params = {
                "class_name": self.f_class_name.text().strip(),
                "motor_left": self.f_m_left.value(),
                "motor_right": self.f_m_right.value(),
                "invert_right": self.f_invert_right.isChecked(),
                "wheel_radius_mm": self.f_wheel_radius.value(),
                "ppr": self.f_ppr.value()
            }
            code_java, code_const = ClassGenerator.generate_differential_drivetrain(params)
            self.current_class_name = params["class_name"]
            self.current_subsystem_code = code_java
            self.current_constants_code = code_const
            return code_java, code_const, "subsystems"

        elif index == 3:  # Garra
            params = {
                "class_name": self.f_class_name.text().strip(),
                "motor_id": self.f_motor_id.value(),
                "has_encoder": self.f_has_encoder.isChecked(),
                "encoder_channel": self.f_encoder_ch.value(),
                "ppr": self.f_ppr.value(),
                "default_speed": self.f_speed.value(),
                "threshold_rpm": self.f_threshold.value()
            }
            code_java, code_const = ClassGenerator.generate_mechanism_subsystem(params)
            self.current_class_name = params["class_name"]
            self.current_subsystem_code = code_java
            self.current_constants_code = code_const
            return code_java, code_const, "subsystems"

        elif index == 4:  # Servo
            params = {
                "class_name": self.f_class_name.text().strip(),
                "servo_channel": self.f_servo_ch.value(),
                "default_angle": self.f_servo_angle.value()
            }
            code_java, code_const = ClassGenerator.generate_servo_subsystem(params)
            self.current_class_name = params["class_name"]
            self.current_subsystem_code = code_java
            self.current_constants_code = code_const
            return code_java, code_const, "subsystems"

        elif index == 5:  # Comando
            params = {
                "command_name": self.f_command_name.text().strip(),
                "subsystem_class": self.f_target_subsystem.text().strip(),
                "subsystem_var": "subsystem",
                "action_type": "timed" if self.f_cmd_type.currentIndex() == 0 else "continuous",
                "duration_sec": self.f_cmd_duration.value()
            }
            code_java = ClassGenerator.generate_command(params)
            self.current_class_name = params["command_name"]
            self.current_subsystem_code = code_java
            self.current_constants_code = ""
            return code_java, "", "commands"

        return "", "", ""

    def action_preview_preset_code(self):
        code_java, code_const, kind = self.generate_current_preset()
        preview_text = f"// ==========================================\n// ARQUIVO: {self.current_class_name}.java ({kind})\n// ==========================================\n\n{code_java}"
        if code_const:
            preview_text += f"\n\n// ==========================================\n// CONSTANTES PARA O Constants.java\n// ==========================================\n\n{code_const}"
        self.code_editor.setText(preview_text)
        self.tabs.setCurrentWidget(self.tab_preview)

    def action_save_preset_code(self):
        code_java, code_const, kind = self.generate_current_preset()
        proj_dir = self.input_couple_proj_path.text().strip()
        if not os.path.exists(proj_dir):
            QMessageBox.warning(
                self, "Projeto Nao Encontrado",
                "Informe o caminho valido da pasta raiz de um projeto WPILib na aba 'Acoplamento Automatico'."
            )
            return

        target_file = os.path.join(proj_dir, "src", "main", "java", "frc", "robot", kind, f"{self.current_class_name}.java")
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(code_java)

        if code_const:
            const_file = os.path.join(proj_dir, "src", "main", "java", "frc", "robot", "Constants.java")
            ProjectCoupler.inject_constants(const_file, code_const)

        QMessageBox.information(
            self, "Classe Salva",
            f"Arquivo gravado com sucesso em:\n{target_file}\n\nConstantes adicionadas ao arquivo Constants.java!"
        )

    # ==========================================
    # ABA 3: ACOPLAMENTO AUTOMÁTICO
    # ==========================================
    def create_tab_coupler(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Barra Superior com Titulo e Botao de Informacoes
        top_bar = QHBoxLayout()
        lbl_section = QLabel("Acoplamento e Injecao de Dependencias no RobotContainer")
        lbl_section.setFont(QFont("Segoe UI", 11, QFont.Bold))
        top_bar.addWidget(lbl_section)
        top_bar.addStretch()

        btn_info = QPushButton("[ ? ] Informacoes Desta Etapa")
        btn_info.setStyleSheet("background-color: #45475a; color: #89b4fa; padding: 6px 14px;")
        btn_info.clicked.connect(self.show_info_coupler)
        top_bar.addWidget(btn_info)
        layout.addLayout(top_bar)

        box = QGroupBox("Projeto WPILib Ativo")
        form = QFormLayout(box)

        default_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lab1Introducao"))
        h_proj = QHBoxLayout()
        self.input_couple_proj_path = QLineEdit(default_base)
        btn_browse = QPushButton("Selecionar Projeto...")
        btn_browse.clicked.connect(self.browse_couple_proj)
        h_proj.addWidget(self.input_couple_proj_path)
        h_proj.addWidget(btn_browse)
        form.addRow("Pasta Raiz do Projeto:", h_proj)
        layout.addWidget(box)

        box_couple = QGroupBox("Conectar Subsistema ao RobotContainer")
        form_couple = QFormLayout(box_couple)

        self.input_subsystem_class = QLineEdit("GarraSubsystem")
        self.input_subsystem_class.setToolTip("Nome exato da classe Java do subsistema que sera instanciado.")
        form_couple.addRow("Classe do Subsistema:", self.input_subsystem_class)

        self.input_subsystem_var = QLineEdit("m_garra")
        self.input_subsystem_var.setToolTip("Nome da variavel privada no RobotContainer (ex: m_garra, m_driveTrain).")
        form_couple.addRow("Nome da Variavel no Container:", self.input_subsystem_var)

        self.combo_xbox_btn = QComboBox()
        self.combo_xbox_btn.addItems([
            "Nenhum (Apenas instanciar sem vincular botoes)",
            "XboxController.Button.kBumperLeft (Enquanto segurar: whenHeld)",
            "XboxController.Button.kBumperRight (Enquanto segurar: whenHeld)",
            "XboxController.Button.kA (Ao pressionar: whenPressed)",
            "XboxController.Button.kB (Ao pressionar: whenPressed)",
            "XboxController.Button.kX (Ao pressionar: whenPressed)",
            "XboxController.Button.kY (Ao pressionar: whenPressed)"
        ])
        form_couple.addRow("Vincular Acao ao Botao do Xbox:", self.combo_xbox_btn)

        layout.addWidget(box_couple)

        btn_inject = QPushButton("Acoplar e Injetar no RobotContainer.java")
        btn_inject.setFixedHeight(45)
        btn_inject.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_inject.clicked.connect(self.action_inject_coupler)
        layout.addWidget(btn_inject)

        layout.addStretch()
        self.tabs.addTab(tab, "Acoplamento Automatico")

    def show_info_coupler(self):
        title = "Informacoes: Acoplamento e Injecao de Dependencias"
        subtitle = "Como o software automatiza a conexao entre o hardware e o RobotContainer"
        html = """
        <h3>O que e Acoplamento e Injecao no RobotContainer?</h3>
        <p>No modelo WPILib Command-Based, criar o arquivo do subsistema nao e suficiente para faze-lo funcionar. Para que o robo reconheca o subsistema e os comandos sejam executados, o subsistema precisa ser <b>declarado, instanciado com a placa Titan e vinculado aos botoes do controle</b> dentro da classe central <code>RobotContainer.java</code>.</p>

        <h3>O que este recurso executa automaticamente no seu codigo Java:</h3>
        <ol>
            <li><b>Importacao da Classe:</b> Adiciona <code>import frc.robot.subsystems.&lt;NomeClasse&gt;;</code> no topo do arquivo se ainda nao estiver presente.</li>
            <li><b>Declaracao do Atributo:</b> Cria a variavel privada no corpo da classe:
                <br><code>private final &lt;NomeClasse&gt; &lt;nomeVariavel&gt;;</code>
            </li>
            <li><b>Instanciacao no Construtor com Injecao do Titan:</b> No construtor <code>RobotContainer()</code>, o objeto e instanciado recebendo a referencia compartilhada da placa Titan:
                <br><code>&lt;nomeVariavel&gt; = new &lt;NomeClasse&gt;(titan);</code>
            </li>
            <li><b>Mapeamento de Botoes do Controle Xbox:</b> Se um botao for selecionado (ex: <i>Bumper Esquerdo</i>), o injetor adiciona a chamada dentro do metodo <code>configureButtonBindings()</code>:
                <br><code>new JoystickButton(joystick, XboxController.Button.kBumperLeft.value).whenHeld(new RunCommand(() -&gt; m_garra.activate(), m_garra));</code>
            </li>
        </ol>

        <h3>Vantagens diretas:</h3>
        <ul>
            <li>Elimina o erro classico de <code>NullPointerException</code> decorrente de subsistemas declarados mas nao instanciados.</li>
            <li>Elimina a necessidade de abrir multiplos arquivos e digitar repetidamente o mesmo codigo estrutural.</li>
            <li>Mantem a arquitetura limpa e desacoplada, seguindo as melhores praticas recomendadas pela FIRST e pela WorldSkills.</li>
        </ul>
        """
        dlg = InfoDialog(title, subtitle, html, self)
        dlg.exec()

    def browse_couple_proj(self):
        dir_selected = QFileDialog.getExistingDirectory(self, "Selecionar Pasta Raiz do Projeto")
        if dir_selected:
            self.input_couple_proj_path.setText(dir_selected)

    def action_inject_coupler(self):
        proj_dir = self.input_couple_proj_path.text().strip()
        container_path = os.path.join(proj_dir, "src", "main", "java", "frc", "robot", "RobotContainer.java")
        if not os.path.exists(container_path):
            QMessageBox.critical(
                self, "Arquivo nao encontrado",
                f"Nao foi localizado o arquivo RobotContainer.java em:\n{container_path}"
            )
            return

        subsystem_class = self.input_subsystem_class.text().strip()
        var_name = self.input_subsystem_var.text().strip()

        btn_idx = self.combo_xbox_btn.currentIndex()
        button_code = None
        if btn_idx > 0:
            btn_selected = self.combo_xbox_btn.currentText().split()[0]
            action_method = "whenHeld" if "whenHeld" in self.combo_xbox_btn.currentText() else "whenPressed"
            button_code = f"new JoystickButton(joystick, {btn_selected}.value).{action_method}(new RunCommand(() -> {var_name}.activate(), {var_name}));"

        success = ProjectCoupler.inject_subsystem_to_container(
            container_path,
            subsystem_class,
            var_name,
            constructor_call=f"new {subsystem_class}(titan)",
            button_binding_code=button_code
        )

        if success:
            QMessageBox.information(
                self, "Acoplamento Concluido",
                f"O subsistema {subsystem_class} foi acoplado com sucesso no RobotContainer.java!\n\n- Atributo privado declarado\n- Objeto instanciado no construtor com Titan\n- Botoes vinculados no configureButtonBindings"
            )
        else:
            QMessageBox.critical(self, "Falha na Injecao", "Nao foi possivel atualizar o arquivo RobotContainer.java.")

    # ==========================================
    # ABA 4: PRÉ-VISUALIZADOR DE CÓDIGO
    # ==========================================
    def create_tab_code_preview(self):
        self.tab_preview = QWidget()
        layout = QVBoxLayout(self.tab_preview)

        top_bar = QHBoxLayout()
        label = QLabel("Visualizador de Codigo Java Gerado:")
        label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        top_bar.addWidget(label)
        top_bar.addStretch()

        btn_info = QPushButton("[ ? ] Informacoes Desta Etapa")
        btn_info.setStyleSheet("background-color: #45475a; color: #89b4fa; padding: 6px 14px;")
        btn_info.clicked.connect(self.show_info_preview)
        top_bar.addWidget(btn_info)
        layout.addLayout(top_bar)

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setReadOnly(True)
        layout.addWidget(self.code_editor)

        self.tabs.addTab(self.tab_preview, "Pre-visualizador")

    def show_info_preview(self):
        title = "Informacoes: Pre-Visualizador de Codigo"
        subtitle = "Como inspecionar e validar o codigo gerado antes de gravar nos arquivos"
        html = """
        <h3>O que esta etapa oferece?</h3>
        <p>O <b>Pre-visualizador de Codigo</b> permite inspecionar de forma clara e organizada o conteudo dos arquivos Java que serao criados ou injetados no seu projeto antes de efetivar as mudancas no disco.</p>

        <h3>O que observar no codigo exibido:</h3>
        <ul>
            <li><b>Pacote e Importacoes:</b> Certifique-se de que o pacote esta definido como <code>package frc.robot.subsystems;</code> ou <code>commands;</code> e que as classes do Titan (<code>com.studica.frc.Titan</code>) estao importadas.</li>
            <li><b>Parametros Customizados:</b> Verifique se as portas dos motores, canais dos encoders e os valores de resolucao (PPR, Gear Ratio) correspondem exatamente a montagem mecanica do seu robo.</li>
            <li><b>Constantes Estaticas:</b> As constantes sao formatadas dentro de uma classe estatica interna (ex: <code>DriveTrainConstants</code>) para serem inseridas sem conflitos no arquivo <code>Constants.java</code>.</li>
        </ul>
        """
        dlg = InfoDialog(title, subtitle, html, self)
        dlg.exec()

    # ==========================================
    # TEMA ESCURO (DARK MODE)
    # ==========================================
    def apply_dark_theme(self):
        dark_style = """
        QMainWindow, QWidget {
            background-color: #1e1e2e;
            color: #cdd6f4;
        }
        QGroupBox {
            border: 1px solid #45475a;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 14px;
            font-weight: bold;
            color: #89b4fa;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 6px;
            selection-background-color: #89b4fa;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #89b4fa;
        }
        QPushButton {
            background-color: #89b4fa;
            color: #11111b;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #b4befe;
        }
        QPushButton:pressed {
            background-color: #74c7ec;
        }
        QTabWidget::pane {
            border: 1px solid #45475a;
            border-radius: 8px;
            background-color: #1e1e2e;
        }
        QTabBar::tab {
            background-color: #313244;
            color: #a6adc8;
            padding: 8px 18px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #45475a;
            color: #cdd6f4;
            font-weight: bold;
        }
        QCheckBox {
            color: #cdd6f4;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #45475a;
            background-color: #313244;
        }
        QCheckBox::indicator:checked {
            background-color: #89b4fa;
        }
        """
        self.setStyleSheet(dark_style)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
