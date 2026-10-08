import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import aiService from "@/services/aiService";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

const VENDOR_SUGGESTED_QUESTIONS = [
  "Show my products",
  "Check my inventory",
  "Which products are low on stock?",
  "Show pending certifications",
];

const VENDOR_GREETING = {
  id: "vendor-greeting",
  sender: "ai",
  text: "Hello! I'm your OrganicKart Vendor Assistant.\nI can help you manage your product catalog, check inventory levels, monitor stock, and view certification status.\nHow can I help you today?",
  sources: [],
};

export default function VendorAIAssistant() {
  const { user, isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([VENDOR_GREETING]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const isVendorOrFarmer =
    isAuthenticated && (user?.role === "VENDOR" || user?.role === "FARMER");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isLoading, isOpen]);

  useEffect(() => {
    const handleOpen = () => {
      setIsOpen(true);
    };
    window.addEventListener("open-vendor-ai", handleOpen);
    return () => window.removeEventListener("open-vendor-ai", handleOpen);
  }, []);

  // Only render for VENDOR / FARMER users
  if (!isVendorOrFarmer) {
    return null;
  }

  const handleSendMessage = async (text) => {
    if (!text.trim() || isLoading) return;

    setError(null);
    const userMsg = {
      id: Date.now().toString(),
      sender: "user",
      text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await aiService.sendVendorMessage(text);
      const aiMsg = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: response.answer || "I'm sorry, I couldn't generate a response. Please try again.",
        sources: response.sources || [],
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      let errorText = "Sorry, I couldn't connect to the Vendor AI Assistant. Please try again.";

      if (err.response) {
        const status = err.response.status;
        if (status === 401) {
          errorText = "Your session has expired. Please log in again.";
        } else if (status === 403) {
          errorText = "You are not authorized to use the Vendor AI Assistant.";
        } else if (status >= 500) {
          errorText = "The AI Assistant is temporarily unavailable. Please try again shortly.";
        }
      }

      setError(errorText);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: "ai",
          text: errorText,
          sources: [],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const roleLabel = user?.role === "FARMER" ? "Farmer" : "Vendor";

  return (
    <div className="fixed bottom-5 right-5 z-50 font-sans">
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2.5 rounded-full bg-amber-700 px-4 py-3 text-sm font-semibold text-white shadow-lg transition-all duration-200 hover:bg-amber-800 hover:shadow-xl active:scale-95"
          aria-label="Open Vendor AI Assistant"
        >
          <span className="text-lg">🌾</span>
          <span>{roleLabel} Assistant</span>
        </button>
      )}

      {/* Chat Window Panel */}
      {isOpen && (
        <div className="flex w-[calc(100vw-2.5rem)] sm:w-96 flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl transition-all duration-200 animate-scale-up max-h-[85vh] h-[550px]">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-amber-800/20 bg-amber-700 px-4 py-3 text-white">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-xl shadow-inner">
                🌾
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <h3 className="text-sm font-bold leading-none">OrganicKart AI</h3>
                  <span className="inline-block h-2 w-2 rounded-full bg-emerald-300 animate-pulse"></span>
                </div>
                <p className="text-[11px] text-amber-100">{roleLabel} Assistant</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 transition hover:bg-white/20 hover:text-white"
              aria-label="Close Vendor AI Assistant"
            >
              ✕
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto bg-slate-50/50 p-3">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {/* Vendor suggested questions shown only on initial greeting */}
            {messages.length === 1 && (
              <div className="my-3 px-1">
                <p className="mb-2 text-xs font-medium text-gray-500">Quick actions:</p>
                <div className="flex flex-wrap gap-2">
                  {VENDOR_SUGGESTED_QUESTIONS.map((q, idx) => (
                    <button
                      key={idx}
                      type="button"
                      disabled={isLoading}
                      onClick={() => handleSendMessage(q)}
                      className="rounded-xl border border-amber-200 bg-amber-50/70 px-3 py-1.5 text-left text-xs font-medium text-amber-800 transition-all hover:border-amber-400 hover:bg-amber-100 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Loading / Typing Indicator */}
            {isLoading && (
              <div className="my-1.5 flex items-center gap-2 text-xs text-gray-500 animate-fade-in">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-600 text-white text-xs">
                  🌾
                </div>
                <div className="flex items-center gap-1 rounded-2xl border border-gray-100 bg-white px-3 py-2 shadow-sm">
                  <span className="font-medium text-gray-600">Vendor AI is thinking</span>
                  <span className="inline-flex gap-0.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce"></span>
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0.2s]"></span>
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0.4s]"></span>
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      )}
    </div>
  );
}
