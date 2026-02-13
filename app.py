from flask import Flask, render_template, request, jsonify
import unicodedata, re
from pathlib import Path

app = Flask(__name__)

class WordDictionary:
    def __init__(self, file_path):
        self.words_by_length = {}
        path = Path(file_path)
        if path.exists():
            # Intentamos varias codificaciones por si el txt es antiguo
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with path.open("r", encoding=enc) as f:
                        for line in f:
                            word = line.strip().split(',')[0].strip().split(' ')[0]
                            if word:
                                length = len(word)
                                if length not in self.words_by_length:
                                    self.words_by_length[length] = set()
                                self.words_by_length[length].add(word)
                    break
                except UnicodeDecodeError:
                    continue
            self.words_by_length = {k: list(v) for k, v in self.words_by_length.items()}

    def normalize(self, text):
        if not text: return ""
        return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

    def search(self, pattern, include="", exclude=""):
        length = len(pattern)
        if length not in self.words_by_length: return []
        
        clean_pattern = self.normalize(pattern).replace('_', '.')
        regex = re.compile(f"^{clean_pattern}$")
        clean_inc, clean_exc = self.normalize(include), self.normalize(exclude)

        results = []
        for word in self.words_by_length[length]:
            norm_word = self.normalize(word)
            if regex.match(norm_word):
                if all(c in norm_word for c in clean_inc) and not any(c in norm_word for c in clean_exc):
                    results.append(word)
        return sorted(results)

dict_engine = WordDictionary("palabras.txt")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buscar')
def buscar():
    patron = request.args.get('p', '')
    inc = request.args.get('i', '')
    exc = request.args.get('e', '')
    return jsonify(dict_engine.search(patron, inc, exc))

if __name__ == '__main__':
    app.run(debug=True)