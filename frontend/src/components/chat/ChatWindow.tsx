import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType } from "../../types";
import ChatMessage from "./ChatMessage";

interface Props {
  messages: ChatMessageType[];
  isTyping: boolean;
}

export default function ChatWindow({ messages, isTyping }: Props) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isTyping]);

  return (
    <div className="chat-shell">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      {isTyping && (
        <div className="chat-row assistant">
          <div className="avatar">🤖</div>
          <div className="bubble">
            <span className="typing-dots" aria-label="Patronus is typing">
              <span />
              <span />
              <span />
            </span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
