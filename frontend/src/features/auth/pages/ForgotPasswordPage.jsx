import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import authService from "@/services/authService";
import Input from "@/components/Input";
import Button from "@/components/Button";
import { useLanguage } from "@/i18n/LanguageContext";
import { getApiErrorMessage } from "@/utils/errorUtils";
import { validateEmail } from "@/utils/validators";

export default function ForgotPasswordPage() {
  const { t } = useLanguage();
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState(searchParams.get("email") || "");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [developmentResetUrl, setDevelopmentResetUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const validationError = validateEmail(email);
    setError(validationError);
    setMessage("");
    setDevelopmentResetUrl("");
    if (validationError) return;

    setIsSubmitting(true);
    try {
      const result = await authService.requestPasswordReset({ email });
      setMessage(t("resetRequestSubmitted"));
      if (result.development_reset_token) {
        setDevelopmentResetUrl(`/reset-password?token=${encodeURIComponent(result.development_reset_token)}`);
      }
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Could not request a password reset."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <div className="card">
        <h1 className="font-display text-2xl font-bold text-primary-900">{t("forgotTitle")}</h1>
        <p className="mt-1 text-sm text-gray-500">{t("forgotDescription")}</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <Input
            id="email"
            name="email"
            type="email"
            label={t("email")}
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            error={error}
          />
          {message && <p role="status" className="rounded-lg border border-green-100 bg-green-50 p-3 text-sm text-green-800">{message}</p>}
          {developmentResetUrl && (
            <Link to={developmentResetUrl} className="inline-flex text-sm font-semibold text-primary-700 hover:underline">
              Open development reset link
            </Link>
          )}
          <Button type="submit" isLoading={isSubmitting} className="w-full">{t("sendResetLink")}</Button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500">
          {t("rememberPassword")} <Link to="/login" className="font-medium text-primary-700 hover:underline">{t("logIn")}</Link>
        </p>
      </div>
    </div>
  );
}