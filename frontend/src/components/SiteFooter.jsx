import toast from "react-hot-toast";
import { Link } from "react-router-dom";

const companyLinks = [
  ["About Us", "/info/about"], ["Careers", "/info/careers"], ["Organic Farmers", "/info/farmers"], ["Press & News", "/info/news"], ["Contact Us", "/info/contact"],
];
const helpLinks = [
  ["FAQs", "/info/faqs"], ["Shipping Policy", "/info/shipping"], ["Returns & Refund", "/info/returns"], ["Terms & Privacy", "/info/terms"], ["Customer Care", "/info/support"],
];

export default function SiteFooter() {
  return (
    <footer className="mt-16 border-t border-gray-200 bg-white text-gray-700">
      <div className="mx-auto w-full px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5">
          <div className="lg:col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-emerald-800 text-lg font-bold text-white shadow-md">🌿</div>
              <span className="font-display text-xl font-bold text-primary-900">OrganicKart</span>
            </Link>
            <p className="max-w-sm text-xs leading-relaxed text-gray-500">Fresh, certified organic groceries and daily essentials in one simple marketplace.</p>
          </div>
          <div>
            <h4 className="font-display text-sm font-bold uppercase tracking-wider text-gray-900">Shop</h4>
            <ul className="mt-3 space-y-2 text-xs"><li><Link to="/products" className="hover:text-primary-700">Browse products</Link></li><li><Link to="/categories" className="hover:text-primary-700">Categories</Link></li></ul>
          </div>
          <div>
            <h4 className="font-display text-sm font-bold uppercase tracking-wider text-gray-900">Company</h4>
            <ul className="mt-3 space-y-2 text-xs">{companyLinks.map(([label, to]) => <li key={to}><Link to={to} className="hover:text-primary-700">{label}</Link></li>)}</ul>
          </div>
          <div>
            <h4 className="font-display text-sm font-bold uppercase tracking-wider text-gray-900">Help &amp; Support</h4>
            <ul className="mt-3 space-y-2 text-xs">{helpLinks.map(([label, to]) => <li key={to}><Link to={to} className="hover:text-primary-700">{label}</Link></li>)}</ul>
          </div>
        </div>
        <div className="mt-10 flex flex-col items-center justify-between gap-4 rounded-2xl border border-primary-100 bg-primary-50 p-6 sm:flex-row">
          <div><h4 className="font-display text-base font-bold text-primary-900">Download OrganicKart App</h4><p className="mt-0.5 text-xs text-gray-600">The OrganicKart mobile app is in development.</p></div>
          <button type="button" onClick={() => toast("OrganicKart app is coming soon!", { icon: "📱" })} className="flex items-center gap-2 rounded-xl bg-black px-4 py-2 text-xs font-semibold text-white transition hover:bg-gray-800"><span>🤖</span> Google Play</button>
        </div>
        <div className="mt-8 flex flex-col items-center justify-between gap-4 border-t border-gray-100 pt-6 text-xs text-gray-500 sm:flex-row"><p>© 2026 OrganicKart Technologies Ltd. All rights reserved.</p><span>100% Organic Certified</span></div>
      </div>
    </footer>
  );
}
