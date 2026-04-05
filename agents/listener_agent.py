import os

def load_model():
    try:
        model_path = os.path.join(os.path.dirname(__file__), "models/emotion_model.pkl")
        # Code to load the model using model_path
        
    except FileNotFoundError as e:
        print(f"Error: The specified model file was not found at {model_path}. Please check the path and try again.")
