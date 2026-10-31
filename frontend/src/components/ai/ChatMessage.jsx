import MarkdownRenderer from "./MarkdownRenderer";

function formatSourceTitle(source) {
  if (!source) return null;
  const doc = (source.document || "").toLowerCase();
  const title = (source.title || "").toLowerCase();
  const combined = `${doc} ${title}`;

  if (combined.includes("general knowledge")) return "General Knowledge";
  if (combined.includes("product service api") || combined.includes("product catalog")) return "Product Catalog";
  if (combined.includes("order service cart") || combined.includes("your cart")) return "Your Cart";
  if (combined.includes("order service")) return "Order Service";
  if (combined.includes("delivery service")) return "Delivery Tracking";
  if (combined.includes("notification service")) return "Notifications";
  if (combined.includes("customer_policies") || combined.includes("policy")) return "OrganicKart Policies";
  if (combined.includes("customer_faq") || combined.includes("faq")) return "Customer FAQ";
  if (combined.includes("organic_products")) return "Organic Products Guide";
  if (combined.includes("organickart_overview") || combined.includes("overview")) return "OrganicKart Overview";
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
          {isUser ? (
            <div className="whitespace-pre-wrap leading-relaxed">{message.text}</div>
          ) : (
            <MarkdownRenderer content={message.text} />
          )}

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
