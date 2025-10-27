from modelo.cliente import Cliente
from modelo.conexionbd import ConexionBd  # Asegúrate de tener esta clase definida

class ClienteDAO:

    def __init__(self):
        self.bd = ConexionBd()
        self.cliente = Cliente()

    def listarClientes(self):
        self.bd.establecerConexionBD()

        cursor = self.bd.conexion.cursor()
        sp = "exec [dbo].[sp_ListarClientes]"
        cursor.execute(sp)
        filas = cursor.fetchall()
        self.bd.cerrarConexionBD()
        return filas

    def guardarCliente(self):
        self.bd.establecerConexionBD()

        cursor = self.bd.conexion.cursor()
        sp = "exec [dbo].[sp_InsertarCliente] @nombre=?, @apellido=?, @correo_electronico=?, @telefono=?, @direccion=?"
        parametros = (
            self.cliente.nombre,
            self.cliente.apellido,
            self.cliente.correo_electronico,
            self.cliente.telefono,
            self.cliente.direccion
        )
        cursor.execute(sp, parametros)
        self.bd.conexion.commit()

        self.bd.cerrarConexionBD()

    def actualizarCliente(self):
        self.bd.establecerConexionBD()

        cursor = self.bd.conexion.cursor()
        sp = "exec [dbo].[sp_ActualizarCliente] @id_cliente=?, @nombre=?, @apellido=?, @correo_electronico=?, @telefono=?, @direccion=?"
        parametros = (
            self.cliente.id_cliente,
            self.cliente.nombre,
            self.cliente.apellido,
            self.cliente.correo_electronico,
            self.cliente.telefono,
            self.cliente.direccion
        )
        cursor.execute(sp, parametros)
        self.bd.conexion.commit()

        self.bd.cerrarConexionBD()

    def eliminarCliente(self):
        self.bd.establecerConexionBD()

        cursor = self.bd.conexion.cursor()
        sp = "exec [dbo].[sp_EliminarCliente] @id_cliente=?"
        parametros = (self.cliente.id_cliente,)
        cursor.execute(sp, parametros)
        self.bd.conexion.commit()

        self.bd.cerrarConexionBD()

    def consultarClientePorID(self):
        self.bd.establecerConexionBD()

        cursor = self.bd.conexion.cursor()
        sp = "exec [dbo].[sp_ConsultarClientePorID] @id_cliente=?"
        parametros = (self.cliente.id_cliente,)
        cursor.execute(sp, parametros)
        resultado = cursor.fetchone()

        if resultado:
            print(resultado)

        self.bd.cerrarConexionBD()

    def buscarClientes(self, termino):
        self.bd.establecerConexionBD()

        cursor = self.bd.conexion.cursor()
        sp = "exec [dbo].[sp_BuscarClientes] @termino=?"
        cursor.execute(sp, (termino,))
        filas = cursor.fetchall()
        self.bd.cerrarConexionBD()
        return filas
