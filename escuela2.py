import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector

# Conexión a la base de datos MySQL
conexion = mysql.connector.connect(host="localhost", user="root", password="12345", database="ESCUELA")

# Función para cargar y mostrar información en el Treeview
def cargar_datos():
    tree.delete(*tree.get_children())  # Borrar datos existentes en el Treeview
    cursor = conexion.cursor()
    cursor.execute("SELECT Alumnos.IDALUMNO, Alumnos.NOMBRE, Alumnos.APELLIDO, Alumnos.DNI, Carreras.NOMBRE, EstadoAlumno.NOMBRE FROM Alumnos JOIN Carreras ON Alumnos.IDCARRERA = Carreras.IDCARRERA JOIN EstadoAlumno ON Alumnos.IDESTADOALUMNO = EstadoAlumno.IDESTADOALUMNO WHERE Alumnos.IDESTADOALUMNO = 2")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

# Función para obtener las carreras desde la base de datos y cargarlas en el ComboBox
def cargar_carreras():
    cursor = conexion.cursor()
    cursor.execute("SELECT IDCARRERA, NOMBRE FROM Carreras ORDER BY NOMBRE")
    carreras = cursor.fetchall()
    carrera_combobox['values'] = [row[1] for row in carreras]
    return carreras 

def cargar_estadoalumno():
    cursor = conexion.cursor()
    cursor.execute("SELECT IDESTADOALUMNO, NOMBRE FROM EstadoAlumno ORDER BY NOMBRE")
    estado_alumnos = cursor.fetchall()
    estado_alumno_combobox['values'] = [row[1] for row in estado_alumnos]
    return estado_alumnos

# Función para mostrar una ventana de alerta
def mostrar_alerta(mensaje):
    messagebox.showwarning("Alerta", mensaje)

# Función para validar un DNI
def validar_dni(dni):
    if not dni.isdigit() or len(dni) != 8:
        return False
    return True
        
# Función para guardar un nuevo registro de alumno
def guardar_alumno():
    nombre = nombre_entry.get().upper()
    apellido = apellido_entry.get().upper()
    dni = dni_entry.get()
    carrera_nombre = carrera_combobox.get()
    estado_alumno_nombre = estado_alumno_combobox.get()
    estado_alumno = 2  # Valor predeterminado para IDESTADOALUMNO

    if not validar_dni(dni):
        mostrar_alerta("El DNI debe contener exactamente 8 números. Inténtelo de nuevo.")
        dni_entry.delete(0, tk.END)  # Limpiar el campo DNI
        dni_entry.focus()  # Establecer el enfoque en el campo DNI para la corrección
        return

    if nombre and apellido and dni and carrera_nombre and estado_alumno:
        # Obtener el ID de la carrera seleccionada
        carreras = cargar_carreras()
        carrera_id = None
        for carrera in carreras:
            if carrera[1] == carrera_nombre:
                carrera_id = carrera[0]
                break

        # Obtener el ID del estado del alumno seleccionado
        estado_alumnos = cargar_estadoalumno()
        estado_alumno_id = None
        for estado_alumno in estado_alumnos:
            if estado_alumno[1] == estado_alumno_nombre:
                estado_alumno_id = estado_alumno[0]
                break

        cursor = conexion.cursor()
        # Insertar un nuevo registro en la tabla Alumnos con el ID de carrera y el ID del estado del alumno
        cursor.execute("INSERT INTO Alumnos (NOMBRE, APELLIDO, DNI, IDCARRERA, IDESTADOALUMNO) VALUES (%s, %s, %s, %s, %s)", (nombre, apellido, dni, carrera_id, estado_alumno_id))
        conexion.commit()
        cargar_datos()  # Actualizar la vista
        # Limpiar los campos después de insertar
        nombre_entry.delete(0, tk.END)
        apellido_entry.delete(0, tk.END)
        dni_entry.delete(0, tk.END)
        carrera_combobox.set("")  # Limpiar la selección del ComboBox
        estado_alumno_combobox.set("")
    else:
        mostrar_alerta("Los campos son obligatorios. Debe completarlos.")


def modificar_alumno():
    seleccion = tree.selection()
    if seleccion:
        item = tree.item(seleccion[0])
        id_alumno = item['values'][0]
        
        nombre_actual = item['values'][1]
        apellido_actual = item['values'][2]
        dni_actual = item['values'][3]
        carrera_actual = item['values'][4]
        estado_alumno_actual = item['values'][5]
        
        nombre_entry.delete(0, tk.END)
        nombre_entry.insert(0, nombre_actual)
        
        apellido_entry.delete(0, tk.END)
        apellido_entry.insert(0, apellido_actual)
        
        dni_entry.delete(0, tk.END)
        dni_entry.insert(0, dni_actual)
        
        carrera_combobox.set(carrera_actual)
        estado_alumno_combobox.set(estado_alumno_actual)
    else:
        mostrar_alerta("Por favor, seleccione un registro para modificar.")


