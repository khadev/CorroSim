"""Translation module for CorroSim"""

import json
import os

class Translator:
    """Simple JSON-based translator"""
    
    _instance = None
    _translations = {}
    _current_lang = "en"
    
    def __init__(self):
        self.load_translations()
    
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def load_translations(self):
        """Load translation files"""
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'lang')
        for lang in ['en', 'fr']:
            filepath = os.path.join(path, f'{lang}.json')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._translations[lang] = json.load(f)
    
    def set_language(self, lang):
        if lang in self._translations:
            self._current_lang = lang
    
    def t(self, key, default=""):
        """Translate a key"""
        return self._translations.get(self._current_lang, {}).get(key, default or key)
    
    @staticmethod
    def tr(key, default=""):
        return Translator.get().t(key, default)