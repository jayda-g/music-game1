"""
MIDI Music Game - Main Entry Point
Orchestrates the game loop with MIDI input and sheet music parsing
"""

import sys
from pathlib import Path
from midi_handler import MIDIHandler
from sheet_music_parser import SheetMusicParser
from note_comparator import NoteComparator
import time

def list_sheet_files():
    """List all MusicXML files in current directory"""
    musicxml_files = list(Path('.').glob('*.musicxml'))
    xml_files = list(Path('.').glob('*.xml'))
    return musicxml_files + xml_files

def select_midi_device():
    """Let user select a MIDI device"""
    handler = MIDIHandler()
    devices = handler.list_devices()
    
    if not devices:
        print("❌ No MIDI devices found. Please connect a MIDI keyboard.")
        return None
    
    print("\n🎹 Available MIDI Devices:")
    for i, device in enumerate(devices):
        print(f"  {i}: {device}")
    
    while True:
        try:
            choice = int(input("\nSelect device (enter number): "))
            if 0 <= choice < len(devices):
                return devices[choice]
        except ValueError:
            pass
        print("Invalid selection. Try again.")

def select_sheet_music():
    """Let user select a sheet music file"""
    files = list_sheet_files()
    
    if not files:
        print("❌ No MusicXML files found in current directory.")
        print("📝 Please add a .musicxml or .xml file or create one with MuseScore.")
        return None
    
    print("\n🎵 Available Sheet Music Files:")
    for i, file in enumerate(files):
        print(f"  {i}: {file.name}")
    
    while True:
        try:
            choice = int(input("\nSelect file (enter number): "))
            if 0 <= choice < len(files):
                return str(files[choice])
        except ValueError:
            pass
        print("Invalid selection. Try again.")

def play_game(midi_device: str, sheet_file: str):
    """Main game loop"""
    
    # Initialize MIDI handler
    print("\n🎹 Initializing MIDI...")
    midi_handler = MIDIHandler(midi_device)
    if not midi_handler.connect():
        return
    
    # Initialize sheet music parser
    print("🎵 Loading sheet music...")
    parser = SheetMusicParser(sheet_file)
    if not parser.load():
        return
    
    # Initialize comparator
    comparator = NoteComparator()
    
    # Get sheet notes
    sheet_notes = parser.get_notes()
    total_duration = parser.get_duration()
    
    print(f"\n✅ Setup complete!")
    print(f"   Tempo: {parser.tempo} BPM")
    print(f"   Notes in piece: {len(sheet_notes)}")
    print(f"   Total duration: {total_duration:.1f} seconds")
    
    print("\n🎮 Ready to play! Press ENTER to start listening...")
    input()
    
    # Listen for MIDI input
    print("🎧 Listening for notes (playing along now)...\n")
    
    def on_note(note, type_):
        if type_ == 'note_on':
            note_name = MIDIHandler().get_note_name(note.note)
            print(f"  🎹 {note_name} (velocity: {note.velocity})")
    
    played_notes = midi_handler.listen(duration=total_duration + 5, callback=on_note)
    
    # Compare results
    print("\n" + "="*50)
    print("📊 RESULTS")
    print("="*50)
    
    results = comparator.compare_sequences(sheet_notes[:len(played_notes)], played_notes)
    
    print(f"Total notes: {results['total_notes']}")
    print(f"Correct: {results['correct_notes']}")
    print(f"Accuracy: {results['accuracy_percentage']:.1f}%")
    print(f"Average score: {results['average_accuracy_score']:.1f}/100")
    
    if results['missed_notes'] > 0:
        print(f"⚠️  Missed {results['missed_notes']} notes")
    
    print("\n📝 Detailed Results:")
    for i, result in enumerate(results['results'][:10]):  # Show first 10
        feedback = comparator.get_feedback(result)
        print(f"  {i+1}. {feedback}")
    
    if len(results['results']) > 10:
        print(f"  ... and {len(results['results']) - 10} more notes")
    
    # Disconnect
    midi_handler.disconnect()
    print("\n✅ Game complete!")

def main():
    """Main function"""
    print("╔════════════════════════════════════════╗")
    print("║     🎵 MIDI MUSIC GAME 🎵             ║")
    print("║   Learn music with your MIDI keyboard ║")
    print("╚════════════════════════════════════════╝\n")
    
    # Select MIDI device
    midi_device = select_midi_device()
    if not midi_device:
        return
    
    # Select sheet music
    sheet_file = select_sheet_music()
    if not sheet_file:
        return
    
    # Play game
    play_game(midi_device, sheet_file)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
