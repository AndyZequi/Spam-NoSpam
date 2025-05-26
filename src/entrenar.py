import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

DATA_PATH = os.path.join("data", "SMSSpamCollection")
MODEL_PATH = os.path.join("models", "modelo_spam.pkl")

def cargar_datos():
    df = pd.read_csv(DATA_PATH, sep='\t', names=["label", "text"])
    return df

def entrenar_modelo():
    df = cargar_datos()
    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', MultinomialNB())
    ])

    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    print("Evaluación del modelo:")
    print(classification_report(y_test, y_pred))
    print("Precisión:", accuracy_score(y_test, y_pred))

    os.makedirs("models", exist_ok=True)
    joblib.dump(modelo, MODEL_PATH)
    print(f"Modelo guardado en: {MODEL_PATH}")

if __name__ == "__main__":
    entrenar_modelo()
