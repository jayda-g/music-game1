"""
MIDI Music Game - Note Guessing Game
Asks the player to play specific notes and provides feedback on timing and velocity
"""

import sys
import random
from midi_handler import MIDIHandler
import time
from chords import chord_feedback, is_major_chord, major_chord_note_names, pitch_class_to_note_name

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

def generate_target_notes(count=3):
    """
    Generate random target notes for the player to play
    
    Args:
        count: Number of notes to generate (default 5)
    
    Returns:
        List of MIDI note numbers
    """
    # Generate random notes in a reasonable range (C4 to C6, MIDI 60-84)
    target_notes = [random.randint(60, 84) for _ in range(count)]
    return target_notes

def midi_number_to_note_name(midi_num):
    """
    Convert MIDI note number to note name
    
    Args:
        midi_num: MIDI note number (0-127)
    
    Returns:
        Note name string (e.g., "C4", "D#5")
    """
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_num // 12) - 1
    note = note_names[midi_num % 12]
    return f"{note}{octave}"


def listen_for_chord(midi_handler, timeout=5):
    """
    Listen for multiple simultaneous notes and return the distinct note numbers.
    """
    chord_notes = set()
    note_velocities = {}

    def note_callback(midi_note, msg_type):
        if msg_type == 'note_on' and midi_note.velocity > 0:
            chord_notes.add(midi_note.note)
            note_velocities[midi_note.note] = max(
                note_velocities.get(midi_note.note, 0),
                midi_note.velocity
            )

    midi_handler.recorded_notes = []
    midi_handler.listen(duration=timeout, callback=note_callback)

    if not chord_notes:
        return None

    return {
        'notes': sorted(chord_notes),
        'velocities': note_velocities
    }

def play_chord_round(midi_device: str, root_note: str = 'C', timeout: int = 8):
    """
    Play one major chord round.
    """
    print(f"\n🎹 Initializing MIDI for chord round...")
    midi_handler = MIDIHandler(midi_device)
    if not midi_handler.connect():
        return False

    root_note = root_note.upper()
    target_notes = major_chord_note_names(root_note)
    chord_name = f"{root_note} major"

    print(f"\n✅ Ready to play a major chord.")
    print(f"📋 Target chord: {chord_name} ({', '.join(target_notes)})\n")
    print("   (Press ENTER when ready, then play the chord)")
    input()

    print(f"   🎧 Listening for {timeout} seconds...")
    chord_result = listen_for_chord(midi_handler, timeout=timeout)

    if chord_result:
        played_notes = chord_result['notes']
        played_names = [midi_number_to_note_name(n) for n in played_notes]
        feedback = chord_feedback(played_notes, root_note)

        is_correct = not feedback['missing'] and not feedback['extra']

        if is_correct:
            print(f"      ✅ Correct chord! You played {chord_name}.")
        else:
            print(f"      ❌ Incorrect chord.")
            if feedback['missing']:
                missing_names = [pitch_class_to_note_name(pc) for pc in sorted(feedback['missing'])]
                print(f"      Missing notes: {', '.join(missing_names)}")
            if feedback['extra']:
                extra_names = [pitch_class_to_note_name(pc) for pc in sorted(feedback['extra'])]
                print(f"      Extra notes: {', '.join(extra_names)}")

        print(f"      Played notes: {', '.join(played_names)}")
    else:
        print(f"      ❌ No notes detected - timeout!")

    midi_handler.disconnect()
    return True

def main():
    """Main function"""
    print("╔════════════════════════════════════════╗")
    print("║     🎵 MIDI NOTE GUESSING GAME 🎵     ║")
    print("║    Play the notes we ask for!          ║")
    print("╚════════════════════════════════════════╝\n")

    midi_device = select_midi_device()
    if not midi_device:
        return

    round_num = 1
    while True:
        print("\nChoose mode:")
        print("  1) Single-note game")
        print("  2) Major chord game (C major by default)")
        mode = input("Select 1 or 2: ").strip()

        if mode == '2':
            play_chord_round(midi_device, root_note='C', timeout=8)
        else:
            play_round(midi_device, round_num)

        print("\n" + "="*50)
        play_again = input("Play another round? (yes/no): ").strip().lower()
        if play_again not in ['yes', 'y']:
            print("\n👋 Thanks for playing!")
            break

        round_num += 1

        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)