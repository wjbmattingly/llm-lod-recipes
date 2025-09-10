import re
import spacy
from spacy.tokens import Doc, Span


def annotated_text_to_spacy_doc(text, nlp=None):
    """
    Converts annotated text in format [Entity](LABEL) to a spaCy Doc with entity spans.
    
    Args:
        text (str): Text with annotations like "[Tom](PERSON) worked for [Microsoft](ORGANIZATION)"
        nlp (spacy.Language, optional): spaCy language model. If None, uses blank English model.
    
    Returns:
        spacy.tokens.Doc: spaCy document with entity spans set
        
    Example:
        >>> text = "[Tom](PERSON) worked for [Microsoft](ORGANIZATION) in 2020 before he lived in [Rome](LOCATION)."
        >>> doc = annotated_text_to_spacy_doc(text)
        >>> spacy.displacy.render(doc, style="ent")
    """
    if nlp is None:
        nlp = spacy.blank("en")
    
    # Pattern to match [text](LABEL) format
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    # Parse the text to extract tokens and entity information
    tokens = []
    entity_spans = []  # List of (start_token_idx, end_token_idx, label)
    custom_labels = set()
    
    # Split text by the pattern and process each part
    last_end = 0
    token_idx = 0
    
    for match in re.finditer(pattern, text):
        # Add tokens before the entity
        before_entity = text[last_end:match.start()]
        if before_entity.strip():
            # Tokenize the text before the entity
            before_tokens = before_entity.split()
            tokens.extend(before_tokens)
            token_idx += len(before_tokens)
        
        # Add the entity tokens
        entity_text = match.group(1)
        entity_label = match.group(2)
        custom_labels.add(entity_label)
        
        # Tokenize the entity text
        entity_tokens = entity_text.split()
        start_token_idx = token_idx
        tokens.extend(entity_tokens)
        token_idx += len(entity_tokens)
        end_token_idx = token_idx
        
        # Store entity span information
        entity_spans.append((start_token_idx, end_token_idx, entity_label))
        
        last_end = match.end()
    
    # Add any remaining tokens after the last entity
    remaining = text[last_end:]
    if remaining.strip():
        remaining_tokens = remaining.split()
        tokens.extend(remaining_tokens)
    
    # Add custom labels to the NLP model if they don't exist
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    for label in custom_labels:
        ner.add_label(label)
    
    # Create spaces array (True for tokens that should have a space after them)
    # Simple heuristic: all tokens except the last one get a space
    spaces = [True] * len(tokens)
    if tokens:
        spaces[-1] = False
    
    # Create the Doc from tokens
    doc = Doc(nlp.vocab, words=tokens, spaces=spaces)
    
    # Create entity spans
    entities = []
    for start_idx, end_idx, label in entity_spans:
        if start_idx < len(doc) and end_idx <= len(doc):
            span = Span(doc, start_idx, end_idx, label=label)
            entities.append(span)
    
    # Set entities on the document
    doc.ents = entities
    
    return doc


def visualize_annotated_text(text, nlp=None, style="ent", jupyter=True):
    """
    Convenience function to convert annotated text and visualize it with displaCy.
    
    Args:
        text (str): Text with annotations like "[Tom](PERSON) worked for [Microsoft](ORGANIZATION)"
        nlp (spacy.Language, optional): spaCy language model. If None, uses blank English model.
        style (str): displaCy style ("ent" or "dep")
        jupyter (bool): Whether to render for Jupyter notebook
    
    Returns:
        Rendered visualization (HTML string if not in Jupyter)
    """
    doc = annotated_text_to_spacy_doc(text, nlp)
    
    try:
        import spacy
        return spacy.displacy.render(doc, style=style, jupyter=jupyter)
    except ImportError:
        print("spaCy not installed. Please install with: pip install spacy")
        return None
