export type Role = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  mood?: string | null;
  topic?: string | null;
  isCrisis?: boolean;
}

export interface ChatApiResponse {
  response: string;
  is_crisis: boolean;
}

export interface MoodOption {
  emoji: string;
  label: string;
}

export interface TopicOption {
  emoji: string;
  label: string;
}
