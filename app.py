import gradio as gr
import spacy
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import json

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

def read_selected_file(file_path):
    """Read the content of the selected file."""
    if not file_path:
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

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

def create_highlighted_html(text, entities):
    """Create HTML with highlighted entities."""
    if not entities:
        return text
    
    # Sort entities by start position
    sorted_entities = sorted(entities, key=lambda x: x['start'])
    
    html = ""
    last_end = 0
    
    colors = {
        'PERSON': '#aa9cfc',
        'ORG': '#7aecec', 
        'GPE': '#feca57',
        'LOC': '#ff9ff3',
        'DATE': '#bfe1d9',
        'TIME': '#bfe1d9',
        'MONEY': '#e4e7d2',
        'PERCENT': '#e4e7d2',
        'CARDINAL': '#e4e7d2',
        'ORDINAL': '#e4e7d2'
    }
    
    for entity in sorted_entities:
        # Add text before entity
        html += text[last_end:entity['start']]
        
        # Add highlighted entity
        color = colors.get(entity['label'], '#ddd')
        html += f'<mark style="background-color: {color}; padding: 2px 4px; margin: 0 2px; border-radius: 3px;">'
        html += f'{entity["text"]} <span style="font-size: 0.8em; font-weight: bold;">({entity["label"]})</span>'
        html += '</mark>'
        
        last_end = entity['end']
    
    # Add remaining text
    html += text[last_end:]
    
    return html

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

def iob_to_dataframe(iob_tags):
    """Convert IOB tags to a pandas DataFrame for display."""
    df = pd.DataFrame(iob_tags)
    return df

def update_entities_from_dataframe(df, tokens):
    """Update entities based on modified DataFrame."""
    entities = []
    current_entity = None
    
    for idx, row in df.iterrows():
        ne_tag = row['NE-COARSE-LIT']
        
        if ne_tag.startswith('B-'):
            # Start of new entity
            if current_entity:
                entities.append(current_entity)
            
            label = ne_tag[2:]  # Remove 'B-' prefix
            current_entity = {
                'text': tokens[idx]['text'],
                'label': label,
                'start_token': idx,
                'end_token': idx + 1,
                'start': tokens[idx]['start_char'],
                'end': tokens[idx]['end_char']
            }
        
        elif ne_tag.startswith('I-') and current_entity:
            # Continue current entity
            label = ne_tag[2:]  # Remove 'I-' prefix
            if label == current_entity['label']:
                current_entity['text'] += tokens[idx]['text']
                current_entity['end_token'] = idx + 1
                current_entity['end'] = tokens[idx]['end_char']
        
        elif ne_tag == 'O':
            # Outside entity - finish current entity if exists
            if current_entity:
                entities.append(current_entity)
                current_entity = None
    
    # Don't forget the last entity
    if current_entity:
        entities.append(current_entity)
    
    return entities

def process_file_selection(file_path):
    """Process selected file and return initial results."""
    if not file_path:
        return "", "", pd.DataFrame()
    
    # Read file content
    text_content = read_selected_file(file_path)
    
    # Process with spaCy
    entities, tokens = process_text_with_spacy(text_content)
    
    # Create highlighted HTML
    highlighted_html = create_highlighted_html(text_content, entities)
    
    # Generate IOB format
    iob_tags = tokens_and_entities_to_iob(tokens, entities)
    iob_df = iob_to_dataframe(iob_tags)
    
    return text_content, highlighted_html, iob_df

def update_visualization_from_edits(original_text, edited_df):
    """Update visualization when IOB tags are edited."""
    if edited_df.empty or not original_text:
        return ""
    
    # Process original text to get tokens
    _, tokens = process_text_with_spacy(original_text)
    
    # Convert DataFrame back to entities
    df_dict = edited_df.to_dict('records')
    entities = update_entities_from_dataframe(edited_df, tokens)
    
    # Create new highlighted HTML
    highlighted_html = create_highlighted_html(original_text, entities)
    
    return highlighted_html

def export_annotations(df, filename="annotations.tsv"):
    """Export annotations to TSV file."""
    if df.empty:
        return "No annotations to export"
    
    output_path = f"output/{filename}"
    os.makedirs("output", exist_ok=True)
    
    df.to_csv(output_path, sep='\t', index=False)
    return f"Annotations exported to {output_path}"

# Create Gradio interface
def create_interface():
    text_files = get_text_files()
    
    with gr.Blocks(title="NER Annotation Tool", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Named Entity Recognition Annotation Tool")
        gr.Markdown("Select a text file, view spaCy predictions, edit annotations, and export results.")
        
        with gr.Row():
            with gr.Column(scale=1):
                file_selector = gr.Dropdown(
                    choices=text_files,
                    label="Select Text File",
                    value=text_files[0] if text_files else None
                )
                
                refresh_btn = gr.Button("Refresh File List", variant="secondary")
            
            with gr.Column(scale=2):
                original_text = gr.Textbox(
                    label="Original Text",
                    lines=4,
                    interactive=False
                )
        
        with gr.Row():
            highlighted_display = gr.HTML(
                label="NER Visualization",
                value="Select a file to see NER results"
            )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Edit IOB Annotations")
                gr.Markdown("You can edit the NE-COARSE-LIT column to modify entity predictions. Use format: O, B-LABEL, I-LABEL")
                
                iob_editor = gr.Dataframe(
                    label="IOB Format (Editable)",
                    interactive=True,
                    wrap=True
                )
        
        with gr.Row():
            update_viz_btn = gr.Button("Update Visualization", variant="primary")
            export_btn = gr.Button("Export Annotations", variant="secondary")
        
        export_status = gr.Textbox(label="Export Status", interactive=False)
        
        # Store original text and tokens for updates
        original_text_state = gr.State()
        
        # Event handlers
        def refresh_files():
            return gr.Dropdown(choices=get_text_files())
        
        def on_file_select(file_path):
            text_content, highlighted_html, iob_df = process_file_selection(file_path)
            return text_content, highlighted_html, iob_df, text_content
        
        def on_update_viz(original_text, edited_df):
            highlighted_html = update_visualization_from_edits(original_text, edited_df)
            return highlighted_html
        
        def on_export(edited_df):
            status = export_annotations(edited_df, "edited_annotations.tsv")
            return status
        
        # Connect events
        refresh_btn.click(
            refresh_files,
            outputs=[file_selector]
        )
        
        file_selector.change(
            on_file_select,
            inputs=[file_selector],
            outputs=[original_text, highlighted_display, iob_editor, original_text_state]
        )
        
        update_viz_btn.click(
            on_update_viz,
            inputs=[original_text_state, iob_editor],
            outputs=[highlighted_display]
        )
        
        export_btn.click(
            on_export,
            inputs=[iob_editor],
            outputs=[export_status]
        )
        
        # Initialize with first file if available
        if text_files:
            demo.load(
                on_file_select,
                inputs=[gr.State(text_files[0])],
                outputs=[original_text, highlighted_display, iob_editor, original_text_state]
            )
    
    return demo

if __name__ == "__main__":
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Launch the app
    demo = create_interface()
    demo.launch(share=True, debug=True)
