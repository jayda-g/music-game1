"""
Note Comparison Engine
Compares played notes against expected notes and calculates accuracy
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass
from midi_handler import MIDINote
from sheet_music_parser import SheetNote
import config

@dataclass
class ComparisonResult:
    expected_note: int
    played_note: int
    semitone_difference: int
    timing_difference: float
    is_correct: bool
    accuracy_score: float  # 0-100

class NoteComparator:
    def __init__(self, tolerance_semitones: int = config.NOTE_TOLERANCE,
                 tolerance_timing: float = config.TIMING_TOLERANCE):
        """
        Initialize comparator
        
        Args:
            tolerance_semitones: How many semitones off is acceptable
            tolerance_timing: How many seconds off is acceptable
        """
        self.tolerance_semitones = tolerance_semitones
        self.tolerance_timing = tolerance_timing
        self.results = []
    
    def compare_notes(self, expected: SheetNote, played: MIDINote) -> ComparisonResult:
        """
        Compare a played note against an expected note
        
        Args:
            expected: The note from the sheet music
            played: The note that was played
        
        Returns:
            ComparisonResult with accuracy information
        """
        pitch_diff = played.note - expected.pitch
        timing_diff = 0.0  # Will be calculated if timing info is available
        
        # Check if note is correct (within tolerance)
        is_correct = abs(pitch_diff) <= self.tolerance_semitones
        
        # Calculate accuracy score (0-100)
        pitch_accuracy = max(0, 100 - (abs(pitch_diff) * 20))  # 5 semitones = 0%
        accuracy_score = pitch_accuracy
        
        result = ComparisonResult(
            expected_note=expected.pitch,
            played_note=played.note,
            semitone_difference=pitch_diff,
            timing_difference=timing_diff,
            is_correct=is_correct,
            accuracy_score=accuracy_score
        )
        
        self.results.append(result)
        return result
    
    def compare_sequences(self, expected_notes: List[SheetNote], 
                         played_notes: List[MIDINote]) -> Dict:
        """
        Compare entire sequences of notes
        
        Args:
            expected_notes: Notes from sheet music
            played_notes: Notes that were played
        
        Returns:
            Dictionary with accuracy statistics
        """
        self.results = []
        correct_count = 0
        total_accuracy = 0
        
        # Match played notes to expected notes
        for i, expected in enumerate(expected_notes):
            if i < len(played_notes):
                played = played_notes[i]
                result = self.compare_notes(expected, played)
                
                if result.is_correct:
                    correct_count += 1
                
                total_accuracy += result.accuracy_score
        
        accuracy_percentage = (correct_count / len(expected_notes)) * 100 if expected_notes else 0
        average_accuracy = total_accuracy / len(expected_notes) if expected_notes else 0
        
        return {
            'total_notes': len(expected_notes),
            'correct_notes': correct_count,
            'accuracy_percentage': accuracy_percentage,
            'average_accuracy_score': average_accuracy,
            'missed_notes': len(expected_notes) - len(played_notes),
            'extra_notes': len(played_notes) - len(expected_notes) if len(played_notes) > len(expected_notes) else 0,
            'results': self.results
        }
    
    def get_feedback(self, result: ComparisonResult) -> str:
        """
        Generate user-friendly feedback for a note comparison
        
        Args:
            result: The comparison result
        
        Returns:
            Feedback string
        """
        if result.is_correct:
            return f"✓ Correct! {self._midi_to_note(result.played_note)}"
        
        if result.semitone_difference > 0:
            direction = "too high"
        else:
            direction = "too low"
        
        return f"✗ {direction} by {abs(result.semitone_difference)} semitone(s). Expected {self._midi_to_note(result.expected_note)}, got {self._midi_to_note(result.played_note)}"
    
    @staticmethod
    def _midi_to_note(midi_num: int) -> str:
        """Convert MIDI number to note name"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_num // 12) - 1
        note = notes[midi_num % 12]
        return f"{note}{octave}"
