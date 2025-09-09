from flask import Flask, render_template, request, jsonify, send_from_directory
import spacy
import os
import pandas as pd
from pathlib import Path
import json

app = Flask(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def get_text_files():
    """Get all text files from the input directory."""
    input_dir = "input"
    text_files = []
    
    if os.path.exists(input_dir):
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.txt'):
                    relative_path = os.path.relpath(os.path.join(root, file), ".")
                    text_files.append(relative_path)
    
    return text_files

def process_text_with_spacy(text):
    """Process text with spaCy and return entities and tokens."""
    if not text:
        return [], []
    
    doc = nlp(text)
    
    # Extract entities
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
            "start_token": ent.start,
            "end_token": ent.end
        })
    
    # Extract tokens
    tokens = []
    for i, token in enumerate(doc):
        tokens.append({
            "text": token.text,
            "idx": i,
            "start_char": token.idx,
            "end_char": token.idx + len(token.text),
            "is_space": token.is_space,
            "whitespace_": token.whitespace_
        })
    
    return entities, tokens

def tokens_and_entities_to_iob(tokens, entities):
    """Convert tokens and entities to IOB format following HIPE standard."""
    # Initialize all tokens as O (outside)
    iob_tags = []
    
    for token in tokens:
        token_data = {
            'TOKEN': token['text'],
            'NE-COARSE-LIT': 'O',
            'NE-COARSE-METO': '_',
            'NE-FINE-LIT': '_',
            'NE-FINE-METO': '_',
            'NE-FINE-COMP': '_',
            'NE-NESTED': '_',
            'NEL-LIT': '_',
            'NEL-METO': '_',
            'MISC': '_'
        }
        iob_tags.append(token_data)
    
    # Assign entity labels
    for entity in entities:
        start_token = entity['start_token']
        end_token = entity['end_token']
        
        for token_idx in range(start_token, end_token):
            if token_idx < len(iob_tags):
                if token_idx == start_token:
                    iob_tags[token_idx]['NE-COARSE-LIT'] = f"B-{entity['label']}"
                else:
                    iob_tags[token_idx]['NE-COARSE-LIT'] = f"I-{entity['label']}"
    
    # Add misc flags
    for i, token_data in enumerate(iob_tags):
        misc_flags = []
        
        # Check for no space after (simplified check)
        if i < len(tokens) - 1 and not tokens[i]['whitespace_']:
            misc_flags.append('NoSpaceAfter')
        
        # Check for end of sentence (simplified)
        if i == len(tokens) - 1:
            misc_flags.append('EndOfSentence')
        
        token_data['MISC'] = '|'.join(misc_flags) if misc_flags else '_'
    
    return iob_tags

@app.route('/')
def index():
    """Main page with file selection and NER interface."""
    text_files = get_text_files()
    return render_template('index.html', text_files=text_files)

@app.route('/api/process_file', methods=['POST'])
def process_file():
    """Process selected file and return NER results."""
    data = request.get_json()
    file_path = data.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text_content = f.read().strip()
        
        # Process with spaCy
        entities, tokens = process_text_with_spacy(text_content)
        
        # Generate IOB format
        iob_tags = tokens_and_entities_to_iob(tokens, entities)
        
        return jsonify({
            'text': text_content,
            'entities': entities,
            'tokens': tokens,
            'iob_tags': iob_tags
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_entity', methods=['POST'])
def update_entity():
    """Update an entity label."""
    data = request.get_json()
    entities = data.get('entities', [])
    tokens = data.get('tokens', [])
    entity_id = data.get('entity_id')
    new_label = data.get('new_label')
    
    if 0 <= entity_id < len(entities):
        entities[entity_id]['label'] = new_label
        
        # Regenerate IOB tags
        iob_tags = tokens_and_entities_to_iob(tokens, entities)
        
        return jsonify({
            'entities': entities,
            'iob_tags': iob_tags
        })
    
    return jsonify({'error': 'Invalid entity ID'}), 400

@app.route('/api/delete_entity', methods=['POST'])
def delete_entity():
    """Delete an entity."""
    data = request.get_json()
    entities = data.get('entities', [])
    tokens = data.get('tokens', [])
    entity_id = data.get('entity_id')
    
    if 0 <= entity_id < len(entities):
        entities.pop(entity_id)
        
        # Regenerate IOB tags
        iob_tags = tokens_and_entities_to_iob(tokens, entities)
        
        return jsonify({
            'entities': entities,
            'iob_tags': iob_tags
        })
    
    return jsonify({'error': 'Invalid entity ID'}), 400

@app.route('/api/add_entity', methods=['POST'])
def add_entity():
    """Add a new entity."""
    data = request.get_json()
    entities = data.get('entities', [])
    tokens = data.get('tokens', [])
    text_content = data.get('text')
    entity_text = data.get('entity_text')
    label = data.get('label')
    start_char = data.get('start_char')
    end_char = data.get('end_char')
    
    # Find corresponding token indices
    start_token = None
    end_token = None
    
    for i, token in enumerate(tokens):
        if token['start_char'] <= start_char < token['end_char']:
            start_token = i
        if token['start_char'] < end_char <= token['end_char']:
            end_token = i + 1
            break
    
    if start_token is not None and end_token is not None:
        new_entity = {
            'text': entity_text,
            'label': label,
            'start': start_char,
            'end': end_char,
            'start_token': start_token,
            'end_token': end_token
        }
        
        # Insert in correct position to maintain order
        inserted = False
        for i, entity in enumerate(entities):
            if entity['start'] > start_char:
                entities.insert(i, new_entity)
                inserted = True
                break
        
        if not inserted:
            entities.append(new_entity)
        
        # Regenerate IOB tags
        iob_tags = tokens_and_entities_to_iob(tokens, entities)
        
        return jsonify({
            'entities': entities,
            'iob_tags': iob_tags
        })
    
    return jsonify({'error': 'Could not determine token boundaries'}), 400

@app.route('/api/export', methods=['POST'])
def export_annotations():
    """Export annotations to TSV file."""
    data = request.get_json()
    iob_tags = data.get('iob_tags', [])
    filename = data.get('filename', 'annotations.tsv')
    
    if not iob_tags:
        return jsonify({'error': 'No annotations to export'}), 400
    
    try:
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Convert to DataFrame and save
        df = pd.DataFrame(iob_tags)
        output_path = f"output/{filename}"
        df.to_csv(output_path, sep='\t', index=False)
        
        return jsonify({
            'message': f'Annotations exported to {output_path}',
            'file_path': output_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output/<filename>')
def download_file(filename):
    """Download exported files."""
    return send_from_directory('output', filename, as_attachment=True)

if __name__ == '__main__':
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
