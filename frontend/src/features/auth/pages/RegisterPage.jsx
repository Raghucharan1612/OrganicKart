import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import toast from "react-hot-toast";
import { registerUser, clearAuthError } from "@/store/slices/authSlice";
import Input from "@/components/Input";
import Button from "@/components/Button";
import FormError from "@/components/FormError";
import { validateEmail, validatePassword, validateRequired, validatePhone } from "@/utils/validators";

// Roles a person can self-select at signup. Must mirror the backend's
// PUBLIC_SIGNUP_ROLES — ADMIN/SUPER_ADMIN are provisioned internally only.
const SIGNUP_ROLES = [
  { value: "CUSTOMER", label: "Customer — shop for organic produce" },
  { value: "FARMER", label: "Farmer — sell what you grow" },
  { value: "VENDOR", label: "Vendor — run an organic store" },
  { value: "DELIVERY_PARTNER", label: "Delivery Partner — fulfil deliveries" },
];

export default function RegisterPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { status, error } = useSelector((state) => state.auth);

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    password: "",
    role: "CUSTOMER",
  });
  const [fieldErrors, setFieldErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) setFieldErrors((prev) => ({ ...prev, [name]: "" }));
    if (error) dispatch(clearAuthError());
  };

  const validate = () => {
    const errors = {
      full_name: validateRequired(form.full_name, "Full name"),
      email: validateEmail(form.email),
      password: validatePassword(form.password),
      phone: validatePhone(form.phone),
    };
    setFieldErrors(errors);
    return Object.values(errors).every((msg) => !msg);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    const payload = { ...form, phone: form.phone || undefined };
    const result = await dispatch(registerUser(payload));

    if (registerUser.fulfilled.match(result)) {
      toast.success("Account created! Please log in.");
      navigate("/login");
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <div className="card">
        <h1 className="font-display text-2xl font-bold text-primary-900">Create your account</h1>
        <p className="mt-1 text-sm text-gray-500">Join OrganicKart's organic marketplace.</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <FormError message={error} />

          <Input
            id="full_name"
            name="full_name"
            label="Full name"
            placeholder="Jane Doe"
            value={form.full_name}
            onChange={handleChange}
            error={fieldErrors.full_name}
          />

          <Input
            id="email"
            name="email"
            type="email"
            label="Email address"
            placeholder="you@example.com"
            value={form.email}
            onChange={handleChange}
            error={fieldErrors.email}
          />

          <Input
            id="phone"
            name="phone"
            label="Phone (optional)"
            placeholder="+91 98765 43210"
            value={form.phone}
            onChange={handleChange}
            error={fieldErrors.phone}
          />

          <Input
            id="password"
            name="password"
            type="password"
            label="Password"
            placeholder="At least 8 characters"
            value={form.password}
            onChange={handleChange}
            error={fieldErrors.password}
          />

          <div>
            <label htmlFor="role" className="mb-1.5 block text-sm font-medium text-gray-700">
              I am signing up as
            </label>
            <select
              id="role"
              name="role"
              value={form.role}
              onChange={handleChange}
              className="input-field"
            >
              {SIGNUP_ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          <Button type="submit" isLoading={status === "loading"} className="w-full">
            Create account
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-primary-700 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
