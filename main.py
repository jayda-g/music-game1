"""
MIDI Music Game - Note Guessing Game
Asks the player to play specific notes and provides feedback on timing and velocity
"""

import sys
import random
from midi_handler import MIDIHandler
from note_comparator import NoteComparator
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
    played_notes = []
    results = []
    
    for i, target_midi in enumerate(target_notes):
        target_name = target_note_names[i]
        print(f"\n🎵 Note {i+1}/{notes_per_round}: Play {target_name}")
        print("   (Press ENTER when ready, then play the note and release it)")
        input()
        
        # Listen for a single note
        print("   🎧 Listening...")
        start_time = time.time()
        
        # Listen for MIDI note on/off
        note_played = None
        note_on_time = None
        note_off_time = None
        velocity = 0
        
        # We'll listen for up to 5 seconds for a note
        while time.time() - start_time < 5:
            try:
                # Get MIDI messages
                msg = midi_handler.input.get_message()
                if msg:
                    message, data = msg
                    
                    # Check for note on message
                    if message.type == 'note_on' and message.velocity > 0:
                        note_played = message.note
                        velocity = message.velocity
                        note_on_time = time.time()
                        print(f"      🎹 Note detected: {midi_number_to_note_name(note_played)} (velocity: {velocity})")
                    
                    # Check for note off message
                    elif (message.type == 'note_off' or 
                          (message.type == 'note_on' and message.velocity == 0)):
                        if note_played is not None:
                            note_off_time = time.time()
                            
                            # Calculate hold duration
                            hold_duration = note_off_time - note_on_time
                            
                            # Determine if note is correct
                            is_correct = (note_played == target_midi)
                            
                            # Store result
                            result = {
                                'target': target_midi,
                                'played': note_played,
                                'correct': is_correct,
                                'hold_duration': hold_duration,
                                'velocity': velocity
                            }
                            results.append(result)
                            played_notes.append(note_played)
                            
                            # Print feedback
                            if is_correct:
                                print(f"      ✅ Correct! Held for {hold_duration:.2f}s at velocity {velocity}")
                            else:
                                print(f"      ❌ Wrong note! Played {midi_number_to_note_name(note_played)} instead. Held for {hold_duration:.2f}s at velocity {velocity}")
                            
                            break
            except:
                pass
            
            time.sleep(0.01)
        
        # Timeout handling
        if note_played is None:
            print(f"      ❌ No note detected - timeout!")
            result = {
                'target': target_midi,
                'played': None,
                'correct': False,
                'hold_duration': 0,
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
        played_name = midi_number_to_note_name(result['played']) if result['played'] else "No note"
        target_name = midi_number_to_note_name(result['target'])
        print(f"  {i+1}. {status} Target: {target_name} | Played: {played_name} | Duration: {result['hold_duration']:.2f}s | Velocity: {result['velocity']}")
    
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
