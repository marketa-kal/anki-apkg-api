from flask import Flask, request, send_file
import genanki
import tempfile
import uuid
import os

app = Flask(__name__)

@app.route('/generate-apkg', methods=['POST'])
def generate_apkg():
    data = request.get_json()
    deck_name = data.get('deckName', 'My Deck')
    cards = data.get('cards', [])

    deck_id = int(uuid.uuid4()) >> 64
    model_id = int(uuid.uuid4()) >> 64

    model = genanki.Model(
        model_id,
        'Basic Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{Back}}',
            },
        ])

    deck = genanki.Deck(deck_id, deck_name)

    for card in cards:
        deck.add_note(genanki.Note(
            model=model,
            fields=[card['question'], card['answer']]
        ))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.apkg') as tmp_file:
        genanki.Package(deck).write_to_file(tmp_file.name)
        return send_file(tmp_file.name, as_attachment=True, download_name=f'{deck_name}.apkg')


if __name__ == '__main__':
    # Railway expects the app to listen on 0.0.0.0 and port from $PORT
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
