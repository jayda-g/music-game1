"""
MIDI Input Handler
Captures and processes MIDI keyboard input
"""

import mido
from typing import Optional, List, Dict
from dataclasses import dataclass
import time

@dataclass
class MIDINote:
    note: int  # MIDI note number (0-127)
    velocity: int  # Velocity (0-127)
    timestamp: float  # When the note was pressed
    duration: float = 0.0  # How long it was held

class MIDIHandler:
    def __init__(self, device_name: Optional[str] = None):
        """
        Initialize MIDI handler
        
        Args:
            device_name: Name of MIDI device. If None, uses first available.
        """
        self.device_name = device_name
        self.input_device = None
        self.active_notes = {}  # Track notes currently being held
        self.recorded_notes = []
        
    def list_devices(self) -> List[str]:
        """List all available MIDI input devices"""
        return mido.get_input_names()
    
    def connect(self) -> bool:
        """
        Connect to MIDI device
        
        Returns:
            bool: True if connection successful
        """
        try:
            devices = self.list_devices()
            
            if not devices:
                print("No MIDI devices found!")
                return False
            
            if self.device_name is None:
                # Use first device
                device = devices[0]
            else:
                device = self.device_name
            
            print(f"Connecting to MIDI device: {device}")
            self.input_device = mido.open_input(device)
            return True
            
        except Exception as e:
            print(f"Failed to connect to MIDI device: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MIDI device"""
        if self.input_device:
            self.input_device.close()
            self.input_device = None
    
    def listen(self, duration: float = None, callback=None) -> List[MIDINote]:
        """
        Listen for MIDI input
        
        Args:
            duration: Listen for this many seconds (None = infinite)
            callback: Optional function called for each note
        
        Returns:
            List of MIDINote objects
        """
        if not self.input_device:
            print("Not connected to MIDI device!")
            return []
        
        self.recorded_notes = []
        start_time = time.time()
        
        try:
            while True:
                if duration and (time.time() - start_time) > duration:
                    break
                
                for message in self.input_device.iter_pending():
                    timestamp = time.time() - start_time
                    
                    if message.type == 'note_on' and message.velocity > 0:
                        # Note pressed
                        self.active_notes[message.note] = {
                            'velocity': message.velocity,
                            'timestamp': timestamp
                        }
                        
                        midi_note = MIDINote(
                            note=message.note,
                            velocity=message.velocity,
                            timestamp=timestamp
                        )
                        self.recorded_notes.append(midi_note)
                        
                        if callback:
                            callback(midi_note, 'note_on')
                    
                    elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                        # Note released
                        if message.note in self.active_notes:
                            start = self.active_notes[message.note]['timestamp']
                            duration_held = timestamp - start
                            
                            # Update duration of last note
                            for note in reversed(self.recorded_notes):
                                if note.note == message.note and note.timestamp == start:
                                    note.duration = duration_held
                                    break
                            
                            del self.active_notes[message.note]
                            
                            if callback:
                                callback(MIDINote(message.note, 0, timestamp, duration_held), 'note_off')
        
        except KeyboardInterrupt:
            print("\nListening stopped.")
        
        return self.recorded_notes
    
    def get_note_name(self, midi_num: int) -> str:
        """Convert MIDI number to note name (C4, D#5, etc.)"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_num // 12) - 1
        note = notes[midi_num % 12]
        return f"{note}{octave}"
