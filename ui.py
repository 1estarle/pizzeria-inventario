import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Toplevel, Label, Entry, Button, messagebox, filedialog
from PIL import Image, ImageTk, UnidentifiedImageError
from db import obtener_productos, agregar_producto_db, actualizar_cantidad, eliminar_producto_db, actualizar_imagen
import os
import datetime

def iniciar_app():
    app = tb.Window(themename="flatly")
    app.title("Inventario Pizzería")
    app.geometry("900x600")

    topbar = tb.Frame(app, bootstyle="primary")
    topbar.pack(side=TOP, fill=X)

    titulo = tb.Label(topbar, text="Inventario Pizzería", font=("Segoe UI", 18, "bold"), foreground="white", bootstyle="inverse-primary")
    titulo.pack(side=LEFT, padx=20, pady=10)

    btn_agregar = tb.Button(topbar, text="Agregar Producto", bootstyle="success", command=lambda: agregar_producto())
    btn_agregar.pack(side=RIGHT, padx=10)

    frame_productos = tb.Frame(app)
    frame_productos.pack(fill=BOTH, expand=True, padx=10, pady=10)

    frame_busqueda = tb.Frame(app)
    frame_busqueda.pack(fill=X, padx=10, pady=5)

    tb.Label(frame_busqueda, text="Buscar:").pack(side=LEFT, padx=5)
    entry_buscar = tb.Entry(frame_busqueda, width=30)
    entry_buscar.insert(0, "Nombre del producto")
    entry_buscar.pack(side=LEFT, padx=5)

    frame_listado = tb.Frame(app)
    frame_listado.pack(fill=BOTH, expand=True, padx=10, pady=5)

    columnas = ("Nombre", "Cantidad", "Última Modificación")
    inventario_total = tb.Treeview(frame_listado, columns=columnas, show="headings")

    for col in columnas:
        inventario_total.heading(col, text=col)

    inventario_total.column("Nombre", width=200, anchor="center")
    inventario_total.column("Cantidad", width=100, anchor="center")
    inventario_total.column("Última Modificación", width=200, anchor="center")

    inventario_total.pack(fill=X, padx=10, pady=5)

    def refrescar_productos(filtro=""):
        for widget in frame_productos.winfo_children():
            widget.destroy()

        productos = obtener_productos()

        if filtro and filtro != "Nombre del producto":
            productos = [p for p in productos if filtro.lower() in p[0].lower()]

        if not productos:
            lbl_vacio = tb.Label(frame_productos, text="No hay productos cargados", font=("Segoe UI", 14), bootstyle="warning")
            lbl_vacio.pack(pady=20)
            actualizar_tabla_total(productos)
            return

        for idx, (nombre, cantidad, imagen, fecha_mod) in enumerate(productos):
            frame = tb.Frame(frame_productos, relief=SOLID, borderwidth=1)
            frame.grid(row=idx//4, column=idx%4, padx=10, pady=10)

            if imagen and os.path.exists(imagen):
                try:
                    img_pil = Image.open(imagen)
                    img_pil = img_pil.resize((100, 100))
                    img = ImageTk.PhotoImage(img_pil)
                    lbl_img = Label(frame, image=img)
                    lbl_img.image = img
                    lbl_img.pack()
                except (UnidentifiedImageError, Exception):
                    lbl_error = tb.Label(frame, text="Imagen inválida", bootstyle="danger")
                    lbl_error.pack()

            lbl_nombre = tb.Label(frame, text=nombre, font=("Segoe UI", 12, "bold"))
            lbl_nombre.pack(pady=5)

            lbl_cantidad = tb.Label(frame, text=f"Stock: {cantidad}", bootstyle="info")
            lbl_cantidad.pack(pady=2)

            btn_modificar = tb.Button(frame, text="Modificar", bootstyle="secondary", command=lambda n=nombre: abrir_modificar(n))
            btn_modificar.pack(pady=2)

            btn_img = tb.Button(frame, text="Cambiar Imagen", bootstyle="info", command=lambda n=nombre: cambiar_imagen(n))
            btn_img.pack(pady=2)

            btn_eliminar = tb.Button(frame, text="Eliminar", bootstyle="danger", command=lambda n=nombre: eliminar_producto(n))
            btn_eliminar.pack(pady=2)

        actualizar_tabla_total(productos)

    def actualizar_tabla_total(productos):
        for row in inventario_total.get_children():
            inventario_total.delete(row)

        for nombre, cantidad, _, fecha_mod in productos:
            inventario_total.insert('', END, values=(nombre, cantidad, fecha_mod))

    def abrir_modificar(nombre):
        top = Toplevel(app)
        top.title(f"Modificar {nombre}")
        top.geometry("300x150")

        productos = dict((p[0], p[1]) for p in obtener_productos())

        cantidad_actual = productos[nombre]
        cantidad_temp = tb.IntVar(value=cantidad_actual)

        tb.Label(top, text="Cantidad actual:").pack(pady=5)

        contenedor = tb.Frame(top)
        contenedor.pack(pady=5)

        def disminuir():
            if cantidad_temp.get() > 0:
                cantidad_temp.set(cantidad_temp.get() - 1)

        def aumentar():
            cantidad_temp.set(cantidad_temp.get() + 1)

        btn_menos = tb.Button(contenedor, text="-", bootstyle="danger", command=disminuir)
        btn_menos.pack(side=LEFT, padx=5)

        tb.Entry(contenedor, textvariable=cantidad_temp, width=10, justify="center").pack(side=LEFT)

        btn_mas = tb.Button(contenedor, text="+", bootstyle="success", command=aumentar)
        btn_mas.pack(side=LEFT, padx=5)

        def guardar():
            actualizar_cantidad(nombre, cantidad_temp.get())
            top.destroy()
            refrescar_productos(entry_buscar.get())

        tb.Button(top, text="Guardar", bootstyle="primary", command=guardar).pack(pady=10)

    def cambiar_imagen(nombre):
        top = Toplevel(app)
        top.title(f"Cambiar Imagen - {nombre}")
        top.geometry("300x150")

        def seleccionar_archivo():
            archivo = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif")])
            if archivo:
                entry_imagen.delete(0, END)
                entry_imagen.insert(0, archivo)

        tb.Label(top, text="Nueva ruta de imagen:").pack(pady=5)
        entry_imagen = tb.Entry(top)
        entry_imagen.pack(pady=5)
        tb.Button(top, text="Buscar", bootstyle="info", command=seleccionar_archivo).pack(pady=5)

        def guardar():
            nueva_imagen = entry_imagen.get()
            if not os.path.exists(nueva_imagen):
                messagebox.showerror("Error", "La ruta no existe")
                return
            try:
                Image.open(nueva_imagen)
            except (UnidentifiedImageError, Exception):
                messagebox.showerror("Error", "El archivo no es una imagen válida")
                return
            actualizar_imagen(nombre, nueva_imagen)
            top.destroy()
            refrescar_productos(entry_buscar.get())

        tb.Button(top, text="Guardar", bootstyle="primary", command=guardar).pack(pady=10)

    def eliminar_producto(nombre):
        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar '{nombre}'?")
        if confirm:
            eliminar_producto_db(nombre)
            refrescar_productos(entry_buscar.get())

    def agregar_producto():
        top = Toplevel(app)
        top.title("Agregar Producto")
        top.geometry("300x300")

        tb.Label(top, text="Nombre:").pack(pady=5)
        entry_nombre = tb.Entry(top)
        entry_nombre.pack(pady=5)

        tb.Label(top, text="Cantidad inicial:").pack(pady=5)
        entry_cantidad = tb.Entry(top)
        entry_cantidad.pack(pady=5)

        tb.Label(top, text="Ruta de imagen:").pack(pady=5)
        entry_imagen = tb.Entry(top)
        entry_imagen.pack(pady=5)

        def seleccionar_archivo():
            archivo = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif")])
            if archivo:
                entry_imagen.delete(0, END)
                entry_imagen.insert(0, archivo)

        tb.Button(top, text="Buscar", bootstyle="info", command=seleccionar_archivo).pack(pady=5)

        def guardar():
            try:
                nombre = entry_nombre.get()
                cantidad = int(entry_cantidad.get())
                imagen = entry_imagen.get()
                if not os.path.exists(imagen):
                    messagebox.showerror("Error", "La ruta no existe")
                    return
                Image.open(imagen)
                agregar_producto_db(nombre, cantidad, imagen)
                top.destroy()
                refrescar_productos(entry_buscar.get())
            except (UnidentifiedImageError, Exception):
                messagebox.showerror("Error", "El archivo no es una imagen válida")

        tb.Button(top, text="Guardar", bootstyle="primary", command=guardar).pack(pady=10)

    entry_buscar.bind("<KeyRelease>", lambda e: refrescar_productos(entry_buscar.get()))

    refrescar_productos()

    app.mainloop()
