import { Link } from "react-router-dom";

export default function UnauthorizedPage() {
  return (
    <div className="mx-auto max-w-md text-center">
      <div className="card">
        <h1 className="font-display text-2xl font-bold text-primary-900">Access denied</h1>
        <p className="mt-2 text-sm text-gray-500">
          You don't have permission to view this page. If you think this is a mistake, contact support.
        </p>
        <Link to="/" className="btn-primary mt-6 inline-flex">
          Back to home
        </Link>
      </div>
    </div>
  );
}
