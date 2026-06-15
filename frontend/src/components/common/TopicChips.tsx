import { TOPICS } from "../../constants";

interface Props {
  selectedTopic: string | null;
  onSelect: (topic: string) => void;
  disabled?: boolean;
}

export default function TopicChips({ selectedTopic, onSelect, disabled }: Props) {
  return (
    <>
      <div className="panel-title">Choose a focus</div>
      <div className="chip-row">
        {TOPICS.map(({ emoji, label }) => (
          <button
            key={label}
            className={`chip-btn${selectedTopic === label ? " is-selected" : ""}`}
            onClick={() => onSelect(label)}
            disabled={disabled}
            aria-pressed={selectedTopic === label}
          >
            {emoji} {label}
          </button>
        ))}
      </div>
    </>
  );
}
