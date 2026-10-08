import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import aiService from "@/services/aiService";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";

const ADMIN_QUICK_PROMPTS = [
  "Show pending certifications",
  "Show vendor sales insights",
  "Show top-selling products",
  "Show low-stock products",
  "Which products have declining sales?",
  "Show order statistics",
];

const ADMIN_GREETING = {
  id: "admin-greeting",
  sender: "ai",
  text: "Hello! I'm your OrganicKart Admin AI Assistant.\nI can help with certification queues, catalog insights, orders, revenue, vendor sales, inventory, and product performance.",
  sources: [],
};

function getAdminErrorMessage(error) {
  const status = error?.response?.status;
  if (status === 401) return "Your session has expired. Please log in again.";
  if (status === 403) return "You are not authorized to use the Admin AI Assistant.";
  if (status === 404 || status === 422) return "Admin AI could not process that request. Please try again.";
  return "Admin AI is temporarily unavailable. Please try again.";
}

export default function AdminAIAssistant() {
  const { user, isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([ADMIN_GREETING]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const isAdmin = isAuthenticated && user?.role === "ADMIN";

  useEffect(() => {
    const handleOpen = () => setIsOpen(true);
    window.addEventListener("open-admin-ai", handleOpen);
    return () => window.removeEventListener("open-admin-ai", handleOpen);
  }, []);

  useEffect(() => {
    if (isOpen) messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, isOpen]);

  if (!isAdmin) return null;

  const handleSendMessage = async (text) => {
    const message = text.trim();
    if (!message || isLoading) return;

    setMessages((previous) => [...previous, { id: `user-${Date.now()}`, sender: "user", text: message }]);
    setIsLoading(true);

    try {
      const response = await aiService.sendAdminMessage(message);
      const answer = typeof response?.answer === "string" && response.answer.trim()
        ? response.answer
        : "Admin AI did not return a response. Please try again.";
      setMessages((previous) => [
        ...previous,
        { id: `assistant-${Date.now()}`, sender: "ai", text: answer, sources: Array.isArray(response?.sources) ? response.sources : [] },
      ]);
    } catch (requestError) {
      const errorText = getAdminErrorMessage(requestError);
      setMessages((previous) => [
        ...previous,
        { id: `error-${Date.now()}`, sender: "ai", text: errorText, sources: [] },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 font-sans">
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2.5 rounded-full bg-slate-800 px-4 py-3 text-sm font-semibold text-white shadow-lg transition-all duration-200 hover:bg-slate-900 hover:shadow-xl active:scale-95"
          aria-label="Open Admin AI Assistant"
        >
          <span className="text-lg">📊</span>
          <span>Admin AI</span>
        </button>
      )}

      {isOpen && (
        <div className="flex h-[min(550px,calc(100vh-2.5rem))] w-[calc(100vw-2.5rem)] max-w-md flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-700 bg-slate-800 px-4 py-3 text-white">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-xl shadow-inner">📊</div>
              <div>
                <div className="flex items-center gap-1.5">
                  <h3 className="text-sm font-bold leading-none">OrganicKart AI</h3>
                  <span className="inline-block h-2 w-2 rounded-full bg-emerald-300" />
                </div>
                <p className="text-[11px] text-slate-300">Admin Intelligence Assistant</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 transition hover:bg-white/20 hover:text-white"
              aria-label="Close Admin AI Assistant"
            >
              ✕
            </button>
          </div>

          <div className="flex-1 overflow-y-auto bg-slate-50/70 p-3">
            {messages.map((message) => <ChatMessage key={message.id} message={message} />)}

            {messages.length === 1 && (
              <div className="my-3 px-1">
                <p className="mb-2 text-xs font-medium text-gray-500">Administrative quick actions:</p>
                <div className="flex flex-wrap gap-2">
                  {ADMIN_QUICK_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      disabled={isLoading}
                      onClick={() => handleSendMessage(prompt)}
                      className="rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-left text-xs font-medium text-slate-700 transition hover:border-slate-500 hover:bg-slate-100 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {isLoading && (
              <div className="my-1.5 flex items-center gap-2 text-xs text-gray-500">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-700 text-white text-xs">📊</div>
                <div className="flex items-center gap-1 rounded-2xl border border-gray-100 bg-white px-3 py-2 shadow-sm">
                  <span className="font-medium text-gray-600">Admin AI is analyzing</span>
                  <span className="inline-flex gap-0.5">
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 [animation-delay:0.2s]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 [animation-delay:0.4s]" />
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      )}
    </div>
  );
}
