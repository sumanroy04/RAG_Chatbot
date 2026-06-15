import type { MoodOption, TopicOption } from "./types";

/**
 * Mirrors MOOD_PROFILES in main.py.
 * "tone" is informational (the backend uses it to steer the system prompt);
 * "ack" is shown to the user as a small confirmation note.
 */
export const MOOD_PROFILES: Record<string, { tone: string; ack: string }> = {
  Happy: {
    tone: "upbeat and affirming",
    ack: "Lovely. I will keep things light and encouraging.",
  },
  Calm: {
    tone: "quiet and grounded",
    ack: "Calm mode is on. I will keep the pace steady.",
  },
  Okay: {
    tone: "balanced and gentle",
    ack: "Okay is a real place to start. I will help you sort things gently.",
  },
  Sad: {
    tone: "warm and validating",
    ack: "I hear you. I will keep my replies soft and manageable.",
  },
  Stressed: {
    tone: "calming and practical",
    ack: "Stress mode is on. I will focus on grounding and practical next steps.",
  },
};

/**
 * Mirrors TOPIC_PROFILES in main.py.
 * "starter" is sent as the first user message when a topic chip is clicked.
 */
export const TOPIC_PROFILES: Record<string, { focus: string; starter: string }> = {
  "Study Stress": {
    focus: "academic pressure, exams, procrastination, focus, burnout, and study planning",
    starter: "I'd like to talk about study stress and how to handle academic pressure.",
  },
  "Sleep Issues": {
    focus: "sleep hygiene, racing thoughts at night, routines, rest, and fatigue",
    starter: "I'd like to talk about sleep issues and how to rest better.",
  },
  Relationships: {
    focus: "relationships, communication, loneliness, conflict, boundaries, and support systems",
    starter: "I'd like to talk about relationships and emotional boundaries.",
  },
  Anxiety: {
    focus: "anxiety, worry, panic, grounding, breathing, and nervous-system regulation",
    starter: "I'd like to talk about anxiety and ways to feel more grounded.",
  },
};

export const MOODS: MoodOption[] = [
  { emoji: "😊", label: "Happy" },
  { emoji: "😌", label: "Calm" },
  { emoji: "😐", label: "Okay" },
  { emoji: "😔", label: "Sad" },
  { emoji: "😤", label: "Stressed" },
];

export const TOPICS: TopicOption[] = [
  { emoji: "📚", label: "Study Stress" },
  { emoji: "😴", label: "Sleep Issues" },
  { emoji: "💖", label: "Relationships" },
  { emoji: "😰", label: "Anxiety" },
];

export function getMoodAcknowledgement(selectedMood: string | null): string {
  if (!selectedMood) return "Choose a mood to tune the assistant's tone.";
  const profile = MOOD_PROFILES[selectedMood];
  return profile ? profile.ack : "Choose a mood to tune the assistant's tone.";
}

export function getButtonStarter(selectedTopic: string, selectedMood: string | null): string {
  const profile = TOPIC_PROFILES[selectedTopic];
  const starter = profile ? profile.starter : `I'd like to talk about ${selectedTopic.toLowerCase()}.`;
  if (selectedMood) {
    return `${starter} I'm feeling ${selectedMood.toLowerCase()} today.`;
  }
  return starter;
}

export const WELCOME_MESSAGE =
  "Hello! I'm Patronus AI. What would you like to talk about today?";

export const DEFAULT_RECENT_CHATS = ["Exam Stress", "Anxiety Help", "Sleep Issues"];
