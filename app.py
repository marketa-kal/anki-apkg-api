from flask import Flask, request, jsonify, send_from_directory
import genanki
import tempfile
import uuid
import os
import random

app = Flask(__name__)
EXPORT_DIR = 'exports'
os.makedirs(EXPORT_DIR, exist_ok=True)

@app.route('/generate-apkg', methods=['POST'])
def generate_apkg():
    data = request.get_json()
    deck_name = data.get('deckName', 'My Deck')
    cards = data.get('cards', [])

    deck_id = random.randint(1_000_000, 9_999_999)
    model_id = random.randint(1_000_000, 9_999_999)

    model = genanki.Model(
        model_id,
        'Basic Model',
        fields=[{'name': 'Front'}, {'name': 'Back'}],
        templates=[{'name': 'Card 1', 'qfmt': '{{Front}}', 'afmt': '{{Back}}'}]
    )

    deck = genanki.Deck(deck_id, deck_name)
    for card in cards:
        deck.add_note(genanki.Note(model=model, fields=[card['question'], card['answer']]))

    filename = f"{uuid.uuid4().hex}.apkg"
    filepath = os.path.join(EXPORT_DIR, filename)
    genanki.Package(deck).write_to_file(filepath)

    full_url = request.host_url.rstrip("/") + f"/download/{filename}"
    return jsonify({"download_url": full_url})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(EXPORT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
