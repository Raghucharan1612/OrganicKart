import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import orderService from "@/services/orderService";
import addressService from "@/services/addressService";
import Spinner from "@/components/Spinner";
import { getApiErrorMessage } from "@/utils/errorUtils";

let razorpayScriptPromise;

function loadRazorpayScript() {
  if (window.Razorpay) return Promise.resolve();
  if (razorpayScriptPromise) return razorpayScriptPromise;

  razorpayScriptPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    script.onload = () => window.Razorpay ? resolve() : reject(new Error("Razorpay Checkout did not load."));
    script.onerror = () => reject(new Error("Unable to load secure payment checkout. Please try again."));
    document.body.appendChild(script);
  }).catch((error) => {
    razorpayScriptPromise = undefined;
    throw error;
  });

  return razorpayScriptPromise;
}

function createIdempotencyKey() {
  return window.crypto?.randomUUID?.() || `checkout-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const paymentAttemptKey = useRef(createIdempotencyKey());
  const isVerifyingRef = useRef(false);
  const [cart, setCart] = useState({ items: [] });
  const [addresses, setAddresses] = useState([]);
  const [selectedAddressId, setSelectedAddressId] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isInitiating, setIsInitiating] = useState(false);
  const [isPaymentOpen, setIsPaymentOpen] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState("");
  const [paymentSession, setPaymentSession] = useState(null);

  useEffect(() => {
    let mounted = true;
    Promise.all([orderService.getCart(), addressService.list()])
      .then(([cartData, savedAddresses]) => {
        if (!mounted) return;
        setCart(cartData || { items: [] });
        const availableAddresses = savedAddresses || [];
        setAddresses(availableAddresses);
        const preferred = availableAddresses.find((address) => address.is_default) || availableAddresses[0];
        if (preferred) setSelectedAddressId(String(preferred.id));
        if (!cartData?.items?.length) setError("Your cart is empty. Add a few products before checkout.");
      })
      .catch((requestError) => mounted && setError(getApiErrorMessage(requestError, "Unable to load checkout details.")))
      .finally(() => mounted && setIsLoading(false));
    return () => { mounted = false; };
  }, []);

  const selectedAddress = addresses.find((address) => String(address.id) === selectedAddressId);

  const openRazorpayCheckout = async (session) => {
    await loadRazorpayScript();
    if (!window.Razorpay) throw new Error("Secure payment checkout is unavailable.");

    const checkout = new window.Razorpay({
      key: session.razorpay_key_id,
      amount: session.amount_paise,
      currency: session.currency,
      order_id: session.razorpay_order_id,
      name: "OrganicKart",
      description: "OrganicKart order payment",
      prefill: {
        name: selectedAddress?.recipient_name || user?.name || "",
        contact: selectedAddress?.phone || user?.phone || "",
        email: user?.email || "",
      },
      notes: { local_order_id: String(session.order_id) },
      theme: { color: "#15803d" },
      handler: async (response) => {
        isVerifyingRef.current = true;
        setIsVerifying(true);
        setIsPaymentOpen(true);
        setError("");
        try {
          const verified = await orderService.verifyPayment({
            order_id: session.order_id,
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });
          if (verified.payment_status !== "PAID") {
            throw new Error("Payment could not be confirmed. Please try again.");
          }
          // The payment result is authoritative; refreshing cart state is a
          // best-effort UI update and must not turn a verified payment into
          // a false failure if that follow-up request is temporarily unavailable.
          await orderService.getCart().catch(() => null);
          window.dispatchEvent(new Event("cart-updated"));
          navigate(`/orders/${session.order_id}`, { replace: true, state: { paymentConfirmed: true } });
        } catch (verificationError) {
          setError(getApiErrorMessage(verificationError, "Payment was received but could not be verified. Please retry securely."));
          isVerifyingRef.current = false;
          setIsVerifying(false);
          setIsPaymentOpen(false);
        }
      },
      modal: {
        ondismiss: () => {
          if (!isVerifyingRef.current) {
            setIsPaymentOpen(false);
            setError("Payment was cancelled. Your cart and pending payment remain unchanged; you can retry.");
          }
        },
      },
    });
    checkout.on("payment.failed", () => {
      setIsPaymentOpen(false);
      setError("Payment failed or was not completed. Your cart remains unchanged; please retry.");
    });
    setIsPaymentOpen(true);
    checkout.open();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!cart.items.length) {
      setError("Your cart is empty.");
      return;
    }
    if (!selectedAddressId) {
      setError("Select a saved delivery address before proceeding to payment.");
      return;
    }

    setIsInitiating(true);
    isVerifyingRef.current = false;
    setError("");
    try {
      const session = paymentSession || await orderService.initiateCheckout(
        Number(selectedAddressId),
        paymentAttemptKey.current,
      );
      setPaymentSession(session);
      await openRazorpayCheckout(session);
    } catch (checkoutError) {
      setError(getApiErrorMessage(checkoutError, "Unable to start secure payment. Please try again."));
      setIsPaymentOpen(false);
    } finally {
      setIsInitiating(false);
    }
  };

  if (isLoading) {
    return <div className="mx-auto max-w-4xl px-4 py-12"><Spinner label="Preparing your checkout details…" /></div>;
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
      <div>
        <h1 className="font-display text-3xl font-extrabold text-gray-900">Checkout</h1>
        <p className="mt-1 text-sm text-gray-500">Choose a saved address, then complete payment securely with Razorpay.</p>
      </div>

      {error && <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">⚠️ {error}</div>}

      <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(300px,1fr)]">
        <form onSubmit={handleSubmit} className="space-y-6">
          <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <h2 className="font-display text-lg font-bold text-gray-900">📍 Delivery Address</h2>
              <Link to="/addresses" className="text-xs font-bold text-primary-700 hover:underline">Manage addresses</Link>
            </div>
            {addresses.length ? (
              <label className="block">
                <span className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Saved address</span>
                <select value={selectedAddressId} onChange={(event) => setSelectedAddressId(event.target.value)} className="input-field mt-1">
                  {addresses.map((address) => <option key={address.id} value={address.id}>{address.label} — {address.address_line1}, {address.city}</option>)}
                </select>
              </label>
            ) : (
              <p className="text-sm text-gray-600">Add a saved delivery address before paying. The server verifies address ownership.</p>
            )}
            {selectedAddress && <p className="rounded-xl bg-primary-50 p-3 text-sm text-primary-900">{formatAddress(selectedAddress)}</p>}
          </section>

          <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <h2 className="font-display text-lg font-bold text-gray-900">🛒 Items in Order ({cart.items.length})</h2>
              <Link to="/cart" className="text-xs font-bold text-primary-700 hover:underline">Edit Cart</Link>
            </div>
            <div className="divide-y divide-gray-50">
              {cart.items.map((item) => <div key={item.id} className="py-3 flex items-center justify-between text-sm"><p className="font-bold text-gray-800">{item.product_name}</p><span className="text-gray-600">Qty {item.quantity}</span></div>)}
            </div>
          </section>

          <button type="submit" disabled={isInitiating || isPaymentOpen || isVerifying || !cart.items.length || !selectedAddressId} className="btn-primary w-full !py-3.5 font-bold text-base shadow-lg disabled:opacity-60">
            {isVerifying ? "Verifying payment…" : isPaymentOpen ? "Payment in progress…" : isInitiating ? "Opening secure payment…" : paymentSession ? "Retry Secure Payment" : "Proceed to Secure Payment"}
          </button>
        </form>

        <aside className="rounded-2xl border border-primary-100 bg-white p-6 shadow-sm space-y-4 self-start">
          <h2 className="font-display text-lg font-bold text-gray-900 border-b border-gray-100 pb-3">Payment Summary</h2>
          {paymentSession ? (
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex justify-between"><span>Server-confirmed total</span><span className="font-bold text-primary-800">₹{formatPaise(paymentSession.amount_paise)}</span></div>
              <div className="flex justify-between"><span>Currency</span><span className="font-semibold">{paymentSession.currency}</span></div>
              <p className="rounded-xl bg-primary-50 p-3 text-xs text-primary-800">Amount and order details were calculated securely by OrganicKart before Razorpay opened.</p>
            </div>
          ) : <p className="text-sm text-gray-600">Your final total is calculated and locked by the server when secure payment starts.</p>}
        </aside>
      </div>
    </div>
  );
}

function formatAddress(address) {
  return [address.recipient_name, address.address_line1, address.address_line2, address.city, address.state, address.postal_code, address.country].filter(Boolean).join(", ");
}

function formatPaise(amountPaise) {
  return (Number(amountPaise) / 100).toFixed(2);
}
