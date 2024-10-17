import json
from ui import SpectralConverterApp

def load_translations():
    try:
        with open("translations.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading translations: {str(e)}")
        return {}

if __name__ == "__main__":
    translations = load_translations()
    app = SpectralConverterApp(translations)
    app.mainloop()