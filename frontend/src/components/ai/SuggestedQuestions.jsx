const SUGGESTED_QUESTIONS = [
  "What are your delivery policies?",
  "What organic products do you have?",
  "What is the status of my order?",
  "Show my recent orders.",
];

export default function SuggestedQuestions({ onSelectQuestion, disabled = false }) {
  return (
    <div className="my-3 px-1">
      <p className="mb-2 text-xs font-medium text-gray-500">Suggested questions:</p>
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectQuestion(q)}
            className="rounded-xl border border-primary-200 bg-primary-50/70 px-3 py-1.5 text-left text-xs font-medium text-primary-800 transition-all hover:border-primary-400 hover:bg-primary-100 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
