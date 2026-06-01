"""
MIDI Music Game - Note Guessing Game
Asks the player to play specific notes and provides feedback on timing and velocity
"""

import sys
import random
from midi_handler import MIDIHandler
import time

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

def generate_target_notes(count=5):
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

def listen_for_single_note(midi_handler, timeout=5):
    """
    Listen for a single note press and release
    
    Args:
        midi_handler: MIDIHandler instance
        timeout: Maximum seconds to listen
    
    Returns:
        Dictionary with note info or None if timeout
    """
    # Variables to track note state
    note_data = {'note': None, 'velocity': 0, 'on_time': None, 'off_time': None}
    
    # Callback to handle MIDI messages
    def note_callback(midi_note, msg_type):
        if msg_type == 'note_on':
            # Note was pressed
            note_data['note'] = midi_note.note
            note_data['velocity'] = midi_note.velocity
            note_data['on_time'] = midi_note.timestamp
        elif msg_type == 'note_off':
            # Note was released
            note_data['off_time'] = midi_note.timestamp
    
    # Listen for the timeout duration
    midi_handler.recorded_notes = []  # Clear previous notes
    midi_handler.listen(duration=timeout, callback=note_callback)
    
    # Check if we got a note
    if note_data['note'] is not None and note_data['off_time'] is not None:
        return {
            'note': note_data['note'],
            'velocity': note_data['velocity'],
            'duration': note_data['off_time'] - note_data['on_time']
        }
    
    return None

def play_round(midi_device: str, round_num: int, notes_per_round: int = 5):
    """
    Play a single round of the note guessing game
    
    Args:
        midi_device: Selected MIDI device name
        round_num: Current round number
        notes_per_round: Number of notes to play in this round
    """
    
    # Initialize MIDI handler
    print(f"\n🎹 Initializing MIDI for Round {round_num}...")
    midi_handler = MIDIHandler(midi_device)
    if not midi_handler.connect():
        return False
    
    # Generate target notes
    print(f"\n📝 Generating {notes_per_round} random notes...")
    target_notes = generate_target_notes(notes_per_round)
    target_note_names = [midi_number_to_note_name(note) for note in target_notes]
    
    print(f"\n✅ Ready to play! You will play {notes_per_round} notes.")
    print(f"📋 Target notes: {', '.join(target_note_names)}\n")
    
    # Play each note
    results = []
    
    for i, target_midi in enumerate(target_notes):
        target_name = target_note_names[i]
        print(f"\n🎵 Note {i+1}/{notes_per_round}: Play {target_name}")
        print("   (Press ENTER when ready, then play the note)")
        input()
        
        # Listen for a single note with timeout
        print("   🎧 Listening for 5 seconds...")
        note_result = listen_for_single_note(midi_handler, timeout=5)
        
        if note_result:
            # We got a note!
            played_midi = note_result['note']
            velocity = note_result['velocity']
            hold_duration = note_result['duration']
            is_correct = (played_midi == target_midi)
            
            played_name = midi_number_to_note_name(played_midi)
            
            # Determine feedback
            if is_correct:
                print(f"      ✅ Correct! Played {played_name}")
            else:
                print(f"      ❌ Wrong! Played {played_name} instead of {target_name}")
            
            print(f"      ⏱️  Held for {hold_duration:.2f}s")
            print(f"      💪 Velocity: {velocity}/127")
            
            # Store result
            result = {
                'target': target_midi,
                'played': played_midi,
                'correct': is_correct,
                'duration': hold_duration,
                'velocity': velocity
            }
            results.append(result)
        else:
            # Timeout - no note detected
            print(f"      ❌ No note detected - timeout!")
            result = {
                'target': target_midi,
                'played': None,
                'correct': False,
                'duration': 0,
                'velocity': 0
            }
            results.append(result)
    
    # Disconnect MIDI
    midi_handler.disconnect()
    
    # Print summary
    print("\n" + "="*50)
    print(f"📊 ROUND {round_num} RESULTS")
    print("="*50)
    
    correct_count = sum(1 for r in results if r['correct'])
    print(f"Correct: {correct_count}/{notes_per_round}")
    print(f"Accuracy: {(correct_count / notes_per_round * 100):.1f}%")
    
    print("\n📝 Detailed Breakdown:")
    for i, result in enumerate(results):
        status = "✅" if result['correct'] else "❌"
        target_name = midi_number_to_note_name(result['target'])
        
        if result['played'] is not None:
            played_name = midi_number_to_note_name(result['played'])
            print(f"  {i+1}. {status} Target: {target_name} | Played: {played_name} | Duration: {result['duration']:.2f}s | Velocity: {result['velocity']}")
        else:
            print(f"  {i+1}. {status} Target: {target_name} | Played: No note detected")
    
    return True

def main():
    """Main function"""
    print("╔════════════════════════════════════════╗")
    print("║     🎵 MIDI NOTE GUESSING GAME 🎵     ║")
    print("║    Play the notes we ask for!          ║")
    print("╚════════════════════════════════════════╝\n")
    
    # Select MIDI device
    midi_device = select_midi_device()
    if not midi_device:
        return
    
    # Play rounds
    round_num = 1
    while True:
        play_round(midi_device, round_num)
        
        # Ask if player wants to play again
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
