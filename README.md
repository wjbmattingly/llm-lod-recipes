# NER Annotation Tool

A Gradio-based web application for Named Entity Recognition annotation using spaCy with HIPE format output.

## Features

- **File Selection**: Choose from text files in the `input/` directory
- **Interactive NER Visualization**: See entity predictions with color-coded highlighting
- **Direct Entity Editing**: Click entities in the visualization to edit labels or delete them
- **Text Selection for New Entities**: Select text to create new entity annotations
- **Table-based Editing**: Modify IOB annotations in a table format
- **Real-time Synchronization**: Visualization and table stay in sync automatically
- **HIPE Format Export**: Export annotations in HIPE-compliant TSV format

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download the spaCy English model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

1. Place your text files in the `input/` directory (supports nested folders)

2. Run the application:
```bash
python app.py
```

3. Open your browser to the provided URL (usually http://localhost:7860)

4. Use the interface:
   - **Select File**: Choose a text file from the dropdown
   - **View Results**: See the original text and NER visualization
   - **Edit Annotations**: Modify the IOB tags in the table
     - Use `O` for tokens outside entities
     - Use `B-LABEL` for the beginning of an entity
     - Use `I-LABEL` for continuation of an entity
   - **Update Visualization**: Click to refresh the highlighting
   - **Export**: Save your annotations as a TSV file

## HIPE Format

The application outputs annotations in HIPE 2022 format with 10 columns:

1. **TOKEN**: The token text
2. **NE-COARSE-LIT**: Coarse entity type (IOB format) for literal sense
3. **NE-COARSE-METO**: Coarse entity type for metonymic sense
4. **NE-FINE-LIT**: Fine-grained entity type for literal sense
5. **NE-FINE-METO**: Fine-grained entity type for metonymic sense
6. **NE-FINE-COMP**: Component type of the entity
7. **NE-NESTED**: Nested entity type (if any)
8. **NEL-LIT**: Entity linking (Wikidata Q-ID) for literal sense
9. **NEL-METO**: Entity linking for metonymic sense
10. **MISC**: Miscellaneous flags (NoSpaceAfter, EndOfSentence, etc.)

## Supported Entity Types

- **PERSON**: Person names
- **ORG**: Organizations
- **GPE**: Geopolitical entities (countries, cities, states)
- **LOC**: Locations
- **DATE**: Dates or periods
- **TIME**: Times
- **MONEY**: Monetary values
- **PERCENT**: Percentages
- **CARDINAL**: Cardinal numbers
- **ORDINAL**: Ordinal numbers

## Directory Structure

```
llm-lod-recipes/
├── app.py              # Main Gradio application
├── requirements.txt    # Python dependencies
├── input/             # Place your text files here
│   ├── text1.txt
│   └── nested/
│       └── text2.txt
├── output/            # Exported annotations go here
└── notebooks/         # Jupyter notebooks for learning
    └── named_entity_recognition.ipynb
```
