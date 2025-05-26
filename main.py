import tkinter as tk
from tkinter import messagebox
import joblib
import os
import csv
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Rutas
MODEL_PATH = "models/modelo_spam.pkl"
HISTORIAL_TXT = "historial.txt"
HISTORIAL_CSV = "historial.csv"

# Ejemplos
ejemplos_mensajes = [
    "Congratulations! You've won a free iPhone! Click here to claim.",
    "Hola, ¿vas a venir a la reunión mañana?",
    "URGENT: Your account has been compromised, click to reset password.",
    "Gracias por tu ayuda con el proyecto.",
    "Te envío el archivo en cuanto lo tenga listo.",
    "¡Gana millones desde casa sin hacer nada!"
]

# Cargar modelo
def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        messagebox.showerror("Error", "El modelo no existe. Ejecuta entrenar.py primero.")
        exit()
    return joblib.load(MODEL_PATH)

modelo = cargar_modelo()

# Clasificación
def clasificar_mensaje(texto):
    prediccion = modelo.predict([texto])[0]
    probabilidad = modelo.predict_proba([texto])[0].max()
    return prediccion, probabilidad

# Guardar historial
def guardar_en_historial_txt(linea):
    with open(HISTORIAL_TXT, "a", encoding="utf-8") as f:
        f.write(linea + "\n")

