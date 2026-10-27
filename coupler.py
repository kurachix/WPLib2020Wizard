"""
Módulo de Acoplamento e Injeção Automática de Código.
Responsável por conectar novos Subsistemas e Comandos aos arquivos
`Constants.java` e `RobotContainer.java` de forma não-destrutiva.
"""

import os
import re
from typing import Optional


class ProjectCoupler:
    """Injeta declarações, instanciações e constantes em arquivos Java existentes."""

    @staticmethod
    def inject_constants(constants_file_path: str, new_constants_code: str) -> bool:
        """
        Injeta bloco de constantes dentro da classe principal `Constants`.
        """
        if not os.path.exists(constants_file_path):
            return False

        with open(constants_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Evita duplicação se o bloco já foi injetado
        # Extrai o nome da classe interna se houver
        match_class = re.search(r"class\s+([A-Za-z0-9_]+Constants)", new_constants_code)
        if match_class:
            class_name = match_class.group(1)
            if class_name in content:
                # Já existe essa classe interna de constantes
                return True

        # Encontra a última chave '}' de fechamento da classe Constants
        last_brace_idx = content.rfind("}")
        if last_brace_idx == -1:
            return False

        updated_content = (
            content[:last_brace_idx].rstrip()
            + "\n\n"
            + new_constants_code
            + "\n\n"
            + content[last_brace_idx:]
        )

        with open(constants_file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return True

    @staticmethod
    def inject_subsystem_to_container(
        robot_container_path: str,
        subsystem_class: str,
        var_name: str,
        constructor_call: Optional[str] = None,
        button_binding_code: Optional[str] = None
    ) -> bool:
        """
        Injeta o subsistema no `RobotContainer.java`:
        1. Importação da classe do subsistema
        2. Atributo privado (`private final Subsystem m_subsystem;`)
        3. Instanciação no construtor (`m_subsystem = new Subsystem(titan);`)
        4. Vinculação de botões opcional no `configureButtonBindings()`.
        """
        if not os.path.exists(robot_container_path):
            return False

        with open(robot_container_path, "r", encoding="utf-8") as f:
            content = f.read()

        if constructor_call is None:
            constructor_call = f"new {subsystem_class}(titan)"

        # 1. Injetar Import se necessário
        import_stmt = f"import frc.robot.subsystems.{subsystem_class};"
        if import_stmt not in content:
            # Insere após o pacote ou último import
            import_matches = list(re.finditer(r"import\s+[^;]+;", content))
            if import_matches:
                last_import = import_matches[-1]
                end_pos = last_import.end()
                content = content[:end_pos] + f"\n{import_stmt}" + content[end_pos:]
            else:
                pkg_match = re.search(r"package\s+[^;]+;", content)
                if pkg_match:
                    end_pos = pkg_match.end()
                    content = content[:end_pos] + f"\n\n{import_stmt}" + content[end_pos:]

        # 2. Injetar Declaração do Atributo
        field_decl = f"  private final {subsystem_class} {var_name};"
        if f"{subsystem_class} {var_name}" not in content:
            # Localizar onde os subsistemas são declarados
            # Procura por "public class RobotContainer"
            match_class_decl = re.search(r"public\s+class\s+RobotContainer[^{]*\{", content)
            if match_class_decl:
                insert_pos = match_class_decl.end()
                content = content[:insert_pos] + f"\n  // Subsistema injetado automaticamente\n{field_decl}\n" + content[insert_pos:]

        # 3. Injetar Instanciação no construtor
        instantiation_stmt = f"    {var_name} = {constructor_call};"
        if instantiation_stmt.strip() not in content:
            # Procura pelo construtor RobotContainer() { ... }
            match_constructor = re.search(r"public\s+RobotContainer\s*\([^\)]*\)\s*\{", content)
            if match_constructor:
                insert_pos = match_constructor.end()
                content = content[:insert_pos] + f"\n{instantiation_stmt}" + content[insert_pos:]

        # 4. Injetar Botão no configureButtonBindings se fornecido
        if button_binding_code:
            match_bindings = re.search(r"private\s+void\s+configureButtonBindings\s*\([^\)]*\)\s*\{", content)
            if match_bindings:
                insert_pos = match_bindings.end()
                content = content[:insert_pos] + f"\n    // Ação vinculada automaticamente\n    {button_binding_code}\n" + content[insert_pos:]

        with open(robot_container_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
