NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLAT_TO_SHARP = {
    'DB': 'C#',
    'EB': 'D#',
    'GB': 'F#',
    'AB': 'G#',
    'BB': 'A#'
}

def normalize_note_name(name: str) -> str:
    name = name.strip().upper()
    if len(name) >= 2 and name[1] in ['#', 'B']:
        base = name[:2]
    else:
        base = name[:1]

    if base.endswith('B') and base in FLAT_TO_SHARP:
        base = FLAT_TO_SHARP[base]

    if base not in NOTE_NAMES:
        raise ValueError(f"Invalid note name: {name}")

    return base

def root_name_to_pitch_class(root_name: str) -> int:
    return NOTE_NAMES.index(normalize_note_name(root_name))

def pitch_class_to_note_name(pc: int) -> str:
    return NOTE_NAMES[pc % 12]

def major_chord_pitch_classes(root_name: str) -> set[int]:
    root_pc = root_name_to_pitch_class(root_name)
    return {(root_pc + interval) % 12 for interval in (0, 4, 7)}

def major_chord_note_names(root_name: str) -> list[str]:
    return [pitch_class_to_note_name(pc) for pc in sorted(major_chord_pitch_classes(root_name))]

def is_major_chord(played_notes: list[int], root_name: str) -> bool:
    played_pc = {note % 12 for note in played_notes}
    return major_chord_pitch_classes(root_name).issubset(played_pc)

def chord_feedback(played_notes: list[int], root_name: str) -> dict:
    played_pc = {note % 12 for note in played_notes}
    expected = major_chord_pitch_classes(root_name)
    return {
        'expected': expected,
        'played': played_pc,
        'missing': expected - played_pc,
        'extra': played_pc - expected
    }