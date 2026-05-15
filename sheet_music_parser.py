"""
Sheet Music Parser
Loads and parses MusicXML files using music21
"""

from music21 import converter, stream
from typing import List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SheetNote:
    pitch: int  # MIDI note number
    duration: float  # Duration in quarter notes
    start_time: float  # Start time in quarter notes
    name: str  # Note name (C4, D#5, etc.)

class SheetMusicParser:
    def __init__(self, file_path: str):
        """
        Initialize parser with a MusicXML file
        
        Args:
            file_path: Path to .musicxml file
        """
        self.file_path = file_path
        self.score = None
        self.notes = []
        self.tempo = 120  # Default tempo in BPM
        
    def load(self) -> bool:
        """
        Load and parse the MusicXML file
        
        Returns:
            bool: True if successful
        """
        try:
            self.score = converter.parse(self.file_path)
            
            # Extract tempo
            self._extract_tempo()
            
            # Extract notes
            self._extract_notes()
            
            print(f"Successfully loaded {len(self.notes)} notes from {self.file_path}")
            return True
            
        except Exception as e:
            print(f"Failed to load sheet music: {e}")
            return False
    
    def _extract_tempo(self):
        """Extract tempo from score"""
        try:
            # Try to find tempo marking
            for element in self.score.flatten().getElementsByClass('MetronomeMark'):
                self.tempo = int(element.number)
                return
        except:
            pass
    
    def _extract_notes(self):
        """Extract all notes from the score"""
        self.notes = []
        current_time = 0.0
        
        try:
            # Get all notes in the score (flattened)
            for element in self.score.flatten().notesAndRests:
                if element.isNote:
                    # Single note
                    midi_num = element.pitch.midi
                    duration = element.quarterLength
                    
                    self.notes.append(SheetNote(
                        pitch=midi_num,
                        duration=duration,
                        start_time=current_time,
                        name=element.pitch.nameWithOctave
                    ))
                    
                    current_time += duration
                
                elif element.isChord:
                    # Multiple notes at once - add each note
                    duration = element.quarterLength
                    
                    for pitch in element.pitches:
                        midi_num = pitch.midi
                        
                        self.notes.append(SheetNote(
                            pitch=midi_num,
                            duration=duration,
                            start_time=current_time,
                            name=pitch.nameWithOctave
                        ))
                    
                    current_time += duration
                
                elif element.isRest:
                    current_time += element.quarterLength
        
        except Exception as e:
            print(f"Error extracting notes: {e}")
    
    def get_notes(self) -> List[SheetNote]:
        """Get the list of notes in the score"""
        return self.notes
    
    def get_duration(self) -> float:
        """Get total duration in seconds"""
        if not self.notes:
            return 0.0
        
        # Calculate total quarter notes
        total_quarters = sum(note.duration for note in self.notes)
        
        # Convert to seconds (quarters * 60 / BPM)
        seconds = (total_quarters * 60) / self.tempo
        return seconds
    
    def get_note_at_time(self, time_quarter: float) -> Optional[SheetNote]:
        """
        Get the note expected at a specific time
        
        Args:
            time_quarter: Time in quarter notes
        
        Returns:
            SheetNote or None
        """
        for note in self.notes:
            if note.start_time <= time_quarter < (note.start_time + note.duration):
                return note
        return None
