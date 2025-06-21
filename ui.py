import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import os
import json
import shutil

ASSETS_DIR = "assets"
INVENTARIO_PATH = "inventario.json"

# Cargar y guardar inventario
def cargar_inventario():
    if os.path.exists(INVENTARIO_PATH):
        with open(INVENTARIO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "Producto 1": {"cantidad": 10, "imagen": "producto1.png"},
            "Producto 2": {"cantidad": 15, "imagen": "producto2.png"},
            "Producto 3": {"cantidad": 8, "imagen": "producto3.png"},
        }

def guardar_inventario():
    with open(INVENTARIO_PATH, "w", encoding="utf-8") as f:
        json.dump(inventario, f, ensure_ascii=False, indent=2)

inventario = cargar_inventario()

def iniciar_app():
    app = tb.Window(themename="flatly")  # Puedes cambiar el tema aquí
    app.title("Gestión de Inventario - Pizzería")
    app.geometry("1000x700")

    # Barra superior
    topbar = tb.Frame(app, bootstyle=PRIMARY)
    topbar.pack(fill=X)

    tb.Label(topbar, text="Gestión de Inventario MUT", font=("Segoe UI", 18, "bold"),
             bootstyle="inverse").pack(side=LEFT, padx=20, pady=15)

    tb.Button(topbar, text="Agregar producto", bootstyle=SUCCESS, command=lambda: agregar_producto(app)).pack(side=RIGHT, padx=20, pady=10)

    # Notebook para pestañas
    notebook = tb.Notebook(app)
    notebook.pack(fill=BOTH, expand=True, padx=20, pady=20)

    frame_inventario = tb.Frame(notebook)
    notebook.add(frame_inventario, text="Inventario")

    frame_productos = tb.Frame(frame_inventario)
    frame_productos.pack(pady=10)

    frame_tabla = tb.Frame(frame_inventario)
    frame_tabla.pack(fill=BOTH, expand=True, padx=10, pady=10)

    tabla = tb.Treeview(frame_tabla, columns=("Producto", "Cantidad"), show="headings", bootstyle="info")
    tabla.heading("Producto", text="Producto")
    tabla.heading("Cantidad", text="Cantidad")
    tabla.column("Producto", width=300, anchor="center")
    tabla.column("Cantidad", width=100, anchor="center")
    tabla.pack(fill=BOTH, expand=True)

    def actualizar_tabla():
        for i in tabla.get_children():
            tabla.delete(i)
        for nombre, datos in inventario.items():
            tabla.insert("", "end", values=(nombre, datos["cantidad"]))

    def guardar_cambio(nombre, nueva_cantidad):
        inventario[nombre]["cantidad"] = nueva_cantidad
        guardar_inventario()
        actualizar_tabla()
        render_productos()

    def eliminar_producto(nombre, ventana):
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}' del inventario?"):
            inventario.pop(nombre, None)
            guardar_inventario()
            actualizar_tabla()
            render_productos()
            ventana.destroy()

    def modificar_producto(nombre):
        top = Toplevel(app)
        top.title(f"Modificar {nombre}")
        top.geometry("320x270")
        top.resizable(False, False)

        cantidad_actual = inventario[nombre]["cantidad"]
        cantidad_temp = tb.IntVar(value=cantidad_actual)

        tb.Label(top, text=nombre, font=("Segoe UI", 14, "bold")).pack(pady=10)

        f = tb.Frame(top)
        f.pack(pady=10)

        tb.Button(f, text="-", width=4, bootstyle=DANGER, command=lambda: cantidad_temp.set(max(0, cantidad_temp.get() - 1))).pack(side=LEFT, padx=10)
        tb.Label(f, textvariable=cantidad_temp, font=("Segoe UI", 14), width=5).pack(side=LEFT)
        tb.Button(f, text="+", width=4, bootstyle=SUCCESS, command=lambda: cantidad_temp.set(cantidad_temp.get() + 1)).pack(side=LEFT, padx=10)

        tb.Button(top, text="Guardar cambios", width=20, bootstyle=PRIMARY,
                  command=lambda: [guardar_cambio(nombre, cantidad_temp.get()), top.destroy()]).pack(pady=10)

        tb.Button(top, text="Eliminar producto", width=20, bootstyle=DANGER,
                  command=lambda: eliminar_producto(nombre, top)).pack(pady=5)

    def agregar_producto(parent):
        top = Toplevel(parent)
        top.title("Agregar producto")
        top.geometry("400x300")
        top.resizable(False, False)

        nombre_var = tb.StringVar()
        cantidad_var = tb.IntVar()
        imagen_path = tb.StringVar()

        tb.Label(top, text="Nombre del producto:").pack(pady=(15, 0))
        tb.Entry(top, textvariable=nombre_var, width=30).pack()

        tb.Label(top, text="Cantidad inicial:").pack(pady=(10, 0))
        tb.Entry(top, textvariable=cantidad_var, width=10).pack()

        def seleccionar_imagen():
            file = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png"), ("All", "*.*")])
            if file:
                imagen_path.set(file)

        tb.Button(top, text="Seleccionar imagen", bootstyle=INFO, command=seleccionar_imagen).pack(pady=10)

        def guardar():
            nombre = nombre_var.get().strip()
            cantidad = cantidad_var.get()
            img_src = imagen_path.get()

            if not nombre or cantidad < 0 or not img_src:
                messagebox.showerror("Error", "Completa todos los campos.")
                return

            if not os.path.exists(ASSETS_DIR):
                os.makedirs(ASSETS_DIR)

            img_name = os.path.basename(img_src)
            shutil.copy(img_src, os.path.join(ASSETS_DIR, img_name))

            inventario[nombre] = {"cantidad": cantidad, "imagen": img_name}
            guardar_inventario()
            actualizar_tabla()
            render_productos()
            top.destroy()

        tb.Button(top, text="Agregar producto", bootstyle=SUCCESS, command=guardar, width=20).pack(pady=15)

    def render_productos():
        for w in frame_productos.winfo_children():
            w.destroy()

        for nombre, datos in inventario.items():
            card = tb.Frame(frame_productos, borderwidth=1, relief="solid", padding=10)
            card.pack(side=tb.LEFT, padx=10, pady=10)

            img_path = os.path.join(ASSETS_DIR, datos["imagen"])
            try:
                img = Image.open(img_path).resize((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                lbl_img = tb.Label(card, image=img_tk)
                lbl_img.image = img_tk
                lbl_img.pack()
            except:
                tb.Label(card, text="[Sin imagen]").pack()

            tb.Label(card, text=nombre, font=("Segoe UI", 11, "bold")).pack(pady=(5, 0))
            tb.Label(card, text=f"Cantidad: {datos['cantidad']}", font=("Segoe UI", 10)).pack()

            tb.Button(card, text="Modificar", bootstyle=PRIMARY, width=15,
                      command=lambda n=nombre: modificar_producto(n)).pack(pady=5)

    render_productos()
    actualizar_tabla()
    app.mainloop()
