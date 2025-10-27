#1.- Importar librerias
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QPropertyAnimation
from PyQt5 import QtCore, QtGui, QtWidgets, uic  
from PyQt5.QtCore import QThreadPool
from modelo.productodao import ProductoDAO
from .worker import Worker
#2.- Cargar archivo .ui
class Load_ui_productos(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Cargar archivo .ui usando ruta absoluta para mayor velocidad
        import os
        ui_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "ui_productos.ui")
        uic.loadUi(ui_file, self)
        
        # Crear DAO una sola vez
        self.productodao = ProductoDAO()
        
        # Configurar la interfaz
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz una sola vez al inicio"""
        # Eliminar barra de título y configurar opacidad
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        
#3.- Configurar contenedores

#eliminar barra y de titulo - opacidad

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        #Cerrar ventana
        self.boton_salir.clicked.connect(lambda: self.close())
        # mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana
        #menu lateral
        self.boton_menu.clicked.connect(self.mover_menu)
        #Fijar ancho columnas
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

#3.5 Fijar ancho columnas

        self.tabla_productos.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch) 

#4.- Conectar botones a funciones

#Botones para cambiar de página
        self.boton_agregar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_agregar))
        self.boton_buscar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_buscar))
        self.boton_actualizar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_actualizar))
        self.boton_eliminar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_eliminar))
        self.boton_consultar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_consultar))

        #Botones para guardar, buscar, actualizar, eliminar y salir
        #Botones para guardar, buscar, actualizar, eliminar y salir
        
        self.boton_accion_agregar.clicked.connect(self.guardar_producto)
        self.boton_accion_refrescar.clicked.connect(self.llenar_tabla)
        self.boton_accion_actualizar.clicked.connect(self.actualizar_producto)
        self.boton_accion_eliminar.clicked.connect(self.eliminar_producto)
        self.boton_accion_limpiar.clicked.connect(self.limpiar_formulario)

        self.boton_buscar_actualizar.clicked.connect(self.buscar_actualizar)
        self.boton_buscar_eliminar.clicked.connect(self.buscar_eliminar)
        self.boton_buscar_buscar.clicked.connect(self.buscar_buscar)

#5.- Operaciones con el modelo de datos 

    def guardar_producto(self):
        self.productodao.producto.clave = self.sku_agregar.text()
        self.productodao.producto.descripcion = self.descripcion_agregar.text()
        self.productodao.producto.existencia = int(self.existencia_agregar.text())
        self.productodao.producto.precio = float(self.precio_agregar.text())

        self.productodao.insertarProducto()

        self.mensaje.setText("El producto ha sido registrado!!!")
        self.sku_agregar.setText("")
        self.descripcion_agregar.setText("")
        self.existencia_agregar.setText("")
        self.precio_agregar.setText("")


    def buscar_producto(self):
        pass

    def actualizar_producto(self):
        pass

    def eliminar_producto(self):
        pass
    
    def llenar_tabla(self):
        # Ejecutar en background para no bloquear la UI
        def handle_result(datos):
            try:
                datos = datos or []
                self.tabla_productos.setRowCount(len(datos))
                fila = 0
                for item in datos:
                    # Asegurar que no dé error si columnas faltan
                    if len(item) > 1:
                        self.tabla_productos.setItem(fila,0,QtWidgets.QTableWidgetItem(str(item[1])))
                    if len(item) > 2:
                        self.tabla_productos.setItem(fila,1,QtWidgets.QTableWidgetItem(str(item[2])))
                    if len(item) > 3:
                        self.tabla_productos.setItem(fila,2,QtWidgets.QTableWidgetItem(str(item[3])))
                    if len(item) > 4:
                        self.tabla_productos.setItem(fila,3,QtWidgets.QTableWidgetItem(str(item[4])))
                    fila += 1
            except Exception:
                pass

        def handle_error(err):
            e, tb = err
            try:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, 'Error', f'Error al listar productos: {e}\n{tb}')
            except Exception:
                pass

        worker = Worker(self.productodao.listarProductos)
        worker.signals.result.connect(handle_result)
        worker.signals.error.connect(handle_error)
        QThreadPool.globalInstance().start(worker)
   
    def limpiar_formulario(self):

        self.sku_buscar.setText('')
        self.descripcion_buscar.setText('')
        self.existencia_buscar.setText('')
        self.precio_buscar.setText('')


    def buscar_actualizar(self):
        pass

    def buscar_eliminar(self):
        pass

    def buscar_buscar(self):

        self.productodao.producto.clave = self.sku_buscar.text()
        datos = self.productodao.buscarProductos()
        if len(datos)==0:
            self.mensaje.setText("SKU no Existe!")
        else:
            self.descripcion_buscar.setText(datos[0][2])
            self.existencia_buscar.setText(str(datos[0][3]))
            self.precio_buscar.setText(str(datos[0][4]))

        

            
            
       
# 6.- mover ventana

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
    def mover_ventana(self, event):
        if self.isMaximized() == False:			
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.clickPosition)
                self.clickPosition = event.globalPos()
                event.accept()

        if event.globalPos().y() <=20:
            self.showMaximized()
        else:
            self.showNormal()

#7.- Mover menú

    def mover_menu(self):
        if True:			
            width = self.frame_lateral.width()
            widthb = self.boton_menu.width()
            normal = 0
            if width==0:
                extender = 200
                self.boton_menu.setText("Menú")
            else:
                extender = normal
                self.boton_menu.setText("")
                
            self.animacion = QPropertyAnimation(self.frame_lateral, b'minimumWidth')
            self.animacion.setDuration(300)
            self.animacion.setStartValue(width)
            self.animacion.setEndValue(extender)
            self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animacion.start()
            
            self.animacionb = QPropertyAnimation(self.boton_menu, b'minimumWidth')
        
            self.animacionb.setStartValue(width)
            self.animacionb.setEndValue(extender)
            self.animacionb.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animacionb.start()