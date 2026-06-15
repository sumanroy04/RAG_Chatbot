interface Props {
  contextLabel: string;
}

export default function HeroStrip({ contextLabel }: Props) {
  return (
    <section className="hero-strip">
      <h2>How are you feeling today?</h2>
      <p>
        Pick a mood to set the tone, then choose a topic chip or write freely. Patronus will adapt
        the response style and retrieval focus.
      </p>
      <span className="context-pill">✨ {contextLabel}</span>
    </section>
  );
}
