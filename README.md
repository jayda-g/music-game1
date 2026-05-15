# MIDI Music Game

A Python-based music learning game that uses a MIDI keyboard to play along with sheet music. The game compares your playing against the expected notes and provides feedback on accuracy.

## Features

- 🎹 Real-time MIDI keyboard input capture
- 🎵 Sheet music rendering and parsing (MusicXML format)
- 📊 Note-by-note accuracy comparison
- 🎯 Scoring and feedback system
- 🎮 Interactive gameplay with difficulty levels

## Project Structure

```
music-game1/
├── main.py                      # Main game entry point
├── midi_handler.py              # MIDI input handling
├── sheet_music_parser.py        # MusicXML parsing with music21
├── note_comparator.py           # Note comparison logic
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Installation

### Prerequisites

- Python 3.8+
- A MIDI keyboard or controller connected to your computer

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jayda-g/music-game1.git
   cd music-game1
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Connect your MIDI keyboard** to your computer

5. **Run the game:**
   ```bash
   python main.py
   ```

## How It Works

### 1. **MIDI Input** (`midi_handler.py`)
- Detects connected MIDI devices
- Listens for note-on/note-off messages
- Records note number, velocity, and timing

### 2. **Sheet Music Parsing** (`sheet_music_parser.py`)
- Loads MusicXML files using `music21`
- Extracts notes, durations, and timing information
- Converts to a playable sequence

### 3. **Note Comparison** (`note_comparator.py`)
- Compares played notes against expected notes
- Calculates accuracy (correct notes, timing, duration)
- Generates feedback and scoring

### 4. **Main Game Loop** (`main.py`)
- Orchestrates MIDI input, sheet music display, and comparison
- Handles game state and scoring
- Provides user feedback

## Usage

### Running the Game

```bash
python main.py
```

You'll be prompted to:
1. Select a MIDI input device
2. Select a sheet music file (`.musicxml`)
3. Begin playing along with the music

### Using Your Own Sheet Music

1. **Create or download** a MusicXML file (from MuseScore, Finale, Sibelius, etc.)
2. **Place it in the project directory** or a subdirectory
3. **Run the game** and select the file when prompted

### Finding MusicXML Files

- **MuseScore** (free): [musescore.com](https://musescore.com) - thousands of scores available
- **Create your own** with free tools like MuseScore, Noteflight, or Flat.io

## Configuration

Edit `config.py` to customize:

```python
# Tolerance for note accuracy (in semitones)
NOTE_TOLERANCE = 1

# Timing tolerance (in seconds)
TIMING_TOLERANCE = 0.5

# Minimum velocity to register a note
MIN_VELOCITY = 10
```

## Dependencies

See `requirements.txt` for the full list:

- **pygame** - Audio playback and UI
- **music21** - MusicXML parsing and music analysis
- **mido** - MIDI input/output
- **python-rtmidi** - Low-level MIDI support (required for mido)
- **numpy** - Numerical operations

## Troubleshooting

### MIDI Device Not Detected

```bash
# List available MIDI inputs
python -c "import mido; print(mido.get_input_names())"
```

If your device isn't listed, check that:
- It's properly connected
- Drivers are installed
- You have permissions to access USB devices

### MusicXML File Won't Load

- Ensure the file is valid MusicXML format
- Try exporting from MuseScore to verify the file
- Check file encoding (should be UTF-8)

### No Sound Output

- Ensure `pygame.mixer` is initialized
- Check system volume
- Verify audio device is set correctly

## Development Roadmap

- [ ] Visual sheet music display with playback
- [ ] Real-time note highlighting
- [ ] Score tracking and leaderboard
- [ ] Multiple difficulty levels
- [ ] Metronome support
- [ ] Export performance reports
- [ ] Web-based version with tone.js

## Contributing

Feel free to fork this repository and submit pull requests for improvements!

## License

MIT License - see LICENSE file for details

## Resources

- [music21 Documentation](https://web.mit.edu/music21/)
- [mido Documentation](https://mido.readthedocs.io/)
- [MusicXML Specification](https://www.musicxml.com/)
- [pygame Documentation](https://www.pygame.org/docs/)

---

**Happy practicing! 🎵**
