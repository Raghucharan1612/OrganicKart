const FLOW = ["PENDING", "CONFIRMED", "PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"];

function normalizeStatus(status) {
  const upper = String(status || "PENDING").toUpperCase();
  if (upper === "ACCEPTED" || upper === "ASSIGNED") {
    return "CONFIRMED";
  }
  return upper;
}

export default function DeliveryTimeline({ status }) {
  const current = normalizeStatus(status);
  const currentIndex = FLOW.includes(current) ? FLOW.indexOf(current) : -1;
  const steps = [...FLOW];

  if (current === "FAILED" || current === "CANCELLED") {
    steps.push(current);
  }

  return (
    <div className="mt-6">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h3 className="font-display text-lg font-semibold text-primary-900">Delivery timeline</h3>
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-primary-600">{current}</span>
      </div>

      <div className="space-y-3">
        {steps.map((step, index) => {
          const isCurrent = step === current;
          const isDone = currentIndex >= 0 ? index <= currentIndex : false;
          const isSpecial = step === "FAILED" || step === "CANCELLED";

          return (
            <div key={`${step}-${index}`} className="flex items-start gap-3">
              <div className="flex flex-col items-center">
                <div
                  className={`flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold ${
                    isCurrent
                      ? "bg-primary-600 text-white"
                      : isDone || isSpecial
                        ? "bg-emerald-500 text-white"
                        : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {isDone || isSpecial ? "✓" : index + 1}
                </div>
                {index < steps.length - 1 && <div className="mt-1 h-7 w-px bg-gray-200" />}
              </div>

              <div className="flex-1 rounded-2xl border border-gray-100 bg-white px-3 py-2 shadow-sm">
                <p className={`text-sm font-medium ${isCurrent ? "text-primary-800" : "text-gray-700"}`}>
                  {step.replace(/_/g, " ")}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