def guardar_cambios_alumno():
    seleccion = tree.selection()
    if seleccion:
        item = tree.item(seleccion[0])
        id_alumno = item['values'][0]
        nombre = nombre_entry.get()
        apellido = apellido_entry.get()
        dni = dni_entry.get()
        carrera_nombre = carrera_combobox.get()
        estado_alumno_nombre = estado_alumno_combobox.get()

        if nombre and apellido and dni and carrera_nombre and estado_alumno_nombre:
            carreras = cargar_carreras()
            carrera_id = None
            for carrera in carreras:
                if carrera[1] == carrera_nombre:
                    carrera_id = carrera[0]
                    break

            estado_alumnos = cargar_estadoalumno()
            estado_alumno_id = None
            for estado_alumno in estado_alumnos:
                if estado_alumno[1] == estado_alumno_nombre:
                    estado_alumno_id = estado_alumno[0]
                    break

            cursor = conexion.cursor()
            cursor.execute("UPDATE Alumnos SET NOMBRE = %s, APELLIDO = %s, DNI = %s, IDCARRERA = %s, IDESTADOALUMNO = %s WHERE IDALUMNO = %s",(nombre, apellido, dni, carrera_id, estado_alumno_id, id_alumno))
            conexion.commit()
            cargar_datos() 
            mostrar_alerta("Registro modificado exitosamente.")
            
            nombre_entry.delete(0, tk.END)
            apellido_entry.delete(0, tk.END)
            dni_entry.delete(0, tk.END)
            carrera_combobox.set("")  
            estado_alumno_combobox.set("")
        else:
            mostrar_alerta("Los campos son obligatorios. Debe completarlos.")
    else:
        mostrar_alerta("Por favor, seleccione un registro para modificar.")


def eliminar_alumno():
    seleccion = tree.selection()
    if seleccion:
        confirmacion = messagebox.askyesno("Confirmación", "¿Está seguro que desea eliminar el registro seleccionado?")
        if confirmacion:
            item = tree.item(seleccion[0])
            id_alumno = item['values'][0]
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Alumnos WHERE IDALUMNO = %s", (id_alumno,))
            conexion.commit()
            cargar_datos() 
            mostrar_alerta("Registro eliminado exitosamente.")
    else:
        mostrar_alerta("Por favor, seleccione un registro para eliminar.")


# Crear ventana
root = tk.Tk()
root.title("Consulta de Alumnos")
root.resizable(0, 0)
root.configure(bg="pink")

# Crear un frame con un borde visible para el formulario de inscripción
formulario_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
formulario_frame.pack(padx=10, pady=10)

# Título del formulario
titulo_label = tk.Label(formulario_frame, text="Formulario Inscripción", font=("Helvetica", 14))
titulo_label.grid(row=0, column=0, columnspan=2, pady=10)

# Campos de entrada para nombre, apellido y DNI con el mismo ancho que el ComboBox
nombre_label = tk.Label(formulario_frame, text="Nombre:")
nombre_label.grid(row=1, column=0)
nombre_entry = tk.Entry(formulario_frame)
nombre_entry.grid(row=1, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="ew")

apellido_label = tk.Label(formulario_frame, text="Apellido:")
apellido_label.grid(row=2, column=0)
apellido_entry = tk.Entry(formulario_frame)
apellido_entry.grid(row=2, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="ew")

dni_label = tk.Label(formulario_frame, text="DNI:")
dni_label.grid(row=3, column=0)
dni_entry = tk.Entry(formulario_frame)
dni_entry.grid(row=3, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="ew")

# Combo box para la carrera
carrera_label = tk.Label(formulario_frame, text="Carrera:")
carrera_label.grid(row=4, column=0)
carrera_combobox = ttk.Combobox(formulario_frame, state="readonly")  # Configurar el ComboBox como de solo lectura
carrera_combobox.grid(row=4, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="ew")

estado_alumno_label = tk.Label(formulario_frame, text="Estado alumno:")
estado_alumno_label.grid(row=5, column=0)
estado_alumno_combobox = ttk.Combobox(formulario_frame, state="readonly")
estado_alumno_combobox.grid(row=5, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="ew")


carreras = cargar_carreras()
estado_alumnos = cargar_estadoalumno()

# Botón para guardar un nuevo registro de alumno
guardar_button = tk.Button(formulario_frame, text="Guardar", command=guardar_alumno)
guardar_button.grid(row=6, columnspan=2, pady=10, sticky="ew")

guardar_cambios_button = tk.Button(formulario_frame, text="Guardar Cambios", command=guardar_cambios_alumno)
guardar_cambios_button.grid(row=7, columnspan=2, pady=10, sticky="ew")

# Crear Treeview para mostrar la información
tree = ttk.Treeview(root, columns=("ID", "Nombre", "Apellido", "DNI", "Carrera", "Estado alumno"))
tree.heading("#1", text="ID")
tree.heading("#2", text="Nombre")
tree.heading("#3", text="Apellido")
tree.heading("#4", text="DNI")
tree.heading("#5", text="Carrera")
tree.heading("#6", text="Estado alumno")
tree.column("#0", width=0, stretch=tk.NO)  # Ocultar la columna #0 que habitualmente muestra las primary key de los objetos
tree.pack(padx=10, pady=10)
tree.column("#1", width=40)
tree.column("#2", width=100)
tree.column("#3", width=100)
tree.column("#4", width=80)
tree.column("#5", width=100)
tree.column("#6", width=100)
tree.pack(padx=10, pady=10)

# Botón para cargar datos
cargar_button = tk.Button(root, text="Cargar Datos", command=cargar_datos)
cargar_button.pack(pady=5)

modificar_button = tk.Button(root, text="Modificar", command=modificar_alumno)
modificar_button.pack(pady=5)

eliminar_button = tk.Button(root, text="Eliminar", command=eliminar_alumno)
eliminar_button.pack(pady=5)


root.mainloop()
conexion.close()