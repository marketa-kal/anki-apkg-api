from flask import Flask, request, send_file
import genanki
import tempfile
import uuid
import os
import random
import traceback

app = Flask(__name__)

@app.route('/generate-apkg', methods=['POST'])
def generate_apkg():
    try:
        data = request.get_json()
        deck_name = data.get('deckName', 'My Deck')
        cards = data.get('cards', [])

        # Bezpečné ID pro SQLite
        deck_id = random.randrange(1 << 30, 1 << 31)
        model_id = random.randrange(1 << 30, 1 << 31)

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
            ]
        )

        deck = genanki.Deck(deck_id, deck_name)

        for card in cards:
            question = card.get('question', '')
            answer = card.get('answer', '')
            if question and answer:
                deck.add_note(genanki.Note(
                    model=model,
                    fields=[question, answer]
                ))

        with tempfile.NamedTemporaryFile(delete=False, suffix='.apkg') as tmp_file:
            genanki.Package(deck).write_to_file(tmp_file.name)
            return send_file(tmp_file.name, as_attachment=True, download_name=f'{deck_name}.apkg')

    except Exception as e:
        traceback.print_exc()
        return f"Chyba při generování .apkg: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
