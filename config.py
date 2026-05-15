"""
Configuration settings for the MIDI Music Game
"""

# MIDI Settings
NOTE_TOLERANCE = 1  # Tolerance in semitones (how close the note needs to be)
TIMING_TOLERANCE = 0.5  # Tolerance in seconds
MIN_VELOCITY = 10  # Minimum velocity to register a note press

# Game Settings
ROUND_DURATION = 30  # Seconds per round
SHOW_FEEDBACK = True  # Show accuracy feedback after each note
AUTO_ADVANCE = True  # Automatically advance to next note after success

# Audio Settings
PLAYBACK_SPEED = 1.0  # Speed multiplier for sheet music playback
METRONOME_ENABLED = False  # Enable metronome
BPM = 120  # Beats per minute
