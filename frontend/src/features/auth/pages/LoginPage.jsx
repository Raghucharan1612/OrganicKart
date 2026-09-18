import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import toast from "react-hot-toast";
import { loginUser, clearAuthError } from "@/store/slices/authSlice";
import Input from "@/components/Input";
import Button from "@/components/Button";
import FormError from "@/components/FormError";
import { validateEmail, validateRequired } from "@/utils/validators";

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { status, error } = useSelector((state) => state.auth);

  const [form, setForm] = useState({ email: "", password: "" });
  const [fieldErrors, setFieldErrors] = useState({});

  const redirectTo = location.state?.from?.pathname || "/";

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) setFieldErrors((prev) => ({ ...prev, [name]: "" }));
    if (error) dispatch(clearAuthError());
  };

  const validate = () => {
    const errors = {
      email: validateEmail(form.email),
      password: validateRequired(form.password, "Password"),
    };
    setFieldErrors(errors);
    return Object.values(errors).every((msg) => !msg);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    const result = await dispatch(loginUser(form));
    if (loginUser.fulfilled.match(result)) {
      toast.success(`Welcome back, ${result.payload.user.full_name}!`);
      navigate(redirectTo, { replace: true });
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <div className="card">
        <h1 className="font-display text-2xl font-bold text-primary-900">Welcome back</h1>
        <p className="mt-1 text-sm text-gray-500">Log in to your OrganicKart account.</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <FormError message={error} />

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
            id="password"
            name="password"
            type="password"
            label="Password"
            placeholder="Your password"
            value={form.password}
            onChange={handleChange}
            error={fieldErrors.password}
          />

          <Button type="submit" isLoading={status === "loading"} className="w-full">
            Log in
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500">
          New to OrganicKart?{" "}
          <Link to="/register" className="font-medium text-primary-700 hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
