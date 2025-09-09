# Flask NER Annotation Tool

A web-based Named Entity Recognition annotation tool built with Flask that provides an intuitive interface for editing entity predictions and exporting HIPE-compliant annotations.

## ✨ Features

- **📁 File Selection**: Choose from text files in the `input/` directory
- **🎯 Interactive Visualization**: Click entities to edit labels or delete them
- **✏️ Text Selection**: Select any text to create new entity annotations
- **📊 Real-time IOB Table**: See HIPE format annotations update automatically
- **💾 Export Functionality**: Download annotations as TSV files
- **🎨 Color-coded Entities**: Visual distinction between entity types
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install flask spacy pandas
   python -m spacy download en_core_web_sm
   ```

2. **Run the Flask app**:
   ```bash
   python flask-app.py
   ```

3. **Open your browser** to: http://localhost:5000

## 🎯 How to Use

### 1. **Load a File**
- Select a text file from the dropdown
- Click "Load File" to process with spaCy

### 2. **Edit Entities**
- **Click any highlighted entity** to edit its label or delete it
- **Select any text** with your mouse to create a new entity
- Choose entity type from dropdown and confirm

### 3. **View IOB Format**
- See real-time HIPE-compliant annotations in the table
- All 10 columns are populated according to HIPE standards

### 4. **Export Results**
- Click "Export TSV" to download your annotations
- Files are saved with timestamps for easy organization

## 🏷️ Supported Entity Types

- **PERSON**: Person names
- **ORG**: Organizations, companies, agencies
- **GPE**: Geopolitical entities (countries, cities, states)  
- **LOC**: Physical locations
- **DATE**: Dates and periods
- **TIME**: Time expressions
- **MONEY**: Monetary values
- **PERCENT**: Percentages
- **CARDINAL**: Cardinal numbers
- **ORDINAL**: Ordinal numbers

## 🔧 Technical Details

### API Endpoints

- `POST /api/process_file` - Process selected file with spaCy
- `POST /api/update_entity` - Update entity label
- `POST /api/delete_entity` - Delete an entity
- `POST /api/add_entity` - Create new entity from text selection
- `POST /api/export` - Export annotations to TSV
- `GET /output/<filename>` - Download exported files

### File Structure

```
llm-lod-recipes/
├── flask-app.py           # Main Flask application
├── templates/
│   └── index.html         # Web interface
├── input/                 # Place your text files here
├── output/                # Exported annotations
└── requirements.txt       # Dependencies
```

## 🎨 User Interface

The web interface provides:

- **Clean, modern design** with Bootstrap styling
- **Entity color legend** showing all supported types
- **Split-panel layout** with visualization and editing controls
- **Real-time feedback** with status messages
- **Keyboard shortcuts** and mouse interactions
- **Mobile-responsive** design for tablet use

## 🔄 Workflow

1. **File Selection** → Load text file
2. **spaCy Processing** → Automatic NER with en_core_web_sm
3. **Interactive Editing** → Click entities or select text
4. **Real-time Updates** → Visualization and IOB table sync
5. **Export** → Download HIPE-compliant TSV

## 🆚 Advantages over Gradio Version

- **Faster interactions** - Direct DOM manipulation
- **Better UX** - Native web interface patterns
- **More reliable** - No complex state management issues
- **Easier debugging** - Standard web dev tools
- **Better mobile support** - Responsive design
- **Customizable** - Easy to modify CSS/JS

This Flask version provides a much smoother experience for NER annotation tasks!
