from flask import Flask, request, jsonify, send_file
import genanki
import os
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return 'Anki .apkg generator is running!'

@app.route('/create-apkg', methods=['POST'])
def create_apkg():
    data = request.get_json()
    deck_name = data.get('deckName', 'MyDeck')
    cards = data.get('cards', [])

    if not cards:
        return jsonify({'error': 'No cards provided'}), 400

    deck_id = int(str(uuid.uuid4().int)[:10])
    my_deck = genanki.Deck(deck_id, deck_name)

    my_model = genanki.Model(
        1607392319,
        'Simple Model',
        fields=[{'name': 'Question'}, {'name': 'Answer'}],
        templates=[{
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        }],
    )

    for card in cards:
        question = card.get('question', '')
        answer = card.get('answer', '')
        if question and answer:
            note = genanki.Note(
                model=my_model,
                fields=[question, answer]
            )
            my_deck.add_note(note)

    filename = f"{deck_name.replace(' ', '_')}.apkg"
    filepath = os.path.join("/tmp", filename)

    genanki.Package(my_deck).write_to_file(filepath)

    return send_file(filepath, as_attachment=True)

# ✅ Nutné pro spuštění na Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
