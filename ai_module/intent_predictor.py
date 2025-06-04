import joblib

clf = joblib.load("intent_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

def predict_intent(text):
    vec = vectorizer.transform([text])
    pred = clf.predict(vec)[0]
    return pred