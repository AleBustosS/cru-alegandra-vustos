from PyQt5 import QtWidgets, uic
import sys
import os
from load.load_ui_productos import Load_ui_productos
from modelo.conexionbd import ConexionBd
from load.load_login import LoginDialog
from load.load_main import MainWindow
from load.load_ui_clientes import Load_ui_clientes


def try_authenticate(usuario: str, password: str) -> bool:
    bd = ConexionBd()
    try:
        bd.establecerConexionBD()
        cursor = bd.conexion.cursor()
        sp = "exec dbo.sp_autenticar_usuario @usuario=?, @password=?"
        cursor.execute(sp, (usuario, password))
        resultado = cursor.fetchone()
        bd.cerrarConexionBD()
        return bool(resultado and len(resultado) > 0 and resultado[0])
    except Exception:
        # fallback admin/admin
        return usuario == "admin" and password == "admin"


def main():
    app = QtWidgets.QApplication(sys.argv)

    base_ui = os.path.normpath(os.path.join(os.path.dirname(__file__), 'ui'))
    iniciar = os.path.join(base_ui, 'iniciar_sesion.ui')

    # Si existe el .ui del usuario y es un MainWindow con stackedWidget, lo usamos como ventana inicial
    if os.path.exists(iniciar):
        try:
            window = QtWidgets.QMainWindow()
            uic.loadUi(iniciar, window)
            
            # Asegurar que se muestre la página de login primero
            if hasattr(window, 'stackedWidget'):
                window.stackedWidget.setCurrentIndex(0)

            # conectar login button (si existe) para validar credenciales y mostrar la segunda página
            if hasattr(window, 'login_btn') and hasattr(window, 'user_edit') and hasattr(window, 'pass_edit'):
                def on_login():
                    u = window.user_edit.text().strip()
                    p = window.pass_edit.text().strip()
                    if not u or not p:
                        if hasattr(window, 'message'):
                            window.message.setText('Ingrese usuario y contraseña')
                        return
                    ok = try_authenticate(u, p)
                    if ok:
                        # cambiar a la página de selección de catálogos si hay stackedWidget
                        if hasattr(window, 'stackedWidget'):
                            try:
                                # asumimos que la página 1 es la de selección
                                window.stackedWidget.setCurrentIndex(1)
                            except Exception:
                                pass
                    else:
                        if hasattr(window, 'message'):
                            window.message.setText('Credenciales inválidas')

                window.login_btn.clicked.connect(on_login)
            # conectar cancelar para cerrar la ventana
            if hasattr(window, 'cancel_btn'):
                window.cancel_btn.clicked.connect(lambda: window.close())

            # Pre-cargar ventana de productos para acceso más rápido
            productos_window = None
            def mostrar_productos():
                nonlocal productos_window
                try:
                    # ocultar la ventana inicial que contiene los botones de catálogo (para poder mostrarla luego)
                    if 'window' in locals() and window is not None:
                        window.hide()
                except Exception:
                    pass
                if not productos_window:
                    productos_window = Load_ui_productos()
                productos_window.show()
                
            # conectar botones de catálogo a las funciones correspondientes
            if hasattr(window, 'catalog_product_btn'):
                window.catalog_product_btn.clicked.connect(mostrar_productos)

            # Pre-cargar ventana de clientes para acceso rápido
            clientes_window = None
            def mostrar_clientes():
                nonlocal clientes_window
                try:
                    if 'window' in locals() and window is not None:
                        window.hide()
                except Exception:
                    pass
                if not clientes_window:
                    clientes_window = Load_ui_clientes()
                clientes_window.show()

            if hasattr(window, 'catalog_client_btn'):
                window.catalog_client_btn.clicked.connect(mostrar_clientes)

            window.show()
            sys.exit(app.exec_())
        except Exception as e:
            print('Error cargando iniciar_sesion.ui:', e)

    # Fallback: mostrar diálogo de login (programático) y luego ventana principal
    login = LoginDialog()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()