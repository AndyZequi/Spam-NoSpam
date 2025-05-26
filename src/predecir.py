import joblib
import os

MODEL_PATH = os.path.join("models", "modelo_spam.pkl")

def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("El modelo no existe. Ejecuta entrenar.py primero.")
    return joblib.load(MODEL_PATH)

def predecir_mensaje(texto):
    modelo = cargar_modelo()
    pred = modelo.predict([texto])[0]
    prob = modelo.predict_proba([texto])[0].max()
    return pred, prob

if __name__ == "__main__":
    texto = input("Escribe un mensaje: ")
    pred, prob = predecir_mensaje(texto)
    etiqueta = "SPAM" if pred == "spam" else "NO SPAM"
    print(f"Predicción: {etiqueta} (confianza: {prob:.2f})")
