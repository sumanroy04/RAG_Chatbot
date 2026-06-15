import { MOODS, getMoodAcknowledgement } from "../constants";

interface Props {
  selectedMood: string | null;
  onSelect: (mood: string) => void;
}

export default function MoodSelector({ selectedMood, onSelect }: Props) {
  return (
    <>
      <div className="mood-row">
        {MOODS.map(({ emoji, label }) => (
          <button
            key={label}
            className={`mood-btn${selectedMood === label ? " is-selected" : ""}`}
            onClick={() => onSelect(label)}
            aria-pressed={selectedMood === label}
          >
            <span className="mood-emoji">{emoji}</span>
            <span>{label}</span>
          </button>
        ))}
      </div>
      <div className="context-note">{getMoodAcknowledgement(selectedMood)}</div>
    </>
  );
}