def guardar_en_historial_csv(tipo):
    nuevo = not os.path.exists(HISTORIAL_CSV)
    with open(HISTORIAL_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if nuevo:
            writer.writerow(["timestamp", "resultado"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo])

# Cargar historial
def cargar_historial(filtro_tipo="Todos", orden="Reciente", busqueda=""):
    historial_text.config(state="normal")
    historial_text.delete("1.0", tk.END)
    if not os.path.exists(HISTORIAL_TXT):
        return

    with open(HISTORIAL_TXT, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    # Filtro por tipo
    if filtro_tipo == "SPAM":
        lineas = [l for l in lineas if "🚫 SPAM" in l]
    elif filtro_tipo == "NO SPAM":
        lineas = [l for l in lineas if "✅ NO SPAM" in l]

    # Búsqueda
    if busqueda:
        lineas = [l for l in lineas if busqueda.lower() in l.lower()]

    # Orden
    if orden == "Reciente":
        lineas = lineas[::-1]

    for linea in lineas:
        historial_text.insert(tk.END, linea)
    historial_text.config(state="disabled")

# Borrar historial
def borrar_historial():
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres borrar todo el historial?"):
        open(HISTORIAL_TXT, "w", encoding="utf-8").close()
        open(HISTORIAL_CSV, "w", encoding="utf-8").close()
        cargar_historial()
        resultado_label.config(text="", fg="black")
        messagebox.showinfo("Listo", "Historial borrado correctamente.")

# Ver estadísticas
def mostrar_estadisticas():
    if not os.path.exists(HISTORIAL_CSV):
        messagebox.showinfo("Estadísticas", "Aún no hay datos registrados.")
        return

    with open(HISTORIAL_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        try:
            resultados = [fila["resultado"] for fila in reader]
        except KeyError:
            messagebox.showerror("Error", "El archivo historial.csv está mal formado.")
            return

    total = len(resultados)
    conteo = Counter(resultados)
    spam = conteo.get("spam", 0)
    no_spam = conteo.get("ham", 0)
    porcentaje_spam = (spam / total * 100) if total > 0 else 0

    if spam == 0 and no_spam == 0:
        messagebox.showinfo("Estadísticas", "No hay datos suficientes para mostrar gráfica.")
        return

    ventana_estadisticas = tk.Toplevel(ventana)
    ventana_estadisticas.title("📊 Estadísticas")
    ventana_estadisticas.geometry("500x400")

    tk.Label(ventana_estadisticas, text=f"Total mensajes: {total}", font=("Arial", 12)).pack(pady=5)
    tk.Label(ventana_estadisticas, text=f"SPAM: {spam}", font=("Arial", 12)).pack(pady=5)
    tk.Label(ventana_estadisticas, text=f"NO SPAM: {no_spam}", font=("Arial", 12)).pack(pady=5)
    tk.Label(ventana_estadisticas, text=f"Porcentaje SPAM: {porcentaje_spam:.2f}%", font=("Arial", 12)).pack(pady=5)

    fig, ax = plt.subplots()
    ax.pie([spam, no_spam], labels=["SPAM", "NO SPAM"], autopct="%1.1f%%", colors=["red", "green"])
    ax.set_title("Distribución de mensajes")

    canvas = FigureCanvasTkAgg(fig, master=ventana_estadisticas)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Acción analizar
def analizar_mensaje():
    texto = texto_entry.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showwarning("Advertencia", "Ingresa un mensaje para analizar.")
        return

    resultado, prob = clasificar_mensaje(texto)
    if resultado == "spam":
        tipo = "🚫 SPAM"
        resultado_label.config(text=f"{tipo} | Confianza: {prob:.2f}", fg="red")
    else:
        tipo = "✅ NO SPAM"
        resultado_label.config(text=f"{tipo} | Confianza: {prob:.2f}", fg="green")

    timestamp = datetime.now().strftime("%H:%M:%S")
    guardar_en_historial_txt(f"[{timestamp}] {tipo} | Confianza: {prob:.2f} | Texto: {texto}")
    guardar_en_historial_csv(resultado)

    cargar_historial(filtro_var.get(), orden_var.get(), buscador_var.get())

# Cargar ejemplo
def cargar_ejemplo(event):
    texto_entry.delete("1.0", tk.END)
    texto_entry.insert(tk.END, ejemplo_var.get())

# Interfaz principal
ventana = tk.Tk()
ventana.title("📧 Clasificador de SPAM")
ventana.geometry("850x720")
ventana.configure(bg="#f4f6f9")

# Estilos
ESTILO_BTN = {"bg": "#4CAF50", "fg": "white", "font": ("Arial", 10, "bold"), "relief": "groove", "bd": 2}
ESTILO_LBL = {"bg": "#f4f6f9", "font": ("Arial", 11)}
ESTILO_INPUT = {"bg": "#ffffff", "fg": "#000000", "font": ("Arial", 10)}

# Entrada y ejemplo
tk.Label(ventana, text="Selecciona un ejemplo o escribe tu mensaje:", **ESTILO_LBL).pack(pady=5)
ejemplo_var = tk.StringVar(value="Ejemplo de mensaje...")
tk.OptionMenu(ventana, ejemplo_var, *ejemplos_mensajes, command=cargar_ejemplo).pack()
texto_entry = tk.Text(ventana, height=4, width=90, **ESTILO_INPUT, wrap="word", bd=2, relief="groove")
texto_entry.pack(pady=5)

tk.Button(ventana, text="🔍 Analizar mensaje", command=analizar_mensaje, **ESTILO_BTN).pack(pady=10)

resultado_label = tk.Label(ventana, text="", font=("Arial", 14, "bold"), bg="#f4f6f9")
resultado_label.pack(pady=5)

# Filtros
filtros_frame = tk.Frame(ventana, bg="#f4f6f9")
filtros_frame.pack(pady=5)

tk.Label(filtros_frame, text="Tipo:", **ESTILO_LBL).grid(row=0, column=0, padx=5)
filtro_var = tk.StringVar(value="Todos")
tk.OptionMenu(filtros_frame, filtro_var, "Todos", "SPAM", "NO SPAM", command=lambda _: cargar_historial(filtro_var.get(), orden_var.get(), buscador_var.get())).grid(row=0, column=1)

tk.Label(filtros_frame, text="Orden:", **ESTILO_LBL).grid(row=0, column=2, padx=5)
orden_var = tk.StringVar(value="Reciente")
tk.OptionMenu(filtros_frame, orden_var, "Reciente", "Antiguo", command=lambda _: cargar_historial(filtro_var.get(), orden_var.get(), buscador_var.get())).grid(row=0, column=3)

# Buscador
buscador_frame = tk.Frame(ventana, bg="#f4f6f9")
buscador_frame.pack()
tk.Label(buscador_frame, text="Buscar:", **ESTILO_LBL).grid(row=0, column=0, padx=5)
buscador_var = tk.StringVar()
tk.Entry(buscador_frame, textvariable=buscador_var, width=40).grid(row=0, column=1)
buscador_var.trace_add("write", lambda *args: cargar_historial(filtro_var.get(), orden_var.get(), buscador_var.get()))

# Historial
tk.Label(ventana, text="Historial de análisis:", font=("Arial", 12, "bold"), bg="#f4f6f9").pack(pady=5)
historial_frame = tk.Frame(ventana)
historial_frame.pack()

historial_scroll = tk.Scrollbar(historial_frame)
historial_scroll.pack(side=tk.RIGHT, fill=tk.Y)

historial_text = tk.Text(historial_frame, height=14, width=100, yscrollcommand=historial_scroll.set, wrap="word", bg="#fdfdfd", state="disabled", font=("Arial", 9))
historial_text.pack(side=tk.LEFT)
historial_scroll.config(command=historial_text.yview)

# Botones inferiores
botones_frame = tk.Frame(ventana, bg="#f4f6f9")
botones_frame.pack(pady=10)

tk.Button(botones_frame, text="🗑️ Borrar historial", command=borrar_historial, bg="#e53935", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
tk.Button(botones_frame, text="📊 Ver estadísticas", command=mostrar_estadisticas, bg="#039be5", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)

# Cargar historial inicial
cargar_historial()

ventana.mainloop()
