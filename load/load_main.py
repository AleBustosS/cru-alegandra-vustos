import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QAction
from load.load_ui_productos import Load_ui_productos


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema - Menú Principal")
        self.setMinimumSize(800, 600)
        # Si existe una UI creada con Qt Designer, cárgala (solo ui_main.ui)
        ui_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'ui_main.ui'))
        ui_path = os.path.normpath(ui_path)
        if os.path.exists(ui_path):
            try:
                uic.loadUi(ui_path, self)
            except Exception:
                # si falla cargar la UI, caemos al modo programático
                central = QtWidgets.QWidget()
                self.setCentralWidget(central)
        else:
            # Área central vacío (cada catálogo abrirá su propia ventana)
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)

        # Menú de catálogos (si no existe en la UI)
        menubar = self.menuBar()
        catalogos_menu = menubar.addMenu("Catálogos")

        productos_action = QAction("Catálogo de Productos", self)
        clientes_action = QAction("Catálogo de Clientes", self)

        catalogos_menu.addAction(productos_action)
        catalogos_menu.addAction(clientes_action)

        productos_action.triggered.connect(self.open_productos)
        clientes_action.triggered.connect(self.open_clientes)

        # Guardamos ventanas hijas para evitar que se recolecten
        self.child_windows = []

    # Si la UI contiene un QStackedWidget, intentamos seleccionar la página
        # que contiene el botón "Catálogo de productos" para que el login lleve ahí.
        if hasattr(self, 'stackedWidget'):
            try:
                for i in range(self.stackedWidget.count()):
                    page = self.stackedWidget.widget(i)
                    for btn in page.findChildren(QtWidgets.QPushButton):
                        text = (btn.text() or '').lower()
                        if 'producto' in text:
                            # seleccionar esta página como la visible al iniciar
                            self.stackedWidget.setCurrentIndex(i)
                            # conectar el botón de productos a la acción
                            btn.clicked.connect(self.open_productos)
                        if 'cliente' in text:
                            btn.clicked.connect(self.open_clientes)
            except Exception:
                # ignore any issues iterating children
                pass
            # además, si los botones tienen objectName conocidos, conéctalos directamente
            try:
                if hasattr(self, 'catalog_product_btn'):
                    self.catalog_product_btn.clicked.connect(self.open_productos)
                if hasattr(self, 'catalog_client_btn'):
                    self.catalog_client_btn.clicked.connect(self.open_clientes)
            except Exception:
                pass

    def open_productos(self):
        win = Load_ui_productos()
        win.show()
        self.child_windows.append(win)

    def open_clientes(self):
        # Si quieres, implementamos Load_ui_clientes similar al de productos.
        QtWidgets.QMessageBox.information(self, "Clientes", "Abrir catálogo de clientes (pendiente de implementar UI).")
