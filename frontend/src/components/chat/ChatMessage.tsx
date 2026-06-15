import type { ChatMessage as ChatMessageType } from "../../types";
import { formatMessageHtml } from "../../utils/formatMessage";
import CrisisCard from "./CrisisCard";

interface Props {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";
  const icon = isUser ? "🧑" : "🤖";

  return (
    <>
      <div className={`chat-row ${message.role}`}>
        <div className="avatar">{icon}</div>
        <div className="bubble" dangerouslySetInnerHTML={{ __html: formatMessageHtml(message.content) }} />
      </div>
      {message.isCrisis && <CrisisCard />}
    </>
  );
}
