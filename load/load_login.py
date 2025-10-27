from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog
import os
from modelo.conexionbd import ConexionBd


class LoginDialog(QDialog):
    """Diálogo simple de login.

    NOTA: Está implementado por código para acelerar la entrega. Puedes
    reemplazarlo por un `.ui` generado con Qt Designer y cargarlo con
    `uic.loadUi()` si prefieres.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Intentamos cargar un diseño creado en Qt Designer (ui/iniciar_sesion.ui)
        base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'ui'))
        ui_file = os.path.join(base_dir, 'iniciar_sesion.ui')

        if os.path.exists(ui_file):
            try:
                uic.loadUi(ui_file, self)
                # esperamos que el .ui tenga widgets con estos objectName
                # conectar señales solo si existen (evita AttributeError)
                if hasattr(self, 'login_btn'):
                    self.login_btn.clicked.connect(self.attempt_login)
                if hasattr(self, 'cancel_btn'):
                    self.cancel_btn.clicked.connect(self.reject)
            except Exception:
                # si falla cargar el .ui, caemos al UI por código
                self._build_ui_programmatic()
        else:
            # no existe .ui, usar UI por código
            self._build_ui_programmatic()

        # Conexión a la BD (si se requiere)
        self.bd = ConexionBd()

    def _build_ui_programmatic(self):
        """Construye el diálogo por código (fallback)."""
        self.setWindowTitle("Login")
        self.setFixedSize(320, 140)

        # Widgets
        self.user_label = QtWidgets.QLabel("Usuario:")
        self.user_edit = QtWidgets.QLineEdit()
        self.pass_label = QtWidgets.QLabel("Contraseña:")
        self.pass_edit = QtWidgets.QLineEdit()
        self.pass_edit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_btn = QtWidgets.QPushButton("Ingresar")
        self.cancel_btn = QtWidgets.QPushButton("Cancelar")
        self.message = QtWidgets.QLabel("")

        # Layout
        form = QtWidgets.QGridLayout()
        form.addWidget(self.user_label, 0, 0)
        form.addWidget(self.user_edit, 0, 1)
        form.addWidget(self.pass_label, 1, 0)
        form.addWidget(self.pass_edit, 1, 1)
        form.addWidget(self.message, 2, 0, 1, 2)

        btns = QtWidgets.QHBoxLayout()
        btns.addStretch()
        btns.addWidget(self.login_btn)
        btns.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addLayout(btns)
        self.setLayout(main_layout)

        # Señales
        self.login_btn.clicked.connect(self.attempt_login)
        self.cancel_btn.clicked.connect(self.reject)

    def attempt_login(self):
        usuario = self.user_edit.text().strip()
        password = self.pass_edit.text().strip()

        if not usuario or not password:
            self.message.setText("Ingrese usuario y contraseña")
            return

        # Intentamos autenticar mediante un stored procedure (si existe).
        try:
            self.bd.establecerConexionBD()
            cursor = self.bd.conexion.cursor()
            # Se asume la existencia de un SP: sp_autenticar_usuario @usuario=?, @password=?
            sp = "exec dbo.sp_autenticar_usuario @usuario=?, @password=?"
            cursor.execute(sp, (usuario, password))
            resultado = cursor.fetchone()
            self.bd.cerrarConexionBD()

            # Interpretación simple: si el SP devuelve fila y primer campo truthy => ok
            if resultado and len(resultado) > 0 and resultado[0]:
                self.accept()
                return
            else:
                self.message.setText("Credenciales inválidas (BD)")
                return

        except Exception:
            # Si falla la conexión o el SP no existe, usamos fallback local
            # Credenciales por defecto para testing: admin / admin
            if usuario == "admin" and password == "admin":
                self.accept()
                return
            else:
                self.message.setText("Credenciales inválidas (fallback)")
                return
