function formatSourceTitle(source) {
  if (!source) return null;
  const doc = (source.document || source.title || "").toLowerCase();
  if (doc.includes("order service") || doc.includes("order_service")) return "Order Service";
  if (doc.includes("customer_policies") || doc.includes("policy")) return "OrganicKart Policies";
  if (doc.includes("organic_products") || doc.includes("product")) return "Product Catalog";
  if (doc.includes("faq")) return "Customer FAQ";
  return source.title || source.document || "OrganicKart Knowledge Base";
}

export default function ChatMessage({ message }) {
  const isUser = message.sender === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} my-1.5 animate-fade-in`}>
      <div className={`flex max-w-[85%] sm:max-w-[80%] items-start gap-2 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        {/* Avatar */}
        <div
          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold shadow-sm ${
            isUser ? "bg-primary-700 text-white" : "bg-emerald-600 text-white"
          }`}
        >
          {isUser ? "👤" : "🤖"}
        </div>

        {/* Message Content Bubble */}
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm shadow-sm ${
            isUser
              ? "bg-primary-600 text-white rounded-tr-none"
              : "border border-gray-100 bg-white text-gray-800 rounded-tl-none"
          }`}
        >
          <div className="whitespace-pre-wrap leading-relaxed">{message.text}</div>

          {/* Sources Section for AI Messages */}
          {!isUser && Array.isArray(message.sources) && message.sources.length > 0 && (
            <div className="mt-2.5 border-t border-gray-100 pt-1.5 text-[11px] text-gray-500">
              <span className="font-semibold text-gray-600">Source: </span>
              {Array.from(
                new Set(
                  message.sources
                    .map(formatSourceTitle)
                    .filter(Boolean)
                )
              ).join(" • ")}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
