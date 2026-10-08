import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import toast from "react-hot-toast";
import { loginUser, clearAuthError } from "@/store/slices/authSlice";
import Input from "@/components/Input";
import Button from "@/components/Button";
import FormError from "@/components/FormError";
import { useLanguage } from "@/i18n/LanguageContext";
import { validateEmail, validateRequired } from "@/utils/validators";

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { status, error } = useSelector((state) => state.auth);
  const { t } = useLanguage();

  const [form, setForm] = useState({ email: "", password: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

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
        <h1 className="font-display text-2xl font-bold text-primary-900">{t("welcomeBack")}</h1>
        <p className="mt-1 text-sm text-gray-500">{t("loginDescription")}</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <FormError message={error} />

          <Input
            id="email"
            name="email"
            type="email"
            label={t("email")}
            placeholder="you@example.com"
            value={form.email}
            onChange={handleChange}
            error={fieldErrors.email}
          />

          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              label={t("yourPassword")}
              placeholder={t("yourPassword")}
              value={form.password}
              onChange={handleChange}
              error={fieldErrors.password}
              inputClassName="pr-12"
            />
            <button
              type="button"
              onClick={() => setShowPassword((visible) => !visible)}
              aria-label={showPassword ? t("hidePasswords") : t("showPasswords")}
              title={showPassword ? t("hidePasswords") : t("showPasswords")}
              aria-pressed={showPassword}
              className="absolute right-3 top-[2.55rem] flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-5 w-5" aria-hidden="true">
                {showPassword ? (
                  <>
                    <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
                    <circle cx="12" cy="12" r="3" />
                  </>
                ) : (
                  <>
                    <path d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8" />
                    <path d="M9.9 5.2A10.8 10.8 0 0 1 12 5c6.4 0 10 7 10 7a14.7 14.7 0 0 1-3.1 3.8M6.2 6.2C3.5 8.1 2 12 2 12s3.6 7 10 7c1.3 0 2.5-.3 3.6-.8" />
                  </>
                )}
              </svg>
            </button>
          </div>

          <div className="-mt-2 text-right">
            <Link to={`/forgot-password?email=${encodeURIComponent(form.email)}`} className="text-sm font-medium text-primary-700 hover:underline">
              {t("forgotPassword")}
            </Link>
          </div>

          <Button type="submit" isLoading={status === "loading"} className="w-full">
            {t("login")}
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500">
          {t("newToOrganicKart")} {" "}
          <Link to="/register" className="font-medium text-primary-700 hover:underline">
            {t("createAccount")}
          </Link>
        </p>
      </div>
    </div>
  );
}
