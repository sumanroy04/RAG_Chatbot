import type { ChatApiResponse } from "../types";

// Configure with VITE_API_BASE_URL in a .env file (see .env.example).
// Falls back to a local FastAPI dev server.
const API_BASE_URL: string =
  (import.meta as unknown as { env: Record<string, string | undefined> }).env
    .VITE_API_BASE_URL || "http://127.0.0.1:8000";

export class ChatApiError extends Error {}

/**
 * Calls the FastAPI POST /chat endpoint.
 */
export async function sendChatMessage(
  message: string,
  mood: string | null,
  topic: string | null,
): Promise<ChatApiResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, mood, topic }),
    });
  } catch {
    throw new ChatApiError(
      `Could not reach the Patronus backend at ${API_BASE_URL}. Is the FastAPI server running?`,
    );
  }

  if (!res.ok) {
    throw new ChatApiError(`Backend returned an error (${res.status}).`);
  }

  return (await res.json()) as ChatApiResponse;
}
export { API_BASE_URL };
