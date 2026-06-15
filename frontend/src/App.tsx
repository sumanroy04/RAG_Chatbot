import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import HeroStrip from "./components/HeroStrip";
import MoodSelector from "./components/MoodSelector";
import TopicChips from "./components/TopicChips";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import { DEFAULT_RECENT_CHATS, WELCOME_MESSAGE, getButtonStarter } from "./constants";
import { sendChatMessage, ChatApiError } from "./api";
import { exportChatToPdf } from "./utils/exportPdf";
import type { ChatMessage } from "./types";

let idCounter = 0;
const nextId = () => `msg-${Date.now()}-${idCounter++}`;

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  const runExchange = async (userContent: string, mood: string | null, topic: string | null) => {
    const userMessage: ChatMessage = {
      id: nextId(),
      role: "user",
      content: userContent,
      mood,
      topic,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    setApiError(null);

    try {
      const result = await sendChatMessage(userContent, mood, topic);
      const assistantMessage: ChatMessage = {
        id: nextId(),
        role: "assistant",
        content: result.response,
        mood,
        topic,
        isCrisis: result.is_crisis,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const text =
        err instanceof ChatApiError ? err.message : "Something went wrong. Please try again.";
      setApiError(text);
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", content: text, mood, topic },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = (content: string) => {
    void runExchange(content, selectedMood, selectedTopic);
  };

  const handleMoodSelect = (mood: string) => {
    setSelectedMood(mood);
  };

  const handleTopicSelect = (topic: string) => {
    if (isTyping) return;
    setSelectedTopic(topic);
    const starter = getButtonStarter(topic, selectedMood);
    void runExchange(starter, selectedMood, topic);
  };

  const handleNewChat = () => {
    setMessages([]);
    setSelectedMood(null);
    setSelectedTopic(null);
    setApiError(null);
  };

  const handleExportPdf = () => {
    setIsExporting(true);
    try {
      exportChatToPdf(messages);
    } finally {
      setIsExporting(false);
    }
  };

  const displayMessages: ChatMessage[] =
    messages.length === 0
      ? [{ id: "welcome", role: "assistant", content: WELCOME_MESSAGE }]
      : messages;

  const userMessages = messages.filter((m) => m.role === "user").map((m) => m.content);
  const recentChats = userMessages.length ? userMessages.slice(-5).reverse() : DEFAULT_RECENT_CHATS;

  const contextParts = [selectedMood, selectedTopic].filter(Boolean) as string[];
  const contextLabel = contextParts.length
    ? contextParts.join(" • ")
    : "Choose a mood or topic to tune replies";

  return (
    <div className="app-shell">
      <Sidebar
        recentChats={recentChats}
        mood={selectedMood}
        topic={selectedTopic}
        canExport={messages.length > 0}
        isExporting={isExporting}
        onNewChat={handleNewChat}
        onExportPdf={handleExportPdf}
      />

      <main className="main-content">
        <Header darkMode={darkMode} onToggleDark={() => setDarkMode((d) => !d)} />

        {apiError && <div className="api-error-banner">⚠️ {apiError}</div>}

        <HeroStrip contextLabel={contextLabel} />

        <MoodSelector selectedMood={selectedMood} onSelect={handleMoodSelect} />

        <TopicChips selectedTopic={selectedTopic} onSelect={handleTopicSelect} disabled={isTyping} />

        <ChatWindow messages={displayMessages} isTyping={isTyping} />

        <ChatInput onSend={handleSend} disabled={isTyping} />
      </main>
    </div>
  );
}
