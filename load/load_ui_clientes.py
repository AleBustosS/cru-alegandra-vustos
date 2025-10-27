from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QThreadPool
import os
from modelo.clientedao import ClienteDAO
from .worker import Worker


class Load_ui_clientes(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Ruta absoluta al .ui para evitar problemas de cwd y mejorar velocidad
        ui_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'clientes.ui')
        # Si el archivo no existe, intentar con la carpeta relativa 'ui'
        if not os.path.exists(ui_file):
            ui_file = os.path.join(os.path.dirname(__file__), '..', 'ui', 'clientes.ui')

        uic.loadUi(ui_file, self)

        # Llamar a configuración adicional si hace falta
        self.setup_ui()

    def setup_ui(self):
        # Ejemplo: conectar botones de cerrar si existen
        try:
            # Instanciar DAO de clientes
            self.dao = ClienteDAO()

            # Si la UI tiene un botón para salir (puede llamarse 'boton_salir' o 'boton_salir_cliente')
            if hasattr(self, 'boton_salir'):
                self.boton_salir.clicked.connect(self.close)
            if hasattr(self, 'boton_salir_cliente'):
                self.boton_salir_cliente.clicked.connect(self.close)
            # Conectar botones del panel lateral a páginas/acciones
            if hasattr(self, 'boton_crear_cliente'):
                self.boton_crear_cliente.clicked.connect(lambda: self.show_page_by_name('page_agregar'))
            if hasattr(self, 'boton_buscar_cliente'):
                self.boton_buscar_cliente.clicked.connect(lambda: self.show_page_by_name('page_buscar'))
            if hasattr(self, 'boton_editar_cliente'):
                self.boton_editar_cliente.clicked.connect(lambda: self.show_page_by_name('page_actualizar'))
            if hasattr(self, 'boton_eliminar_cliente'):
                self.boton_eliminar_cliente.clicked.connect(lambda: self.show_page_by_name('page_eliminar'))
            if hasattr(self, 'boton_listar_cliente'):
                # listar mostrará la página de consulta y rellenará la tabla
                self.boton_listar_cliente.clicked.connect(self.on_listar)

            # Conectar botones de acción dentro de las páginas a mensajes o acciones básicas
            if hasattr(self, 'boton_accion_crear_cliente'):
                self.boton_accion_crear_cliente.clicked.connect(self.crear_cliente)
            if hasattr(self, 'boton_accion_actualizar_cliente'):
                self.boton_accion_actualizar_cliente.clicked.connect(self.actualizar_cliente)
            if hasattr(self, 'boton_accion_eliminar_cliente'):
                self.boton_accion_eliminar_cliente.clicked.connect(self.eliminar_cliente)
            if hasattr(self, 'boton_accion_refrescar_cliente'):
                self.boton_accion_refrescar_cliente.clicked.connect(self.on_listar)

            # Quitar borde de ventana si se desea (igual que productos)
            self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
            self.setWindowOpacity(1)
        except Exception:
            pass

    def show_page_by_name(self, name: str):
        """Buscar la página con objectName `name` dentro del stackedWidget y mostrar su índice."""
        try:
            if not hasattr(self, 'stackedWidget'):
                return
            for i in range(self.stackedWidget.count()):
                w = self.stackedWidget.widget(i)
                if w.objectName() == name:
                    self.stackedWidget.setCurrentIndex(i)
                    return
        except Exception:
            pass

    def on_listar(self):
        """Llama al DAO para obtener filas y las muestra en `tabla_cliente`."""
        try:
            # Mostrar la página de consulta si existe
            self.show_page_by_name('page_consultar')

            # Ejecutar listado en background para no bloquear la UI
            def handle_result(filas):
                try:
                    filas = filas or []
                    if not filas:
                        QMessageBox.information(self, 'Clientes', 'No se encontraron clientes.')
                        if hasattr(self, 'tabla_cliente'):
                            self.tabla_cliente.setRowCount(0)
                        return

                    if hasattr(self, 'tabla_cliente'):
                        num_rows = len(filas)
                        num_cols = len(filas[0]) if num_rows > 0 else 0
                        self.tabla_cliente.setRowCount(num_rows)
                        self.tabla_cliente.setColumnCount(num_cols)
                        for r, row in enumerate(filas):
                            for c, val in enumerate(row):
                                item = QTableWidgetItem(str(val))
                                self.tabla_cliente.setItem(r, c, item)
                except Exception as e:
                    QMessageBox.warning(self, 'Error', f'Error al poblar tabla: {e}')

            def handle_error(err):
                e, tb = err
                QMessageBox.warning(self, 'Error', f'Error al listar clientes: {e}\n{tb}')

            worker = Worker(self.dao.listarClientes)
            worker.signals.result.connect(handle_result)
            worker.signals.error.connect(handle_error)
            QThreadPool.globalInstance().start(worker)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error al mostrar lista: {e}')
    def crear_cliente(self):
        """Recoger campos del formulario de crear y llamar al DAO en background."""
        try:
            nombre = getattr(self, 'nombre_crear', None)
            mail = getattr(self, 'mail_crear', None)
            cliente_id = getattr(self, 'cliente_crear', None)
            if nombre is None or mail is None or cliente_id is None:
                QMessageBox.warning(self, 'Error', 'Campos de crear no encontrados en la UI')
                return

            nombre_val = nombre.text().strip()
            mail_val = mail.text().strip()
            id_val = cliente_id.text().strip()

            # preparar objeto cliente en DAO
            self.dao.cliente.nombre = nombre_val
            # no hay campo apellido en la UI, dejar vacío
            self.dao.cliente.apellido = ''
            self.dao.cliente.correo_electronico = mail_val

            def fn():
                self.dao.guardarCliente()
                return True

            def on_done(_):
                self.mensaje.setText('Cliente creado correctamente')
                self.on_listar()

            def on_error(err):
                e, tb = err
                QMessageBox.warning(self, 'Error', f'Error creando cliente: {e}\n{tb}')

            worker = Worker(fn)
            worker.signals.result.connect(on_done)
            worker.signals.error.connect(on_error)
            QThreadPool.globalInstance().start(worker)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error al iniciar crear cliente: {e}')

    def actualizar_cliente(self):
        try:
            id_field = getattr(self, 'id_actualizar', None)
            nombre_field = getattr(self, 'nombre_actualizar', None)
            mail_field = getattr(self, 'mail_actualizar', None)
            if id_field is None or nombre_field is None or mail_field is None:
                QMessageBox.warning(self, 'Error', 'Campos de actualizar no encontrados en la UI')
                return

            id_val = id_field.text().strip()
            nombre_val = nombre_field.text().strip()
            mail_val = mail_field.text().strip()

            if not id_val:
                QMessageBox.warning(self, 'Error', 'Debe indicar el id del cliente a actualizar')
                return

            self.dao.cliente.id_cliente = int(id_val)
            self.dao.cliente.nombre = nombre_val
            self.dao.cliente.correo_electronico = mail_val

            def fn():
                self.dao.actualizarCliente()
                return True

            def on_done(_):
                self.mensaje.setText('Cliente actualizado correctamente')
                self.on_listar()

            def on_error(err):
                e, tb = err
                QMessageBox.warning(self, 'Error', f'Error actualizando cliente: {e}\n{tb}')

            worker = Worker(fn)
            worker.signals.result.connect(on_done)
            worker.signals.error.connect(on_error)
            QThreadPool.globalInstance().start(worker)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error al iniciar actualizar cliente: {e}')

    def eliminar_cliente(self):
        try:
            id_field = getattr(self, 'id_eliminar', None)
            if id_field is None:
                QMessageBox.warning(self, 'Error', 'Campo id eliminar no encontrado en la UI')
                return
            id_val = id_field.text().strip()
            if not id_val:
                QMessageBox.warning(self, 'Error', 'Debe indicar el id del cliente a eliminar')
                return

            self.dao.cliente.id_cliente = int(id_val)

            def fn():
                self.dao.eliminarCliente()
                return True

            def on_done(_):
                self.mensaje.setText('Cliente eliminado correctamente')
                self.on_listar()

            def on_error(err):
                e, tb = err
                QMessageBox.warning(self, 'Error', f'Error eliminando cliente: {e}\n{tb}')

            worker = Worker(fn)
            worker.signals.result.connect(on_done)
            worker.signals.error.connect(on_error)
            QThreadPool.globalInstance().start(worker)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error al iniciar eliminar cliente: {e}')
