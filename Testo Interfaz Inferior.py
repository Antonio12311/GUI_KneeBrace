import tkinter as tk
from tkinter import ttk, messagebox

from numpy.f2py.crackfortran import endifs


def validar_entrada(text):
    return text.isdigit() or text == ""


def actualizar_estado(event=None):
    # Habilita la entrada solo si Nivel 4 o Nivel 5 están seleccionados
    if combobox.get() in ["Nivel 4", "Nivel 5"]:
        entrada.config(state="normal")
    else:
        entrada.config(state="disabled")
        entrada.delete(0, tk.END)


def verificar_niveles_anteriores(nivel_actual):
    # Pregunta solo si es la primera vez seleccionando un nivel mayor a 1
    if nivel_actual > 1 and not niveles_superados[nivel_actual - 2]:
        respuesta = messagebox.askquestion("Confirmación", f"¿Pasó exitosamente los niveles 1 a {nivel_actual - 1}?")
        if respuesta == "yes":
            for i in range(nivel_actual - 1):
                cuadros[4 - i].config(bg="green")
                niveles_superados[i] = True
            return True
        else:
            messagebox.showwarning("Aviso", "Por favor, seleccione el nivel 1 para hacer los test de forma correcta.")
            combobox.set("Nivel 1")
            return False
    elif nivel_actual > 1 and not niveles_superados[nivel_actual - 1]:
        messagebox.showwarning("AVISO", "El nivel anterior no fue superado con éxito, favor de reintentar")
        return False
    return True

"""
def verificar_niveles_anteriores(nivel_actual):
    if nivel_actual > 1 and not niveles_superados[nivel_actual - 2]:
        respuesta = messagebox.askquestion("Confirmación", f"¿Pasó exitosamente los niveles 1 a {nivel_actual - 1}?")

        if respuesta == "yes":
            for i in range(nivel_actual - 1):
                cuadros[4 - i].config(bg="green")  # Cambia el color de los cuadros
                niveles_superados[i] = True  # Marca niveles como superados
            return True
        else:
            messagebox.showwarning("Aviso", f"Por favor, seleccione el nivel faltante para hacer las pruebas de forma correcta.")
            return False
    return True
"""
def aplicar_cambios():
    nivel = combobox.get()
    valor = entrada.get()

    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])

        if nivel_num == 4 and valor.isdigit() and int(valor) > 10:
            mensaje_label.config(text="Límite de valor es 10 en Nivel 4", fg="red")
            return
        elif nivel_num == 5 and valor.isdigit() and int(valor) > 20:
            mensaje_label.config(text="Límite de valor es 20 en Nivel 5", fg="red")
            return
        elif nivel_num in (4, 5) and ((not valor.strip() or not valor.isdigit()) or int(valor) == 0):
            mensaje_label.config(text="ERROR. Ingrese un valor de fuerza", fg="red")
            return

        if not verificar_niveles_anteriores(nivel_num):
            return

        mensaje_label.config(text="Cambios aplicados correctamente", fg="green")
        boton_iniciar.config(state="normal")
        boton_detener.config(state="normal")
        entrada.config(state="disabled")
        combobox.config(state="disabled")

    mensaje_label.after(5000, lambda: mensaje_label.config(text=""))


def iniciar_animacion():
    nivel = combobox.get()

    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])
        if 1 <= nivel_num <= 5:
            global animacion_activa, blink_state
            animacion_activa = True
            blink_state = True
            parpadear(cuadros[5 - nivel_num])

            combobox.config(state="disabled")
            boton_si.config(state="normal")
            boton_no.config(state="normal")
            entrada.config(state="disabled")
            boton_iniciar.config(state="disabled")


def parpadear(cuadro):
    global animacion_activa, blink_state
    if animacion_activa:
        color = "blue" if blink_state else "white"
        cuadro.config(bg=color)
        blink_state = not blink_state
        cuadro.after(500, lambda: parpadear(cuadro))


def detener_animacion():
    global animacion_activa
    nivel = combobox.get()
    animacion_activa = False
    boton_si.config(state="disabled")
    boton_no.config(state="disabled")
    combobox.config(state="normal")
    boton_iniciar.config(state="disabled")
    boton_detener.config(state="disabled")
    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])
        if nivel_num > 3:
            entrada.config(state="normal")



def marcar_llegada(color):
    nivel = combobox.get()

    if nivel.startswith("Nivel "):
        nivel_num = int(nivel.split(" ")[1])
        if 1 <= nivel_num <= 3:
            detener_animacion()
            cuadros[5 - nivel_num].config(bg=color)
            niveles_superados[nivel_num - 1] = True
            entrada.config(state="disabled")
        else:
            detener_animacion()
            cuadros[5 - nivel_num].config(bg=color)
            niveles_superados[nivel_num - 1] = True
            entrada.config(state="normal")


def main():
    global combobox, entrada, mensaje_label, cuadros, boton_si, boton_no, boton_iniciar, boton_detener, niveles_superados

    root = tk.Tk()
    root.title("Selector de Nivel de Fuerza")
    root.geometry("1280x720")

    label = tk.Label(root, text="Seleccione un nivel de fuerza:", font=("Arial", 14))
    label.pack(pady=20)

    niveles = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
    combobox = ttk.Combobox(root, values=niveles, font=("Arial", 16), width=20)
    combobox.set("Elija el nivel de fuerza")
    combobox.place(x=50, y=550)

    vcmd = root.register(validar_entrada)
    entrada = tk.Entry(root, font=("Arial", 16), width=10, validate="key", validatecommand=(vcmd, "%P"))
    entrada.place(x=320, y=550)
    entrada.config(state="disabled")

    boton_aplicar = tk.Button(root, text="Aplicar cambios", font=("Arial", 14), command=aplicar_cambios)
    boton_aplicar.place(x=50, y=610)

    mensaje_label = tk.Label(root, text="", font=("Arial", 12))
    mensaje_label.place(x=50, y=650)

    cuadros = []
    for i in range(5):
        cuadro = tk.Label(root, text=str(5 - i), font=("Arial", 14), width=10, height=2, relief="solid", bg="white")
        cuadro.place(x=500, y=600 - (i * 50))
        cuadros.append(cuadro)

    boton_iniciar = tk.Button(root, text="Iniciar", font=("Arial", 20), command=iniciar_animacion, state="disabled")
    boton_iniciar.place(x=850, y=500)

    boton_detener = tk.Button(root, text="Detener", font=("Arial", 20), command=detener_animacion, state="disabled")
    boton_detener.place(x=850, y=600)

    boton_si = tk.Button(root, text="Si llegó", font=("Arial", 20), bg="green", state="disabled", command=lambda: marcar_llegada("green"))
    boton_si.place(x=700, y=500)

    boton_no = tk.Button(root, text="No llegó", font=("Arial", 20), bg="red", state="disabled", command=lambda: marcar_llegada("red"))
    boton_no.place(x=700, y=600)

    combobox.bind("<<ComboboxSelected>>", actualizar_estado)

    niveles_superados = [False] * 5

    root.mainloop()


animacion_activa = False
blink_state = True

main()