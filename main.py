"""
WPILib 2020 Robot Wizard & Class Generator
Interface Gráfica Desktop desenvolvida em PySide6 para Studica VMX-pi e Titan Quad.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QSpinBox, QDoubleSpinBox, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from class_generator import ClassGenerator
from project_generator import ProjectGenerator
from coupler import ProjectCoupler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WPILib 2020 Robot Wizard - Studica VMX-pi / Titan")
        self.resize(920, 720)

        # Estado atual de código gerado
        self.current_subsystem_code = ""
        self.current_constants_code = ""
        self.current_class_name = ""

        self.init_ui()

    def init_ui(self):
        # Widget Central e Tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_label = QLabel("🤖 WPILib 2020 Robot Wizard & Class Generator")
        header_font = QFont("Segoe UI", 16, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        subtitle_label = QLabel("Crie projetos, gere subsistemas parametrizados e acople automaticamente no RobotContainer e Constants.")
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Inicializa Abas
        self.create_tab_new_project()
        self.create_tab_class_generator()
        self.create_tab_coupler()
        self.create_tab_code_preview()

        # Aplica estilo moderno Dark Mode
        self.apply_dark_theme()

    # ==========================================
    # ABA 1: NOVO PROJETO
    # ==========================================
    def create_tab_new_project(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        box = QGroupBox("Configurações do Novo Projeto")
        form = QFormLayout(box)

        self.input_proj_name = QLineEdit("RoboWorldSkills2026")
        form.addRow("Nome do Projeto:", self.input_proj_name)

        h_dir = QHBoxLayout()
        # Diretório padrão: pasta pai do script
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.input_proj_dir = QLineEdit(default_dir)
        btn_browse_dir = QPushButton("Selecionar...")
        btn_browse_dir.clicked.connect(self.browse_project_dir)
        h_dir.addWidget(self.input_proj_dir)
        h_dir.addWidget(btn_browse_dir)
        form.addRow("Diretório de Destino:", h_dir)

        self.input_titan_id = QSpinBox()
        self.input_titan_id.setRange(1, 63)
        self.input_titan_id.setValue(42)
        form.addRow("Titan Quad CAN ID:", self.input_titan_id)

        # Vendors
        vendors_box = QGroupBox("Vendordeps Obrigatórios")
        v_layout = QVBoxLayout(vendors_box)
        self.chk_studica = QCheckBox("Studica (Titan Quad, VMX-pi, Servos, Motores)")
        self.chk_studica.setChecked(True)
        self.chk_commands = QCheckBox("WPILib New Commands (CommandBase, SubsystemBase)")
        self.chk_commands.setChecked(True)
        self.chk_navx = QCheckBox("NavX IMU / Giroscópio (KauaiLabs)")
        self.chk_navx.setChecked(True)
        v_layout.addWidget(self.chk_studica)
        v_layout.addWidget(self.chk_commands)
        v_layout.addWidget(self.chk_navx)
        form.addRow("Dependências de Fornecedor:", vendors_box)

        layout.addWidget(box)

        btn_create = QPushButton("🚀 Criar Estrutura Completa do Projeto WPILib")
        btn_create.setFixedHeight(45)
        btn_create.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_create.clicked.connect(self.action_create_project)
        layout.addWidget(btn_create)

        layout.addStretch()
        self.tabs.addTab(tab, "📁 Novo Projeto")

    def browse_project_dir(self):
        dir_selected = QFileDialog.getExistingDirectory(self, "Selecionar Diretório")
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
            "titan_id": self.input_titan_id.value(),
            "vendors": vendors
        }

        try:
            path = ProjectGenerator.create_project(params)
            QMessageBox.information(
                self, "Projeto Criado",
                f"Projeto criado com sucesso em:\n{path}\n\nAbra esta pasta no VS Code com WPILib para iniciar!"
            )
            # Atualiza o campo de projeto ativo na aba de acoplamento
            self.input_couple_proj_path.setText(path)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao criar projeto", str(e))

    # ==========================================
    # ABA 2: GERADOR DE CLASSES COM PRESETS
    # ==========================================
    def create_tab_class_generator(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top_h = QHBoxLayout()
        top_h.addWidget(QLabel("Escolha o Preset:"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItems([
            "Tração Omni 3 Rodas (Kiwi Drive - Studica VMX)",
            "Tração Diferencial / Tanque (2 Motores)",
            "Garra / Manipulador (Motor + Encoder)",
            "Atuador Servo Motor (Studica Titan)",
            "Comando Personalizado (CommandBase)"
        ])
        self.combo_preset.currentIndexChanged.connect(self.on_preset_changed)
        top_h.addWidget(self.combo_preset)
        layout.addLayout(top_h)

        # Área de Formulário Dinâmico
        self.preset_form_group = QGroupBox("Parâmetros do Preset (Totalmente Customizável)")
        self.preset_form = QFormLayout(self.preset_form_group)
        layout.addWidget(self.preset_form_group)

        # Botões de Ação
        btn_h = QHBoxLayout()
        btn_preview = QPushButton("👁️ Pré-visualizar Código")
        btn_preview.clicked.connect(self.action_preview_preset_code)
        btn_save = QPushButton("💾 Salvar Classe no Projeto")
        btn_save.clicked.connect(self.action_save_preset_code)
        btn_h.addWidget(btn_preview)
        btn_h.addWidget(btn_save)
        layout.addLayout(btn_h)

        # Constrói o formulário inicial
        self.build_preset_form(0)

        layout.addStretch()
        self.tabs.addTab(tab, "⚙️ Gerador de Classes")

    def on_preset_changed(self, index):
        self.build_preset_form(index)

    def clear_preset_form(self):
        while self.preset_form.rowCount() > 0:
            self.preset_form.removeRow(0)

    def build_preset_form(self, index):
        self.clear_preset_form()

        if index == 0:  # Omni 3 Rodas
            self.f_class_name = QLineEdit("DriveTrain")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.f_class_name)

            self.f_m_right = QSpinBox()
            self.f_m_right.setValue(0)
            self.preset_form.addRow("Porta Motor Direito (Right):", self.f_m_right)

            self.f_m_back = QSpinBox()
            self.f_m_back.setValue(2)
            self.preset_form.addRow("Porta Motor Traseiro (Back):", self.f_m_back)

            self.f_m_left = QSpinBox()
            self.f_m_left.setValue(3)
            self.preset_form.addRow("Porta Motor Esquerdo (Left):", self.f_m_left)

            self.f_wheel_radius = QDoubleSpinBox()
            self.f_wheel_radius.setRange(1.0, 500.0)
            self.f_wheel_radius.setValue(55.0)
            self.f_wheel_radius.setSuffix(" mm")
            self.preset_form.addRow("Raio da Roda (Omni):", self.f_wheel_radius)

            self.f_ppr = QDoubleSpinBox()
            self.f_ppr.setRange(1.0, 10000.0)
            self.f_ppr.setValue(1440.0)
            self.preset_form.addRow("Pulsos por Revolução (PPR):", self.f_ppr)

            self.f_gear_ratio = QLineEdit("1.0 / 61.0")
            self.preset_form.addRow("Relação de Redução (Gear Ratio):", self.f_gear_ratio)

        elif index == 1:  # Tração Tanque
            self.f_class_name = QLineEdit("DriveTrain")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.f_class_name)

            self.f_m_left = QSpinBox()
            self.f_m_left.setValue(0)
            self.preset_form.addRow("Porta Motor Esquerdo:", self.f_m_left)

            self.f_m_right = QSpinBox()
            self.f_m_right.setValue(1)
            self.preset_form.addRow("Porta Motor Direito:", self.f_m_right)

            self.f_invert_right = QCheckBox("Inverter lado direito")
            self.f_invert_right.setChecked(True)
            self.preset_form.addRow("Inversão:", self.f_invert_right)

            self.f_wheel_radius = QDoubleSpinBox()
            self.f_wheel_radius.setValue(50.0)
            self.f_wheel_radius.setSuffix(" mm")
            self.preset_form.addRow("Raio da Roda:", self.f_wheel_radius)

            self.f_ppr = QDoubleSpinBox()
            self.f_ppr.setValue(1440.0)
            self.preset_form.addRow("Pulsos por Revolução (PPR):", self.f_ppr)

        elif index == 2:  # Garra / Manipulador
            self.f_class_name = QLineEdit("GarraSubsystem")
            self.preset_form.addRow("Nome da Classe Subsystem:", self.f_class_name)

            self.f_motor_id = QSpinBox()
            self.f_motor_id.setValue(2)
            self.preset_form.addRow("Porta do Motor no Titan:", self.f_motor_id)

            self.f_has_encoder = QCheckBox("Possui Encoder")
            self.f_has_encoder.setChecked(True)
            self.preset_form.addRow("Encoder:", self.f_has_encoder)

            self.f_encoder_ch = QSpinBox()
            self.f_encoder_ch.setValue(2)
            self.preset_form.addRow("Canal do Encoder:", self.f_encoder_ch)

            self.f_ppr = QDoubleSpinBox()
            self.f_ppr.setValue(1440.0)
            self.preset_form.addRow("Pulsos por Revolução (PPR):", self.f_ppr)

            self.f_speed = QDoubleSpinBox()
            self.f_speed.setRange(0.0, 1.0)
            self.f_speed.setSingleStep(0.1)
            self.f_speed.setValue(0.8)
            self.preset_form.addRow("Velocidade Padrão (0 a 1):", self.f_speed)

            self.f_threshold = QDoubleSpinBox()
            self.f_threshold.setRange(0.0, 5000.0)
            self.f_threshold.setValue(100.0)
            self.preset_form.addRow("Threshold de RPM (isAtSpeed):", self.f_threshold)

        elif index == 3:  # Servo Motor
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
            self.preset_form.addRow("Ângulo Inicial:", self.f_servo_angle)

        elif index == 4:  # Comando Personalizado
            self.f_command_name = QLineEdit("AtivarMecanismo")
            self.preset_form.addRow("Nome do Comando:", self.f_command_name)

            self.f_target_subsystem = QLineEdit("GarraSubsystem")
            self.preset_form.addRow("Classe do Subsistema Alvo:", self.f_target_subsystem)

            self.f_cmd_type = QComboBox()
            self.f_cmd_type.addItems(["Temporizado (Executa por X segundos)", "Contínuo (Até ser interrompido)"])
            self.preset_form.addRow("Tipo de Execução:", self.f_cmd_type)

            self.f_cmd_duration = QDoubleSpinBox()
            self.f_cmd_duration.setRange(0.1, 60.0)
            self.f_cmd_duration.setValue(2.5)
            self.f_cmd_duration.setSuffix(" s")
            self.preset_form.addRow("Duração:", self.f_cmd_duration)

    def generate_current_preset(self):
        index = self.combo_preset.currentIndex()
        if index == 0:  # Omni 3
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

        elif index == 1:  # Diferencial
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

        elif index == 2:  # Garra
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

        elif index == 3:  # Servo
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

        elif index == 4:  # Comando
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
            QMessageBox.warning(self, "Projeto Não Encontrado", "Informe o caminho válido de um projeto na aba 'Acoplamento Automático'.")
            return

        target_file = os.path.join(proj_dir, "src", "main", "java", "frc", "robot", kind, f"{self.current_class_name}.java")
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(code_java)

        # Se houver constantes, injeta em Constants.java
        if code_const:
            const_file = os.path.join(proj_dir, "src", "main", "java", "frc", "robot", "Constants.java")
            ProjectCoupler.inject_constants(const_file, code_const)

        QMessageBox.information(
            self, "Classe Salva",
            f"Arquivo salvo com sucesso em:\n{target_file}\n\nConstantes injetadas no Constants.java!"
        )

    # ==========================================
    # ABA 3: ACOPLAMENTO AUTOMÁTICO
    # ==========================================
    def create_tab_coupler(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

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

        box_couple = QGroupBox("Injetar Subsistema no RobotContainer")
        form_couple = QFormLayout(box_couple)

        self.input_subsystem_class = QLineEdit("GarraSubsystem")
        form_couple.addRow("Classe do Subsistema:", self.input_subsystem_class)

        self.input_subsystem_var = QLineEdit("m_garra")
        form_couple.addRow("Nome da Variável no Container:", self.input_subsystem_var)

        self.combo_xbox_btn = QComboBox()
        self.combo_xbox_btn.addItems([
            "Nenhum (Apenas instanciar)",
            "XboxController.Button.kBumperLeft (whenHeld)",
            "XboxController.Button.kBumperRight (whenHeld)",
            "XboxController.Button.kA (whenPressed)",
            "XboxController.Button.kB (whenPressed)",
            "XboxController.Button.kX (whenPressed)",
            "XboxController.Button.kY (whenPressed)"
        ])
        form_couple.addRow("Vincular Botão do Xbox:", self.combo_xbox_btn)

        layout.addWidget(box_couple)

        btn_inject = QPushButton("⚡ Acoplar e Injetar no RobotContainer.java")
        btn_inject.setFixedHeight(45)
        btn_inject.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_inject.clicked.connect(self.action_inject_coupler)
        layout.addWidget(btn_inject)

        layout.addStretch()
        self.tabs.addTab(tab, "🔗 Acoplamento Automático")

    def browse_couple_proj(self):
        dir_selected = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Projeto")
        if dir_selected:
            self.input_couple_proj_path.setText(dir_selected)

    def action_inject_coupler(self):
        proj_dir = self.input_couple_proj_path.text().strip()
        container_path = os.path.join(proj_dir, "src", "main", "java", "frc", "robot", "RobotContainer.java")
        if not os.path.exists(container_path):
            QMessageBox.critical(self, "Arquivo não encontrado", f"Não foi encontrado RobotContainer.java em:\n{container_path}")
            return

        subsystem_class = self.input_subsystem_class.text().strip()
        var_name = self.input_subsystem_var.text().strip()

        # Binding de botão se selecionado
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
                self, "Acoplamento Concluído",
                f"O subsistema {subsystem_class} foi injetado com sucesso no RobotContainer.java!\n\n- Campo declarado\n- Instanciado no construtor\n- Botão mapeado"
            )
        else:
            QMessageBox.critical(self, "Falha na Injeção", "Não foi possível injetar o código no RobotContainer.")

    # ==========================================
    # ABA 4: PRÉ-VISUALIZADOR DE CÓDIGO
    # ==========================================
    def create_tab_code_preview(self):
        self.tab_preview = QWidget()
        layout = QVBoxLayout(self.tab_preview)

        label = QLabel("Código Java Gerado:")
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(label)

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setReadOnly(True)
        layout.addWidget(self.code_editor)

        self.tabs.addTab(self.tab_preview, "📄 Pré-visualizador")

    # ==========================================
    # TEMA ESCURO (DARK MODE)
    # ==========================================
    def apply_dark_theme(self):
        dark_style = """
        QMainWindow, QWidget {
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
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
            padding: 8px 16px;
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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
